# 导演 / 广告节奏 Skill — 开源抽取清单

> 状态：**待开发**（规划文档，尚未落地 skill 目录）  
> 目的：从开源仓库抽取「可展示的导演美学 / 广告节奏」能力，接到 VidAU Creative Agent（Hermes Skill + MCP）  
> 前置：命中率规则见 [SKILL_ROUTING.md](./SKILL_ROUTING.md)（`description` ≤60 字符）

---

## 目标目录总览

```text
creative-agent-skill/
├── L0-foundation/
│   └── creative-director-styles/          # 新增：导演镜头语言库
├── L1-capability/
│   └── creative-ad-rhythm/                # 新增：广告节奏 / Hook / beat sheet
└── L2-vertical/
    ├── style-neon-port/                   # 展示：东方霓虹文艺（改编自王家卫镜头语言）
    ├── style-luxury-product/              # 展示：奢侈品广告节奏
    ├── style-ugc-hook/                    # 展示：UGC 开场节奏
    └── style-saas-launch/                 # 展示：SaaS/产品发布片
```

外加：**增强现有** `L0-foundation/creative-seedance2-prompt`（注入风格/节奏钩子，不整仓复制外部 repo）。

**命中率约束：** 勿一口气挂过多几乎同构的 L2；风格明细优先放 `references/`，用 `skill_view(name, path)` 渐进加载。L2 最多 2–4 个互斥入口。

---

## 1) `L0-foundation/creative-director-styles`

**职责：** 可切换的「镜头语言 lens」；被 seedance / script2film / L2 style skill 引用。不直接调 MCP。

| 来源 repo | 抽这些文件 | 落到 |
|-----------|------------|------|
| [wuwangzhang1216/DirectorSKILL](https://github.com/wuwangzhang1216/DirectorSKILL) | `references/director_styles/09_wong_kar_wai.md` | `references/lenses/neon-port.md`（改名，去真名） |
| 同上 | `references/director_styles/03_kubrick.md` | `references/lenses/symmetrical-tableau.md` |
| 同上 | `references/director_styles/12_fincher.md` | `references/lenses/clinical-precision.md` |
| 同上 | `references/cinematic-language.md` | `references/cinematic-language.md`（精简） |
| 同上 | `assets/shot-plan-template.md` | `references/shot-plan-template.md` |
| 同上 | `assets/video-prompt-template.md` | `references/video-prompt-template.md` |
| [crowscc/seedance-director](https://github.com/crowscc/seedance-director) | `skills/seedance-director/references/vocabulary.md` | `references/camera-vocab-extra.md`（与现有 `camera-vocabulary.md` 去重合并） |
| 同上 | `skills/seedance-director/references/narrative-structures.md` | `references/narrative-structures.md` |

**自写：** `SKILL.md`（路由：用户说「某某风格」→ 加载对应 lens → 输出约束块给下游）  

**suggested description（≤60）：**

```yaml
description: Use when cinematic lens/style (neon-port/kubrick-like)
```

**不要抽：** 全 14 个导演真名文件一次性上线；先 3 个脱敏 lens 够展示。

**Manifest 草稿：**

```yaml
- id: creative-director-styles
  layer: L0-foundation
  path: L0-foundation/creative-director-styles
  title: Director Style Lenses
  tags: [foundation, style, cinematography]
  requires: []
```

---

## 2) `L1-capability/creative-ad-rhythm`

**职责：** Hook / beat sheet / CTA / 平台时长；输出「节奏计划」给 script2film 或后续混剪。

| 来源 repo | 抽这些文件 | 落到 |
|-----------|------------|------|
| [Creatify-AI/video-ad-generator](https://github.com/Creatify-AI/video-ad-generator) | `SKILL.md` 里 Hook / Body / CTA / Multi-Format 段落 | `references/hook-formulas.md`、`references/body-structures.md`、`references/cta-patterns.md`、`references/platform-formats.md` |
| [ImTaegan/claude-ugc-skills](https://github.com/ImTaegan/claude-ugc-skills) | `skills/hook-generator/SKILL.md` | `references/hook-frameworks.md` |
| 同上 | `skills/ugc-script/SKILL.md` | `references/ugc-script-beats.md`（时间戳分镜模板） |
| [charlesdove977/UGC-Factory](https://github.com/charlesdove977/UGC-Factory) | `skill/frameworks/ugc-ad-structure.md` | `references/ugc-ad-structure.md` |
| 同上 | `skill/frameworks/style-routing.md` | `references/style-routing.md`（风格→节奏映射表） |

**自写：** `SKILL.md`（输入 brief → 输出 beat sheet JSON/Markdown；再交 L1 生成）  

**suggested description（≤60）：**

```yaml
description: Use when ad hooks/beat sheet/CTA timing needed
```

**不要抽：** Creatify API 自动化、UGC-Factory 的 Higgsfield Elements / stitch 管线。

**Manifest 草稿：**

```yaml
- id: creative-ad-rhythm
  layer: L1-capability
  path: L1-capability/creative-ad-rhythm
  title: Ad Rhythm / Hook / Beat Sheet
  tags: [ad, hook, ugc, rhythm]
  requires: [creative-narrative-router, creative-seedance2-prompt]
```

---

## 3) 四个可展示 L2 Skill

### A. `L2-vertical/style-neon-port`（东方霓虹文艺）

| 来源 | 抽 | 落到 |
|------|----|------|
| DirectorSKILL | `09_wong_kar_wai.md`（镜头/光/剪辑要点） | `references/lens.md` |
| seedance-director | `templates/multi-segment.md` 结构 | `references/prompt-shape.md` |
| 现有 | `creative-seedance2-prompt` + `creative-script2film` | `SKILL.md`：先 lens → seedance → script2film |

**对外名：** 「霓虹港风短片」— 不要写王家卫。  

**suggested description：** `Use when neon/港风 cinematic short; load director lens`

---

### B. `L2-vertical/style-luxury-product`（奢侈品广告）

| 来源 | 抽 | 落到 |
|------|----|------|
| [rediumvex/ai-video-generator-claude](https://github.com/rediumvex/ai-video-generator-claude) | `skills/06-luxury-aesthetic/SKILL.md` | `references/prompt-playbook.md`（去 Higgsfield 粘贴步骤，改成 MCP） |
| UGC-Factory | `skill/styles/07-ecommerce-ad/SKILL.md` + `13-fashion-lookbook/SKILL.md` 的镜头/节奏段 | `references/genre-notes.md` |
| creative-ad-rhythm | （依赖） | beat：慢推 / 静物 / packshot |

**管线：** product image/url → ad-rhythm → seedance/script2film。  

**suggested description：** `Use when luxury/fashion product ad pacing & look`

---

### C. `L2-vertical/style-ugc-hook`（UGC 开场节奏）

| 来源 | 抽 | 落到 |
|------|----|------|
| rediumvex | `skills/01-viral-hook/SKILL.md` | `references/viral-hook.md` |
| claude-ugc-skills | `hook-generator` + `ugc-script` 核心表 | `references/hooks.md`、`references/script-template.md` |
| UGC-Factory | `skill/styles/11-social-hook/SKILL.md` | `references/social-hook-genre.md` |
| Creatify | Hook 分类段落 | 合并进 `hooks.md` |

**管线：** brief → 10 hooks 选 1 → 15–30s beat → `creative-direct` 或短 script2film。  

**suggested description：** `Use when UGC viral hook 15–30s short; NOT luxury/URL`

---

### D. `L2-vertical/style-saas-launch`（产品发布片）

| 来源 | 抽 | 落到 |
|------|----|------|
| rediumvex | `skills/02-saas-launch/SKILL.md` | `references/saas-launch.md` |
| rediumvex（可选） | `skills/07-before-after/SKILL.md` | `references/before-after.md` |
| Creatify | Body Structures（PAS / feature cascade） | `references/structure.md` |

**管线：** 产品能力点 → Apple-keynote 式节奏 → script2film。  

**suggested description：** `Use when SaaS/product launch keynote-style film`

---

## 4) 增强现有，不新建

| 现有目录 | 从哪抽 | 怎么合 |
|----------|--------|--------|
| `creative-seedance2-prompt` | seedance-director：`vocabulary.md`、`scene-strategies.md` | 补进 `references/`；`SKILL.md` 增加可选 `style_lens` / `ad_rhythm` 注入段 |
| `creative-narrative-router` | seedance-director：`narrative-structures.md` | 作为额外 narrative preset |
| `trend-viral-short` | rediumvex `01-viral-hook` | 可选 `requires: [creative-ad-rhythm]` |

---

## 5) 明确不要搬的文件

| Repo | 跳过 |
|------|------|
| UGC-Factory | `skill/tasks/run-pipeline.md`、`seedance-elements.md`、Higgsfield/ffmpeg 整仓流水线 |
| Creatify | API batch / webhook 段（若 `SKILL.md` 里有） |
| DirectorSKILL | 一次上齐 14 真名导演；`ai-video-tool-adapters.md` 里非 VidAU 栈的工具表可整段丢 |
| rediumvex | 「粘贴到 Higgsfield」操作指南；只留 prompt 结构与 timing |
| seedance-director | `templates/output.html`、平台能力里与 VidAU 冲突的部分 |

---

## 6) 建议落地顺序

**Day 1**

1. 建 `creative-director-styles`（3 lens 脱敏）  
2. 建 `creative-ad-rhythm`（Hook + beat sheet）  
3. 改 `creative-seedance2-prompt` 支持注入 lens/rhythm  

**Day 2**

4. 上 `style-ugc-hook` + `style-luxury-product`（电商最能打）  
5. 再上 `style-neon-port` + `style-saas-launch`（导演/发布片展示）  
6. 更新 `_manifest.yaml`：`requires` 链到现有 L1；跑 `node scripts/validate-skills.mjs`  

---

## 7) `_manifest.yaml` 追加草稿

```yaml
  - id: creative-director-styles
    layer: L0-foundation
    path: L0-foundation/creative-director-styles
    title: Director Style Lenses
    tags: [foundation, style, cinematography]
    requires: []

  - id: creative-ad-rhythm
    layer: L1-capability
    path: L1-capability/creative-ad-rhythm
    title: Ad Rhythm / Hook / Beat Sheet
    tags: [ad, hook, ugc, rhythm]
    requires: [creative-narrative-router, creative-seedance2-prompt]

  - id: style-ugc-hook
    layer: L2-vertical
    path: L2-vertical/style-ugc-hook
    title: UGC Hook Short
    requires: [creative-ad-rhythm, creative-seedance2-prompt, creative-direct, creative-job-runner]

  - id: style-luxury-product
    layer: L2-vertical
    path: L2-vertical/style-luxury-product
    title: Luxury Product Ad
    requires: [creative-ad-rhythm, creative-director-styles, creative-seedance2-prompt, creative-script2film]

  - id: style-neon-port
    layer: L2-vertical
    path: L2-vertical/style-neon-port
    title: Neon Port Cinematic
    requires: [creative-director-styles, creative-seedance2-prompt, creative-script2film]

  - id: style-saas-launch
    layer: L2-vertical
    path: L2-vertical/style-saas-launch
    title: SaaS Launch Film
    requires: [creative-ad-rhythm, creative-seedance2-prompt, creative-script2film]
```

---

## 8) 一句话对应关系

| 目标 | 主要抽自 | 落成 |
|------|----------|------|
| 导演美学货架 | DirectorSKILL lenses + cinematic-language | `creative-director-styles` + `style-neon-port` |
| 广告节奏 | Creatify + UGC hooks + UGC-Factory structure | `creative-ad-rhythm` + `style-ugc-hook` |
| 风格目录 demo | rediumvex 10 skills 里挑 3 | `luxury` / `saas` / `viral-hook` |
| Seedance 执行对齐 | seedance-director vocab/templates | 增强现有 `creative-seedance2-prompt` |

---

## 9) 合规注意

- 对外展示用脱敏风格名（霓虹港风 / 对称童话风），内部再映射导演 lens  
- 保留开源许可证声明（多数 MIT）；改编时在 `SKILL.md` Overview 注明来源 repo  
- 不复制真名导演作为对外 skill `name` / 营销标题
