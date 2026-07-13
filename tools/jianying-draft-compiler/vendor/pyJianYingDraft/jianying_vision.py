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


def activate_jianying_window() -> bool:
    """Bring Jianying/CapCut main window to foreground via Win32 (no UIA tree)."""
    try:
        import win32con
        import win32gui
    except ImportError:
        logger.warning("win32gui unavailable; cannot activate Jianying window")
        return False

    keywords = ("剪映", "Jianying", "CapCut", "Capcut")
    found: list[int] = []

    def _enum(hwnd: int, _: None) -> None:
        if not win32gui.IsWindowVisible(hwnd):
            return
        title = win32gui.GetWindowText(hwnd) or ""
        if any(k in title for k in keywords):
            # Skip tiny tool windows
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

    hwnd = found[0]
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
    except Exception as exc:
        logger.warning("SetForegroundWindow failed: %r", exc)
        return False
    time.sleep(0.6)
    return True


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
    """Loose match for draft titles (ellipsis / truncation / OCR noise)."""
    ui = re.sub(r"\s+", "", ui_text or "")
    t = re.sub(r"\s+", "", target or "")
    if not ui or not t:
        return False
    if ui == t or t in ui or ui in t:
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
    if ui_alnum and t_alnum and (ui_alnum in t_alnum or t_alnum in ui_alnum):
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


def click_hit(hit: OcrHit, *, settle: float = 0.4) -> None:
    click_xy(hit.cx, hit.cy, settle=settle)


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
) -> OcrHit:
    """Find needle on screen via OCR and click it.

    prefer: any | top | bottom | right | left
    region: normalized (x0,y0,x1,y1) in 0..1 of full screen
    """
    last_err = f"OCR 未找到文案: {needle}"
    for attempt in range(retries):
        activate_jianying_window()
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
            click_hit(hit, settle=settle)
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
