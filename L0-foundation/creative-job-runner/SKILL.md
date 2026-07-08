---
name: creative-job-runner
description: Track image/video jobs in chat after submit (no sleep/auto-polling in conversation)
metadata:
  layer: L0-foundation
  requires: []
  tags: [foundation, async, tracking]
---

# Creative Job Runner — Submit and return + chat tracking

**All** VidAU image/video skills must follow this tracking protocol after MCP calls.

**Do not** `sleep` or loop `creative_get_job` until completion in chat (script2film may take 10–30 minutes).

## When to enable automatically

| MCP tool | Tracking mode |
|----------|---------------|
| `creative_submit_*` | **Chat tracking** — reply immediately after submit; user can ask for progress in this thread |
| `creative_generate_image` | **Sync** — tell estimated time before call; read `tracking.user_message` when done |
| `creative_generate_video` / `creative_image_to_video` / `creative_first_frame_to_video` | **Async** — submit returns `job_id`; send `tracking.user_message` immediately; no sleep/polling in chat |
| Any tool returning `job_id` | Must use chat tracking — no auto polling |

## Async job standard flow (required)

1. **On submit** — read `tracking.user_message` from response, **send to user immediately** (job_id, estimated time); tell user they can ask for progress anytime in this thread.
2. **End the turn** — when `tracking.should_continue_polling` is `false`, **do not** call `creative_get_job`, **do not** `sleep`.
3. **Progress checks** — when user asks in this thread, call `creative_get_job` or `creative_list_jobs` once and answer; **no** auto sleep/polling loops.
4. **User follow-up** — single `creative_get_job` or `creative_list_jobs` per question; still **no** polling loop.
5. **Cancel** — user says "cancel" → `creative_cancel_job`.

## vs old behavior

| ❌ Old (forbidden) | ✅ Now (required) |
|-------------------|-------------------|
| Poll `creative_get_job` every 10s / 30s / 60s | Return immediately after submit |
| `sleep` in chat | Query only when user asks |
| Wait for final video before replying | Confirm submit + job_id; user can follow up |

## Sync image / async video (creative-direct)

**Image (sync)**: tell user "Generating image, ~1–2 minutes…" before `creative_generate_image`; deliver artifacts when tool returns.

**Video (async)**: tell user estimated time before submit; send `tracking.user_message` + `job_id` immediately; **end turn** — do not wait for video.

## Agent behavior

- Follow `tracking.agent_action` literally; if it says "no polling", do not ignore.
- **Do not** send task dashboard links; progress stays in this chat.
- User says "my jobs" → `creative_list_jobs` and show list in chat.

## Delivery

- When job is `completed` and user is still in thread, deliver `artifacts[0].urls.download` + local save hint.
- `delivery.mode=both` (default): URL + `local.suggested_filename` / `suggested_subpath`
