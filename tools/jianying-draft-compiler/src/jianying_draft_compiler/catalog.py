from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

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


@lru_cache(maxsize=1)
def _catalog_name_sets() -> tuple[frozenset[str], frozenset[str], frozenset[str], frozenset[str]]:
    """Cached display-name sets: transitions, effects, text_intros, text_outros."""
    return (
        frozenset(i.name for i in list_transitions()),
        frozenset(i.name for i in list_effects()),
        frozenset(i.name for i in list_text_intros()),
        frozenset(i.name for i in list_text_outros()),
    )


def clear_catalog_cache() -> None:
    _catalog_name_sets.cache_clear()


def normalize_catalog_name(name: str) -> str:
    return (name or "").strip()


def is_transition_name(name: str) -> bool:
    n = normalize_catalog_name(name)
    return bool(n) and n in _catalog_name_sets()[0]


def is_effect_name(name: str) -> bool:
    n = normalize_catalog_name(name)
    return bool(n) and n in _catalog_name_sets()[1]


def is_text_intro_name(name: str) -> bool:
    n = normalize_catalog_name(name)
    return bool(n) and n in _catalog_name_sets()[2]


def is_text_outro_name(name: str) -> bool:
    n = normalize_catalog_name(name)
    return bool(n) and n in _catalog_name_sets()[3]


def explain_wrong_slot(name: str, *, expected: str) -> str:
    """Human-readable error when a catalog name is used in the wrong Plan field."""
    n = normalize_catalog_name(name)
    trans, eff, intros, outros = _catalog_name_sets()
    in_t, in_e = n in trans, n in eff
    in_ti, in_to = n in intros, n in outros

    if expected == "transition":
        if in_e and not in_t:
            return (
                f"'{n}' 是画面特效（effect），不能写在 junctions[].transition；"
                f"请放到 overlays 且 type=effect"
            )
        if in_ti or in_to:
            kind = "intro" if in_ti else "outro"
            return (
                f"'{n}' 是文字{kind}动画，不能当转场；"
                f"请写在 overlays[].{kind}（type=text|subtitle）"
            )
        if not in_t:
            return (
                f"未知转场 '{n}'；请用 `jy-compile transitions` 查目录。"
                f"不要把特效名（如边框/胶片）写进 transition"
            )
    if expected == "effect":
        if in_t and not in_e:
            return (
                f"'{n}' 是转场（transition），不能写在 overlays type=effect；"
                f"请放到 junctions[].transition"
            )
        if in_ti or in_to:
            kind = "intro" if in_ti else "outro"
            return (
                f"'{n}' 是文字{kind}动画，不能当画面特效；"
                f"请写在 overlays[].{kind}"
            )
        if not in_e:
            return (
                f"未知特效 '{n}'；请用 `jy-compile effects --grep …` 查目录。"
                f"不要把转场名写进 effect overlay"
            )
    if expected == "text_intro" and not in_ti:
        if in_to:
            return f"'{n}' 是文字outro，请写在 overlays[].outro"
        if in_t or in_e:
            return f"'{n}' 不是文字intro；转场/特效用 junctions / overlays.effect"
        return f"未知文字intro '{n}'；请用 `jy-compile text-animations --kind intro`"
    if expected == "text_outro" and not in_to:
        if in_ti:
            return f"'{n}' 是文字intro，请写在 overlays[].intro"
        if in_t or in_e:
            return f"'{n}' 不是文字outro；转场/特效用 junctions / overlays.effect"
        return f"未知文字outro '{n}'；请用 `jy-compile text-animations --kind outro`"
    return f"catalog name invalid for {expected}: {n}"


def validate_transition_name(name: str) -> None:
    n = normalize_catalog_name(name)
    if not is_transition_name(n):
        raise ValueError(explain_wrong_slot(n, expected="transition"))


def validate_effect_name(name: str) -> None:
    n = normalize_catalog_name(name)
    if not is_effect_name(n):
        raise ValueError(explain_wrong_slot(n, expected="effect"))


def validate_text_intro_name(name: str) -> None:
    n = normalize_catalog_name(name)
    if not is_text_intro_name(n):
        raise ValueError(explain_wrong_slot(n, expected="text_intro"))


def validate_text_outro_name(name: str) -> None:
    n = normalize_catalog_name(name)
    if not is_text_outro_name(n):
        raise ValueError(explain_wrong_slot(n, expected="text_outro"))


def validate_edit_plan_catalog(plan) -> list[str]:
    """Return catalog/slot errors for an EditPlan. Empty list = OK."""
    errors: list[str] = []
    for j in plan.junctions:
        try:
            validate_transition_name(j.transition)
        except ValueError as e:
            errors.append(f"junctions[after_clip={j.after_clip}].transition: {e}")
    for i, ov in enumerate(plan.overlays):
        prefix = f"overlays[{i}]"
        if ov.type == "effect":
            try:
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
    return errors


def resolve_transition(name: str):
    ensure_engine_on_path()
    import pyJianYingDraft as draft

    n = normalize_catalog_name(name)
    validate_transition_name(n)
    # Prefer display-name match (meta.name); fall back to enum member from_name
    for t in draft.TransitionType:
        if t.value.name == n:
            return t
    try:
        return draft.TransitionType.from_name(n)
    except ValueError as e:
        raise KeyError(str(e)) from e


def resolve_effect(name: str):
    ensure_engine_on_path()
    from pyJianYingDraft.metadata import VideoCharacterEffectType, VideoSceneEffectType

    n = normalize_catalog_name(name)
    validate_effect_name(n)
    for effect_type in VideoSceneEffectType:
        if effect_type.value.name == n:
            return effect_type
    for effect_type in VideoCharacterEffectType:
        if effect_type.value.name == n:
            return effect_type
    raise KeyError(f"effect not found: {n}")


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

    n = normalize_catalog_name(name)
    validate_text_intro_name(n)
    return _resolve_anim_enum(TextIntro, n, "text intro")


def resolve_text_outro(name: str):
    ensure_engine_on_path()
    from pyJianYingDraft.metadata import TextOutro

    n = normalize_catalog_name(name)
    validate_text_outro_name(n)
    return _resolve_anim_enum(TextOutro, n, "text outro")
