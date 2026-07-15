# Voiceover timing · lipsync vs mux

## Mode choice (this skill default)

Handheld **default render** = batch direct video (see [batch-direct-video.md](batch-direct-video.md)), **not** script2film mux/lipsync flags.

| Need | Path |
|------|------|
| On-camera lip sync (default) | Per-shot `reference_audio_urls` + direct_video / image_to_video |
| Off-camera VO only | Still batch direct video **or** hand off script2film `voiceover_mode=mux` |
## Per-shot pipeline

1. Parse `## Voiceover Copy` (one line per shot, ordered)
2. TTS: prefer MCP `creative_generate_tts` (Runware MiniMax Speech 2.8)
   - EN default voice OK; ZH → pass e.g. `Chinese (Mandarin)_Warm_Girl` + `language_boost: zh`
3. Duration:
   ```bash
   ffprobe -v error -show_entries format=duration -of csv=p=0 vo-NN.mp3
   ```
4. `duration_sec = clamp(ceil(measured + 0.4), 4, 12)`
5. Plan entry:

```json
{
  "index": 1,
  "text": "…",
  "duration_sec": 6,
  "audio_url": "https://…/vo-01.mp3"
}
```

`audio_url` **required for predictable lipsync** (server can auto-TTS if omitted, but prefer client URLs).

## Word / char budgets (guide)

Aim so TTS ≈ target shot length before clamp:

| Shot target | EN words (conversational) | ZH chars (approx) |
|-------------|---------------------------|-------------------|
| 5s | 12–15 | 18–22 |
| 8s | 20–24 | 28–36 |
| 12s | 30–36 | 42–54 |

If sum of `duration_sec` differs from `target_duration_sec` by **>3s**, rewrite copy or re-TTS before submit.

## ≤15s single shot

One line TTS → async `creative_image_to_video` / `direct_video` with `reference_audio_urls: [audio_url]` + product/talent refs. Skip script2film.
