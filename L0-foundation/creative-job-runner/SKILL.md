---
name: creative-job-runner
description: Use after submit; sleep ETA then poll every 20s
metadata:
  layer: L0-foundation
  requires: []
  tags: [foundation, async, tracking]
---

# Creative Job Runner — Submit → wait ETA → poll → continue

**All** VidAU image/video skills must follow this tracking protocol after MCP calls.

**Default (async)**: After submit, notify the user, then run a **background wait**: sleep for the job’s estimated time, then poll every **20s** until terminal, then **continue** the skill’s next steps in the same session.

**Skill override**: An active L1/L2 skill may tighten intervals, ETA fallback, or timeout (e.g. handheld §8, product→jianying remix). Overrides may only make waiting **stricter or more specific** — they must **not** revert to “submit and stop / ask user to ping.”

## When to enable automatically

| MCP tool | Tracking mode |
|----------|---------------|
| `creative_submit_*` | **Async** — `job_id`; default Wait-then-poll |
| `creative_generate_video` / `creative_image_to_video` / `creative_first_frame_to_video` | **Async** — `job_id`; default Wait-then-poll |
| `creative_generate_image` (and TTS/BGM sync tools) | **Sync** — tell estimated time before call; read `tracking.user_message` when done |
| Any tool returning `job_id` | Wait-then-poll unless the active skill defines a stricter schedule |

## Async job standard flow (default)

1. **On submit** — read `tracking.user_message` from response, **send to user immediately** (job_id, estimated credits/time). Say generation is running in the background and you will continue when ready.
2. **Background wait** — `sleep` once for **ETA**:
   - Prefer `estimate.eta_sec` from the submit response (or max ETA across a batch).
   - Fallback if missing: **180s** (video) / skill-stated fallback.
   - Do **not** busy-poll before ETA ends.
3. **Poll** — call `creative_get_job` (or `creative_list_jobs` for a batch). If still `queued` / `running` → `sleep 20s` → query again.
4. **Continue** — when job(s) are terminal (`completed` / `failed` / `cancelled`):
   - `completed` → deliver artifacts (or run the skill’s next step: concat, mux, remix, etc.) **in the same session**.
   - `failed` / `cancelled` → report error; offer retry with a new `client_request_id`.
5. **Timeout** — stop after ~**30 min** total after the first post-ETA poll; list unfinished `job_id`s.
6. **User mid-wait** — if the user asks status while waiting, answer with one query round, then **resume** the 20s loop (do not abandon it).
7. **Cancel** — user says "cancel" → `creative_cancel_job`.

### Batch / multi-job

- `wait_sec = max(estimate.eta_sec)` across submitted jobs (fallback 180s).
- After ETA, poll all non-terminal jobs every 20s until **all** are terminal, then continue.

## vs old behavior

| ❌ Forbidden | ✅ Default now |
|-------------|----------------|
| End turn after submit; “ask me for progress anytime” as the only path | Notify → sleep ETA → poll 20s → continue |
| Busy-poll every few seconds from t=0 | Sleep full ETA first, then 20s interval |
| Ignore `job_id` / never follow up | Keep `job_id`s until delivery or skill next step |
| Stop after notify and wait for user ping | Agent drives the wait/poll loop |

## Sync generation (image / audio only)

**Before** calling sync image/TTS/BGM: tell user expected wait.

After tool returns, deliver `tracking.user_message` + artifact URLs. VIP or coin errors → follow **creative-platform** billing rules.

**Video is never sync** — tools return `job_id`. Always use the async Wait-then-poll flow above.

## Agent behavior

- Prefer this L0 schedule over `tracking.agent_action` / `should_continue_polling` that say “no polling” — those fields reflected the old chat-only mode. Still use `tracking.user_message` for user-facing copy.
- **Do not** send task dashboard links; progress stays in this chat.
- User says "my jobs" → `creative_list_jobs` and show list in chat.
- Progress tips: brief status every 1–2 poll rounds (e.g. `3/5 done`); do not spam.

## Delivery

- When job is `completed`, deliver `artifacts[0].urls.download` + local save hint (or hand off to the active skill’s next step).
- `delivery.mode=both` (default): URL + `local.suggested_filename` / `suggested_subpath`
