from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Literal

from .paths import ensure_engine_on_path

EffectKind = Literal["all", "scene", "character"]
EffectResolveKind = Literal["auto", "scene", "character"]


@dataclass(frozen=True)
class CatalogEntry:
    name: str
    is_vip: bool | None = None
    kind: str = "unknown"


@dataclass(frozen=True)
class CatalogNameSets:
    transitions: frozenset[str]
    effects: frozenset[str]
    scene_effects: frozenset[str]
    character_effects: frozenset[str]
    text_intros: frozenset[str]
    text_outros: frozenset[str]
    filters: frozenset[str]
    video_intros: frozenset[str]
    video_outros: frozenset[str]
    video_groups: frozenset[str]
    masks: frozenset[str]
    fonts: frozenset[str]
    text_loops: frozenset[str]


def _meta_display_name(meta, *, title: bool = False) -> str:
    return getattr(meta, "title" if title else "name")


def _list_enum(enum_cls, kind: str, *, title: bool = False) -> list[CatalogEntry]:
    items: list[CatalogEntry] = []
    for t in enum_cls:
        meta = t.value
        is_vip = getattr(meta, "is_vip", None)
        if is_vip is None:
            is_vip = bool(getattr(meta, "is_vip", False))
        items.append(
            CatalogEntry(name=_meta_display_name(meta, title=title), is_vip=is_vip, kind=kind)
        )
    return items


def list_transitions() -> list[CatalogEntry]:
    ensure_engine_on_path()
    import pyJianYingDraft as draft

    return _list_enum(draft.TransitionType, "transition")


def list_effects(kind: EffectKind = "all") -> list[CatalogEntry]:
    ensure_engine_on_path()
    from pyJianYingDraft.metadata import VideoCharacterEffectType, VideoSceneEffectType

    items: list[CatalogEntry] = []
    if kind in ("all", "scene"):
        items.extend(_list_enum(VideoSceneEffectType, "scene_effect"))
    if kind in ("all", "character"):
        items.extend(_list_enum(VideoCharacterEffectType, "character_effect"))
    return items


def list_filters() -> list[CatalogEntry]:
    ensure_engine_on_path()
    from pyJianYingDraft.metadata import FilterType

    return _list_enum(FilterType, "filter")


def list_video_intros() -> list[CatalogEntry]:
    ensure_engine_on_path()
    from pyJianYingDraft.metadata import IntroType

    return _list_enum(IntroType, "video_intro", title=True)


def list_video_outros() -> list[CatalogEntry]:
    ensure_engine_on_path()
    from pyJianYingDraft.metadata import OutroType

    return _list_enum(OutroType, "video_outro", title=True)


def list_video_groups() -> list[CatalogEntry]:
    ensure_engine_on_path()
    from pyJianYingDraft.metadata import GroupAnimationType

    return _list_enum(GroupAnimationType, "video_group", title=True)


def list_masks() -> list[CatalogEntry]:
    ensure_engine_on_path()
    from pyJianYingDraft.metadata import MaskType

    return _list_enum(MaskType, "mask")


def list_fonts() -> list[CatalogEntry]:
    ensure_engine_on_path()
    from pyJianYingDraft.metadata import FontType

    return _list_enum(FontType, "font")


def list_text_intros() -> list[CatalogEntry]:
    ensure_engine_on_path()
    from pyJianYingDraft.metadata import TextIntro

    return _list_enum(TextIntro, "text_intro", title=True)


def list_text_outros() -> list[CatalogEntry]:
    ensure_engine_on_path()
    from pyJianYingDraft.metadata import TextOutro

    return _list_enum(TextOutro, "text_outro", title=True)


def list_text_loops() -> list[CatalogEntry]:
    ensure_engine_on_path()
    from pyJianYingDraft.metadata import TextLoopAnim

    return _list_enum(TextLoopAnim, "text_loop", title=True)


@lru_cache(maxsize=1)
def _catalog_name_sets() -> CatalogNameSets:
    scene = frozenset(i.name for i in list_effects(kind="scene"))
    character = frozenset(i.name for i in list_effects(kind="character"))
    return CatalogNameSets(
        transitions=frozenset(i.name for i in list_transitions()),
        effects=scene | character,
        scene_effects=scene,
        character_effects=character,
        text_intros=frozenset(i.name for i in list_text_intros()),
        text_outros=frozenset(i.name for i in list_text_outros()),
        filters=frozenset(i.name for i in list_filters()),
        video_intros=frozenset(i.name for i in list_video_intros()),
        video_outros=frozenset(i.name for i in list_video_outros()),
        video_groups=frozenset(i.name for i in list_video_groups()),
        masks=frozenset(i.name for i in list_masks()),
        fonts=frozenset(i.name for i in list_fonts()),
        text_loops=frozenset(i.name for i in list_text_loops()),
    )


def clear_catalog_cache() -> None:
    _catalog_name_sets.cache_clear()


def normalize_catalog_name(name: str) -> str:
    return (name or "").strip()


def _in_set(name: str, values: frozenset[str]) -> bool:
    n = normalize_catalog_name(name)
    return bool(n) and n in values


def is_transition_name(name: str) -> bool:
    return _in_set(name, _catalog_name_sets().transitions)


def is_effect_name(name: str, *, kind: EffectResolveKind = "auto") -> bool:
    sets = _catalog_name_sets()
    n = normalize_catalog_name(name)
    if not n:
        return False
    if kind == "scene":
        return n in sets.scene_effects
    if kind == "character":
        return n in sets.character_effects
    return n in sets.effects


def is_scene_effect_name(name: str) -> bool:
    return is_effect_name(name, kind="scene")


def is_character_effect_name(name: str) -> bool:
    return is_effect_name(name, kind="character")


def is_text_intro_name(name: str) -> bool:
    return _in_set(name, _catalog_name_sets().text_intros)


def is_text_outro_name(name: str) -> bool:
    return _in_set(name, _catalog_name_sets().text_outros)


def is_filter_name(name: str) -> bool:
    return _in_set(name, _catalog_name_sets().filters)


def is_video_intro_name(name: str) -> bool:
    return _in_set(name, _catalog_name_sets().video_intros)


def is_video_outro_name(name: str) -> bool:
    return _in_set(name, _catalog_name_sets().video_outros)


def is_video_group_name(name: str) -> bool:
    return _in_set(name, _catalog_name_sets().video_groups)


def is_mask_name(name: str) -> bool:
    return _in_set(name, _catalog_name_sets().masks)


def is_font_name(name: str) -> bool:
    return _in_set(name, _catalog_name_sets().fonts)


def is_text_loop_name(name: str) -> bool:
    return _in_set(name, _catalog_name_sets().text_loops)


_SLOT_HINTS: dict[str, str] = {
    "transition": "junctions[].transition",
    "effect": "overlays[].name (type=effect)",
    "scene_effect": "overlays[].name (type=effect, effect_kind=scene)",
    "character_effect": "clips[].character_effect 或 overlays (effect_kind=character)",
    "text_intro": "overlays[].intro (type=text|subtitle)",
    "text_outro": "overlays[].outro (type=text|subtitle)",
    "filter": "clips[].filter",
    "video_intro": "clips[].intro",
    "video_outro": "clips[].outro",
    "video_group": "clips[].group_animation",
    "mask": "clips[].mask",
    "font": "overlays[].font (type=text|subtitle)",
    "text_loop": "overlays[].loop (type=text|subtitle)",
}


def _memberships(name: str) -> dict[str, bool]:
    sets = _catalog_name_sets()
    n = normalize_catalog_name(name)
    return {
        "transition": n in sets.transitions,
        "effect": n in sets.effects,
        "scene_effect": n in sets.scene_effects,
        "character_effect": n in sets.character_effects,
        "text_intro": n in sets.text_intros,
        "text_outro": n in sets.text_outros,
        "filter": n in sets.filters,
        "video_intro": n in sets.video_intros,
        "video_outro": n in sets.video_outros,
        "video_group": n in sets.video_groups,
        "mask": n in sets.masks,
        "font": n in sets.fonts,
        "text_loop": n in sets.text_loops,
    }


def _other_slots(name: str, expected: str) -> list[str]:
    return [slot for slot, present in _memberships(name).items() if present and slot != expected]


def explain_wrong_slot(name: str, *, expected: str) -> str:
    """Human-readable error when a catalog name is used in the wrong Plan field."""
    n = normalize_catalog_name(name)
    m = _memberships(n)
    hint = _SLOT_HINTS.get(expected, expected)

    if expected == "transition":
        if m["effect"] and not m["transition"]:
            return f"'{n}' 是画面特效（effect），不能写在 junctions[].transition；请放到 overlays 且 type=effect"
        if m["filter"]:
            return f"'{n}' 是滤镜，请写在 clips[].filter"
        if m["video_intro"] or m["video_outro"] or m["video_group"]:
            return f"'{n}' 是视频动画，请写在 clips[].intro / outro / group_animation"
        if m["text_intro"] or m["text_outro"] or m["text_loop"]:
            kind = "intro" if m["text_intro"] else ("outro" if m["text_outro"] else "loop")
            return f"'{n}' 是文字{kind}动画，不能当转场；请写在 overlays[].{kind}"
        if not m["transition"]:
            return f"未知转场 '{n}'；请用 `jy-compile catalog --type transitions` 查目录"
    elif expected == "effect":
        if m["transition"] and not m["effect"]:
            return f"'{n}' 是转场（transition），不能写在 overlays type=effect；请放到 junctions[].transition"
        if m["filter"]:
            return f"'{n}' 是滤镜，请写在 clips[].filter"
        if m["video_intro"] or m["video_outro"] or m["video_group"]:
            return f"'{n}' 是视频动画，请写在 clips[].intro / outro / group_animation"
        if m["text_intro"] or m["text_outro"] or m["text_loop"]:
            kind = "intro" if m["text_intro"] else ("outro" if m["text_outro"] else "loop")
            return f"'{n}' 是文字{kind}动画，不能当画面特效；请写在 overlays[].{kind}"
        if not m["effect"]:
            return f"未知特效 '{n}'；请用 `jy-compile catalog --type effects --grep …` 查目录"
    elif expected == "scene_effect":
        if m["character_effect"] and not m["scene_effect"]:
            return f"'{n}' 是人物特效，请写在 clips[].character_effect 或 effect_kind=character"
        if not m["scene_effect"]:
            others = _other_slots(n, "scene_effect")
            if others:
                return f"'{n}' 不是场景特效；它属于 {others[0]}，请写在 {_SLOT_HINTS[others[0]]}"
            return f"未知场景特效 '{n}'；请用 `jy-compile catalog --type effects --kind scene`"
    elif expected == "character_effect":
        if m["scene_effect"] and not m["character_effect"]:
            return f"'{n}' 是场景特效，请写在 overlays type=effect（effect_kind=scene）"
        if not m["character_effect"]:
            others = _other_slots(n, "character_effect")
            if others:
                return f"'{n}' 不是人物特效；它属于 {others[0]}，请写在 {_SLOT_HINTS[others[0]]}"
            return f"未知人物特效 '{n}'；请用 `jy-compile catalog --type effects --kind character`"
    elif expected == "text_intro":
        if m["text_outro"]:
            return f"'{n}' 是文字outro，请写在 overlays[].outro"
        if m["text_loop"]:
            return f"'{n}' 是文字循环动画，请写在 overlays[].loop"
        if m["transition"] or m["effect"] or m["filter"]:
            return f"'{n}' 不是文字intro；转场/特效/滤镜用 junctions / overlays.effect / clips.filter"
        if m["video_intro"]:
            return f"'{n}' 是视频入场动画，请写在 clips[].intro"
        if not m["text_intro"]:
            return f"未知文字intro '{n}'；请用 `jy-compile catalog --type text-intros`"
    elif expected == "text_outro":
        if m["text_intro"]:
            return f"'{n}' 是文字intro，请写在 overlays[].intro"
        if m["text_loop"]:
            return f"'{n}' 是文字循环动画，请写在 overlays[].loop"
        if m["transition"] or m["effect"] or m["filter"]:
            return f"'{n}' 不是文字outro；转场/特效/滤镜用 junctions / overlays.effect / clips.filter"
        if m["video_outro"]:
            return f"'{n}' 是视频出场动画，请写在 clips[].outro"
        if not m["text_outro"]:
            return f"未知文字outro '{n}'；请用 `jy-compile catalog --type text-outros`"
    elif expected == "text_loop":
        if m["text_intro"] or m["text_outro"]:
            kind = "intro" if m["text_intro"] else "outro"
            return f"'{n}' 是文字{kind}，请写在 overlays[].{kind}"
        if not m["text_loop"]:
            others = _other_slots(n, "text_loop")
            if others:
                return f"'{n}' 不是文字循环动画；它属于 {others[0]}，请写在 {_SLOT_HINTS[others[0]]}"
            return f"未知文字循环动画 '{n}'；请用 `jy-compile catalog --type text-loops`"
    elif expected == "filter":
        if not m["filter"]:
            others = _other_slots(n, "filter")
            if others:
                return f"'{n}' 不是滤镜；它属于 {others[0]}，请写在 {_SLOT_HINTS[others[0]]}"
            return f"未知滤镜 '{n}'；请用 `jy-compile catalog --type filters`"
    elif expected == "video_intro":
        if m["video_outro"]:
            return f"'{n}' 是视频出场动画，请写在 clips[].outro"
        if m["video_group"]:
            return f"'{n}' 是视频组合动画，请写在 clips[].group_animation"
        if m["text_intro"]:
            return f"'{n}' 是文字intro，请写在 overlays[].intro"
        if not m["video_intro"]:
            others = _other_slots(n, "video_intro")
            if others:
                return f"'{n}' 不是视频入场动画；它属于 {others[0]}，请写在 {_SLOT_HINTS[others[0]]}"
            return f"未知视频入场动画 '{n}'；请用 `jy-compile catalog --type video-intros`"
    elif expected == "video_outro":
        if m["video_intro"]:
            return f"'{n}' 是视频入场动画，请写在 clips[].intro"
        if m["video_group"]:
            return f"'{n}' 是视频组合动画，请写在 clips[].group_animation"
        if m["text_outro"]:
            return f"'{n}' 是文字outro，请写在 overlays[].outro"
        if not m["video_outro"]:
            others = _other_slots(n, "video_outro")
            if others:
                return f"'{n}' 不是视频出场动画；它属于 {others[0]}，请写在 {_SLOT_HINTS[others[0]]}"
            return f"未知视频出场动画 '{n}'；请用 `jy-compile catalog --type video-outros`"
    elif expected == "video_group":
        if m["video_intro"] or m["video_outro"]:
            kind = "intro" if m["video_intro"] else "outro"
            return f"'{n}' 是视频{kind}动画，请写在 clips[].{kind}"
        if not m["video_group"]:
            others = _other_slots(n, "video_group")
            if others:
                return f"'{n}' 不是视频组合动画；它属于 {others[0]}，请写在 {_SLOT_HINTS[others[0]]}"
            return f"未知视频组合动画 '{n}'；请用 `jy-compile catalog --type video-groups`"
    elif expected == "mask":
        if not m["mask"]:
            others = _other_slots(n, "mask")
            if others:
                return f"'{n}' 不是蒙版；它属于 {others[0]}，请写在 {_SLOT_HINTS[others[0]]}"
            return f"未知蒙版 '{n}'；请用 `jy-compile catalog --type masks`"
    elif expected == "font":
        if not m["font"]:
            others = _other_slots(n, "font")
            if others:
                return f"'{n}' 不是字体；它属于 {others[0]}，请写在 {_SLOT_HINTS[others[0]]}"
            return f"未知字体 '{n}'；请用 `jy-compile catalog --type fonts`"

    return f"catalog name invalid for {hint}: {n}"


def _validate(expected: str, name: str, *, predicate) -> None:
    n = normalize_catalog_name(name)
    if not predicate(n):
        raise ValueError(explain_wrong_slot(n, expected=expected))


def validate_transition_name(name: str) -> None:
    _validate("transition", name, predicate=is_transition_name)


def validate_effect_name(name: str, *, kind: EffectResolveKind = "auto") -> None:
    _validate("effect", name, predicate=lambda n: is_effect_name(n, kind=kind))


def validate_scene_effect_name(name: str) -> None:
    _validate("scene_effect", name, predicate=is_scene_effect_name)


def validate_character_effect_name(name: str) -> None:
    _validate("character_effect", name, predicate=is_character_effect_name)


def validate_text_intro_name(name: str) -> None:
    _validate("text_intro", name, predicate=is_text_intro_name)


def validate_text_outro_name(name: str) -> None:
    _validate("text_outro", name, predicate=is_text_outro_name)


def validate_filter_name(name: str) -> None:
    _validate("filter", name, predicate=is_filter_name)


def validate_video_intro_name(name: str) -> None:
    _validate("video_intro", name, predicate=is_video_intro_name)


def validate_video_outro_name(name: str) -> None:
    _validate("video_outro", name, predicate=is_video_outro_name)


def validate_video_group_name(name: str) -> None:
    _validate("video_group", name, predicate=is_video_group_name)


def validate_mask_name(name: str) -> None:
    _validate("mask", name, predicate=is_mask_name)


def validate_font_name(name: str) -> None:
    _validate("font", name, predicate=is_font_name)


def validate_text_loop_name(name: str) -> None:
    _validate("text_loop", name, predicate=is_text_loop_name)


def _clip_timeline_ranges(plan) -> list[tuple[int, int] | None]:
    """Axis ranges [start_ms, end_ms) per clip; None if out_ms missing (unknown duration)."""
    ranges: list[tuple[int, int] | None] = []
    t = 0
    for clip in plan.clips:
        if clip.out_ms is None:
            ranges.append(None)
            # cannot advance timeline without duration
            break
        dur = max(0, clip.out_ms - clip.in_ms)
        ranges.append((t, t + dur))
        t += dur
    while len(ranges) < len(plan.clips):
        ranges.append(None)
    return ranges


def _ranges_overlap(a0: int, a1: int, b0: int, b1: int, *, min_ms: int = 1) -> bool:
    return min(a1, b1) - max(a0, b0) >= min_ms


def _is_character_overlay(ov) -> bool:
    if ov.effect_kind == "character":
        return True
    if ov.effect_kind == "scene":
        return False
    name = ov.name or ""
    return is_character_effect_name(name) and not is_scene_effect_name(name)


def validate_edit_plan_catalog(plan) -> list[str]:
    """Return catalog/slot errors for an EditPlan. Empty list = OK."""
    errors: list[str] = []

    for j in plan.junctions:
        try:
            validate_transition_name(j.transition)
        except ValueError as e:
            errors.append(f"junctions[after_clip={j.after_clip}].transition: {e}")

    for i, clip in enumerate(plan.clips):
        prefix = f"clips[{i}]"
        if clip.group_animation and (clip.intro or clip.outro):
            errors.append(
                f"{prefix}: group_animation 不能与 intro/outro 同时设置"
            )
        if clip.intro:
            try:
                validate_video_intro_name(clip.intro)
            except ValueError as e:
                errors.append(f"{prefix}.intro: {e}")
        if clip.outro:
            try:
                validate_video_outro_name(clip.outro)
            except ValueError as e:
                errors.append(f"{prefix}.outro: {e}")
        if clip.group_animation:
            try:
                validate_video_group_name(clip.group_animation)
            except ValueError as e:
                errors.append(f"{prefix}.group_animation: {e}")
        if clip.filter:
            try:
                validate_filter_name(clip.filter)
            except ValueError as e:
                errors.append(f"{prefix}.filter: {e}")
        if clip.mask:
            try:
                validate_mask_name(clip.mask)
            except ValueError as e:
                errors.append(f"{prefix}.mask: {e}")
        if clip.character_effect:
            try:
                validate_character_effect_name(clip.character_effect)
            except ValueError as e:
                errors.append(f"{prefix}.character_effect: {e}")

    for i, ov in enumerate(plan.overlays):
        prefix = f"overlays[{i}]"
        if ov.type == "effect":
            try:
                if ov.effect_kind == "scene":
                    validate_scene_effect_name(ov.name or "")
                elif ov.effect_kind == "character":
                    validate_character_effect_name(ov.name or "")
                else:
                    validate_effect_name(ov.name or "")
            except ValueError as e:
                errors.append(f"{prefix}.name: {e}")
        if ov.type in ("text", "subtitle"):
            if ov.intro:
                try:
                    validate_text_intro_name(ov.intro)
                except ValueError as e:
                    errors.append(f"{prefix}.intro: {e}")
            if ov.outro:
                try:
                    validate_text_outro_name(ov.outro)
                except ValueError as e:
                    errors.append(f"{prefix}.outro: {e}")
            if ov.font:
                try:
                    validate_font_name(ov.font)
                except ValueError as e:
                    errors.append(f"{prefix}.font: {e}")
            if ov.loop:
                try:
                    validate_text_loop_name(ov.loop)
                except ValueError as e:
                    errors.append(f"{prefix}.loop: {e}")

    # Per-clip effect budget: ≤1 scene overlay + ≤1 character (clip field or overlay)
    effect_ovs = [
        (i, ov)
        for i, ov in enumerate(plan.overlays)
        if ov.type == "effect" and ov.end_ms > ov.start_ms
    ]
    clip_ranges = _clip_timeline_ranges(plan)
    for ci, span in enumerate(clip_ranges):
        if span is None:
            continue
        t0, t1 = span
        if t1 <= t0:
            continue
        overlapping = [
            (oi, ov)
            for oi, ov in effect_ovs
            if _ranges_overlap(t0, t1, ov.start_ms, ov.end_ms)
        ]
        scene_hits = [
            (oi, ov)
            for oi, ov in overlapping
            if not _is_character_overlay(ov)
        ]
        char_hits = [
            (oi, ov)
            for oi, ov in overlapping
            if _is_character_overlay(ov)
        ]
        if len(scene_hits) > 1:
            names = ", ".join(
                f"overlays[{oi}]={ov.name!r}" for oi, ov in scene_hits
            )
            errors.append(
                f"clips[{ci}]: 同段场景特效过多（最多 1 个），当前: {names}"
            )
        char_total = len(char_hits) + (
            1 if plan.clips[ci].character_effect else 0
        )
        if char_total > 1:
            parts = []
            if plan.clips[ci].character_effect:
                parts.append(f"clips[{ci}].character_effect={plan.clips[ci].character_effect!r}")
            parts.extend(
                f"overlays[{oi}]={ov.name!r}" for oi, ov in char_hits
            )
            errors.append(
                f"clips[{ci}]: 同段人物特效过多（最多 1 个），当前: {', '.join(parts)}"
            )

    # Fallback when trim unknown: any two overlapping scene effect overlays
    if any(span is None for span in clip_ranges) or not plan.clips:
        for a in range(len(effect_ovs)):
            ai, aov = effect_ovs[a]
            if _is_character_overlay(aov):
                continue
            for b in range(a + 1, len(effect_ovs)):
                bi, bov = effect_ovs[b]
                if _is_character_overlay(bov):
                    continue
                if _ranges_overlap(
                    aov.start_ms, aov.end_ms, bov.start_ms, bov.end_ms
                ):
                    errors.append(
                        f"overlays[{ai}] 与 overlays[{bi}] 时间重叠且均为场景特效；"
                        f"同段最多 1 个场景特效（{aov.name!r} / {bov.name!r}）"
                    )

    return errors


def _resolve_meta_enum(enum_cls, name: str, *, kind: str, title: bool = False):
    n = normalize_catalog_name(name)
    try:
        return enum_cls.from_name(n)
    except ValueError:
        pass
    for t in enum_cls:
        meta = t.value
        if _meta_display_name(meta, title=title) == n:
            return t
    loose = n.lower().replace(" ", "").replace("_", "")
    for t in enum_cls:
        meta = t.value
        display = _meta_display_name(meta, title=title)
        if display.lower().replace(" ", "").replace("_", "") == loose:
            return t
    raise KeyError(f"{kind} not found: {name}")


def resolve_transition(name: str):
    ensure_engine_on_path()
    import pyJianYingDraft as draft

    n = normalize_catalog_name(name)
    validate_transition_name(n)
    for t in draft.TransitionType:
        if t.value.name == n:
            return t
    try:
        return draft.TransitionType.from_name(n)
    except ValueError as e:
        raise KeyError(str(e)) from e


def resolve_effect(name: str, *, kind: EffectResolveKind = "auto"):
    ensure_engine_on_path()
    from pyJianYingDraft.metadata import VideoCharacterEffectType, VideoSceneEffectType

    n = normalize_catalog_name(name)
    if kind == "scene":
        validate_scene_effect_name(n)
        search = (VideoSceneEffectType,)
    elif kind == "character":
        validate_character_effect_name(n)
        search = (VideoCharacterEffectType,)
    else:
        validate_effect_name(n)
        search = (VideoSceneEffectType, VideoCharacterEffectType)

    for effect_type in search:
        for member in effect_type:
            if member.value.name == n:
                return member
    raise KeyError(f"effect not found: {n}")


def resolve_character_effect(name: str):
    return resolve_effect(name, kind="character")


def resolve_filter(name: str):
    ensure_engine_on_path()
    from pyJianYingDraft.metadata import FilterType

    n = normalize_catalog_name(name)
    validate_filter_name(n)
    return _resolve_meta_enum(FilterType, n, kind="filter")


def resolve_video_intro(name: str):
    ensure_engine_on_path()
    from pyJianYingDraft.metadata import IntroType

    n = normalize_catalog_name(name)
    validate_video_intro_name(n)
    return _resolve_anim_enum(IntroType, n, "video intro")


def resolve_video_outro(name: str):
    ensure_engine_on_path()
    from pyJianYingDraft.metadata import OutroType

    n = normalize_catalog_name(name)
    validate_video_outro_name(n)
    return _resolve_anim_enum(OutroType, n, "video outro")


def resolve_video_group(name: str):
    ensure_engine_on_path()
    from pyJianYingDraft.metadata import GroupAnimationType

    n = normalize_catalog_name(name)
    validate_video_group_name(n)
    return _resolve_anim_enum(GroupAnimationType, n, "video group")


def resolve_mask(name: str):
    ensure_engine_on_path()
    from pyJianYingDraft.metadata import MaskType

    n = normalize_catalog_name(name)
    validate_mask_name(n)
    return _resolve_meta_enum(MaskType, n, kind="mask")


def resolve_font(name: str):
    ensure_engine_on_path()
    from pyJianYingDraft.metadata import FontType

    n = normalize_catalog_name(name)
    validate_font_name(n)
    return _resolve_meta_enum(FontType, n, kind="font")


def _resolve_anim_enum(enum_cls, name: str, kind: str):
    """Match by enum member name or AnimationMeta.title."""
    try:
        return enum_cls.from_name(name)
    except ValueError:
        pass
    needle = name.strip()
    for t in enum_cls:
        if t.value.title == needle:
            return t
    loose = needle.lower().replace(" ", "").replace("_", "")
    for t in enum_cls:
        if t.value.title.lower().replace(" ", "").replace("_", "") == loose:
            return t
    raise KeyError(f"{kind} not found: {name}")


def resolve_text_intro(name: str):
    ensure_engine_on_path()
    from pyJianYingDraft.metadata import TextIntro

    n = normalize_catalog_name(name)
    validate_text_intro_name(n)
    return _resolve_anim_enum(TextIntro, n, "text intro")


def resolve_text_outro(name: str):
    ensure_engine_on_path()
    from pyJianYingDraft.metadata import TextOutro

    n = normalize_catalog_name(name)
    validate_text_outro_name(n)
    return _resolve_anim_enum(TextOutro, n, "text outro")


def resolve_text_loop(name: str):
    ensure_engine_on_path()
    from pyJianYingDraft.metadata import TextLoopAnim

    n = normalize_catalog_name(name)
    validate_text_loop_name(n)
    return _resolve_anim_enum(TextLoopAnim, n, "text loop")


def list_catalog(
    catalog_type: str,
    *,
    kind: EffectKind = "all",
    grep: str = "",
    free: bool = False,
    limit: int = 0,
) -> list[CatalogEntry]:
    """Unified catalog listing for CLI/API."""
    loaders = {
        "transitions": lambda: list_transitions(),
        "effects": lambda: list_effects(kind=kind),
        "filters": list_filters,
        "video-intros": list_video_intros,
        "video-outros": list_video_outros,
        "video-groups": list_video_groups,
        "masks": list_masks,
        "fonts": list_fonts,
        "text-intros": list_text_intros,
        "text-outros": list_text_outros,
        "text-loops": list_text_loops,
    }
    loader = loaders.get(catalog_type)
    if loader is None:
        raise ValueError(f"unknown catalog type: {catalog_type}")

    items = loader()
    if free:
        items = [i for i in items if not i.is_vip]
    if grep:
        items = [i for i in items if grep in i.name]
    if limit > 0:
        items = items[:limit]
    return items
