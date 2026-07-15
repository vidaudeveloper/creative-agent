# Batch direct video + concat (no script2film)

Default render for handheld talking-head. Each shot = one Seedance clip; Hermes concatenates locally.

## Why not script2film

| script2film | This path |
|-------------|-----------|
| Element boards + keyframes + concat + BGM | Skip all boards; user talent + TTS audio only |
| One job | N parallel `direct_video` jobs |
| Server concat | Client ffmpeg concat |
| Auto BGM | No BGM unless asked |

## Per-shot MCP payload

```json
{
  "prompt": "…",
  "duration_sec": 6,
  "aspect_ratio": "9:16",
  "video_mode": "reference",
  "reference_image_urls": ["https://…/product.jpg", "https://…/talent.jpg"],
  "reference_video_urls": ["https://…/talent.mp4"],
  "reference_audio_urls": ["https://…/vo-01.mp3"],
  "generate_audio": true
}
```

- Lipsync speaking shot: **always** set `reference_audio_urls` to that shot’s TTS  
- Default handheld: every item is a speaking shot (face + product)  
- Product-only B-roll: **only if user asked**; images only; `generate_audio` true/false OK  
- Max **3** `reference_video_urls`; max **9** images  

## Submit patterns

### A. Async batch (≥2 shots) — preferred

Follow **creative-batch-orchestrator**:

```yaml
batch_label: "handheld-vo-30s"
items:
  - label: "shot-01"
    skill: creative-direct-video
    mode: image_to_video
    input:
      prompt: "…"
      duration_sec: 6
      aspect_ratio: "9:16"
      reference_image_urls: ["…"]
      reference_video_urls: ["…"]
      reference_audio_urls: ["…/vo-01.mp3"]
      generate_audio: true
  - label: "shot-02"
    skill: creative-direct-video
    mode: image_to_video
    input: { … }
```

Map each item → `creative_submit_workflow` `workflow_type=direct_video` + unique `client_request_id`.

### B. Convenience tools (same async jobs)

`creative_image_to_video` with the same fields (also async → `job_id`). Still follow **Wait-then-poll** below.

## Wait-then-poll (required after video submit)

**This skill overrides** creative-job-runner’s “submit and end turn / no poll”.

```text
submit all shot jobs (parallel)
  → notify user (job_ids + ETA)
  → sleep once for max(estimate.eta_sec)  // fallback 180s
  → query all job_ids
  → if all terminal → concat (or report failures)
  → else sleep 20s → query again → loop until all terminal
```

| Step | Action |
|------|--------|
| 1 | Collect each submit’s `job_id` + `estimate.eta_sec` |
| 2 | `wait_sec = max(etas)` or **180** if none |
| 3 | Background sleep `wait_sec` (scheduled wait — not chat idle forever without a plan) |
| 4 | `creative_get_job` each id (or one `creative_list_jobs` + filter) |
| 5 | All `completed` → download + ffmpeg concat (§ below) |
| 6 | Any non-terminal → sleep **20s**, goto 4 |
| 7 | Timeout ~**30 min** total after first poll → stop, list unfinished `job_id`s |

User may still ask for status mid-wait; answer with one query round, then resume the 20s loop.

## Tracking table

- Keep `job_id` ↔ shot `index` until concat finishes
- Progress tip: `completed_count / total` every 1–2 poll rounds

## Concat (required for ≥2 shots)

After all succeeded, download in **index order**:

```bash
# concat.txt
file 'shot-01.mp4'
file 'shot-02.mp4'
file 'shot-03.mp4'

ffmpeg -y -f concat -safe 0 -i concat.txt -c copy final-handheld.mp4
```

If codecs differ, re-encode:

```bash
ffmpeg -y -f concat -safe 0 -i concat.txt -c:v libx264 -c:a aac final-handheld.mp4
```

**Do not** add BGM unless user asks.

## Single shot

Skip concat; deliver the one artifact URL directly.
