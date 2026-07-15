# Voiceover timing · lipsync vs mux

## Mode choice (this skill default)

Handheld **default render** = batch direct video (see [batch-direct-video.md](batch-direct-video.md)), **not** script2film mux/lipsync flags.

| Need | Path |
|------|------|
| On-camera lip sync (default) | Per-shot `reference_audio_urls` + direct_video / image_to_video |
| Off-camera VO only | Still batch direct video **or** hand off script2film `voiceover_mode=mux` |

## Voice lock（硬门禁 — 整片同一音色）

多镜口播 **必须** 使用 **同一个** MiniMax `voice` + 同一个 `language_boost`。  
音色不一致（甚至性别跳变）几乎总是因为：逐镜漏传 / 换传 `voice`，或省略后落到服务端英文默认声。

### 锁定时机

Hint 确认后、**第一声 TTS 之前** 选定一次，写入 agent 记忆：

```yaml
tts_voice: "<MiniMax voice id>"
tts_language_boost: "zh"   # or en / omit only if EN default voice
```

之后每一镜 `creative_generate_tts` **原样复用**这两项。用户未改口要求换声前，**禁止**改 ID。

### 默认音色表（按 persona + 口播语言选一次）

| 口播语言 | Persona 性别 | `voice`（锁定用） | `language_boost` |
|----------|--------------|-------------------|------------------|
| 中文 | 女 / 未指定 | `Chinese (Mandarin)_Warm_Girl` | `zh` |
| 中文 | 男 | `Chinese (Mandarin)_Radio_Host` | `zh` |
| English | female / unstated | `English_Upbeat_Woman` | `en`（或省略） |
| English | male | `English_Trustworthy_Man` | `en`（或省略） |

- 用户指定音色 ID → 整片用用户指定的（仍须每镜显式传入）  
- 换声仅当用户明确说「换成男声/女声/某某音色」→ **整批**用新 ID **全部重跑 TTS**（不要只改几镜）  
- **Forbidden**: 一镜 Hot Girl、一镜 Radio Host；一镜中文声、一镜英文默认声；省略 `voice`「让模型自己挑」

### MCP 调用模板（每镜相同 voice）

```json
{
  "text": "<shot VO line>",
  "voice": "<LOCKED tts_voice>",
  "language_boost": "<LOCKED tts_language_boost>"
}
```

服务端默认（省略 `voice` 时）= `English_Upbeat_Woman` — **中文口播切勿省略**。

---

## Per-shot pipeline

1. Parse `## Voiceover Copy` (one line per shot, ordered)
2. **Lock voice**（上节）→ then TTS each line via `creative_generate_tts` with the **same** `voice` + `language_boost`
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
  "audio_url": "https://…/vo-01.mp3",
  "voice": "<same locked id>"
}
```

`audio_url` **required for predictable lipsync** (server can auto-TTS if omitted, but prefer client URLs — and server TTS also needs a single `tts_voice` if used).

## Word / char budgets (guide)

Aim so TTS ≈ target shot length before clamp:

| Shot target | EN words (conversational) | ZH chars (approx) |
|-------------|---------------------------|-------------------|
| 5s | 12–15 | 18–22 |
| 8s | 20–24 | 28–36 |
| 12s | 30–36 | 42–54 |

If sum of `duration_sec` differs from `target_duration_sec` by **>3s**, rewrite copy or re-TTS **with the same locked voice** before submit.

## ≤15s single shot

One line TTS → async `creative_image_to_video` / `direct_video` with `reference_audio_urls: [audio_url]` + product/talent refs. Skip script2film.
