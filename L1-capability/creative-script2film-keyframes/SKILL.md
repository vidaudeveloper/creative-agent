---
name: creative-script2film-keyframes
description: 脚本→成片（首尾帧/首帧生视频）— 逐镜关键帧驱动 Seedance 过渡动画
metadata:
  layer: L1-capability
  requires: [creative-job-runner, creative-platform]
  tags: [storyboard, async, script2film, keyframes, first-frame, one-click]
---

# Creative Script2Film — 首尾帧生视频

与 **creative-script2film**（参考图生视频）共用同一 script2film 工作流，但逐镜生视频使用 **首帧 / 首尾帧** 模式，而非 reference 参考图。

## 何时选用

| 场景 | 推荐 Skill |
|------|------------|
| 产品/人物需与参考图高度一致、多 reference 约束 | **creative-script2film**（reference） |
| 镜头间需平滑过渡、运动轨迹可控 | **本 Skill**（first_last_frame） |
| 单镜从静态关键帧展开动作、无需尾帧 | 本 Skill + `video_mode: first_frame` |
| 单段短视频（非多镜成片） | **creative-direct** + `creative_first_frame_to_video` |

## 流程（与 reference 版共用 script2film 工作流）

与 **creative-script2film** 共用同一服务端 pipeline，**仅 `video_mode` 不同**（本 Skill 默认 `first_last_frame`）。

1. `creative_estimate` workflow_type=`script2film`
2. **`creative_submit_script2film_keyframes`**（默认 `video_mode=first_last_frame`）:

```json
{
  "script": "<用户脚本>",
  "target_duration_sec": 30,
  "aspect_ratio": "9:16",
  "reference_image_urls": ["<产品主图>"],
  "brief": { "product": "..." },
  "client_request_id": "<uuid>"
}
```

3. **creative-job-runner** — 提交后立即发送 `tracking.user_message`，**禁止** sleep / 轮询；**artifacts[0]** 为成片（含 BGM，除非 `skip_bgm: true`）

### 服务端执行顺序（与 reference 版一致）

1. **提取关键元素** — character / scene / prop / style / brand，绑定用户参考图
2. **规划分镜** — 镜数、每镜 `duration_sec`（总和 = 目标时长）、`key_element_ids`
3. **生成元素参考图** — Identity Board 设定板（全片视觉锚点）
4. **并行生图** — 逐镜关键帧；prompt 织入元素描述 + 图N，refs = 该镜关联元素图
5. **并行生视频** — Seedance **first_last_frame**（见下节）
6. FFmpeg 拼接 + BGM

## 首尾帧原理（与 reference 版的唯一差异）

| 阶段 | reference 版 | 首尾帧版（本 Skill） |
|------|-------------|---------------------|
| 关键元素 + 元素参考图 | ✅ 相同 | ✅ 相同 |
| 逐镜生图 | 元素锚点 + 织入 prompt | ✅ 相同 |
| 逐镜生视频 | Seedance **reference**（元素图 + 关键帧） | Seedance **first_last_frame**（仅首/尾关键帧） |
| motion prompt | 织入元素描述 | ✅ 相同（帮助动作与主体一致） |

每镜生视频：

- **首帧** = 本镜关键帧（已由元素锚点约束）
- **尾帧** = 下一镜关键帧（最后一镜尾帧 = 本镜关键帧）

> 元素参考图**不传入** Seedance 生视频（首尾帧模式只用关键帧图片），一致性主要靠 **步骤 3–4** 锁定的关键帧外观；镜头间过渡更顺。

## 关键元素与用户参考图

与 **creative-script2film** 相同：用户参考图在**提取关键元素**阶段语义绑定，再生成元素 Identity Board，逐镜生图时按 `key_element_ids` 传入对应元素参考图。

| 阶段 | 首尾帧版行为 |
|------|-------------|
| 提取 / 规划 / 元素参考图 | 与 reference 版相同 |
| 逐镜生图 | 元素锚点 + 织入 prompt |
| 逐镜生视频 | 仅用本镜/下一镜**关键帧**，不用 reference 元素图 |

## 时长规划

与 reference 版相同：`target_duration_sec` 在规划期分配各镜 duration，**总和必须等于目标**（±3s）。

## video_mode 参数

| 值 | 说明 |
|----|------|
| `first_last_frame` | **默认** — 首帧 + 尾帧，镜头过渡更顺 |
| `first_frame` | 仅首帧，适合单镜内动作展开 |

也可走通用入口 `creative_submit_script2film` 并显式传 `video_mode`。

## 同步单段（非成片）

已有首尾帧图片、只需一段视频时：

```
creative_first_frame_to_video:
  prompt: "..."
  first_frame_url: "<首帧 URL>"
  last_frame_url: "<尾帧 URL>"   # 可选；省略则 first_frame 模式
  duration_sec: 5
  aspect_ratio: "9:16"
```

## 依赖

- 服务端 ffmpeg（或 `FFMPEG_BIN`）
- `RUNWARE_API_KEY`（BGM，可选）

## 分镜失败与重试

与 **creative-script2film** 相同：若某镜因 Seedance **版权/IP** 或 **真人脸隐私** 拦截失败，请引导用户**修改该镜 prompt / 更换参考图**后，用**新 `client_request_id`** 重提任务。详见 reference 版 Skill 的「分镜失败与重试」章节。
