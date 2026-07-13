from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import AliasChoices, BaseModel, Field, model_validator


class AspectRatio(str, Enum):
    RATIO_9_16 = "9:16"
    RATIO_16_9 = "16:9"
    RATIO_1_1 = "1:1"


ASPECT_SIZE: dict[str, tuple[int, int]] = {
    "9:16": (1080, 1920),
    "16:9": (1920, 1080),
    "1:1": (1080, 1080),
}


class ClipSpec(BaseModel):
    """One source clip. Prefer local `path`; `url` is downloaded into the draft assets."""

    path: str | None = None
    url: str | None = None
    in_ms: int = Field(0, ge=0, description="Trim start in source, milliseconds")
    out_ms: int | None = Field(
        None,
        description="Trim end in source, milliseconds; default = full media duration",
    )

    @model_validator(mode="after")
    def require_source(self) -> ClipSpec:
        if not self.path and not self.url:
            raise ValueError("clip needs either path or url")
        if self.out_ms is not None and self.out_ms <= self.in_ms:
            raise ValueError("out_ms must be > in_ms")
        return self


class JunctionSpec(BaseModel):
    """Transition between clip[i] and clip[i+1]. Applied on the preceding clip."""

    after_clip: int = Field(..., ge=0, description="Index of the clip that ends before the cut")
    transition: str = Field(..., min_length=1, description="Jianying transition name, e.g. 竖向模糊")
    duration_ms: int = Field(500, gt=0, description="Transition duration in milliseconds")


class OverlaySpec(BaseModel):
    """Visual overlay: scene effect, text/subtitle, or sticker (local image / resource_id)."""

    type: Literal["effect", "text", "subtitle", "sticker"] = "effect"
    name: str | None = Field(None, description="Effect catalog name when type=effect")
    text: str | None = Field(None, description="Caption content when type=text|subtitle")
    path: str | None = Field(None, description="Local sticker image path (png/jpg/webp/gif)")
    url: str | None = Field(None, description="Remote sticker image URL")
    resource_id: str | None = Field(None, description="Jianying built-in sticker resource_id")
    start_ms: int = Field(0, ge=0)
    end_ms: int = Field(..., gt=0)
    # typography / layout
    font_size: float = Field(8.0, gt=0, description="Jianying text size (subtitle ~7–9, title ~10–14)")
    color: list[float] = Field(
        default_factory=lambda: [1.0, 1.0, 1.0],
        description="RGB in 0–1",
    )
    bold: bool = False
    align: Literal[0, 1, 2] = Field(1, description="0 left / 1 center / 2 right")
    transform_x: float = Field(0.0, description="X offset in half-canvas units")
    transform_y: float | None = Field(
        None,
        description="Y offset in half-canvas units; default subtitle=-0.75, text=0, sticker=0.55",
    )
    scale: float = Field(0.45, gt=0, description="Sticker scale (image overlay)")
    border: bool = Field(True, description="Dark stroke for text readability")
    # rich text (jcaigc add_text_style style)
    keywords: str | list[str] | None = Field(
        None,
        description='Highlight keywords; pipe string "A|B" or list ["A","B"] (alias: keyword)',
        validation_alias=AliasChoices("keywords", "keyword"),
    )
    keyword_color: str | list[float] = Field(
        default="#ff7100",
        description="Keyword color: #RRGGBB or [r,g,b] 0–1",
    )
    keyword_font_size: float | None = Field(
        None,
        gt=0,
        description="Keyword size; default ≈ font_size+2",
    )
    # text animations (vendor TextIntro / TextOutro catalog names)
    intro: str | None = Field(None, description="Text intro animation name, e.g. 渐显 / 弹入")
    outro: str | None = Field(None, description="Text outro animation name, e.g. 渐隐 / 弹出")
    intro_duration_ms: int | None = Field(None, ge=0, description="Override intro duration (ms)")
    outro_duration_ms: int | None = Field(None, ge=0, description="Override outro duration (ms)")

    model_config = {"populate_by_name": True}

    @model_validator(mode="after")
    def range_and_payload_ok(self) -> OverlaySpec:
        if self.end_ms <= self.start_ms:
            raise ValueError("overlay end_ms must be > start_ms")
        if self.type == "effect":
            if not self.name:
                raise ValueError("effect overlay needs name")
        elif self.type in ("text", "subtitle"):
            if not (self.text and self.text.strip()):
                raise ValueError(f"{self.type} overlay needs text")
            if len(self.color) != 3:
                raise ValueError("color must be [r,g,b] with 3 floats in 0–1")
            if isinstance(self.keyword_color, list) and len(self.keyword_color) != 3:
                raise ValueError("keyword_color list must be [r,g,b]")
        elif self.type == "sticker":
            if not self.path and not self.url and not self.resource_id:
                raise ValueError("sticker overlay needs path, url, or resource_id")
        return self


class BgmSpec(BaseModel):
    """Background music on an audio track (local file or downloadable URL)."""

    path: str | None = None
    url: str | None = None
    in_ms: int = Field(0, ge=0, description="Trim start inside the audio file")
    out_ms: int | None = Field(None, description="Trim end inside the audio file; default = full file")
    start_ms: int = Field(0, ge=0, description="Timeline start; default 0")
    end_ms: int | None = Field(
        None,
        description="Timeline end; default = full video duration",
    )
    volume: float = Field(0.35, ge=0, le=2.0, description="1.0 = original; BGM often 0.25–0.45")
    fade_in_ms: int = Field(400, ge=0)
    fade_out_ms: int = Field(800, ge=0)
    loop: bool = Field(True, description="If audio shorter than timeline span, tile until end")

    @model_validator(mode="after")
    def require_source(self) -> BgmSpec:
        if not self.path and not self.url:
            raise ValueError("bgm needs either path or url")
        if self.out_ms is not None and self.out_ms <= self.in_ms:
            raise ValueError("bgm out_ms must be > in_ms")
        if self.end_ms is not None and self.end_ms <= self.start_ms:
            raise ValueError("bgm end_ms must be > start_ms")
        return self


class EditPlan(BaseModel):
    """Director output — renderer-agnostic edit intent."""

    aspect: AspectRatio | str = AspectRatio.RATIO_9_16
    width: int | None = None
    height: int | None = None
    clips: list[ClipSpec] = Field(..., min_length=1)
    junctions: list[JunctionSpec] = Field(default_factory=list)
    overlays: list[OverlaySpec] = Field(default_factory=list)
    bgm: BgmSpec | None = None
    mute_original_audio: bool | None = Field(
        None,
        description="Mute video clip audio. None=auto (mute when bgm is set; keep when no bgm)",
    )
    title: str = "vidau-p0"

    def canvas_size(self) -> tuple[int, int]:
        if self.width and self.height:
            return self.width, self.height
        key = self.aspect.value if isinstance(self.aspect, AspectRatio) else str(self.aspect)
        if key not in ASPECT_SIZE:
            raise ValueError(f"unknown aspect {key}; set width/height explicitly")
        return ASPECT_SIZE[key]


class CompileResult(BaseModel):
    draft_id: str
    draft_dir: str
    zip_path: str | None = None
    duration_ms: int
    width: int
    height: int
    warnings: list[str] = Field(default_factory=list)
    manifest_path: str
