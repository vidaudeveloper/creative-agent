from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

from .import_draft import detect_jianying_draft_root
from .paths import ensure_engine_on_path


def is_windows() -> bool:
    return sys.platform == "win32"


def export_supported() -> tuple[bool, str]:
    if not is_windows():
        return False, "自动导出仅支持 Windows（剪映 UI 自动化）"
    try:
        ensure_engine_on_path()
        import pyJianYingDraft as draft  # noqa: F401
    except Exception as e:
        return False, f"engine unavailable: {e}"
    try:
        import uiautomation  # noqa: F401
        import pyautogui  # noqa: F401
    except ImportError:
        return (
            False,
            "缺少 Windows 依赖。请执行: uv sync --extra windows  （或 pip install uiautomation pyautogui pywin32）",
        )
    return True, "ok"


def _trigger_directory_scan(draft_dir: Path) -> None:
    """Best-effort: robocopy self-copy to nudge Jianying to rescan drafts."""
    if not is_windows() or not draft_dir.is_dir():
        return
    tmp = Path(str(draft_dir) + ".tmp")
    try:
        cmd = [
            "robocopy",
            str(draft_dir),
            str(tmp),
            "/E",
            "/COPY:DAT",
            "/R:1",
            "/W:1",
            "/NP",
            "/NJH",
            "/NJS",
        ]
        subprocess.run(cmd, check=False, capture_output=True)
    finally:
        if tmp.exists():
            shutil.rmtree(tmp, ignore_errors=True)


def export_draft_to_mp4(
    draft_name: str,
    output_mp4: Path | str,
    *,
    jy_root: Path | str | None = None,
    resolution: str | None = "1080P",
    framerate: str | None = None,
    timeout: float = 600,
) -> dict:
    """
    Windows-only: drive Jianying UI to export an already-imported draft.

    Prerequisites:
    - Draft folder exists at ``{jy_root}/{draft_name}/``
    - JianyingPro is running and on the home page
    - Windows extras installed
    """
    ok, reason = export_supported()
    if not ok:
        raise RuntimeError(reason)

    root = Path(jy_root).expanduser().resolve() if jy_root else detect_jianying_draft_root()
    draft_dir = root / draft_name
    if not draft_dir.is_dir():
        raise FileNotFoundError(f"草稿目录不存在: {draft_dir}（请先 jy-compile import）")

    outfile = Path(output_mp4).expanduser().resolve()
    outfile.parent.mkdir(parents=True, exist_ok=True)
    if outfile.exists():
        outfile.unlink()

    _trigger_directory_scan(draft_dir)

    ensure_engine_on_path()
    import pyJianYingDraft as draft
    from pyJianYingDraft.jianying_controller import ExportFramerate, ExportResolution
    from uiautomation import UIAutomationInitializerInThread

    if draft.JianyingController is None:
        raise RuntimeError("JianyingController 不可用（非 Windows 或缺少依赖）")

    res_enum = None
    if resolution:
        raw = resolution.strip().upper().replace(" ", "")
        for e in ExportResolution:
            if e.value.upper() == raw or e.name == raw or e.name == f"RES_{raw}":
                res_enum = e
                break
        if res_enum is None:
            raise ValueError(f"unknown resolution: {resolution}")

    fps_enum = None
    if framerate:
        fraw = str(framerate).strip().lower().replace(" ", "")
        if fraw.isdigit():
            fraw = f"{fraw}fps"
        for e in ExportFramerate:
            if e.value.lower() == fraw or e.name.lower() == fraw:
                fps_enum = e
                break
        if fps_enum is None:
            raise ValueError(f"unknown framerate: {framerate}")

    with UIAutomationInitializerInThread():
        ctrl = draft.JianyingController()
        ctrl.export_draft(
            draft_name,
            str(outfile),
            resolution=res_enum,
            framerate=fps_enum,
            timeout=timeout,
            draft_dir=str(draft_dir),
        )

    if not outfile.is_file() or outfile.stat().st_size < 1024:
        raise RuntimeError(f"导出未生成有效文件: {outfile}")

    return {
        "ok": True,
        "draft_name": draft_name,
        "draft_dir": str(draft_dir),
        "output_mp4": str(outfile),
        "size_bytes": outfile.stat().st_size,
        "platform": "win32",
    }
