---
name: creative-script2film
description: 15秒以上长视频/多镜成片 — 一句话→脚本→参考图生视频 + FFmpeg 拼接 + BGM
metadata:
  layer: L1-capability
  requires: [creative-job-runner, creative-platform]
  tags: [storyboard, async, script2film, reference, bgm, one-click, long-video, script]
---

# Creative Script2Film — 参考图生视频

将脚本（或一句话创意）自动做到可投放短片。**默认 video_mode=reference**：逐镜用 Seedance 参考图生视频（用户参考图 + 本镜关键帧）。  
若需**首尾帧过渡**，请改用 Skill **creative-script2film-keyframes**。

## 何时选用（优先命中本 Skill）

| 用户意图 | 选用 |
|----------|------|
| **15 秒以上**长视频（16s–120s）、30s/60s 带货片、品牌短片 | **本 Skill** |
| 只有一句话 / 几个卖点，还没有脚本 | **本 Skill**（先 `creative_generate_script`） |
| 多镜成片 + 产品/人物 reference 约束 | **本 Skill** → `creative_submit_script2film` |
| 多镜成片 + 镜头间平滑过渡（首尾帧） | **creative-script2film-keyframes** |
| **单段 ≤15s** 短视频、单镜直出 | **creative-direct**（勿用本 Skill） |

**路由规则**：用户说「30 秒视频」「一分钟短片」「多分镜」「故事板成片」，或 `duration > 15s` → 命中本 Skill；≤15s 单段 → **creative-direct**。

## Agent 流程（用户侧）

### 0. 收集输入（可极简）

用户可能只给一句话，例如：「帮我做 30 秒竖版带货视频，卖这款蓝牙耳机，强调降噪和续航。」

先补问（缺则问，有则跳过）：
- 产品/主题、核心卖点
- 目标时长（**>15s 默认 30s**）、画幅（默认 9:16）
- 参考图（产品图/模特/场景）及各自用途

### 1. 生成脚本（用户无完整脚本时必做）

调用 **`creative_generate_script`**（不扣积分）：

```json
{
  "creative_request": "用户原话或整理后的创意描述",
  "brief": {
    "product": "蓝牙耳机",
    "audience": "年轻通勤族",
    "platform": "抖音"
  },
  "target_duration_sec": 30,
  "aspect_ratio": "9:16",
  "voiceover": false
}
```

**交付给用户**：将返回的 **`spec_markdown`** 以 Markdown 文档完整展示（含 `# Final Video Spec`、画面概述编号列表等）。  
**必须等用户确认**（或按用户修改意见重新 `creative_generate_script`）后再提交成片。

> 用户已粘贴完整 Final Video Spec / 分镜脚本时，可跳过本步，直接用 `script.full_text` 或用户原文作为 `creative_submit_script2film.script`。

### 2. 估积分 + 提交

1. `creative_estimate` workflow_type=`script2film`
2. `creative_submit_script2film`:
   ```json
   {
     "script": "<spec_markdown 或用户确认后的脚本文本>",
     "target_duration_sec": 30,
     "aspect_ratio": "9:16",
     "reference_image_urls": ["<用户上传图1 URL>", "<图2 URL>"],
     "brief": {
       "product": "...",
       "audience": "...",
       "reference_image_urls": ["<同上，可写在 brief 内>"]
     },
     "delivery": { "mode": "both" },
     "client_request_id": "<uuid>"
   }
   ```
3. 将返回的 `job_id` 交给 **creative-job-runner** — **立即**发送 `tracking.user_message`，**结束对话轮次**；**禁止** sleep / 轮询 `creative_get_job`
4. 用户在本对话中询问进度时查询；完成后 **artifacts[0]** 为合成成片（**已自动混入 BGM**，除非 `skip_bgm: true`）

## 服务端 pipeline（提交后自动执行）

与 vidau-agent 故事板一致，按以下顺序执行：

1. **解析脚本** — 规范化为 **Final Video Spec** 结构化 Markdown（标题/时长/画幅/画面概述等）
2. **提取关键元素** — 识别 `character`（人物）/ `scene`（场景）/ `prop|brand`（产品）/ `style`（风格），用户参考图按语义绑定（产品图→prop，人物图→character，场景图→scene）
3. **规划分镜** — 每镜绑定 `key_element_ids`：**所有 character + scene 强制绑定到每一镜**（跨镜人物/场景一致）；主产品 prop/brand 全片绑定
4. **生成元素参考图** — Identity Board 设定板，按类型排序命名 `element-01-character-*.jpg`、`element-02-prop-*.jpg` …
5. **并行生图** — 逐镜关键帧，**必须**以绑定元素的 Identity Board 为 reference；命名 `shot-01-keyframe.jpg`
6. **并行生视频** — reference 模式使用元素参考图 + 关键帧；`generate_audio=false`（无镜内原声）；命名 `shot-01-video.mp4`
7. **合成无声成片**（按 **分镜 index 顺序** 拼接，非并行完成顺序）→ **BGM** → **混音成片**（**丢弃分镜原声，仅保留 BGM**）

任务 progress 会附带 `script_spec_preview`、`key_elements`（含 `shot_indexes` 绑定）、`shots` 结构化摘要。

可通过环境变量 `SCRIPT2FILM_SHOT_CONCURRENCY` 限制并发（如 `3`）；默认 `all` 即全部分镜同时跑。

progress 会显示 `解析脚本` / `提取关键元素` / `规划分镜` / `生成元素参考图` / `并行生图` / `并行生视频` / `合成无声成片` / `生成配乐` / `混音合成成片` 等步骤。

## BGM 配乐（自动）

script2film 在**无声成片拼接完成后**才生成 BGM（与 vidau-agent 一致），确保：

- 配乐时长 = **实际成片时长**（ffprobe 探测，非规划估算）
- 配乐 prompt 包含**完整分镜 visual/motion 描述**，与画面叙事匹配

| 参数 | 说明 |
|------|------|
| `skip_bgm` | 设为 `true` 跳过自动配乐 |
| `bgm_hint` | 配乐风格 hint，如「轻快电子、适合带货」 |
| `bgm_url` | 使用已有 BGM URL，跳过生成 |

也可手动分步调用：

- `creative_generate_bgm` — 单独生成 BGM 试听
- `creative_mux_bgm_into_video` — 将 BGM 混入指定视频

需配置 `RUNWARE_API_KEY`；未配置时跳过 BGM，仍交付无声成片。

## 关键元素与用户参考图

| 阶段 | 行为 |
|------|------|
| **生成脚本** | `creative_generate_script` → `spec_markdown`（Final Video Spec） |
| **解析脚本** | 输出 Final Video Spec Markdown；progress 含 `script_spec_preview` |
| **提取关键元素** | LLM 识别人物/场景/产品/风格；用户参考图语义绑定到对应 `element_type` |
| **规划分镜** | 每镜强制绑定全部 character + scene；progress 含 `shots[].key_element_ids` |
| **元素参考图** | Identity Board；文件名 `element-01-character-*.jpg` 等（带序号，按 character→prop→scene 排序） |
| **逐镜生图** | refs = 该镜绑定元素的 Identity Board；文件名 `shot-NN-keyframe.jpg` |
| **逐镜生视频** | reference 模式：`elementReferenceUrls` 优先；无镜内音频；文件名 `shot-NN-video.mp4` |
| **拼接顺序** | 严格按 `shots[].index` 升序，不受并行完成先后影响 |
| **最终音轨** | 分镜原声丢弃，成片仅含 BGM（混音失败则任务失败，不会静默跳过） |

收集参考图 URL（任选，会合并去重）：

- 顶层 `reference_image_urls`
- `brief.reference_image_urls`

**Agent 职责**：提交前在 brief 说明各图用途（产品/模特/场景/风格）；若只有图无文字，用 `creative_generate_script` 从图+brief 扩写脚本。

## 时长规划

| 参数 | 说明 |
|------|------|
| `target_duration_sec` | 目标总时长（**16–120s**，>15s 用本 Skill）。规划期分配各镜 duration，**总和必须等于目标**（±3s） |
| `shot_duration_sec` | **可选**兜底均值（默认 5s），仅用于估算镜数；各镜实际时长由规划器按脚本内容分配（4–12s） |
| `SCRIPT2FILM_MAX_SHOTS` | 环境变量，镜头数上限（默认 4，30s 建议设为 **6**） |

**30 秒示例**：`target_duration_sec=30`，不传 `shot_duration_sec`；规划器会让各镜 duration 之和接近 30s（如 4+6+5+7+4+4），**不会每镜固定 5s**。

若规划总时长 `< target`，任务仍会完成但 progress 会提示未达目标时长。

## 依赖

- 服务端需安装 **ffmpeg** 与 **ffprobe**（或设置 `FFMPEG_BIN`）
- 脚本扩写需配置 `LLM_BASE_URL` + `LLM_API_KEY`（未配置时用启发式模板兜底）

## 输入不足时

先向用户补问：产品、卖点、投放平台、画幅、**目标时长（>15s）**；有图则确认图与产品的对应关系。  
仅一句话也可直接 `creative_generate_script`，再展示脚本请用户确认。

## 注意

- 同一 `client_request_id` 幂等，避免重复扣费
- 长任务勿阻塞对话；提交后告知用户可在本对话中随时询问进度
- 参考图最多 **8 张**（生图）；生视频最多 **9 张** reference（含本镜关键帧）

## 分镜失败与重试（内容安全 / 版权）

Seedance 可能在**单镜生视频**阶段拦截，与「真人脸隐私拦截（privacy）」不同，常见两类：

| 类型 | 典型报错 | 说明 |
|------|----------|------|
| **版权 / IP** | `output video may be related to copyright restrictions` | 生成结果疑似受保护 IP、品牌视觉等（**输出侧**审核） |
| **隐私 / 真人脸** | `PrivacyInformation` / `InputImageSensitiveContentDetected` | **输入参考图**含可识别真人肖像；服务端会尝试 `asset://` 重试 |

**Agent 处理建议**（某镜 `progress` 报错或 `error` 含上述关键词时）：

1. 向用户说明是**该镜**被模型拦截，其余镜可能已成功（任务可能仍带分段 artifacts）
2. 请用户**修改该镜脚本描述**（更抽象、电影化，避免 IP 名/品牌/名人）并/或**更换参考图**（原创/AI 图，避免版权角色）
3. 用**新 `client_request_id`** 重新提交整单 script2film（或让用户调整脚本后重跑）
4. 同一 prompt 有时**重试即可过**（拦截带随机性）；若反复失败再改文案/换图

> 首尾帧模式见 **creative-script2film-keyframes**，失败处理原则相同。

## 合成与转存

- FFmpeg 拼接前，服务端会将 **TOS 等非平台 URL 重试转存**到 VidAU CDN，再下载拼接（避免直连 `volces.com` 超时）
- BGM 混音使用与 concat 相同的可靠下载（带重试），混音后验证输出含音频轨
- 可调环境变量：`FETCH_CONNECT_TIMEOUT_MS`（默认 30s）、`REMOTE_FETCH_MAX_ATTEMPTS`（默认 3）、`PLATFORM_REHOST_MAX_ATTEMPTS`（默认 4）
