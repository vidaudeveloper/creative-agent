---
name: creative-task-runner
description: Use after submit; MUST arm bg sleep+poll; NOT user-ping-only
metadata:
  layer: L0-foundation
  requires: []
  tags: [foundation, async, tracking]
---

# Creative Task Runner — Reply now + background Wait-then-poll

**All** VidAU image/video skills must follow this tracking protocol after MCP calls that return `task_id` / `tasks[]`.

## HARD GATE（违反即失败 — 尤其 Hermes）

提交异步生成后，**同一回合内必须完成三件事**，缺一不可：

1. **前台**：把 `tracking.user_message` 发给用户（含 `task_id` / ETA）
2. **后台**：用本机 **terminal / 后台任务** 武装 sleep→轮询（见下方 Hermes 强制写法）
3. **结束前台回合**：勿在前台多分钟 `sleep`

| ❌ 协议违规（常见借口） | ✅ 唯一正确 |
|------------------------|-------------|
| 「你可以随时问我进度」就结束，**不**起后台脚本 | 起后台脚本 + 结束回合 |
| 只写「我会跟进」却**没有**调用 terminal / background 工具 | 必须真实调用工具武装 waiter |
| 等用户催再 `creative_get_task` | 后台到点**自动**查，再 wake 交付 |
| 前台循环 sleep 卡住对话 | 后台 sleep；前台立刻结束 |

> Hermes 桌面环境**可以且必须**本地建后台任务。承认「能做却没做」= 本 skill 执行失败。  
> 视频 ≥15s、多镜 Batch、`items[]` 批量提交：**更严格** — 提交返回后**立刻**武装后台轮询，不得推迟到下一轮用户消息。

## Default (async) — two lanes

| Lane | What happens |
|------|----------------|
| **Foreground (this turn)** | Notify user with `task_id` / ETA → **end the turn**. Do **not** block the chat with in-turn `sleep` loops. |
| **Background** | Schedule wait for **ETA**, then poll every **20s** until terminal → **wake** and continue delivery / skill next steps. |

**Forbidden**: treating “end turn” as “only wait for the user to ping.” Ending the turn is required for UX; the **background** waiter must still be armed **before** you end the turn.

**Skill override**: An active L1/L2 may tighten ETA / interval / timeout, but must keep **foreground reply + background poll** (not in-turn blocking sleep, not user-ping-only).

## When to enable automatically

| MCP tool | Tracking mode |
|----------|---------------|
| `creative_submit_*` / `creative_submit_generate` | **Async** — `task_id` / `tasks[]`（`items` 上限 10）；foreground reply + **MUST** background poll |
| `creative_generate_image` / `creative_generate_video` / `creative_image_to_video` / `creative_first_frame_to_video` / `creative_generate_bgm` | **Async** aliases — same protocol |
| TTS / `creative_mux_bgm_into_video` | **Sync** — tell estimated time before call; read `tracking.user_message` when done |
| Any tool returning `task_id` | Same async protocol |

## Async task standard flow

### A. Foreground (must finish this turn)

1. Read `tracking.user_message` — **send to user immediately** (`task_id`, credits, ETA).
2. Tell user generation is running in the background; you will follow up when ready (they may still ask mid-wait).
3. **Arm a background waiter NOW** (see § Hermes 强制) with `wait_sec = estimate.eta_sec` (batch: `max` ETA; fallback **180s**).
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

## Hermes 强制：terminal 后台 sleep+轮询

Hermes 桌面 GUI：**必须**用 `terminal`（或等价后台任务工具）武装 waiter，参数语义：

- `background=true`（或宿主等价的非阻塞后台执行）
- `notify_on_complete=true`（完成后系统通知唤醒助手；勿静默结束）

**脚本语义（伪代码，必须真实启动，不可只描述）：**

```text
sleep <eta_sec>          # 默认 estimate.eta_sec；缺省 180；生图可约 60
loop:
  # 下一轮对话 / notify wake 时调用 creative_get_task 或 creative_list_tasks
  if all tasks terminal → exit 0（notify 唤醒 → 交付）
  else sleep 20 → continue
# 总上限约 30 min
```

最小可执行示例（把 `TASK_IDS` / `ETA` 换成本次返回值；用宿主支持的后台方式启动）：

```bash
# Hermes: terminal with background=true, notify_on_complete=true
ETA=180
TASK_IDS="id1 id2"
sleep "$ETA"
# 退出码 0 → notify 唤醒助手；助手再 MCP 查状态；未完成则再后台 sleep 20
echo "AGENT_LOOP_WAKE_creative_task task_ids=$TASK_IDS action=creative_get_task_or_list"
```

未终态时：**再次**用同样方式后台 `sleep 20` + `notify_on_complete`，直到全部终态或超时。

### 其他 runtime

- Cursor / shell: background `sleep <eta_sec>` then wake sentinel（如 `AGENT_LOOP_WAKE_creative_task`）with `task_id`s；未完成再 `sleep 20`。
- 语义必须与 Hermes 相同：**真实调度**，不是文案承诺。

Do **not** hold the user-visible turn inside a multi-minute `sleep`.

### Batch / multi-task / 长视频

- Foreground: notify with **all** `task_id`s → arm **one** background waiter with `max(ETA)`.
- Background: poll until **all** terminal → then continue.
- `creative_submit_generate` 返回 `tasks[]` 后：用返回的全部 `task_id` 武装**一次**后台脚本（不要只盯第一个）。

## vs wrong patterns

| ❌ Forbidden | ✅ Required |
|-------------|-------------|
| Block the chat turn with ETA `sleep` + poll loop | Reply → **arm background terminal** → end turn |
| End turn with **no** background waiter (“ask me anytime” only) | Background ETA → 20s poll → auto continue |
| Promise to follow up without calling background tools | Call terminal/background **in the same turn as submit** |
| Busy-poll from t=0 | Sleep full ETA first, then 20s |
| Drop `task_id` after notify | Keep until delivery / next skill step |

## Sync generation (TTS / mux only)

**Before** calling sync TTS / `creative_mux_bgm_into_video`: tell user expected wait.

After tool returns, deliver `tracking.user_message` + artifact URLs. VIP or coin errors → follow **creative-platform** billing rules.

**Image, video, and BGM are never sync** — tools return `task_id`. Use foreground reply + background poll.

## Agent behavior

- Prefer this L0 protocol over any `tracking.agent_action` that still says “no polling / wait for user” — those strings may lag; still use `tracking.user_message` for user-facing copy.
- MCP `async_strategy` / `agent_action` 要求后台 sleep+轮询时：**立刻执行**，不要等用户再说「你自己轮询」。
- **Do not** send task dashboard links; progress stays in this chat.
- User says "my tasks" / "我的任务" → `creative_list_tasks` and show list in chat.

## Delivery

- On background wake with `completed` (or sync generation done): follow MCP `delivery_strategy`.
- **Default**: save image/video into the conversation **产物** (artifacts) and show the user the artifact + `urls.download`.
- **Do not** default to curl/wget into a local folder. Ignore `local.suggested_subpath` / `suggested_filename` as a default save path.
- Temporary local download is allowed only when the user asks for a disk path, or a later step needs files on disk (ffmpeg concat / mux / etc.).
