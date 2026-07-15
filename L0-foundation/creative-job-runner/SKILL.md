---
name: creative-job-runner
description: Use after submit; no poll unless active skill Wait-then-poll
metadata:
  layer: L0-foundation
  requires: []
  tags: [foundation, async, tracking]
---

# Creative Job Runner — Submit and return + chat tracking

**All** VidAU image/video skills must follow this tracking protocol after MCP calls.

**Default**: Do not `sleep` or loop `creative_get_job` until completion in chat (script2film may take 10–30 minutes).

**Exception (wins over default)**: If the **active** skill defines **Wait-then-poll** (e.g. **handheld-product-avatar** §8, product→jianying remix), you **MUST** sleep + poll per that skill. Do **not** end the turn with “ask me for progress.” The L2 schedule overrides this L0 default.

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

## Wait-then-poll (skill override — mandatory when skill says so)

When the active skill requires it (e.g. **handheld-product-avatar** after batch video submit):

1. After submit, notify user with job_ids + ETA.
2. **Call sleep** once for **max ETA** (from `estimate.eta_sec`; skill fallback, often 180s).
3. Query all jobs; if all terminal → continue that skill’s next step (concat / remix) **in the same session**.
4. Else sleep **interval from that skill** (handheld = **20s**) and query again until done or skill timeout.
5. **Do not** end the turn after step 1. **Do not** ask the user to ping you for progress as a substitute for sleep+poll.

## vs old behavior

| ❌ Forbidden (default path) | ✅ Default now | ✅ Wait-then-poll skills |
|----------------------------|----------------|-------------------------|
| Busy-poll every 10s forever | Return after submit | Sleep ETA → poll → continue skill |
| Ignore job_id | Confirm submit + job_id | Same, **then** auto-wait |
| — | Query only when user asks | Agent drives sleep+poll loop |

## Sync generation (image / audio only)

**Before** calling sync image/TTS/BGM: tell user expected wait.

After tool returns, deliver `tracking.user_message` + artifact URLs. VIP or coin errors → follow **creative-platform** billing rules.

**Video is never sync** — tools return `job_id`. Default: confirm submit, wait for user follow-up. **Exception**: skills with Wait-then-poll (e.g. handheld-product-avatar) **must** auto-wait ETA then poll.

## Agent behavior

- Follow `tracking.agent_action` literally; if it says "no polling", do not ignore — **except** when active skill Wait-then-poll overrides.
- **Do not** send task dashboard links; progress stays in this chat.
- User says "my jobs" → `creative_list_jobs` and show list in chat.

## Delivery

- When job is `completed` and user is still in thread, deliver `artifacts[0].urls.download` + local save hint.
- `delivery.mode=both` (default): URL + `local.suggested_filename` / `suggested_subpath`
