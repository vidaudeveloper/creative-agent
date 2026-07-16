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
  "reference_image_urls": ["https://…/product.jpg", "https://…/handheld-still.jpg"],
  "reference_video_urls": ["https://…/talent.mp4"],
  "reference_audio_urls": ["https://…/vo-01.mp3"],
  "reference_audio_role": "lipsync",
  "generate_audio": true
}
```

- Lipsync speaking shot: **always** set `reference_audio_urls` + **`reference_audio_role: "lipsync"`**  
- Prompt **must** say on-camera speech / lip-sync — **never** 旁白 / voiceover / narration（见 handheld-prompt § 口播 vs 旁白）  
- Default handheld: every item is a speaking shot (face + product); image refs = product + **confirmed handheld still**  
- Product-only B-roll: **only if user asked**; images only; `generate_audio` true/false OK  
- Max **3** `reference_video_urls`; max **9** images  
- 其它 skill 若要旁白/节拍：用 `reference_audio_role: "guide"` 或不传 role；旁白成片更推荐 mux 后混，勿设 `lipsync`  

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

`creative_image_to_video` with the same fields (also async → `task_id`). Still follow **Wait-then-poll** below.

## Wait-then-poll（强制主步骤 — 与 SKILL.md §8 同级）

**Required after every video submit on this skill. Not optional. Not “reference only.”**

Follows **creative-task-runner** (foreground reply + background ETA → poll 20s); on wake **must** continue to concat.

```text
submit all shot jobs (parallel)
  → notify user (task_ids + ETA) + arm background waiter  → end foreground turn
  → [background] sleep once for max(estimate.eta_sec)  // fallback 180s
  → [background wake] query all task_ids
  → if all terminal → concat (or report failures)
  → else re-arm background sleep 20s → query again → loop until all terminal
```

| Step | Action |
|------|--------|
| 1 | Collect each submit’s `task_id` + `estimate.eta_sec` |
| 2 | `wait_sec = max(etas)` or **180** if none |
| 3 | Arm **background** sleep for `wait_sec` — end foreground turn (do **not** block chat) |
| 4 | On wake: `creative_get_task` each id (or one `creative_list_tasks` + filter) |
| 5 | All `completed` → download + ffmpeg concat (§ below) **immediately** |
| 6 | Any non-terminal → re-arm background sleep **20s**, goto 4 |
| 7 | Timeout ~**30 min** total after first poll → stop, list unfinished `task_id`s |

**Forbidden**

- Ending the turn with **no** background waiter (“你可以随时问我进度” only)
- Describing this section without arming background sleep + query
- Blocking the foreground turn with multi-minute in-turn sleep

User may still ask for status mid-wait; answer with one query round; **keep** the background schedule.


## Tracking table

- Keep `task_id` ↔ shot `index` until concat finishes
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
