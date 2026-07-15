---
name: creative-job-runner
description: Use after submit to track job_id; never sleep/poll loop
metadata:
  layer: L0-foundation
  requires: []
  tags: [foundation, async, tracking]
---

# Creative Job Runner — Submit and return + chat tracking

**All** VidAU image/video skills must follow this tracking protocol after MCP calls.

**Default**: Do not `sleep` or loop `creative_get_job` until completion in chat (script2film may take 10–30 minutes).

**Exception**: Skills that explicitly define **Wait-then-poll** / auto-poll (e.g. **handheld-product-avatar**, product→jianying remix) **must** follow that skill’s schedule instead of “submit and stop”.

## When to enable automatically

| MCP tool | Tracking mode |
|----------|---------------|
| `creative_submit_*` | **Chat tracking** by default — reply after submit; user can ask for progress |
| `creative_generate_video` / `creative_image_to_video` / `creative_first_frame_to_video` | **Async** — returns `job_id`; default chat tracking |
| `creative_generate_image` (and TTS/BGM sync tools) | **Sync** — tell estimated time before call; read `tracking.user_message` when done |
| Any tool returning `job_id` | Chat tracking **unless** the active L2 skill mandates Wait-then-poll |

## Async job standard flow (default)

1. **On submit** — read `tracking.user_message` from response, **send to user immediately** (job_id, estimated credits/time); tell user they can ask for progress anytime in this thread.
2. **End the turn** — when `tracking.should_continue_polling` is `false`, **do not** call `creative_get_job`, **do not** `sleep` — **unless** the active skill says Wait-then-poll.
3. **Progress checks** — when user asks in this thread, call `creative_get_job` or `creative_list_jobs` once and answer; **no** auto sleep/polling loops (default).
4. **User follow-up** — single `creative_get_job` or `creative_list_jobs` per question; still **no** polling loop (default).
5. **Cancel** — user says "cancel" → `creative_cancel_job`.

## Wait-then-poll (skill override)

When the active skill requires it (handheld batch video, etc.):

1. After submit, notify user with job_ids + ETA.
2. Sleep once for **max ETA** (from `estimate.eta_sec`; skill may set fallback).
3. Query all jobs; if all terminal → continue that skill’s next step (concat / remix).
4. Else sleep **interval from that skill** (handheld = **20s**) and query again until done or skill timeout.

## vs old behavior

| ❌ Old (forbidden) | ✅ Now (required) |
|-------------------|-------------------|
| Poll `creative_get_job` every 10s / 30s / 60s | Return immediately after submit |
| `sleep` in chat | Query only when user asks |
| Wait for final video before replying | Confirm submit + job_id; user can follow up |

## Sync generation (image / audio only)

**Before** calling sync image/TTS/BGM: tell user expected wait.

After tool returns, deliver `tracking.user_message` + artifact URLs. VIP or coin errors → follow **creative-platform** billing rules.

**Video is never sync** — tools return `job_id`. Default: confirm submit, wait for user follow-up. **Exception**: skills with Wait-then-poll (e.g. handheld-product-avatar) auto-wait ETA then poll.

## Agent behavior

- Follow `tracking.agent_action` literally; if it says "no polling", do not ignore.
- **Do not** send task dashboard links; progress stays in this chat.
- User says "my jobs" → `creative_list_jobs` and show list in chat.

## Delivery

- When job is `completed` and user is still in thread, deliver `artifacts[0].urls.download` + local save hint.
- `delivery.mode=both` (default): URL + `local.suggested_filename` / `suggested_subpath`
