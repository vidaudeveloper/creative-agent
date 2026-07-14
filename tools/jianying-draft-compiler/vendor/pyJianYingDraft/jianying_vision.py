"""Screen OCR + click helpers for Jianying RPA when UIA tree is empty.

Requires Windows extras: pyautogui, Pillow, rapidocr-onnxruntime (optional until used).
"""

from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass
from typing import Callable, Iterable, Optional

logger = logging.getLogger("jianying_vision")

try:
    import pyautogui
except ImportError:  # pragma: no cover
    pyautogui = None  # type: ignore

# Short OCR needles (e.g. "vest") must not reverse-match into longer unrelated words.
_SHORT_NAME_MAX_LEN = 6
# Home draft card: title sits under thumbnail — click above the OCR text box.
_DEFAULT_DRAFT_CLICK_OFFSET_Y = -80


@dataclass(frozen=True)
class OcrHit:
    text: str
    conf: float
    cx: int
    cy: int
    x0: int
    y0: int
    x1: int
    y1: int


_OCR_ENGINE = None


def vision_deps_ok() -> tuple[bool, str]:
    if pyautogui is None:
        return False, "缺少 pyautogui"
    try:
        import PIL  # noqa: F401
    except ImportError:
        return False, "缺少 Pillow"
    try:
        from rapidocr_onnxruntime import RapidOCR  # noqa: F401
    except ImportError:
        return False, "缺少 rapidocr-onnxruntime（uv sync --extra windows）"
    return True, "ok"


def _get_ocr():
    global _OCR_ENGINE
    if _OCR_ENGINE is None:
        from rapidocr_onnxruntime import RapidOCR

        _OCR_ENGINE = RapidOCR()
    return _OCR_ENGINE


def _is_jianying_title(title: str) -> bool:
    keywords = ("剪映", "Jianying", "CapCut", "Capcut")
    return any(k in (title or "") for k in keywords)


def _foreground_is_jianying() -> bool:
    try:
        import win32gui
    except ImportError:
        return False
    try:
        hwnd = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(hwnd) or ""
    except Exception:
        return False
    return _is_jianying_title(title)


def _alt_tab_nudge() -> None:
    """Best-effort focus steal: Alt briefly held then released (allows SetForegroundWindow)."""
    if pyautogui is None:
        return
    try:
        pyautogui.keyDown("alt")
        time.sleep(0.05)
        pyautogui.keyUp("alt")
        time.sleep(0.15)
    except Exception as exc:
        logger.warning("Alt nudge failed: %r", exc)


def activate_jianying_window(*, max_retries: int = 3) -> bool:
    """Bring Jianying/CapCut main window to foreground via Win32 (no UIA tree).

    Windows often blocks bare SetForegroundWindow from background processes.
    Strategy: SW_MAXIMIZE + BringWindowToTop + SetForegroundWindow, verify
    foreground title, then Alt nudge + retry (up to max_retries).
    """
    try:
        import win32con
        import win32gui
        import win32process
    except ImportError:
        logger.warning("win32gui unavailable; cannot activate Jianying window")
        return False

    found: list[int] = []

    def _enum(hwnd: int, _: None) -> None:
        if not win32gui.IsWindowVisible(hwnd):
            return
        title = win32gui.GetWindowText(hwnd) or ""
        if not _is_jianying_title(title):
            return
        try:
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        except Exception:
            return
        if (right - left) < 400 or (bottom - top) < 300:
            return
        found.append(hwnd)

    win32gui.EnumWindows(_enum, None)
    if not found:
        logger.warning("No Jianying window found by title")
        return False

    # Prefer largest area (main frame over tiny popups)
    def _area(hwnd: int) -> int:
        try:
            l, t, r, b = win32gui.GetWindowRect(hwnd)
            return max(0, r - l) * max(0, b - t)
        except Exception:
            return 0

    hwnd = max(found, key=_area)
    title = win32gui.GetWindowText(hwnd) or ""

    for attempt in range(1, max_retries + 1):
        try:
            # Allow foreground switch from this process when possible
            try:
                import ctypes

                ctypes.windll.user32.AllowSetForegroundWindow(-1)  # ASFW_ANY
            except Exception:
                pass

            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
            try:
                win32gui.BringWindowToTop(hwnd)
            except Exception:
                pass
            try:
                # Attach thread input trick for stubborn focus
                fg = win32gui.GetForegroundWindow()
                cur_tid = win32process.GetCurrentThreadId()
                fg_tid, _ = win32process.GetWindowThreadProcessId(fg) if fg else (0, 0)
                tgt_tid, _ = win32process.GetWindowThreadProcessId(hwnd)
                if fg_tid and fg_tid != cur_tid:
                    win32process.AttachThreadInput(cur_tid, fg_tid, True)
                if tgt_tid and tgt_tid != cur_tid:
                    win32process.AttachThreadInput(cur_tid, tgt_tid, True)
                win32gui.SetForegroundWindow(hwnd)
                if fg_tid and fg_tid != cur_tid:
                    win32process.AttachThreadInput(cur_tid, fg_tid, False)
                if tgt_tid and tgt_tid != cur_tid:
                    win32process.AttachThreadInput(cur_tid, tgt_tid, False)
            except Exception as exc:
                logger.warning("SetForegroundWindow attempt %d: %r", attempt, exc)
                try:
                    win32gui.SetForegroundWindow(hwnd)
                except Exception:
                    pass

            time.sleep(0.5)
            if _foreground_is_jianying():
                logger.info(
                    "Jianying foreground OK (attempt %d): %r", attempt, title
                )
                return True

            logger.warning(
                "Jianying not foreground after activate attempt %d/%d (fg may be Hermes/other)",
                attempt,
                max_retries,
            )
            _alt_tab_nudge()
            try:
                win32gui.SetForegroundWindow(hwnd)
            except Exception:
                pass
            time.sleep(0.4)
            if _foreground_is_jianying():
                logger.info("Jianying foreground OK after Alt nudge (attempt %d)", attempt)
                return True
        except Exception as exc:
            logger.warning("activate_jianying_window attempt %d failed: %r", attempt, exc)
            time.sleep(0.3)

    logger.error(
        "Failed to activate Jianying window after %d attempts; OCR may capture wrong window",
        max_retries,
    )
    return False


def screenshot_bgr():
    """Return full-screen screenshot as RGB numpy array (same coords as pyautogui.click)."""
    import numpy as np

    if pyautogui is None:
        raise RuntimeError("pyautogui missing")
    img = pyautogui.screenshot()
    return np.array(img.convert("RGB"))


def ocr_screen(*, retries: int = 2) -> list[OcrHit]:
    ok, reason = vision_deps_ok()
    if not ok:
        raise RuntimeError(reason)
    engine = _get_ocr()
    last: list[OcrHit] = []
    for attempt in range(retries):
        img = screenshot_bgr()
        result, _ = engine(img)
        hits: list[OcrHit] = []
        if result:
            for item in result:
                box, text, score = item[0], str(item[1]).strip(), float(item[2])
                xs = [p[0] for p in box]
                ys = [p[1] for p in box]
                x0, x1 = int(min(xs)), int(max(xs))
                y0, y1 = int(min(ys)), int(max(ys))
                hits.append(
                    OcrHit(
                        text=text,
                        conf=score,
                        cx=(x0 + x1) // 2,
                        cy=(y0 + y1) // 2,
                        x0=x0,
                        y0=y0,
                        x1=x1,
                        y1=y1,
                    )
                )
        last = hits
        logger.info("OCR attempt %d: %d text boxes", attempt + 1, len(hits))
        if hits:
            return hits
        time.sleep(0.5)
    return last


def names_match(ui_text: str, target: str) -> bool:
    """Loose match for draft titles (ellipsis / truncation / OCR noise).

    Short targets (len <= 6, e.g. ``vest``): exact / token-boundary only —
    forbid bare substring (``vest`` in ``investigate``) and reverse ``ui in t``.
    """
    ui = re.sub(r"\s+", "", ui_text or "")
    t = re.sub(r"\s+", "", target or "")
    if not ui or not t:
        return False
    if ui == t:
        return True

    short = len(t) <= _SHORT_NAME_MAX_LEN

    def _token_boundary_contains(hay: str, needle: str) -> bool:
        """True if needle appears as a token in hay (not mid-word)."""
        if not needle or needle not in hay:
            return False
        # Prefer delimiter-aware match on original-ish separators
        pattern = (
            r"(?i)(?:^|[^0-9a-zA-Z\u4e00-\u9fff])"
            + re.escape(needle)
            + r"(?:$|[^0-9a-zA-Z\u4e00-\u9fff])"
        )
        if re.search(pattern, hay):
            return True
        # Alnum-only forms: still require boundary in stripped string via lookaround
        h = re.sub(r"[^0-9a-zA-Z\u4e00-\u9fff]", "", hay)
        n = re.sub(r"[^0-9a-zA-Z\u4e00-\u9fff]", "", needle)
        if not n or n not in h:
            return False
        pattern2 = r"(?i)(?<![0-9a-zA-Z])" + re.escape(n) + r"(?![0-9a-zA-Z])"
        return re.search(pattern2, h) is not None

    if short:
        # Short needle: exact already handled; allow token match in longer draft titles
        # e.g. "vest" in "mens-vest-remix", but NOT in "investigate"
        return _token_boundary_contains(ui, t)

    if t in ui or ui in t:
        return True

    for ell in ("...", "…", "⋯", "..", "．"):
        if ell in ui:
            left, _, right = ui.partition(ell)
            if left and t.startswith(left) and (not right or t.endswith(right)):
                return True
        if ui.endswith(ell):
            prefix = ui[: -len(ell)]
            if len(prefix) >= 4 and t.startswith(prefix):
                return True

    # OCR often drops dashes/underscores
    ui_alnum = re.sub(r"[^0-9a-zA-Z\u4e00-\u9fff]", "", ui)
    t_alnum = re.sub(r"[^0-9a-zA-Z\u4e00-\u9fff]", "", t)
    if ui_alnum and t_alnum:
        if t_alnum in ui_alnum or ui_alnum in t_alnum:
            return True

    if len(ui) >= 6 and len(ui) < len(t) and t.startswith(ui):
        return True
    return False


def find_hits(
    hits: Iterable[OcrHit],
    *,
    equals: Optional[str] = None,
    contains: Optional[str] = None,
    match_fn: Optional[Callable[[str], bool]] = None,
    min_conf: float = 0.4,
) -> list[OcrHit]:
    out: list[OcrHit] = []
    for h in hits:
        if h.conf < min_conf:
            continue
        text = h.text
        ok = False
        if match_fn is not None:
            ok = match_fn(text)
        elif equals is not None:
            ok = text == equals or names_match(text, equals)
        elif contains is not None:
            ok = contains in text
        if ok:
            out.append(h)
    return out


def click_xy(x: int, y: int, *, settle: float = 0.4) -> None:
    if pyautogui is None:
        raise RuntimeError("pyautogui missing")
    logger.info("vision click (%d, %d)", x, y)
    pyautogui.click(x=x, y=y, button="left")
    time.sleep(settle)


def click_hit(
    hit: OcrHit,
    *,
    settle: float = 0.4,
    click_offset_x: int = 0,
    click_offset_y: int = 0,
) -> None:
    """Click hit center, optionally offset (e.g. draft title → thumbnail above)."""
    x = hit.cx + click_offset_x
    y = hit.cy + click_offset_y
    if click_offset_x or click_offset_y:
        logger.info(
            "vision click offset from text=%r center=(%d,%d) -> (%d,%d)",
            hit.text,
            hit.cx,
            hit.cy,
            x,
            y,
        )
    click_xy(x, y, settle=settle)


def click_text(
    needle: str,
    *,
    mode: str = "equals",
    prefer: str = "any",
    region: Optional[tuple[float, float, float, float]] = None,
    screen_size: Optional[tuple[int, int]] = None,
    retries: int = 3,
    interval: float = 1.0,
    settle: float = 0.5,
    click_offset_x: int = 0,
    click_offset_y: int = 0,
    require_jianying_fg: bool = True,
) -> OcrHit:
    """Find needle on screen via OCR and click it.

    prefer: any | top | bottom | right | left
    region: normalized (x0,y0,x1,y1) in 0..1 of full screen
    click_offset_*: pixel delta from OCR text center (draft cards: y=-80)
    """
    last_err = f"OCR 未找到文案: {needle}"
    for attempt in range(retries):
        activated = activate_jianying_window()
        if require_jianying_fg and not activated and not _foreground_is_jianying():
            last_err = (
                f"无法将剪映置于前台，OCR 可能截到其它窗口（attempt {attempt + 1}/{retries}）"
            )
            logger.warning(last_err)
            time.sleep(interval)
            continue

        hits = ocr_screen()
        if mode == "contains":
            matched = find_hits(hits, contains=needle)
        elif mode == "draft":
            matched = find_hits(hits, match_fn=lambda t: names_match(t, needle))
        else:
            matched = find_hits(hits, equals=needle)

        if region is not None and matched:
            if screen_size is not None:
                w, h = screen_size
            elif pyautogui is not None:
                w, h = pyautogui.size()
            else:
                w = h = 0
            if w and h:
                rx0, ry0, rx1, ry1 = region
                x0, y0, x1, y1 = int(rx0 * w), int(ry0 * h), int(rx1 * w), int(ry1 * h)
                matched = [m for m in matched if x0 <= m.cx <= x1 and y0 <= m.cy <= y1]

        if matched:
            hit = _pick(matched, prefer)
            # Draft mode default: click thumbnail above title text
            ox, oy = click_offset_x, click_offset_y
            if mode == "draft" and ox == 0 and oy == 0:
                oy = _DEFAULT_DRAFT_CLICK_OFFSET_Y
            click_hit(hit, settle=settle, click_offset_x=ox, click_offset_y=oy)
            return hit
        last_err = f"OCR 未找到文案: {needle} (attempt {attempt + 1}/{retries})"
        logger.info(last_err)
        time.sleep(interval)
    raise RuntimeError(last_err)


def _pick(hits: list[OcrHit], prefer: str) -> OcrHit:
    if prefer == "top":
        return min(hits, key=lambda h: h.cy)
    if prefer == "bottom":
        return max(hits, key=lambda h: h.cy)
    if prefer == "right":
        return max(hits, key=lambda h: h.cx)
    if prefer == "left":
        return min(hits, key=lambda h: h.cx)
    return hits[0]


def screen_has(text: str, *, mode: str = "contains", retries: int = 1) -> bool:
    for _ in range(retries):
        hits = ocr_screen()
        if mode == "equals":
            if find_hits(hits, equals=text):
                return True
        else:
            if find_hits(hits, contains=text):
                return True
        time.sleep(0.3)
    return False


def try_click_text(needle: str, **kwargs) -> bool:
    try:
        click_text(needle, **kwargs)
        return True
    except RuntimeError:
        return False
