"""UIA selector profiles for Jianying export automation.

legacy: CapCut/Jianying ≤6 (AutomationId / FullDescription from upstream)
v10: Jianying Pro 10.9+ (Chinese visible Name fallbacks from screenshots)
auto: try legacy ids first, then v10 name matching
"""

from __future__ import annotations

import os
from typing import Literal

UiaProfile = Literal["auto", "legacy", "v10"]

# Visible Name strings observed on 10.9.0 Chinese Pro (see references/uia-10.9-from-screenshots.md)
V10 = {
    "export_btn": "导出",
    "cancel_btn": "取消",
    "cancel_export_btn": "取消导出",
    "close_btn": "关闭",
    "got_it": "知道了",
    "exporting": "正在导出",
    "export_ok_title": "导出成功",
    "publish": "发布",
    "view_draft": "查看草稿",
    "local_drafts": "本地草稿",
    "start_create": "开始创作",
    "resolution_original": "原始",
}


def resolve_profile(explicit: str | None = None) -> UiaProfile:
    raw = (explicit or os.environ.get("JY_UIA_PROFILE") or "auto").strip().lower()
    if raw in ("v10", "v10_9", "10.9", "10"):
        return "v10"
    if raw in ("legacy", "v6", "6", "old"):
        return "legacy"
    return "auto"
