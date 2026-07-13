from __future__ import annotations

import json
import os
import shutil
import time
import uuid
from pathlib import Path


def _windows_jy_candidates() -> list[Path]:
    home = Path.home()
    local = os.environ.get("LOCALAPPDATA", "")
    candidates: list[Path] = []
    if local:
        base = Path(local)
        candidates.extend(
            [
                base / "JianyingPro/User Data/Projects/com.lveditor.draft",
                base / "CapCut/User Data/Projects/com.lveditor.draft",
            ]
        )
    candidates.extend(
        [
            home / "AppData/Local/JianyingPro/User Data/Projects/com.lveditor.draft",
            home / "AppData/Local/CapCut/User Data/Projects/com.lveditor.draft",
        ]
    )
    return candidates


def detect_jianying_draft_root() -> Path:
    candidates = [
        Path.home() / "Movies/JianyingPro/User Data/Projects/com.lveditor.draft",
        Path.home()
        / "Library/Containers/com.lemon.lvpro/Data/Movies/JianyingPro/User Data/Projects/com.lveditor.draft",
        Path.home() / "Movies/CapCut/User Data/Projects/com.lveditor.draft",
        *_windows_jy_candidates(),
    ]
    # env override
    env = os.environ.get("JIANYING_DRAFT_ROOT") or os.environ.get("VIDAU_JY_DRAFT_ROOT")
    if env:
        candidates.insert(0, Path(env).expanduser())

    for p in candidates:
        if (p / "root_meta_info.json").is_file() or (p / ".recycle_bin").is_dir():
            return p.resolve()
        # Windows: empty root may still exist after install
        if p.is_dir() and any(p.iterdir()):
            return p.resolve()
    raise FileNotFoundError(
        "未找到剪映草稿根目录。请确认已安装剪映专业版，或设置环境变量 "
        "JIANYING_DRAFT_ROOT / VIDAU_JY_DRAFT_ROOT，或传 --jy-root"
    )


def _now_us() -> int:
    return int(time.time() * 1_000_000)


def _patch_draft_meta(draft_dir: Path, draft_name: str, jy_root: Path, duration_us: int) -> str:
    meta_path = draft_dir / "draft_meta_info.json"
    if meta_path.is_file():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            # 新版剪映可能加密该文件；用最小可用元数据覆盖
            meta = {}
    else:
        meta = {}

    draft_id = str(meta.get("draft_id") or str(uuid.uuid4()).upper())
    now = _now_us()
    meta.update(
        {
            "draft_id": draft_id,
            "draft_name": draft_name,
            "draft_fold_path": str(draft_dir),
            "draft_root_path": str(jy_root),
            "draft_cover": str(draft_dir / "draft_cover.jpg"),
            "tm_draft_create": int(meta.get("tm_draft_create") or now),
            "tm_draft_modified": now,
            "tm_draft_removed": 0,
            "tm_duration": int(duration_us),
        }
    )
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=4), encoding="utf-8")
    return draft_id


def _register_root_meta(
    jy_root: Path,
    *,
    draft_dir: Path,
    draft_name: str,
    draft_id: str,
    duration_us: int,
) -> None:
    root_meta_path = jy_root / "root_meta_info.json"
    backup = jy_root / f"root_meta_info.json.bak.{int(time.time())}"
    if root_meta_path.is_file():
        shutil.copy2(root_meta_path, backup)
        root = json.loads(root_meta_path.read_text(encoding="utf-8"))
    else:
        root = {"all_draft_store": [], "draft_ids": 0, "root_path": str(jy_root)}

    store = root.setdefault("all_draft_store", [])
    # drop existing same folder / name
    store[:] = [
        e
        for e in store
        if e.get("draft_fold_path") != str(draft_dir) and e.get("draft_name") != draft_name
    ]

    now = _now_us()
    json_file = draft_dir / "draft_info.json"
    if not json_file.is_file():
        json_file = draft_dir / "draft_content.json"

    entry = {
        "cloud_draft_cover": False,
        "cloud_draft_sync": False,
        "draft_cloud_last_action_download": False,
        "draft_cloud_purchase_info": "",
        "draft_cloud_template_id": "",
        "draft_cloud_tutorial_info": "",
        "draft_cloud_videocut_purchase_info": "",
        "draft_cover": str(draft_dir / "draft_cover.jpg"),
        "draft_fold_path": str(draft_dir),
        "draft_id": draft_id,
        "draft_is_ai_shorts": False,
        "draft_is_cloud_temp_draft": False,
        "draft_is_invisible": False,
        "draft_is_web_article_video": False,
        "draft_json_file": str(json_file),
        "draft_name": draft_name,
        "draft_new_version": "",
        "draft_root_path": str(jy_root),
        "draft_timeline_materials_size": _dir_size(draft_dir),
        "draft_type": "",
        "draft_web_article_video_enter_from": "",
        "streaming_edit_draft_ready": True,
        "tm_draft_cloud_completed": "",
        "tm_draft_cloud_entry_id": -1,
        "tm_draft_cloud_modified": 0,
        "tm_draft_cloud_parent_entry_id": -1,
        "tm_draft_cloud_space_id": -1,
        "tm_draft_cloud_user_id": -1,
        "tm_draft_create": now,
        "tm_draft_modified": now,
        "tm_draft_removed": 0,
        "tm_duration": int(duration_us),
    }
    store.insert(0, entry)
    root["draft_ids"] = len(store)
    root["root_path"] = str(jy_root)
    root_meta_path.write_text(json.dumps(root, ensure_ascii=False, indent=2), encoding="utf-8")


def _dir_size(path: Path) -> int:
    total = 0
    for f in path.rglob("*"):
        if f.is_file():
            total += f.stat().st_size
    return total


def _rewrite_material_paths(draft_dir: Path) -> int:
    """Point media paths at files inside the imported draft (Jianying sandbox).

    Compile writes absolute paths under output/; after copy into Movies/JianyingPro
    those paths are unreachable (「暂无访问权限」). Rewrite any ``path`` that
    ends with a file present under ``draft_dir`` to the local absolute path.
    """
    by_name: dict[str, Path] = {}
    for f in draft_dir.rglob("*"):
        if f.is_file():
            by_name[f.name] = f

    changed = 0

    def walk(node: object) -> None:
        nonlocal changed
        if isinstance(node, list):
            for item in node:
                walk(item)
            return
        if not isinstance(node, dict):
            return
        path_val = node.get("path")
        if isinstance(path_val, str) and path_val:
            name = Path(path_val).name
            local = by_name.get(name)
            if local is not None:
                new_path = str(local.resolve())
                if path_val != new_path:
                    node["path"] = new_path
                    changed += 1
        for v in node.values():
            walk(v)

    for fname in ("draft_content.json", "draft_info.json"):
        path = draft_dir / fname
        if not path.is_file():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        before = changed
        walk(data)
        if changed > before:
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return changed


def _strip_quarantine(draft_dir: Path) -> int:
    """Remove macOS quarantine flags that make Jianying show 暂无访问权限."""
    cleared = 0
    for f in draft_dir.rglob("*"):
        if not f.is_file():
            continue
        try:
            # -c clears all xattrs; prefer targeted delete when possible
            import subprocess

            r = subprocess.run(
                ["xattr", "-d", "com.apple.quarantine", str(f)],
                capture_output=True,
                text=True,
            )
            if r.returncode == 0:
                cleared += 1
        except OSError:
            continue
    return cleared


def _sync_draft_json_pair(draft_dir: Path) -> None:
    """Keep draft_info.json identical to draft_content.json (plaintext).

    Jianying 8.9+ encrypts draft_info on first open and thereafter ignores
    draft_content for media paths. First open must therefore see correct
    paths already present in draft_info.
    """
    content = draft_dir / "draft_content.json"
    info = draft_dir / "draft_info.json"
    if not content.is_file():
        return
    raw = content.read_bytes()
    # validate JSON
    json.loads(raw.decode("utf-8"))
    info.write_bytes(raw)


def _read_duration_us(draft_dir: Path) -> int:
    for name in ("draft_content.json", "draft_info.json"):
        p = draft_dir / name
        if not p.is_file():
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(data.get("duration"), (int, float)):
                return int(data["duration"])
        except json.JSONDecodeError:
            continue
    manifest = draft_dir / "vidau_manifest.json"
    if manifest.is_file():
        data = json.loads(manifest.read_text(encoding="utf-8"))
        return int(data.get("duration_ms", 0)) * 1000
    return 0


def import_draft(
    source_dir: Path | str,
    *,
    jy_root: Path | str | None = None,
    draft_name: str | None = None,
) -> dict:
    """Copy a compiled draft folder into Jianying and register it in root_meta_info.json."""
    source = Path(source_dir).expanduser().resolve()
    if not source.is_dir():
        raise FileNotFoundError(f"draft folder not found: {source}")

    root = Path(jy_root).expanduser().resolve() if jy_root else detect_jianying_draft_root()
    name = draft_name or f"vidau-{source.name}"
    dest = root / name
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(source, dest)

    rewritten = _rewrite_material_paths(dest)
    _sync_draft_json_pair(dest)
    cleared = _strip_quarantine(dest)
    duration_us = _read_duration_us(dest)
    draft_id = _patch_draft_meta(dest, name, root, duration_us)
    _register_root_meta(
        root,
        draft_dir=dest,
        draft_name=name,
        draft_id=draft_id,
        duration_us=duration_us,
    )
    return {
        "imported": str(dest),
        "draft_name": name,
        "paths_rewritten": rewritten,
        "quarantine_cleared": cleared,
        "jy_root": str(root),
    }
