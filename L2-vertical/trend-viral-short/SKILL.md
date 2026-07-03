---
name: trend-viral-short
description: 热点短视频 — 批量钩子变体，适合 TikTok/Reels 带货
metadata:
  layer: L2-vertical
  requires: [creative-job-runner, creative-platform, creative-script2film, creative-script2film-keyframes, creative-direct]
  tags: [trend, batch, ecommerce, image]
---

# 热点短视频（Trend Viral Short）

追热点、快速产出多条可 A/B 的竖版短视频变体。

## 适用

- MCN 日更、热点跟进
- 同一产品多种开头钩子测试（**图片**变体）

## 用户要「视频成片」时

本 Skill 默认出**批量图片**。若用户要视频，按需求切换 L1 Skill：

| 需求 | Skill | MCP |
|------|-------|-----|
| 多镜带货成片 + 产品 reference | creative-script2film | `creative_submit_script2film` |
| 多镜 + 首尾帧转场 | creative-script2film-keyframes | `creative_submit_script2film_keyframes` |
| 单段热点短视频 | creative-direct | `creative_generate_video` / `creative_first_frame_to_video` |

确认意图后再提交，不要默认走 batch_variants。

## 流程（图片变体）

1. 整理 brief：`product`、`trend_tags`（热点关键词）、`hook_idea`（可选）
2. `creative_estimate` workflow_type=`batch_variants`, params=`{ count: 5 }`
3. `creative_submit_batch_variants`:
   - `prompt`: 结合热点与卖点的英文/中文提示词
   - `count`: 默认 **5**
   - `aspect_ratio`: **9:16**
   - `preset`: **trend_viral_v1**
4. **creative-job-runner** — 提交后立即推送 `tracking.user_message`，**禁止** sleep / 轮询
5. 按变体编号列出 artifacts，并给出投放优先级建议

## Preset 约束（trend_viral_v1）

- 前 3 秒强钩子
- 产品特写 ≤ 全片 40%
- 禁止侵权热点、敏感内容

## Technique 注入

编排时参考 preset 文件：`presets/trend_viral_v1.json`
