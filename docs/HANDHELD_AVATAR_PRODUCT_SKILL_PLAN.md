# 手持产品展示 · 口播数字人 Skill 方案

> 状态：**Skill 已落地** — 默认 **批量 direct_video + 客户端拼接**（不走 script2film）；MCP 支持 reference_audio / reference_video  
> 参考：[Creatify-AI/ai-avatar-video](https://github.com/Creatify-AI/ai-avatar-video/blob/main/SKILL.md)  
> 相关：[SKILL_ROUTING.md](./SKILL_ROUTING.md) · [batch-direct-video.md](../L2-vertical/handheld-product-avatar/references/batch-direct-video.md)  
> 目标：用户给**产品图 + 卖点**，产出「人手持产品 + 口播讲解」的竖屏带货片（可交付）

---

## 1. 对标 Creatify 要什么 / 我们改什么

Creatify skill 分两块：**方法论（Part 1）** + **Creatify API 自动化（Part 2）**。

| Creatify 能力 | 是否复用 | 我们的落点 |
|---------------|----------|------------|
| 口播脚本节奏 / Hook→CTA / 口语化 | ✅ 直接改编 | Skill `references/` |
| Persona 选型（垂类信任感） | ✅ 改编为「数字人画像 brief」 | 不用 1500 人像库 ID |
| 多镜结构（15/30/60s） | ✅ | 对接 `script2film` + `voiceover` |
| UGC 真实感（自拍角、居家背景） | ✅ | Seedance prompt 约束 |
| Green screen / 透明底叠加 | ⏸ Phase 2 | 现无透明数字人 MCP |
| Avatar / Aurora lipsync API | ❌ 不套壳 | **MVP 用 Seedance `reference_audio`**（`voiceover_mode=lipsync`） |
| TTS / Voice clone API | ✅ MCP 付费 TTS | `creative_generate_tts`（Runware `minimax:speech@2.8`）；亦可 Hermes TTS |

**差异化卖点（Creatify 没有强调、我们要做）：手持产品一致性**

- 产品外观与参考图一致（SKU 锁定）
- 人**手持 / 展示**产品入镜（不是纯大头口播）
- 口播与画面对齐：TTS 时长驱动分镜；对口型镜用音频作 Seedance 参考

---

## 2. 产品定义

### 用户输入

| 字段 | 必填 | 说明 |
|------|------|------|
| `product_image` | ✅ | 产品主图 HTTPS URL |
| `selling_points` / brief | ✅ | 卖点或一句话 |
| `duration` | 默认 30s | 15 / 30 / 60 |
| `aspect_ratio` | 默认 9:16 | |
| `persona` | 可选 | 年龄/气质/垂类；否则按品类表默认 |
| `locale` | 跟随用户语言 | 口播文案语言 |
| `talent_ref` | 可选 | AI 定妆图优先；可识别真人脸 ref 仍禁止（Seedance 合规） |

### 输出

- 口播脚本（按镜 / 按时长）
- Seedance 分镜 + 成片（`script2film` + 口播双模式）
- 可选字幕（客户端后处理）

### 口播模式选择（写进 SKILL 路由）

| 条件 | `voiceover_mode` | 说明 |
|------|------------------|------|
| 人出镜说话、要对口型（本 skill 默认） | **`lipsync`** | TTS → `voiceover_shot_plan[].audio_url` → Seedance `reference_audio` |
| 纯产品特写 / 画外音旁白、不需要对口型 | **`mux`** | 静音分镜，成片后混 VO |

### Hermes description（≤60）

```yaml
description: Use when handheld product talking-head ad; NOT still-life only
```

触发词：手持、口播数字人、带货口播、产品讲解、talking head + product、UGC 手持展示。  
互斥：纯静物片、仅产品 URL 抓取成片（走 `product-url-to-video`）、无口播的多镜故事片。

> 落地 description（≤60）：`Use when 人物口播/handheld product VO; NOT still-life`

---

## 3. 技术路径（分阶段）

### Phase 1 — MVP（现有 MCP，含 Seedance 对口型）

```text
产品图 + brief
  → 口播脚本（Creatify 节奏表改编）
  → persona brief（文字，非 Creatify ID）
  → 推荐：手持定妆图 (gpt-image-2，产品 ref + 手持构图，风格化模特脸)
  → creative_generate_script(voiceover=true) / 或 skill 内写 Final Spec
  → 每镜 creative_generate_tts → audio_url + duration_sec
  → creative_submit_script2film(
       voiceover_enabled: true,
       voiceover_mode: "lipsync",          // 本 skill 默认
       voiceover_shot_plan: [{ index, text, duration_sec, audio_url }],
       reference_image_urls: [product, talent still]
     )
  → 成片已含对口型口播 + BGM；可选客户端烧字幕（无需再混 VO）
```

**备选路径（同 skill 内）：** 用户明确只要旁白、画面无人说话 → `voiceover_mode=mux`，成片后客户端混 VO（见 script2film [client-voiceover-post.md](../L1-capability/creative-script2film/references/client-voiceover-post.md)）。

**画面策略（Seedance）：**

- `reference_image_urls[0]` = 产品主体（外观一致）
- 推荐 `[1]` = AI「手持定妆」静帧（同一产品、同一人设）
- Prompt：中近景、产品清晰入镜、手持/托举/展示；lipsync 镜追加「跟参考音频对口型、脸部可见」
- **禁止**上传可识别真人脸做 ref；数字人用「风格化模特 / AI 合成脸」

**诚实边界：**

- Phase 1 lipsync = Seedance `reference_audio` 驱动，质量取决于模型，**不是** Creatify Aurora / OmniHuman 级专用口型引擎
- 单镜仍 ≤12–15s；长片靠多镜 `voiceover_shot_plan` 对齐

### Phase 2 — 更高质量口型 / 透明底（可选 provider）

当 Seedance lipsync 不够用时，再插拔专用口型：

| 选项 | 能力 | 手持产品难点 |
|------|------|----------------|
| Creatify Aurora / OmniHuman 等 | 图+音 → 专用 lipsync | 需高质量手持定妆图 |
| Green screen 透明底 | 后期叠加 | 现无 MCP |
| Duix-Avatar 类本地 | 形象克隆 | 工程重，合规复杂 |

流水线增量：

```text
（Phase 1 脚本/TTS/定妆不变）
  → 可选：专用 lipsync MCP 替换 Seedance reference_audio 镜
  → 可选 B-roll 混剪
```

脚本/节奏/persona 层可原样复用；**不必再为「能对口型」单独等 Phase 2**。

---

## 4. Skill 目录结构

```text
L2-vertical/handheld-product-avatar/
├── SKILL.md
└── references/
    ├── script-templates.md      # 从 Creatify §1.1 改编 + 手持镜位提示
    ├── persona-by-vertical.md   # 从 Creatify §1.2 改编
    ├── multi-scene.md           # §1.3 + 手持/特写/口播交替
    ├── ugc-authenticity.md      # §1.4–1.6 精简
    ├── handheld-prompt.md       # Seedance 手持+产品一致性；lipsync prompt 后缀
    └── voiceover-timing.md      # voiceover_shot_plan / 语速表 / lipsync vs mux
```

**不建** Creatify API Part 2；专用 lipsync 仅在 Phase 2 以 provider adapter 附录出现。

**Manifest 草稿：**

```yaml
- id: handheld-product-avatar
  layer: L2-vertical
  path: L2-vertical/handheld-product-avatar
  title: Handheld Product Talking Avatar
  tags: [ecommerce, avatar, handheld, voiceover, ugc, lipsync]
  requires:
    [
      creative-platform,
      creative-task-runner,
      creative-seedance2-prompt,
      creative-gpt-image2-prompt,
      creative-narrative-router,
      creative-script2film,
      creative-ad-rhythm,          # 若已落地；否则内嵌 hook 表
    ]
```

---

## 5. 从 Creatify 抽取 → 改编对照

| Creatify 章节 | 抽取内容 | 改编要点 |
|---------------|----------|----------|
| §1.1 Pacing / Hook-CTA | 15/30/60s 模板、语速表、口语标记 | 每 beat 加「画面：手持/特写/点头」；中文语速另表 |
| §1.2 Persona | 垂类信任画像表 | 输出文字 persona brief，不调用 `/personas/` |
| §1.3 Multi-scene | 2/3/5 镜结构 | **默认全程手持口播**；产品特写/B-roll **仅用户点名**才加；禁止全程大头无产品 |
| §1.4 Audio | 情绪/停顿/发音 | → `creative_generate_tts` + `voiceover_shot_plan`（含 `audio_url`） |
| §1.5 Green screen | 透明叠加 | Phase 2；MVP 跳过 |
| §1.6 UGC | 自拍角、居家、第一人称 | 写入 `handheld-prompt.md` 默认 |
| §2 API | 全部 | **不复制**；Phase 2 另写 adapter |

---

## 6. Agent 主流程（SKILL.md 纲要）

1. **收输入** — 产品图上传（`creative-platform`）+ brief + 时长  
2. **Persona** — 读 `persona-by-vertical.md`，确认或给默认  
3. **口播脚本** — 按时长套模板；口语化；字数卡在语速表内；按镜切开（单镜朗读 ≤12s）  
4. **（推荐）手持定妆图** — `creative-gpt-image2-prompt` + `creative_generate_image`  
5. **分镜 Spec** — `creative-narrative-router` → `product_ad`；产品 ref + 定妆 ref；`voiceover=true`  
6. **选口播模式** — 默认 **`lipsync`**；仅旁白/无人说话 → **`mux`**  
7. **TTS** — `creative_generate_tts`（或 Hermes）→ `voiceover_shot_plan[{ text, duration_sec, audio_url }]`  
8. **提交** — `creative_submit_script2film` + 对应 `voiceover_mode` + Seedance 手持 prompt 门禁  
9. **交付** — lipsync：成片已含 VO，可选字幕；mux：客户端混 VO + 可选字幕  

### Seedance 硬约束（写进 `handheld-prompt.md`）

- 产品外观与参考图一致；logo/颜色/形状不漂移  
- 产品须在画面中清晰可见（≥画面 15–30%）  
- 中近景为主；允许插入产品特写镜（特写镜可 `mux` 旁白，说话镜用 `lipsync`）  
- UGC：轻微手持晃动、自然光、居家/街边，避免棚拍感  
- lipsync 镜：脸部清晰可见；避免剧烈转头打断口型  
- 禁止：无产品的纯头像口播、名人/真人脸 ref、竞品品牌名  

---

## 7. 与现有 Skill 关系

| Skill | 关系 |
|-------|------|
| `product-url-to-video` | URL 抓完详情后可 **handoff** 到本 skill（若用户要「手持口播」） |
| `creative-script2film` | 执行引擎（`voiceover_mode=lipsync\|mux`） |
| `creative-ad-rhythm` | 共享 Hook/CTA；本 skill 专精手持+口播 |
| `style-ugc-hook` | 偏开场钩子；本 skill 偏完整带货口播 |
| `creative-direct` | 仅当用户只要 ≤15s 单段手持口播时可降级（同步工具可带 `reference_audio_urls`） |

---

## 8. 验收标准（MVP）

- [ ] 用户只给产品图 + 一句卖点，能出 15/30s 竖屏成片  
- [ ] 成片中产品可辨认且与参考图一致（人工抽检）  
- [ ] 默认**每一镜**均为人物手持产品口播（非纯大头、非默认产品特写）  
- [ ] 未要求时不插入产品静物/B-roll；用户点名展示片段才加  
- [ ] 默认 lipsync（`reference_audio_urls`），口播与出镜大致对口型  
- [ ] 旁白场景可降级 `mux`，时长与脚本对齐  
- [ ] `description` ≤60 且能与 `product-url-to-video` / `creative-direct` 区分命中  
- [ ] 不调用 Creatify API；不上传真实人脸做数字人训练  

---

## 9. 建议排期

| 阶段 | 工作量（估） | 产出 |
|------|--------------|------|
| P0 文档与 references 改编 | 0.5–1d | `references/*` + SKILL 骨架（含 lipsync/mux 路由） |
| P1 定妆图 + script2film **lipsync** 闭环 | 1–2d | 可演示端到端对口型手持片 |
| P2 prompt 门禁与失败重试（产品漂移） | 0.5d | 一致性提升 |
| P3 专用 lipsync provider（可选） | 视供应商 | 高于 Seedance 的口型质量 |

---

## 10. 一句话结论

**先做「Creatify 方法论 + Seedance `reference_audio` lipsync + 手持产品一致性」的带货口播 Skill；旁白场景兼容 `mux`。专用口型厂商作为质量升级可选项，不是 MVP 前置。**
