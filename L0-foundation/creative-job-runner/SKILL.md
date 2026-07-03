---
name: creative-job-runner
description: 生图/生视频任务提交后在对话中追踪进度（不在对话里 sleep/自动轮询）
metadata:
  layer: L0-foundation
  requires: []
  tags: [foundation, async, tracking]
  hermes:
    category: vidau-creative
---

# Creative Job Runner — 提交即返回 + 对话追踪

**所有** VidAU 生图/生视频 Skill 在调用 MCP 后，必须启用本 Skill 的追踪协议。  
**禁止** 在对话中 `sleep` 或循环 `creative_get_job` 直到任务完成（script2film 可能需 10–30 分钟）。

## 何时自动启用

| MCP 工具 | 追踪模式 |
|----------|----------|
| `creative_submit_*` | **对话追踪** — 提交后立即回复用户，提示可在对话中查询进度 |
| `creative_generate_image` / `_video` / `image_to_video` | **同步** — 调用前告知预估耗时，完成后读 `tracking.user_message` |
| 任意返回 `job_id` 的工具 | 必须走对话追踪（勿自动轮询） |

## 异步任务标准流程（必做）

1. **提交瞬间** — 读取响应里的 `tracking.user_message`，**立刻发给用户**（含 job_id、预估积分/耗时），并告知用户可在本对话中随时询问任务进度。
2. **结束当前轮次** — `tracking.should_continue_polling` 为 `false`，**不要**再调用 `creative_get_job`，**不要** `sleep`。
3. **进度查看** — 用户在本对话中主动询问时，调用 `creative_get_job` 或 `creative_list_jobs` 回答当前进度；**禁止**自动 sleep / 轮询。
4. **用户主动追问** — 单次调用 `creative_get_job` 或 `creative_list_jobs` 回答，仍 **禁止** 进入轮询环。
5. **取消** — 用户说「取消」→ `creative_cancel_job`。

## 与旧行为的区别

| ❌ 旧（禁止） | ✅ 现（必做） |
|-------------|-------------|
| 每 10s / 30s / 60s 轮询 `creative_get_job` | 提交后立刻返回 |
| 对话里 `sleep` 等待 | 用户询问时再查进度 |
| 等成片完成再回复 | 提交成功即告知 job_id，用户可随时追问 |

## 同步生成（creative-direct）

调用 **之前** 先告诉用户：「正在生成，约需 1–3 分钟，请稍候。」  
工具返回后，将 `tracking.user_message` 与 artifacts URL 一并交付。

## Hermes 行为要点

- 按 `tracking.hermes_action` 字面执行；其中若含「禁止轮询」，不得忽略。
- **不要**向用户发送任何任务页链接；进度统一在本对话中查询。
- 用户说「我的任务」→ `creative_list_jobs`，并在对话中展示列表。

## 交付

- 任务 completed 后，若用户仍在对话中，交付 `artifacts[0].urls.download` 与 `local` 落盘提示。
- `delivery.mode=both`（默认）：URL + `local.suggested_filename` / `suggested_subpath`
