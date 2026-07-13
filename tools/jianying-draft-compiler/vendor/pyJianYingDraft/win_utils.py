"""Windows helpers for Jianying RPA (standalone; no capcut-mate ``src.utils``)."""

from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path

logger = logging.getLogger("jianying_controller")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)


def trigger_directory_scan_with_robocopy(draft_dir: str | Path) -> None:
    """Best-effort robocopy self-copy to nudge Jianying to rescan local drafts."""
    path = Path(draft_dir)
    if not path.is_dir():
        return
    tmp = Path(str(path) + ".tmp")
    try:
        cmd = [
            "robocopy",
            str(path),
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
    except OSError as exc:
        logger.warning("robocopy scan failed: %r", exc)
    finally:
        if tmp.exists():
            shutil.rmtree(tmp, ignore_errors=True)
