from __future__ import annotations

from dataclasses import dataclass

from .paths import ensure_engine_on_path


@dataclass(frozen=True)
class CatalogEntry:
    name: str
    is_vip: bool | None = None
    kind: str = "unknown"


def list_transitions() -> list[CatalogEntry]:
    ensure_engine_on_path()
    import pyJianYingDraft as draft

    items: list[CatalogEntry] = []
    for t in draft.TransitionType:
        meta = t.value
        is_vip = getattr(meta, "is_vip", None)
        items.append(CatalogEntry(name=meta.name, is_vip=is_vip, kind="transition"))
    return items


def list_effects() -> list[CatalogEntry]:
    ensure_engine_on_path()
    from pyJianYingDraft.metadata import VideoCharacterEffectType, VideoSceneEffectType

    items: list[CatalogEntry] = []
    for enum_cls, kind in (
        (VideoSceneEffectType, "scene_effect"),
        (VideoCharacterEffectType, "character_effect"),
    ):
        for t in enum_cls:
            meta = t.value
            is_vip = getattr(meta, "is_vip", None)
            if is_vip is None:
                # EffectMeta often stores vip as 2nd ctor arg / attribute `is_vip` or similar
                is_vip = bool(getattr(meta, "is_vip", False))
            items.append(CatalogEntry(name=meta.name, is_vip=is_vip, kind=kind))
    return items


def list_text_intros() -> list[CatalogEntry]:
    ensure_engine_on_path()
    from pyJianYingDraft.metadata import TextIntro

    items: list[CatalogEntry] = []
    for t in TextIntro:
        meta = t.value
        items.append(CatalogEntry(name=meta.title, is_vip=bool(meta.is_vip), kind="text_intro"))
    return items


def list_text_outros() -> list[CatalogEntry]:
    ensure_engine_on_path()
    from pyJianYingDraft.metadata import TextOutro

    items: list[CatalogEntry] = []
    for t in TextOutro:
        meta = t.value
        items.append(CatalogEntry(name=meta.title, is_vip=bool(meta.is_vip), kind="text_outro"))
    return items


def resolve_transition(name: str):
    ensure_engine_on_path()
    import pyJianYingDraft as draft

    return draft.TransitionType.from_name(name)


def resolve_effect(name: str):
    ensure_engine_on_path()
    from pyJianYingDraft.metadata import VideoCharacterEffectType, VideoSceneEffectType

    for effect_type in VideoSceneEffectType:
        if effect_type.value.name == name:
            return effect_type
    for effect_type in VideoCharacterEffectType:
        if effect_type.value.name == name:
            return effect_type
    raise KeyError(f"effect not found: {name}")


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
    # loose: ignore spaces/underscores on title
    loose = needle.lower().replace(" ", "").replace("_", "")
    for t in enum_cls:
        if t.value.title.lower().replace(" ", "").replace("_", "") == loose:
            return t
    raise KeyError(f"{kind} not found: {name}")


def resolve_text_intro(name: str):
    ensure_engine_on_path()
    from pyJianYingDraft.metadata import TextIntro

    return _resolve_anim_enum(TextIntro, name, "text intro")


def resolve_text_outro(name: str):
    ensure_engine_on_path()
    from pyJianYingDraft.metadata import TextOutro

    return _resolve_anim_enum(TextOutro, name, "text outro")
