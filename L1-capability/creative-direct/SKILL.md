---
name: creative-direct
description: 直出生图、生视频、图生视频（同步，单段 ≤15 秒；默认有声）
metadata:
  layer: L1-capability
  requires: [creative-platform, creative-job-runner]
  tags: [image, video, sync, one-click]
---

# Creative Direct — 直出

适用于单张广告图、**单段 ≤15 秒**带货短视频，无需故事板。

> **时长路由**：用户要 **16 秒以上** / 30s / 60s / 多镜 / 故事板 → 用 **creative-script2film**（先 `creative_generate_script`），**勿**用本 Skill 硬做长片。

> **任务追踪**：调用任何生成工具前加载 **creative-job-runner**；同步任务也要给用户实时状态反馈。

## 生视频 Skill 选型

| 需求 | Skill | MCP |
|------|-------|-----|
| 有 reference 图，要产品一致 | **creative-script2film** | `creative_submit_script2film` |
| 首尾帧过渡、运镜可控 | **creative-script2film-keyframes** | `creative_submit_script2film_keyframes` |
| 单段短视频 | **本 Skill** | `creative_generate_video` / `creative_image_to_video` / `creative_first_frame_to_video` |

## 生图

1. 告知用户：「正在生图，约 1–2 分钟…」
2. **有用户本地/附件参考图时**（`@image` 等）：
   - **优先** `creative_get_upload_instructions` → 本机 curl/terminal PUT 上传到 S3 → 取 `upload.file_url`
   - 兜底（无本机终端）：`creative_upload_reference`（`content_base64`）
3. `creative_generate_image`:
   - `prompt`: 用户描述
   - `aspect_ratio`: `9:16` | `1:1` | `16:9`
   - `reference_urls`: 可选，填入上一步 `file_url`（或已有 HTTPS 外链）
4. 读取 `tracking.user_message`，返回 `artifacts[0].urls.download` 与 `local` 落盘提示

## 生视频

1. 告知用户：「正在生视频，约 2–5 分钟…」
2. 有用户参考图时用 **`creative_image_to_video`**（Seedance **参考生视频**，`reference_image` 角色，**非首尾帧**）：
   - `reference_image_urls`: 产品 / 人物 / 场景 / 风格等（最多 9 张）
   - 或单张 `reference_image_url`
4. 无参考图时用 `creative_generate_video`（纯文生视频）
5. 交付 artifacts + `tracking.user_message`

## 可选：BGM 配乐

单段短视频如需背景音乐：

1. `creative_generate_bgm`（可传 `script` / `brief` / `bgm_hint` 自动规划提示词）
2. `creative_mux_bgm_into_video` — `video_url` + `bgm_url` 混入配乐

> script2film 一键成片会在工作流内**自动**完成 BGM；直出视频需手动调用上述两步。

## 默认参数

- 竖版短视频：`aspect_ratio=9:16`, `duration_sec=5`
- **有声视频**：`generate_audio=true`（默认）；镜内音效由 Seedance 生成
