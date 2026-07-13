---
name: product-image-to-jianying-remix
description: >-
  Accepts batch video generation from one product image — async parallel
  creative_submit_workflow (direct_video, default 5×4s) → poll every 15s →
  jianying-remix CapCut/Jianying draft remix and export.
metadata:
  layer: L2-vertical
  requires:
    [
      creative-platform,
      creative-job-runner,
      creative-seedance2-prompt,
      creative-batch-orchestrator,
      jianying-remix,
    ]
  tags: [ecommerce, product, image, batch, video, jianying, remix, end-to-end]
---

# 产品图 → 场景片段批量生成 → 剪映混剪

用户只上传**一张产品图**时启用：先**批量生成**多段「产品应用场景」短视频，轮询全部完成后，再加载 **jianying-remix** 做本机剪映级混剪成片。

## 接受「批量生成」

本 skill **明确接受**用户的批量生成诉求，例如：

- 「批量生成 5 段场景视频再混剪」
- 「用这张产品图批量出应用场景」
- 「生成多段演示片然后剪映混剪」

| 字段 | 默认 | 可改 |
|------|------|------|
| `batch` / 批量生成 | **开启**（本 skill 主路径） | — |
| `clip_count` | `5` | 1–10（>10 拆批） |
| `duration_sec` | `4` | 4–15 |
| `aspect_ratio` | `9:16` | `1:1` / `16:9` |
| `product_image` | 必填 | 附图 / 本地 / URL |

**批量 MCP 约定（仅本 L2 出片阶段）：**

- 入口：并行多次 `creative_submit_workflow`，`workflow_type=direct_video`
- **不是** `creative_submit_batch_variants`（出图变体）
- **不是** sync `creative_image_to_video` / `creative_generate_video`
- 提交后每 **15 秒**轮询，齐套再交给 **jianying-remix**（混剪阶段**禁止**再调 `direct_video`）

> 只有产品图 → 本 L2 负责 AI 出片段；已有多段用户视频 → 直接 **jianying-remix**（可 §1.0 批量多版转场/特效/BGM）。

---

## 何时使用

- 用户丢一张产品图，要「多场景展示 + 剪映混剪成片」
- 明确说**批量生成**场景片段 / 产品演示混剪 / 图生多段视频再剪映

## 何时不用

| 需求 | 改走 |
|------|------|
| 只有产品页 URL，要先抓详情 | **product-url-to-video** |
| 只要一张/几张营销图变体 | **trend-viral-short** + `creative_submit_batch_variants` |
| 只要单条 ≤15s 短视频、不要混剪 | **creative-direct** |
| 已有多段本地视频，只要混剪 / 多版转场特效 BGM | 直接 **jianying-remix** |
| 批量生成但无产品图（文生多段） | **creative-direct** / batch-orchestrator — **不要**指望 jianying-remix 出片 |
| 只要 30s+ 多镜故事成片（云端拼接） | **creative-script2film** |

---

## 总流程

```
1. 收产品图 → 上传得 HTTPS URL
2. 确认产品信息 + 规划 N 个应用场景（默认 5）← 接受批量参数
3. creative-seedance2-prompt → 每段独立视频 prompt
4. creative_estimate（按段汇总）→ 告知积分/耗时
5. 【批量生成】并行 creative_submit_workflow × N（direct_video，4s）
6. 后台每 15s 轮询全部 job_id，直到完成/失败
7. 收集视频 URL（尽量落本地）
8. 加载 jianying-remix → Edit Plan → 编译/导入/（Windows）导出
```

---

## 1. 收图与上传

1. 用户附图 / `@image` / 本地路径 / 已有 HTTPS URL
2. 走 **creative-platform**：
   - 优先 `creative_get_upload_instructions` → 本机 PUT → `upload.file_url`
   - 无终端时 `creative_upload_reference`（`content_base64`）
3. 记下唯一 `product_image_url`（后续每段 `reference_image_urls` 都用它）

若无法得到可访问 URL：**停止**，请用户重传。

---

## 2. 场景规划（默认 5 段 · 批量规格）

解析用户批量意图（可一次确认默认）：

| 参数 | 默认 | 可改 |
|------|------|------|
| `clip_count` | `5` | 1–10（与 batch 上限对齐） |
| `duration_sec` | `4` | 4–15（MCP 约束） |
| `aspect_ratio` | `9:16` | `1:1` / `16:9` |
| 字幕 | 默认不加 | 用户明确要再写 |
| BGM | 混剪阶段默认开 | 用户说不要则关 |

识别品类与**产品图特点 + 用户需求**后，按 [references/scene-presets.md](references/scene-presets.md) 的原则**现场推导** N 段互不重复的展示意图；每段写自定义 `label` + 一句意图。

**禁止**照抄固定场景清单（不要默认「街拍/通勤/咖啡/影棚/居家」五件套）。

**服饰 / 鞋子 / 服装配饰（默认规则，场景内容不写死）：**

- `clip_count=5`（用户另有指定则服从）  
- **不同模特 × 不同场景** 的穿着/穿戴展示为主  
- 具体场景与模特气质：**根据该单品特点与用户需求判断**（如户外服偏户外、正装偏职场/正式、跑鞋偏运动场等）  
- 不要默认平铺静物；除非用户只要静物/特写

把规划表发给用户（产品判断 + 每段 label/模特差异/场景）；用户可改。未反对即按**该次推导的表**执行。

---

## 3. Prompt 门禁（每段必做）

对每一段：

1. 加载 **creative-seedance2-prompt**
2. 输入：产品图角色（主体参考）+ 该段场景意图 + `duration_sec=4` + 画幅
3. 输出可粘贴的 Seedance prompt（强调：**产品外观与参考图一致**、场景差异化、镜头与动效）
4. **服饰/鞋子**：写明该段模特差异 + **本次推导的**场景地点（来自产品与需求，非模板）
5. **禁止**把用户原话直接当 MCP `prompt`

同一产品图、不同场景 → **N 条不同 prompt**，不要复制粘贴同一句。

---

## 4. 估价

对每个 clip 估一次（或汇总告知）：

```text
creative_estimate
  workflow_type: direct_video
  params: { duration_sec: 4 }
```

向用户报：`合计约 credits × N`、`预计生成约数分钟（并行）`。用户明确说继续 / 默认同意后再提交。

---

## 5. 批量异步提交（并行 = 批量生成）

对每个场景生成一个 UUID `client_request_id`，**并行**调用：

```json
{
  "workflow_type": "direct_video",
  "input": {
    "prompt": "<该段 Seedance prompt>",
    "duration_sec": 4,
    "aspect_ratio": "9:16",
    "reference_image_urls": ["<product_image_url>"]
  },
  "delivery": { "mode": "both" },
  "client_request_id": "<uuid>"
}
```

规则：

- 用 **`creative_submit_workflow`**，不要 sync 的 `creative_image_to_video` / `creative_generate_video`
- 不要用 `creative_submit_batch_variants`（图变体，不是视频）
- `clip_count > 10` 时拆成多批（对齐 **creative-batch-orchestrator** 上限）
- 提交后立刻给用户一张表：`# | 场景 label | job_id | 状态=submitted`

可参考 **creative-batch-orchestrator** 的 manifest 组织方式，但本 skill **不在提交后结束回合**——必须进入轮询。

出片仅发生在本 L2；**jianying-remix 不负责** `direct_video`。

---

## 6. 后台轮询（每 15 秒）

**本 skill 强制轮询**（例外于 creative-job-runner 的「提交即停」）：

1. 记下全部 `job_id`
2. 告知用户：「批量生成中，后台每 15 秒检查；全部完成后自动进入剪映混剪」
3. 循环：
   - `sleep` / 等待 **15 秒**
   - 对每个未终态 job 调用 `creative_get_job`
   - 状态：`queued` / `running` → 继续；`completed` → 收 artifact；`failed` / `cancelled` → 记失败原因
4. 退出条件：全部 job 为 `completed` / `failed` / `cancelled`
5. 轮询期间可向用户推送简短进度（如 `3/5 完成`），避免刷屏——大约每 1–2 轮汇总一次即可

### 结果处理

| 结果 | 动作 |
|------|------|
| ≥2 段 `completed` | 用成功片段继续混剪；失败段写入 warnings |
| 仅 1 段成功 | 询问：仍用单段做极简混剪，还是重试失败段 |
| 0 段成功 | **停止**；展示错误；可重试提交，不进入 jianying-remix |

从每个成功 job 取 `artifacts[0].urls.download`（或同等视频 URL）。尽量下载到本地临时目录（如 `/tmp/vidau-product-clips/`），文件名带场景序号，便于 Edit Plan 写 `path`。

---

## 7. 交接 jianying-remix

**必须加载完整 jianying-remix skill**，按其流程执行（探测 `jy-compile`、写 Edit Plan、校验、编译、导入、Windows 可 export）。  
把已生成片段当作**用户提供视频**交给它；**禁止**在混剪阶段再调 `creative_submit_workflow` / `direct_video`。若用户还要多版转场/特效/BGM，走 jianying-remix **§1.0 批量混剪变体**。

对本流水线的约定：

- `clips[]`：按场景顺序放入成功片段的本地 `path`（或 `url`）；`in_ms=0`，`out_ms` 可用满时长（约 4000）
- `junctions`：相邻段按内容气质选不同转场（见 jianying-remix presets）
- `overlays`：按段选不同轻特效；**默认不加字幕**（用户要再加）
- `bgm`：默认开启 → 用户无文件时用 MCP **`creative_generate_bgm`**（不要走曲库 select）
- 有 BGM 时原片默认静音（编译器自动）

交付话术示例：

> 已批量生成 N 段场景视频并完成剪映混剪。草稿名 `<name>`。场景：1…N。失败段：…（若有）。请打开剪映预览；Windows 已尝试自动导出则附 MP4 路径。

---

## 检查清单

- [ ] 已接受用户批量生成意图（`clip_count` / `duration_sec`）  
- [ ] 产品图已上传为 HTTPS URL  
- [ ] 服饰/鞋子时：5 段不同模特 × 不同场景（场景按产品与需求推导，非写死模板）  
- [ ] N 个场景互不重复，每段独立 Seedance prompt  
- [ ] 并行 `creative_submit_workflow` × N，`duration_sec=4`  
- [ ] 每 15s 轮询至全部终态  
- [ ] 成功片段 URL/本地 path 齐全  
- [ ] 已加载并跑完 **jianying-remix**（含 BGM 默认）  

## 相关

- 场景候选：[references/scene-presets.md](references/scene-presets.md)  
- 混剪（仅用户视频 / 多版转场特效 BGM）：`L1-capability/jianying-remix/SKILL.md`  
- 批量提交惯例：`L1-capability/creative-batch-orchestrator/SKILL.md`
