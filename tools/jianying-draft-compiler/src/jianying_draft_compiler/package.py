from __future__ import annotations

import json
import zipfile
from pathlib import Path
from typing import Any


def write_manifest(draft_dir: Path, payload: dict[str, Any]) -> Path:
    path = draft_dir / "vidau_manifest.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def zip_draft_dir(draft_dir: Path, zip_path: Path) -> Path:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    if zip_path.exists():
        zip_path.unlink()
    root_name = draft_dir.name
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file in draft_dir.rglob("*"):
            if file.is_file():
                arcname = Path(root_name) / file.relative_to(draft_dir)
                zf.write(file, arcname.as_posix())
    return zip_path
