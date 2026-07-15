---
name: handheld-product-avatar
description: Use when 人物口播/handheld product VO; NOT still-life
metadata:
  layer: L2-vertical
  requires:
    [
      creative-platform,
      creative-job-runner,
      creative-seedance2-prompt,
      creative-gpt-image2-prompt,
      creative-narrative-router,
      creative-direct,
      creative-batch-orchestrator,
    ]
  tags: [ecommerce, avatar, handheld, voiceover, ugc, lipsync]
  hermes:
    related_skills:
      - creative-direct
      - creative-batch-orchestrator
      - product-url-to-video
      - creative-narrative-router
---

# Handheld Product Talking Avatar

Turn **product image + selling points** into a vertical UGC-style ad: person **holding / showing the product** while speaking.

> **Default shot plan**: **全程人物手持产品口播**（每镜都是 talking-handheld + lipsync）。  
> **不要**默认插入产品特写 / 静物展示 / B-roll；仅当用户**明确要求**「产品展示片段 / 特写 / 开箱」时才加。  
> **Hint 确认**：口播文案 + 人物形象图出来后进入 **Hint 模式**，用户可反复改文案/形象；**明确确认后**才 TTS / 生视频。  
> **Default render path**: **batch direct video** (per-shot Seedance) — **not** `creative_submit_script2film`.  
> Pipeline: TTS per shot → parallel async `direct_video` (or `creative_image_to_video` → same job) → **client ffmpeg concat** (no BGM).  
> Lip sync = Seedance `reference_audio` (not Creatify Aurora).  
> **Never** upload recognizable real-face refs unless user accepts privacy risk.

## When to use

| Trigger | This skill |
|---------|------------|
| 手持产品口播、带货数字人、talking head + product | ✅ |
| Product image + on-camera VO | ✅ |
| Still-life / no talking person | ❌ → `product-url-to-video` / `creative-script2film` |
| Product **URL** scrape first | ❌ → `product-url-to-video`, then handoff here |
| Single ≤15s one shot | Same path with **1** video job (no concat) |

## Prompt gates

- Talent/product still: **creative-gpt-image2-prompt**
- Each shot video prompt: **creative-seedance2-prompt** + [handheld-prompt.md](references/handheld-prompt.md)

## References

| File | When |
|------|------|
| [script-templates.md](references/script-templates.md) | VO pacing / Hook→CTA |
| [persona-by-vertical.md](references/persona-by-vertical.md) | Persona brief |
| [multi-scene.md](references/multi-scene.md) | 15/30/60s grids |
| [ugc-authenticity.md](references/ugc-authenticity.md) | UGC look |
| [voiceover-timing.md](references/voiceover-timing.md) | TTS + duration |
| [handheld-prompt.md](references/handheld-prompt.md) | Seedance constraints |
| [batch-direct-video.md](references/batch-direct-video.md) | Parallel submit + ffmpeg concat |
| [hint-mode.md](references/hint-mode.md) | 文案+形象确认环；确认前禁止 TTS/视频 |

---

## Agent flow

### 1. Collect inputs

- Product image → **creative-platform** upload → HTTPS URL  
- Selling points / brief  
- Defaults: duration **30s**, aspect **9:16**, locale = user language  
- If user attached **talent image/video** → use as refs; **do not** regenerate talent still  

### 2. Persona (text only)

Load [persona-by-vertical.md](references/persona-by-vertical.md) unless talent media already defines look.

### 3. Script → per-shot VO lines

Load [script-templates.md](references/script-templates.md) + [multi-scene.md](references/multi-scene.md).

- Spoken copy; **each shot ≤12s** after TTS  
- **Every shot default**: person on camera, product in hand, speaking (lipsync)  
- **No** product-only / macro / B-roll shots unless user asked for showcase  
- Optional: `creative_generate_script` (`voiceover: true`) then parse `## Voiceover Copy`  

### 4. Talent refs

| User has | Use as |
|----------|--------|
| 人物形象图 | `reference_image_urls` (+ product) |
| 人物视频 | `reference_video_urls` (max 3); optional still too |
| Neither | `creative_generate_image` once → talent still |

### 5. Hint 确认模式（硬门禁）

Load [hint-mode.md](references/hint-mode.md).

1. 展示完整分镜口播文案 + 人物形象图（及 persona 摘要）  
2. **结束本回合**，等用户反馈  
3. 用户可反复：**改文案** / **重生或换形象** → 每次改完再展示 → 继续等  
4. **仅当**用户明确说「确认 / 可以生成 / 开始出片」等 → 锁定文案与形象，进入 §6  
5. Hint 期间 **禁止** `creative_generate_tts`、任何视频 submit  

### 6. TTS (required before video)

For each **confirmed** shot line → `creative_generate_tts` → `{ index, text, duration_sec, audio_url }`  
See [voiceover-timing.md](references/voiceover-timing.md).

### 7. Batch direct video (default — **no script2film**)

Load [batch-direct-video.md](references/batch-direct-video.md) + **creative-batch-orchestrator** when ≥2 shots.

For **each shot** submit one job (parallel, unique `client_request_id`):

**Preferred (async, trackable):**

```json
{
  "workflow_type": "direct_video",
  "input": {
    "prompt": "<Seedance prompt: handheld + product + speak to camera>",
    "aspect_ratio": "9:16",
    "duration_sec": 6,
    "video_mode": "reference",
    "reference_image_urls": ["<product>", "<talent_still?>"],
    "reference_video_urls": ["<talent_video?>"],
    "reference_audio_urls": ["<this shot TTS audio_url>"],
    "generate_audio": true
  },
  "client_request_id": "<uuid>"
}
```

MCP: `creative_submit_workflow` with above, **or** `creative_image_to_video` (also async → same `direct_video` job). Prefer batch submit for ≥2 shots.

**Do not** call `creative_submit_script2film` on this default path.

### 7b. Wait-then-poll until all video jobs done (**overrides** creative-job-runner “submit and stop”)

After all shot jobs are submitted:

1. Tell user jobs are running + list `job_id` ↔ shot index; give **max ETA** from submit responses (`estimate.eta_sec`, fallback **180s** if missing).
2. **Background wait**: sleep once for that ETA (do not busy-poll early).
3. Query every `job_id` (`creative_get_job` or `creative_list_jobs`).
4. If **all** are terminal (`completed` / `failed` / `cancelled`):
   - Any `failed`/`cancelled` → report which shots failed; ask retry or continue with successes.
   - All `completed` → go to **§8 Client concat** immediately (no waiting for user ping).
5. If any still `queued`/`running`: sleep **20s**, then repeat step 3 until all terminal (cap ~30 min; then report stuck jobs).
6. While polling, optional short progress every 1–2 rounds (e.g. `3/5 done`) — do not spam.

Details: [batch-direct-video.md](references/batch-direct-video.md) § Wait-then-poll.

### 8. Client concat (no BGM)

When all shot videos succeeded:

1. Download shot MP4s in index order  
2. ffmpeg concat demuxer → `final.mp4`  
3. **No BGM** unless user asks (`creative_generate_bgm` + mux)  
4. Optional subtitles from VO lines  

Example concat list + command: [batch-direct-video.md](references/batch-direct-video.md).

### 9. When to fall back to script2film

Only if user wants **full storyboard identity boards / auto BGM / mux post VO** without providing talent media — then hand off to **creative-script2film**. Default handheld VO stays on batch direct video.

---

## Continuity

- Same product + talent refs on **every** shot  
- Hard cuts OK; cut on VO pauses  
- Default: every shot has `reference_audio_urls` (lipsync handheld)  
- Showcase / product-only shot: **only if user requested**; then TTS optional / may omit `reference_audio_urls`  

## Compliance

- No Creatify API  
- No celebrity lookalikes / real-face training  
- Product must match reference SKU  
- Real-face refs may be Seedance privacy-blocked — tell user if so  
