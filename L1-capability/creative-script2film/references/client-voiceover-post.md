# Client voiceover & subtitles (Hermes terminal)

Server delivers **video + BGM only**. TTS and subtitle burn-in run on the **Hermes agent terminal** (local TTS config + ffmpeg).

## When to enable

Ask the user before script submit:

| Flag | Meaning |
|------|---------|
| `voiceover_enabled` | Per-shot narration; server disables Seedance in-shot audio |
| `subtitles_enabled` | Burn subtitles with ffmpeg after VO mux (same text as voiceover) |

If `voiceover_enabled=true`, you **must** build `voiceover_shot_plan` before `creative_submit_script2film`.

## 1. Check local TTS

Read `~/.hermes/config.yaml` → `tts:` (provider + voice), or run Hermes TTS check if available.

If no TTS provider is configured → **stop** and tell the user to configure TTS (Edge / ElevenLabs / MiniMax / local Piper, etc.). Do not submit with `voiceover_enabled`.

## 1b. Check local ffmpeg (before submit if `subtitles_enabled`, always before post-process)

VO mux needs **any** recent `ffmpeg` + `ffprobe`. Subtitle burn-in needs ffmpeg built **with libass** (`subtitles` filter).

**Run once** (or when user enables subtitles):

```bash
command -v ffmpeg ffprobe
ffmpeg -filters 2>/dev/null | grep -E '^[^ ]+.*subtitles' || echo "MISSING_SUBTITLES_FILTER"
```

| Result | Action |
|--------|--------|
| `ffmpeg` / `ffprobe` not found | **Stop** — tell user to install ffmpeg; do not start post-process |
| VO only (`subtitles_enabled=false`) | Standard Homebrew `ffmpeg` is OK |
| Subtitles enabled + `MISSING_SUBTITLES_FILTER` | **Stop before burn** — install libass-enabled ffmpeg (see macOS below); **do not** run obsolete `brew install ffmpeg --with-libass` |

### macOS (Homebrew)

Regular `brew install ffmpeg` **does not** include libass. For subtitles:

```bash
brew install ffmpeg-full
export FFMPEG_BIN=/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg
export FFPROBE_BIN=/opt/homebrew/opt/ffmpeg-full/bin/ffprobe

# Verify subtitle filter
$FFMPEG_BIN -filters 2>/dev/null | grep subtitles
```

Use `$FFMPEG_BIN` / `$FFPROBE_BIN` in all post-process commands below when set.

**Do not use** deprecated flags: `--with-libass`, `--with-freetype`, etc. — they fail on current Homebrew and cause silent hangs while the agent retries.

If subtitle ffmpeg is missing and user wants delivery now → **mux VO first**, tell user subtitles are blocked pending `ffmpeg-full`, deliver `final-vo.mp4` without waiting on failed brew loops.

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

## 3. Local TTS + duration (before submit)

For each shot line:

1. Synthesize to `vo-NN.mp3` (Hermes `tts_tool` / configured provider).
2. Measure duration: `ffprobe -v error -show_entries format=duration -of csv=p=0 vo-NN.mp3`
3. `duration_sec = clamp(ceil(measured + 0.4), 4, 12)` (Seedance shot limits).

Save a **voiceover manifest** in the workspace (for post-process):

```json
{
  "locale": "zh-CN",
  "shots": [
    {
      "index": 1,
      "text": "…",
      "audio_path": "vo-01.mp3",
      "duration_sec": 6,
      "start_sec": 0
    }
  ]
}
```

Recompute `start_sec` as cumulative sum of prior `duration_sec`.

If sum of `duration_sec` differs from `target_duration_sec` by >3s, warn the user and adjust copy or re-TTS before submit.

## 4. Submit with client shot plan

```json
{
  "creative_submit_script2film": {
    "script": "<confirmed spec_markdown>",
    "target_duration_sec": 30,
    "aspect_ratio": "9:16",
    "voiceover_enabled": true,
    "subtitles_enabled": true,
    "voiceover_shot_plan": [
      { "index": 1, "text": "Shot 1 VO line", "duration_sec": 6 },
      { "index": 2, "text": "Shot 2 VO line", "duration_sec": 8 }
    ],
    "client_request_id": "<uuid>"
  }
}
```

Server uses **`voiceover_shot_plan` durations as authoritative** (no re-normalization). Job `progress.shots[]` includes `voiceover_text` + `duration_sec` for client post-process.

## 5. After job completes — local post-process

Download `artifacts[0].urls.download` (BGM mixed master). Use saved `vo-NN.mp3` files (or re-TTS from `progress.shots[].voiceover_text`).

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

### Mux voiceover (example)

Use `${FFMPEG_BIN:-ffmpeg}` and `${FFPROBE_BIN:-ffprobe}` when set.

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

Deliver `final-vo-sub.mp4` to the user with local save hint.

## Server vs client

| Step | Where |
|------|--------|
| Script / VO copy | Server `creative_generate_script` |
| TTS + measure duration | **Hermes client** |
| Shot duration for video gen | Server (from `voiceover_shot_plan`) |
| Keyframes / video / concat / BGM | Server |
| VO mux + subtitles | **Hermes client ffmpeg** |

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| User asks "怎么样了" — no reply | Turn stuck on brew/tool; status not reported | Follow §5 progress rules; `/interrupt` then resume with explicit step |
| `Error: invalid option: --with-libass` | Obsolete Homebrew flags | Use `brew install ffmpeg-full` (§1b) |
| `libass` installed but subtitles still fail | ffmpeg not linked to libass | Use `ffmpeg-full` binary path via `FFMPEG_BIN` |
| Long brew with no chat update | Agent violated progress rules | Stop retry loop; tell user blocker + offer VO-only deliverable |
