---
name: creative-batch-orchestrator
description: 批量编排 — 同一批次最多 10 条，可混用不同 Skill/MCP 并行提交与追踪
metadata:
  layer: L1-capability
  requires: [creative-job-runner, creative-platform, creative-direct, creative-script2film, creative-script2film-keyframes]
  tags: [batch, orchestrator, multi-skill, video, async]
---

# Creative Batch Orchestrator — 批量编排

将**多条独立生成任务**组成一个批次，**允许混用不同 Skill**（script2film、首尾帧、直出视频、批量图变体等），并行提交后统一追踪与交付。

> **依赖**：必须先加载 **creative-job-runner**（多 job UI 追踪）与 **creative-platform**（积分/权益）。  
> **典型规模**：**10 条/批**（硬上限 10；超出则拆成多批）。  
> **任务可见性**：批次内**全部走异步 job**（含直出图/视频），均出现在 `creative_list_jobs` / Dashboard；**禁止**在批次内调用同步 MCP（`creative_generate_*` / `creative_image_to_video` 等）。

## 适用

- 同一产品用多种成片方式 A/B（reference vs 首尾帧 vs 直出）
- 多个商品 / 多条脚本一次性出片
- 混排：3 条 script2film + 5 条 direct_video + 2 条 batch_variants 图片
- 运营日更：批量提交后后台追踪，不必逐条等完再提交下一条

## 不适用

- 单条任务 → 直接用对应 L1/L2 Skill，勿套批次
- 同一 prompt 只要 N 张图变体 → **trend-viral-short** + `creative_submit_batch_variants`（单 job 即可）
- 单条「当场就要结果、不进任务列表」→ **creative-direct** 同步 MCP（勿放入批次）

---

## 批次清单格式

向用户确认或自行整理为 **items 数组**（1–10 条）：

```yaml
batch_label: "618 带货批次-A"          # 可选，便于汇报
items:
  - label: "SKU-A 参考图成片"
    skill: creative-script2film
    input:
      script: "..."
      target_duration_sec: 30
      aspect_ratio: "9:16"
      reference_image_urls: ["https://..."]
      brief: { product: "...", audience: "..." }
      delivery: { mode: "both" }

  - label: "SKU-B 首尾帧"
    skill: creative-script2film-keyframes
    input:
      script: "..."
      target_duration_sec: 30
      shot_duration_sec: 5

  - label: "热点钩子-直出"
    skill: creative-direct-video
    mode: image_to_video                    # text_to_video | image_to_video | first_frame | first_last_frame
    input:
      prompt: "..."
      duration_sec: 5
      aspect_ratio: "9:16"
      reference_image_urls: ["https://..."]

  - label: "主图-直出"
    skill: creative-direct-image
    input:
      prompt: "..."
      aspect_ratio: "9:16"
      reference_urls: ["https://..."]

  - label: "钩子图变体 x5"
    skill: trend-viral-short
    input:
      prompt: "..."
      count: 5
      aspect_ratio: "9:16"
      preset: trend_viral_v1

  - label: "独立站链接-成片"
    skill: product-url-to-video
    workflow: script2film                   # script2film | keyframes | direct
    input:
      product_url: "https://..."
      # Agent 先按 product-url-to-video Skill 抓取后再填 script / reference_image_urls
```

每条 **必须** 有唯一 `label`（交付表格用）。提交前为每条生成 **`client_request_id`（UUID）**，幂等防重复扣费。

---

## Skill → MCP 映射（提交时严格按表调用）

| `skill` 字段 | 加载的 Skill 文档 | MCP 工具 | workflow_type |
|--------------|-------------------|----------|---------------|
| `creative-script2film` | creative-script2film | `creative_submit_script2film` | `script2film` |
| `creative-script2film-keyframes` | creative-script2film-keyframes | `creative_submit_script2film_keyframes` | `script2film` |
| `creative-direct-video` | creative-direct | `creative_submit_workflow` | `direct_video` |
| `creative-direct-image` | creative-direct | `creative_submit_workflow` | `direct_image` |
| `trend-viral-short` | trend-viral-short | `creative_submit_batch_variants` | `batch_variants` |
| `product-url-to-video` | product-url-to-video | 抓取完成后 → 上表任一 L1 MCP | 见 workflow |

**批次内全部为异步 job**，提交后均有 `job_id`，可用 `creative_get_job` / `creative_list_jobs` / `creative_cancel_job` 追踪。

### 直出视频 `mode` → `creative_submit_workflow` 的 `input`

统一调用：

```json
{
  "workflow_type": "direct_video",
  "input": { "...见下表..." },
  "delivery": { "mode": "both" },
  "client_request_id": "<uuid>"
}
```

| mode | `input` 必填字段 |
|------|------------------|
| `text_to_video`（无参考图） | `prompt`, `duration_sec`, `aspect_ratio` |
| `image_to_video`（参考图生视频） | 上列 + `reference_image_urls` 或 `reference_image_url` |
| `first_frame`（单首帧） | 上列 + `video_mode: "first_frame"`, `first_frame_url` |
| `first_last_frame`（首尾帧） | 上列 + `video_mode: "first_last_frame"`, `first_frame_url`, `last_frame_url` |

示例（参考图直出视频）：

```json
{
  "workflow_type": "direct_video",
  "input": {
    "prompt": "产品特写，缓慢旋转，带货风格",
    "duration_sec": 5,
    "aspect_ratio": "9:16",
    "reference_image_urls": ["https://example.com/product.jpg"]
  },
  "delivery": { "mode": "both" },
  "client_request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 直出图片 → `creative_submit_workflow`

```json
{
  "workflow_type": "direct_image",
  "input": {
    "prompt": "...",
    "aspect_ratio": "9:16",
    "reference_urls": ["https://..."]
  },
  "delivery": { "mode": "both" },
  "client_request_id": "<uuid>"
}
```

### L2 垂类（product-url-to-video）

批次项为 `product-url-to-video` 时：

1. **先**按 **product-url-to-video** Skill 完成 URL 抓取与用户确认（可批量抓取，再一次性确认整批）
2. 根据该项的 `workflow` 字段映射到 L1 MCP（默认 `script2film`）
3. `workflow: direct` 时映射为 `creative-direct-video` + `creative_submit_workflow`（`direct_video`），主图写入 `reference_image_urls`
4. 将抓取到的 `product_name`、`description`、主图 URL 写入 `script` / `brief` / `reference_image_urls` 后再提交

---

## 标准流程（必做）

### 1. 校验批次

- `items.length` 为 **1–10**；超过 10 → 拆批并告知用户
- 每条 `label` 非空；`skill` 在上表范围内
- 缺 script / prompt / URL 等必填项 → 向用户补问，**勿提交半成品**
- 确认未使用同步 MCP（`creative_generate_*` 等）

### 2. 估积分

1. `platform_get_credits`
2. 对**每条**调用 `creative_estimate`（`workflow_type` 与 input 对齐）：

| skill | estimate workflow_type | params 示例 |
|-------|------------------------|-------------|
| creative-script2film / keyframes | `script2film` | `{ target_duration_sec: 30 }` |
| trend-viral-short | `batch_variants` | `{ count: 5 }` |
| creative-direct-video | `direct_video` | `{ duration_sec: 5 }` |
| creative-direct-image | `direct_image` | `{}` |

3. **汇总表格**给用户确认（label、skill、预估积分、预估耗时）：

```
| # | label | skill | 预估积分 | 备注 |
|---|-------|-------|----------|------|
| 1 | SKU-A | script2film | 120 | ~15min |
| 2 | 热点直出 | direct_video | 8 | ~3min job |
| … | … | … | … | … |
| 合计 | | | 528 | 约 20–40min 并行 |
```

用户确认后再提交。

### 3. 并行提交

- **全部 items 异步提交**：一次性并行调用各 `creative_submit_*` / `creative_submit_workflow`（每条独立 `client_request_id`）
- 维护内存表 **batch_tracker**（与 `creative_list_jobs` 互补）：

```json
{
  "batch_label": "618 带货批次-A",
  "items": [
    {
      "index": 1,
      "label": "SKU-A",
      "skill": "creative-script2film",
      "workflow_type": "script2film",
      "client_request_id": "uuid-1",
      "job_id": "uuid-job-1",
      "status": "running"
    },
    {
      "index": 2,
      "label": "热点直出",
      "skill": "creative-direct-video",
      "workflow_type": "direct_video",
      "client_request_id": "uuid-2",
      "job_id": "uuid-job-2",
      "status": "queued"
    }
  ]
}
```

提交后立即发送汇总：`已提交 N 条异步任务` + 各 `job_id`，并告知用户可在本对话中随时询问进度

### 4. 追踪（creative-job-runner 扩展）

1. **禁止** sleep / 循环 `creative_get_job`；每条 submit 后发送 `tracking.user_message`
2. 告知用户可在本对话中随时询问整批或单条任务进度
3. 用户主动追问批次进度时，可 **单次** `creative_list_jobs` 或针对某 `job_id` 调用 `creative_get_job` 回答
4. 全部终态后在本对话交付批次结果表（见 §5）

**勿在对话中长时间等待**；保留各 `job_id`，用户可随时在本对话中询问进度

### 5. 交付

全部终态后输出 **批次结果表**：

```
| # | label | skill | job_id | 状态 | 产物 |
|---|-------|-------|--------|------|------|
| 1 | SKU-A | script2film | uuid-1 | ✅ | https://... |
| 2 | 热点直出 | direct_video | uuid-2 | ✅ | https://... |
| 3 | 链接B | script2film | uuid-3 | ❌ | error: ... |
```

- 成功项：`artifacts[0].urls.download` + `local` 落盘提示
- 失败项：`error` + 是否建议单条重试（新 `client_request_id`）
- 统计：成功 M / 共 N，总消耗积分

---

## 取消与重试

| 操作 | 行为 |
|------|------|
| 用户说「取消整批」 | 对 batch_tracker 中 `queued`/`running` 的 job 逐个 `creative_cancel_job` |
| 用户说「取消第 3 条」 | 仅 cancel 对应 `job_id` |
| 单条失败重试 | **新 UUID** 作为 `client_request_id`，勿复用失败项 id |
| 整批重跑失败项 | 仅重提 failed 条目，保留成功项结果 |

---

## 并发建议

| 类型 | 建议 |
|------|------|
| script2film / keyframes | 可并行提交（服务端镜内并行）；整批 10 条同时跑时注意积分峰值 |
| direct_video / direct_image | 可与其他 job 并行提交；单 job 内 1 步，耗时约 2–5 分钟 |
| batch_variants | 单 job 内已批量，占 1 个批次槽位 |
| 混合批次 | 10 条可一次性全部 submit，统一在本对话中追踪 |

---

## 示例：10 条混排批次

用户：「这 3 个商品链接各出 reference 成片，再加 2 条首尾帧脚本，5 条热点直出视频。」

1. 拆 10 items（3×product-url-to-video + 2×keyframes + 5×direct-video）
2. 抓取 3 个 URL → 生成 3 份 script + reference
3. estimate 汇总 → 用户确认
4. **并行 submit 10 个异步 job**（5× `direct_video` 走 `creative_submit_workflow`）
5. 提交后立即告知用户可在对话中查询进度；用户追问或任务全终态后 → 交付 10 行结果表（含 job_id）

---

## 注意

- 批次是 **Agent 侧编排概念**，服务端无统一 parent job；靠 `batch_tracker` + `creative_list_jobs` 维护
- **直出也进任务列表**：批次内直出必须用 `creative_submit_workflow`，勿用 `creative_generate_video` 等同步工具
- 单条对话、不进面板 → 仍可用 **creative-direct** 同步 MCP
- 同一 `client_request_id` 幂等：重试必须换新 UUID
- L2 Skill 的 preset / 约束（如 trend_viral_v1）仍按原 Skill 执行，本 Skill 只负责调度
- 视频类优先确认用户要 **成片** 而非仅图片变体
