from __future__ import annotations

import shutil
import uuid
from pathlib import Path
from urllib.parse import urlparse

import requests


def ms_to_us(ms: int) -> int:
    return int(ms) * 1000


def us_to_ms(us: int) -> int:
    return int(us) // 1000


def ensure_local_media(source_path: str | None, source_url: str | None, dest_dir: Path) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    if source_path:
        src = Path(source_path).expanduser().resolve()
        if not src.is_file():
            raise FileNotFoundError(f"media not found: {src}")
        dest = dest_dir / src.name
        if src.resolve() != dest.resolve():
            shutil.copy2(src, dest)
        return dest

    assert source_url
    parsed = urlparse(source_url)
    name = Path(parsed.path).name or f"media_{uuid.uuid4().hex[:8]}.mp4"
    dest = dest_dir / name
    with requests.get(source_url, stream=True, timeout=120) as resp:
        resp.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in resp.iter_content(chunk_size=1024 * 256):
                if chunk:
                    f.write(chunk)
    return dest
