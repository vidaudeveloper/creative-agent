from __future__ import annotations

import datetime
import json
import shutil
import uuid
from pathlib import Path

from .catalog import resolve_effect, resolve_text_intro, resolve_text_outro, resolve_transition
from .media import ensure_local_media, ms_to_us, us_to_ms
from .models import CompileResult, EditPlan
from .package import write_manifest, zip_draft_dir
from .paths import DEFAULT_OUTPUT_DIR, TEMPLATE_DIR, ensure_engine_on_path
from .text_style import build_keyword_styles, parse_color


def _new_draft_id() -> str:
    stamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{stamp}{uuid.uuid4().hex[:8]}"


def _create_script(draft_dir: Path, width: int, height: int):
    ensure_engine_on_path()
    import pyJianYingDraft as draft

    if draft_dir.exists():
        shutil.rmtree(draft_dir)
    shutil.copytree(TEMPLATE_DIR, draft_dir)

    draft_info = draft_dir / "draft_info.json"
    draft_content = draft_dir / "draft_content.json"
    script = draft.ScriptFile.load_template(str(draft_info))
    script.dual_file_compatibility = True
    script.width, script.height = width, height
    script.content["canvas_config"]["width"] = width
    script.content["canvas_config"]["height"] = height
    script.save_path = str(draft_content)
    script.save()
    script.add_track(track_type=draft.TrackType.video, track_name="main_track", relative_index=0)
    script.save()
    return script


def _add_bgm(script, draft, plan, draft_dir: Path, total_ms: int, warnings: list[str]) -> None:
    """Place BGM on an audio track; optionally loop to cover the timeline span."""
    from pyJianYingDraft import Timerange

    bgm = plan.bgm
    assert bgm is not None

    audio_dir = draft_dir / "assets" / "audio"
    try:
        local = ensure_local_media(bgm.path, bgm.url, audio_dir)
        material = draft.AudioMaterial(str(local))
    except Exception as e:
        warnings.append(f"bgm skipped: {e}")
        return

    source_in_us = ms_to_us(bgm.in_ms)
    source_out_us = ms_to_us(bgm.out_ms) if bgm.out_ms is not None else material.duration
    source_out_us = min(source_out_us, material.duration)
    if source_in_us >= source_out_us:
        warnings.append("bgm skipped: empty trim range")
        return
    usable_us = source_out_us - source_in_us

    tl_start_ms = min(bgm.start_ms, total_ms)
    tl_end_ms = min(bgm.end_ms if bgm.end_ms is not None else total_ms, total_ms)
    if tl_end_ms <= tl_start_ms:
        warnings.append("bgm skipped: empty timeline range after clamp")
        return

    need_us = ms_to_us(tl_end_ms - tl_start_ms)
    track = "audio_track_bgm"
    script.add_track_ordered(track_type=draft.TrackType.audio, track_name=track)

    cursor_us = ms_to_us(tl_start_ms)
    remaining_us = need_us
    chunk_i = 0
    while remaining_us > 0:
        take_us = min(usable_us, remaining_us)
        if take_us <= 0:
            break
        seg = draft.AudioSegment(
            material=material,
            target_timerange=Timerange(start=cursor_us, duration=take_us),
            source_timerange=Timerange(start=source_in_us, duration=take_us),
            speed=1.0,
            volume=bgm.volume,
        )
        # Fade only on first / last chunk of the BGM span
        fade_in = ms_to_us(bgm.fade_in_ms) if chunk_i == 0 and bgm.fade_in_ms > 0 else 0
        fade_out = (
            ms_to_us(bgm.fade_out_ms)
            if remaining_us <= usable_us and bgm.fade_out_ms > 0
            else 0
        )
        if fade_in or fade_out:
            # clamp fades to segment length
            fade_in = min(fade_in, take_us)
            fade_out = min(fade_out, max(0, take_us - fade_in))
            if fade_in or fade_out:
                seg.add_fade(fade_in, fade_out)
        script.add_segment(seg, track)
        cursor_us += take_us
        remaining_us -= take_us
        chunk_i += 1
        if not bgm.loop:
            if remaining_us > 0:
                warnings.append(
                    f"bgm shorter than timeline by {us_to_ms(remaining_us)}ms (loop=false); left silent"
                )
            break


def compile_edit_plan(
    plan: EditPlan,
    *,
    output_root: Path | str | None = None,
    draft_id: str | None = None,
    make_zip: bool = True,
) -> CompileResult:
    """Compile an Edit Plan into a Jianying draft folder (+ optional zip)."""
    ensure_engine_on_path()
    import pyJianYingDraft as draft
    from pyJianYingDraft import Timerange, trange

    width, height = plan.canvas_size()
    draft_id = draft_id or _new_draft_id()
    output_root = Path(output_root or DEFAULT_OUTPUT_DIR)
    output_root.mkdir(parents=True, exist_ok=True)
    draft_dir = output_root / draft_id

    warnings: list[str] = []
    script = _create_script(draft_dir, width, height)

    # BGM 在场时默认静音原片；显式 mute_original_audio=false 可保留原声混音
    mute_clips = (
        plan.mute_original_audio
        if plan.mute_original_audio is not None
        else plan.bgm is not None
    )

    video_dir = draft_dir / "assets" / "videos"
    video_dir.mkdir(parents=True, exist_ok=True)

    track_name = "video_track_main"
    script.add_track_ordered(track_type=draft.TrackType.video, track_name=track_name)

    junction_by_clip = {j.after_clip: j for j in plan.junctions}
    cursor_us = 0
    placed_segments: list = []

    for i, clip in enumerate(plan.clips):
        local = ensure_local_media(clip.path, clip.url, video_dir)
        material = draft.VideoMaterial(str(local))

        source_in_us = ms_to_us(clip.in_ms)
        if clip.out_ms is not None:
            source_out_us = ms_to_us(clip.out_ms)
        else:
            source_out_us = material.duration

        if source_in_us >= material.duration:
            raise ValueError(f"clip[{i}] in_ms beyond media duration")
        source_out_us = min(source_out_us, material.duration)
        source_dur_us = source_out_us - source_in_us
        if source_dur_us <= 0:
            raise ValueError(f"clip[{i}] empty after trim")

        segment = draft.VideoSegment(
            material=material,
            target_timerange=trange(start=cursor_us, duration=source_dur_us),
            source_timerange=trange(start=source_in_us, duration=source_dur_us),
            speed=1.0,
            volume=0.0 if mute_clips else 1.0,
            clip_settings=draft.ClipSettings(),
        )

        junction = junction_by_clip.get(i)
        if junction is not None:
            if i >= len(plan.clips) - 1:
                warnings.append(f"junction after_clip={i} ignored (last clip)")
            else:
                try:
                    t_type = resolve_transition(junction.transition)
                    segment.add_transition(t_type, duration=ms_to_us(junction.duration_ms))
                except ValueError as e:
                    warnings.append(f"transition '{junction.transition}' skipped: {e}")

        script.add_segment(segment, track_name)
        placed_segments.append(segment)
        cursor_us += source_dur_us

    total_ms = us_to_ms(cursor_us)

    sticker_dir = draft_dir / "assets" / "stickers"
    effect_idx = 0
    text_idx = 0
    sticker_idx = 0

    for overlay in plan.overlays:
        end_ms = min(overlay.end_ms, total_ms) if total_ms > 0 else overlay.end_ms
        start_ms = min(overlay.start_ms, end_ms)
        if end_ms <= start_ms:
            warnings.append(f"{overlay.type} overlay skipped: empty range after clamp")
            continue
        tr = Timerange(start=ms_to_us(start_ms), duration=ms_to_us(end_ms - start_ms))

        if overlay.type == "effect":
            try:
                effect_type = resolve_effect(overlay.name or "")
            except KeyError as e:
                warnings.append(str(e))
                continue
            # One track per effect so overlays can stack (Jianying forbids overlap on same effect track).
            effect_track = f"effect_track_{effect_idx}"
            effect_idx += 1
            script.add_track_ordered(track_type=draft.TrackType.effect, track_name=effect_track)
            script.add_segment(draft.EffectSegment(effect_type, tr), effect_track)
            continue

        if overlay.type in ("text", "subtitle"):
            from pyJianYingDraft import TextBorder, TextSegment, TextStyle

            is_sub = overlay.type == "subtitle"
            ty = overlay.transform_y if overlay.transform_y is not None else (-0.75 if is_sub else 0.0)
            rgb = tuple(float(c) for c in overlay.color[:3])
            style = TextStyle(
                size=overlay.font_size,
                bold=overlay.bold,
                color=rgb,  # type: ignore[arg-type]
                align=overlay.align,
                auto_wrapping=True,
                max_line_width=0.85,
            )
            border = (
                TextBorder(alpha=1.0, color=(0.0, 0.0, 0.0), width=40.0)
                if overlay.border
                else None
            )
            clip_settings = draft.ClipSettings(transform_x=overlay.transform_x, transform_y=ty)
            text_track = f"text_track_{text_idx}"
            text_idx += 1
            script.add_track_ordered(track_type=draft.TrackType.text, track_name=text_track)
            content = overlay.text or ""
            seg = TextSegment(
                content,
                tr,
                style=style,
                clip_settings=clip_settings,
                border=border,
            )
            if overlay.keywords:
                try:
                    kw_rgb = parse_color(overlay.keyword_color)
                except ValueError as e:
                    warnings.append(f"text keyword_color: {e}")
                    kw_rgb = (1.0, 0.443, 0.0)
                styles = build_keyword_styles(
                    content,
                    overlay.keywords,
                    font_size=overlay.font_size,
                    color=rgb,  # type: ignore[arg-type]
                    keyword_color=kw_rgb,
                    keyword_font_size=overlay.keyword_font_size,
                )
                if styles:
                    seg.extra_styles = styles
                else:
                    warnings.append(f"keywords not found in text: {overlay.keywords!r}")
            if overlay.intro:
                try:
                    intro = resolve_text_intro(overlay.intro)
                    dur = (
                        ms_to_us(overlay.intro_duration_ms)
                        if overlay.intro_duration_ms is not None
                        else None
                    )
                    seg.add_animation(intro, duration=dur)
                except (KeyError, ValueError) as e:
                    warnings.append(f"text intro: {e}")
            if overlay.outro:
                try:
                    outro = resolve_text_outro(overlay.outro)
                    dur = (
                        ms_to_us(overlay.outro_duration_ms)
                        if overlay.outro_duration_ms is not None
                        else None
                    )
                    seg.add_animation(outro, duration=dur)
                except (KeyError, ValueError) as e:
                    warnings.append(f"text outro: {e}")
            script.add_segment(seg, text_track)
            continue

        if overlay.type == "sticker":
            ty = overlay.transform_y if overlay.transform_y is not None else 0.55
            clip_settings = draft.ClipSettings(
                transform_x=overlay.transform_x,
                transform_y=ty,
                scale_x=overlay.scale,
                scale_y=overlay.scale,
            )
            if overlay.resource_id:
                sticker_track = f"sticker_track_{sticker_idx}"
                sticker_idx += 1
                script.add_track_ordered(track_type=draft.TrackType.sticker, track_name=sticker_track)
                script.add_segment(
                    draft.StickerSegment(overlay.resource_id, tr, clip_settings=clip_settings),
                    sticker_track,
                )
            else:
                try:
                    local = ensure_local_media(overlay.path, overlay.url, sticker_dir)
                    material = draft.VideoMaterial(str(local))
                    # Photo materials are long; pin source window to target length.
                    src_dur = min(tr.duration, material.duration)
                    sticker_track = f"sticker_img_track_{sticker_idx}"
                    sticker_idx += 1
                    script.add_track_ordered(track_type=draft.TrackType.video, track_name=sticker_track)
                    seg = draft.VideoSegment(
                        material=material,
                        target_timerange=tr,
                        source_timerange=Timerange(start=0, duration=src_dur),
                        speed=src_dur / tr.duration if tr.duration else 1.0,
                        volume=0.0,
                        clip_settings=clip_settings,
                    )
                    script.add_segment(seg, sticker_track)
                except Exception as e:
                    warnings.append(f"sticker skipped: {e}")
            continue

    if plan.bgm is not None and total_ms > 0:
        _add_bgm(script, draft, plan, draft_dir, total_ms, warnings)

    # 草稿显示名：空 name 会导致剪映首页/UIA 按标题搜不到
    display_name = (plan.title or "").strip() or draft_id
    script.content["name"] = display_name

    script.save()

    manifest_path = write_manifest(
        draft_dir,
        {
            "draft_id": draft_id,
            "title": plan.title,
            "width": width,
            "height": height,
            "duration_ms": total_ms,
            "plan": plan.model_dump(mode="json"),
            "warnings": warnings,
            "engine": "pyJianYingDraft (vendored from capcut-mate)",
            "phase": "P0",
            "note": "Copy this folder into Jianying/CapCut draft directory to open. No cloud render.",
        },
    )

    zip_path = None
    if make_zip:
        zip_path = str(zip_draft_dir(draft_dir, output_root / f"{draft_id}.zip"))

    return CompileResult(
        draft_id=draft_id,
        draft_dir=str(draft_dir),
        zip_path=zip_path,
        duration_ms=total_ms,
        width=width,
        height=height,
        warnings=warnings,
        manifest_path=str(manifest_path),
    )


def compile_edit_plan_file(
    plan_path: Path | str,
    **kwargs,
) -> CompileResult:
    path = Path(plan_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    return compile_edit_plan(EditPlan.model_validate(data), **kwargs)
