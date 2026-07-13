from __future__ import annotations

import sys
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
VENDOR_ROOT = PACKAGE_ROOT / "vendor"
TEMPLATE_DIR = VENDOR_ROOT / "template_default2"
ENGINE_DIR = VENDOR_ROOT / "pyJianYingDraft"
DEFAULT_OUTPUT_DIR = PACKAGE_ROOT / "output" / "draft"


def ensure_engine_on_path() -> None:
    """Make vendored pyJianYingDraft importable as top-level `pyJianYingDraft`."""
    vendor = str(VENDOR_ROOT)
    if vendor not in sys.path:
        sys.path.insert(0, vendor)
    if not ENGINE_DIR.is_dir():
        raise FileNotFoundError(
            f"Missing vendor engine at {ENGINE_DIR}. Run scripts/sync_vendor.sh"
        )
    if not TEMPLATE_DIR.is_dir():
        raise FileNotFoundError(
            f"Missing draft template at {TEMPLATE_DIR}. Run scripts/sync_vendor.sh"
        )
