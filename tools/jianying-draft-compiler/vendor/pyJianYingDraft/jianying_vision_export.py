"""Vision/OCR-driven Jianying export (fallback when UIA children are empty)."""

from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Optional

from . import jianying_vision as vision
from .jianying_uia import V10

logger = logging.getLogger("jianying_vision_export")


def _newest_video(search_roots: list[Path], *, newer_than: float) -> Optional[Path]:
    best: Optional[tuple[float, Path]] = None
    for root in search_roots:
        if not root.is_dir():
            continue
        for dirpath, _, filenames in os.walk(root):
            # Keep shallow-ish; Jianying export folders are usually flat
            depth = Path(dirpath).relative_to(root).parts
            if len(depth) > 2:
                continue
            for name in filenames:
                lower = name.lower()
                if not lower.endswith((".mp4", ".mov", ".mkv")):
                    continue
                path = Path(dirpath) / name
                try:
                    mtime = path.stat().st_mtime
                except OSError:
                    continue
                if mtime < newer_than - 2:
                    continue
                if best is None or mtime > best[0]:
                    best = (mtime, path)
    return best[1] if best else None


def _default_search_dirs() -> list[Path]:
    home = Path.home()
    vids = home / "Videos"
    return [
        vids,
        home / "Documents" / "JianyingPro Drafts",
        home / "AppData" / "Local" / "JianyingPro",
        Path(os.environ.get("USERPROFILE", str(home))) / "Videos",
    ]


def export_draft_via_vision(
    draft_name: str,
    output_path: str | Path,
    *,
    timeout: float = 600,
    open_wait: float = 12.0,
) -> dict:
    """Open draft on Jianying home via OCR, export, move file to output_path.

    Prerequisites: Jianying Pro visible on home (local drafts list).
    Resolution/framerate are left as Jianying defaults (usually 原始).
    """
    ok, reason = vision.vision_deps_ok()
    if not ok:
        raise RuntimeError(reason)

    outfile = Path(output_path).expanduser().resolve()
    outfile.parent.mkdir(parents=True, exist_ok=True)
    if outfile.exists():
        outfile.unlink()

    t0 = time.time()
    logger.info("vision export start draft=%s out=%s", draft_name, outfile)
    vision.activate_jianying_window()

    # Dismiss tips if any
    vision.try_click_text(V10["got_it"], mode="equals", retries=1, settle=0.6)

    # Open draft card by OCR title
    logger.info("OCR locating draft title: %s", draft_name)
    vision.click_text(
        draft_name,
        mode="draft",
        prefer="any",
        retries=8,
        interval=2.0,
        settle=1.0,
    )
    time.sleep(open_wait)
    vision.activate_jianying_window()
    vision.try_click_text(V10["got_it"], mode="equals", retries=2, settle=0.6)

    # Edit page: top-right 「导出」
    logger.info("OCR click edit-page export (prefer top)")
    vision.click_text(
        V10["export_btn"],
        mode="equals",
        prefer="top",
        region=(0.55, 0.0, 1.0, 0.22),
        retries=8,
        interval=1.5,
        settle=1.0,
    )
    time.sleep(3.0)

    # Export dialog: bottom 「导出」 (not 取消)
    logger.info("OCR click final export (prefer bottom)")
    # Prefer bottom region to avoid re-clicking titlebar export
    vision.click_text(
        V10["export_btn"],
        mode="equals",
        prefer="bottom",
        region=(0.4, 0.7, 1.0, 1.0),
        retries=8,
        interval=1.5,
        settle=1.0,
    )

    export_started = time.time()
    # Wait for success
    succeeded = False
    while time.time() - t0 < timeout:
        vision.activate_jianying_window()
        hits = vision.ocr_screen()
        if vision.find_hits(hits, contains=V10["export_ok_title"]) or vision.find_hits(
            hits, equals=V10["close_btn"]
        ):
            # Prefer 关闭 over 发布 / 查看草稿
            closes = vision.find_hits(hits, equals=V10["close_btn"])
            if closes:
                hit = max(closes, key=lambda h: h.cy)
                vision.click_hit(hit, settle=1.0)
                succeeded = True
                break
            # Fallback: click 导出成功 area then try 关闭 again
            oks = vision.find_hits(hits, contains=V10["export_ok_title"])
            if oks:
                time.sleep(0.5)
                vision.try_click_text(V10["close_btn"], mode="equals", prefer="bottom", retries=3)
                succeeded = True
                break
        # Soft dismiss VIP / 知道了 during export
        vision.try_click_text(V10["got_it"], mode="equals", retries=1, settle=0.3)
        time.sleep(2.0)

    if not succeeded:
        # Maybe dialog already closed; still try to pick file
        logger.warning("Did not observe export-success UI within timeout; scanning for new video")

    roots = _default_search_dirs()
    src = _newest_video(roots, newer_than=export_started)
    if src is None:
        # Broader: any new video since job start
        src = _newest_video(roots, newer_than=t0)
    if src is None:
        raise RuntimeError(
            "视觉导出未找到新生成的视频文件；请检查剪映默认导出目录，或手动导出"
        )

    import shutil

    shutil.move(str(src), str(outfile))
    if not outfile.is_file() or outfile.stat().st_size < 1024:
        raise RuntimeError(f"导出文件无效: {outfile}")

    logger.info("vision export done -> %s (%d bytes)", outfile, outfile.stat().st_size)
    return {
        "ok": True,
        "driver": "vision",
        "draft_name": draft_name,
        "output_mp4": str(outfile),
        "size_bytes": outfile.stat().st_size,
        "elapsed_sec": round(time.time() - t0, 1),
        "source_file": str(src),
    }
