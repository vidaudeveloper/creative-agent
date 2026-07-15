# Client voiceover & subtitles (Hermes terminal)

Two voiceover paths are supported. Choose by whether an on-screen person needs lip sync.

| `voiceover_mode` | When | Server behavior | Client post |
|------------------|------|-----------------|-------------|
| **`mux`** (default) | No lip sync needed (product B-roll, off-camera VO) | Silent Seedance shots; BGM only | Mux TTS + optional subtitles |
| **`lipsync`** | Real person / avatar talking on camera | TTS audio → Seedance `reference_audio`; VO baked in | Skip VO mux; optional subtitles only |

Ask the user before script submit:

| Flag | Meaning |
|------|---------|
| `voiceover_enabled` | Enable narration |
| `voiceover_mode` | `mux` \| `lipsync` |
| `subtitles_enabled` | Burn subtitles with ffmpeg after (same text as voiceover) |

If `voiceover_enabled=true`, you **must** build `voiceover_shot_plan` before `creative_submit_script2film`.

## Mode selection (routing)

- User says 对口型 / talking head / 真人出境说话 / handheld avatar speaking → **`lipsync`**
- User says 旁白 / 画外音 / 产品展示配音 / no face talking → **`mux`**

## 1. TTS source

### Option A — MCP paid TTS (recommended for lipsync)

Call `creative_generate_tts` per shot → get `audio_url` → put into `voiceover_shot_plan[].audio_url`.

### Option B — Hermes local TTS (mux-friendly)

Read `~/.hermes/config.yaml` → `tts:`. If missing and mode is **mux** → stop and ask user to configure, **or** use `creative_generate_tts` instead.

For **lipsync**, if `audio_url` is omitted the **server** will generate TTS via Runware (needs `RUNWARE_API_KEY`).

## 1b. Check local ffmpeg (mux / subtitles)

VO mux needs **any** recent `ffmpeg` + `ffprobe`. Subtitle burn-in needs ffmpeg with libass.

**Skip VO mux** when `voiceover_mode=lipsync` (audio already driven into the video). Still need ffmpeg for optional subtitles.

```bash
command -v ffmpeg ffprobe
ffmpeg -filters 2>/dev/null | grep -E '^[^ ]+.*subtitles' || echo "MISSING_SUBTITLES_FILTER"
```

| Result | Action |
|--------|--------|
| `ffmpeg` / `ffprobe` not found | **Stop** for mux/subtitles — tell user to install ffmpeg |
| VO mux only | Standard Homebrew `ffmpeg` is OK |
| Subtitles + `MISSING_SUBTITLES_FILTER` | Install `ffmpeg-full` (see below) |

### macOS (Homebrew)

```bash
brew install ffmpeg-full
export FFMPEG_BIN=/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg
export FFPROBE_BIN=/opt/homebrew/opt/ffmpeg-full/bin/ffprobe
```

## 2. Generate script with VO copy

```json
{
  "creative_generate_script": {
    "voiceover": true,
    "target_duration_sec": 30,
    "aspect_ratio": "9:16"
  }
}
```

Parse `## Voiceover Copy` from `spec_markdown` — one line per shot, in order.

## 3. Build voiceover_shot_plan (before submit)

For each shot line:

1. Synthesize TTS (`creative_generate_tts` or local) → `vo-NN.mp3` / `audio_url`
2. Measure duration: `ffprobe …`
3. `duration_sec = clamp(ceil(measured + 0.4), 4, 12)`

### mux submit

```json
{
  "voiceover_enabled": true,
  "voiceover_mode": "mux",
  "voiceover_shot_plan": [
    { "index": 1, "text": "…", "duration_sec": 6 }
  ]
}
```

### lipsync submit

```json
{
  "voiceover_enabled": true,
  "voiceover_mode": "lipsync",
  "voiceover_shot_plan": [
    {
      "index": 1,
      "text": "…",
      "duration_sec": 6,
      "audio_url": "https://…/vo-01.mp3"
    }
  ]
}
```

Omit `audio_url` only if you want the **server** to call TTS (lipsync). Prefer providing `audio_url` for predictable timing.

Save a local **voiceover manifest** for mux post-process (same as before).

If sum of `duration_sec` differs from `target_duration_sec` by >3s, warn and adjust before submit.

## 4. After job completes

| Mode | Client action |
|------|----------------|
| `mux` | Download master → mux `vo-NN.mp3` by shot offsets → optional subtitles |
| `lipsync` | Download master (VO already in video) → optional subtitles only; **do not** remux VO |

Server job message for lipsync: 「口播已由 reference_audio 对口型，无需再混 VO」.

### Mux voiceover (example)

Use the existing adelay/amix recipe below only when `voiceover_mode=mux`.

## 5. After job completes — local post-process

Download `artifacts[0].urls.download` (BGM mixed master).

- **`mux`**: Use saved `vo-NN.mp3` (or re-TTS from `progress.shots[].voiceover_text`).
- **`lipsync`**: Skip VO mux; optional subtitles only.

**Preflight again** (§1b) if you have not verified ffmpeg this session. If check fails → reply to user immediately with fix steps; **do not** spawn background `brew` without telling the user what step you are on.

### Progress reporting (required — no silent hang)

Client post-process is **not** tracked by `creative_get_job`. When the user asks status (`怎么样了`, `进度`, `how's it going`, `status?`, etc.) — even mid-turn or while a shell command runs — you **must reply in chat first** with:

1. **Current step** (one of): `preflight` / `downloading master` / `muxing VO` / `building SRT` / `burning subtitles` / `delivering` / `blocked: <reason>`
2. **Done** vs **remaining** (e.g. "口播已混完，卡在字幕：ffmpeg 缺少 subtitles 滤镜")
3. **Next action** (one line) or **what you need from the user**

Rules:

- **Never** run long `brew install` / downloads without a prior user-visible status line.
- If a tool or background process is running → still answer status questions; do not wait for it to finish.
- If blocked (missing TTS, missing libass ffmpeg) → say so explicitly; offer VO-only delivery or install command.
- After each major step completes → one short checkpoint message (e.g. "✓ 口播混音完成 → final-vo.mp4").

### Mux voiceover (ffmpeg)

Use `${FFMPEG_BIN:-ffmpeg}` and `${FFPROBE_BIN:-ffprobe}` when set. **Only for `voiceover_mode=mux`.**

Offsets from `progress.shots` or manifest `start_sec`:

```bash
${FFMPEG_BIN:-ffmpeg} -y -i final-with-bgm.mp4 -i vo-01.mp3 -i vo-02.mp3 \
  -filter_complex \
  "[1:a]adelay=0|0[vo1];[2:a]adelay=6000|6000[vo2];[0:a][vo1][vo2]amix=inputs=3:duration=first:dropout_transition=0:normalize=0[aout]" \
  -map 0:v -map "[aout]" -c:v copy -c:a aac -b:a 192k final-vo.mp4
```

Adjust `adelay` ms = `start_sec * 1000`. If base video has no audio track, omit `[0:a]` from amix.

### Burn subtitles (optional)

Build `subtitles.srt` from manifest (start/end from TTS duration):

```srt
1
00:00:00,000 --> 00:00:06,000
Shot 1 VO line
```

```bash
${FFMPEG_BIN:-ffmpeg} -y -i final-vo.mp4 -vf "subtitles=subtitles.srt:force_style='FontSize=24,MarginV=40'" \
  -c:a copy final-vo-sub.mp4
```

Deliver `final-vo-sub.mp4` to conversation **产物** + show URL (do not default-download to a random local path).

## Server vs client

| Step | Where |
|------|--------|
| Script / VO copy | Server `creative_generate_script` |
| TTS + measure duration | Client (`creative_generate_tts` or Hermes) — or server auto-TTS in lipsync |
| Shot duration for video gen | Server (from `voiceover_shot_plan`) |
| Keyframes / video / concat / BGM | Server |
| `lipsync` reference_audio | Server Seedance |
| VO mux | **Client only when `mux`** |
| Subtitles | **Hermes client ffmpeg** |

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| User asks "怎么样了" — no reply | Turn stuck on brew/tool; status not reported | Follow §5 progress rules; `/interrupt` then resume with explicit step |
| `Error: invalid option: --with-libass` | Obsolete Homebrew flags | Use `brew install ffmpeg-full` (§1b) |
| `libass` installed but subtitles still fail | ffmpeg not linked to libass | Use `ffmpeg-full` binary path via `FFMPEG_BIN` |
| Long brew with no chat update | Agent violated progress rules | Stop retry loop; tell user blocker + offer VO-only deliverable |
| lipsync but no mouth sync | Missing `audio_url` / wrong mode | Set `voiceover_mode=lipsync` and pass per-shot `audio_url` |
