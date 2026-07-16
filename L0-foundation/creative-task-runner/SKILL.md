---
name: creative-task-runner
description: Use after submit; reply then background ETA poll
metadata:
  layer: L0-foundation
  requires: []
  tags: [foundation, async, tracking]
---

# Creative Task Runner — Reply now + background Wait-then-poll

**All** VidAU image/video skills must follow this tracking protocol after MCP calls.

**Default (async)** — two lanes:

| Lane | What happens |
|------|----------------|
| **Foreground (this turn)** | Notify user with `task_id` / ETA → **end the turn**. Do **not** block the chat with in-turn `sleep` loops. |
| **Background** | Schedule wait for **ETA**, then poll every **20s** until terminal → **wake** and continue delivery / skill next steps. |

**Forbidden**: treating “end turn” as “only wait for the user to ping.” Ending the turn is required for UX; the **background** waiter must still be armed.

**Skill override**: An active L1/L2 may tighten ETA / interval / timeout, but must keep **foreground reply + background poll** (not in-turn blocking sleep, not user-ping-only).

## When to enable automatically

| MCP tool | Tracking mode |
|----------|---------------|
| `creative_submit_*` | **Async** — `task_id`; foreground reply + background poll |
| `creative_generate_video` / `creative_image_to_video` / `creative_first_frame_to_video` / `creative_generate_bgm` | **Async** — same |
| `creative_generate_image` (and TTS/BGM mux sync tools) | **Sync** — tell estimated time before call; read `tracking.user_message` when done |
| Any tool returning `task_id` | Same async protocol unless skill defines a stricter **background** schedule |

## Async task standard flow

### A. Foreground (must finish this turn)

1. Read `tracking.user_message` — **send to user immediately** (`task_id`, credits, ETA).
2. Tell user generation is running in the background; you will follow up when ready (they may still ask mid-wait).
3. **Arm a background waiter** (see § Background arming) with `wait_sec = estimate.eta_sec` (batch: `max` ETA; fallback **180s**).
4. **End the turn** — do **not** call in-turn `sleep` / busy-poll in the foreground.

### B. Background (after ETA / each wake)

1. On wake → `creative_get_task` (or `creative_list_tasks` for a batch).
2. If still `queued` / `running` → re-arm background wait for **20s** → end wake quietly (brief progress ok every 1–2 wakes; no spam).
3. If terminal:
   - `completed` → deliver artifacts **or** continue the skill’s next step (concat / mux / remix / …).
   - `failed` / `cancelled` → report error; offer retry with a new `client_request_id`.
4. **Timeout** — stop ~**30 min** after the first post-ETA poll; list unfinished `task_id`s.
5. **User mid-wait** — answer with one query; **do not** cancel the background schedule.
6. **Cancel** — user says "cancel" → `creative_cancel_task` and stop the background waiter.

### Background arming (runtime)

Use the host’s **non-blocking** schedule (pick what the runtime supports):

- Cursor / shell: background `sleep <eta_sec>` then emit a wake sentinel (e.g. `AGENT_LOOP_WAKE_creative_task`) with `task_id`s + next action in the payload; on not-done, re-arm `sleep 20`.
- Hermes / other: equivalent deferred wake / cron / background task — **same semantics**.

Do **not** hold the user-visible turn inside a multi-minute `sleep`.

### Batch / multi-task

- Foreground: notify with all `task_id`s → arm one background waiter with `max(ETA)`.
- Background: poll until **all** terminal → then continue.

## vs wrong patterns

| ❌ Forbidden | ✅ Required |
|-------------|-------------|
| Block the chat turn with ETA `sleep` + poll loop | Reply → arm background → end turn |
| End turn with **no** background waiter (“ask me anytime” only) | Background ETA → 20s poll → auto continue |
| Busy-poll from t=0 | Sleep full ETA first, then 20s |
| Drop `task_id` after notify | Keep until delivery / next skill step |

## Sync generation (image / mux only)

**Before** calling sync image/TTS/`creative_mux_bgm_into_video`: tell user expected wait.

After tool returns, deliver `tracking.user_message` + artifact URLs. VIP or coin errors → follow **creative-platform** billing rules.

**Video and BGM are never sync** — tools return `task_id`. Use foreground reply + background poll.

## Agent behavior

- Prefer this L0 protocol over `tracking.agent_action` that still says “no polling / wait for user” — those strings may lag; still use `tracking.user_message` for user-facing copy.
- **Do not** send task dashboard links; progress stays in this chat.
- User says "my tasks" / "我的任务" → `creative_list_tasks` and show list in chat.

## Delivery

- On background wake with `completed` (or sync generation done): follow MCP `delivery_strategy`.
- **Default**: save image/video into the conversation **产物** (artifacts) and show the user the artifact + `urls.download`.
- **Do not** default to curl/wget into a local folder. Ignore `local.suggested_subpath` / `suggested_filename` as a default save path.
- Temporary local download is allowed only when the user asks for a disk path, or a later step needs files on disk (ffmpeg concat / mux / etc.).
