---
name: jianying-remix
description: >-
  Local CapCut/Jianying remix director for user-provided videos only —
  intelligently picks per-clip filters, video intro/outro/group animations,
  scene/character effects, transitions, fonts and text animations; optional
  subtitles/stickers; BGM on by default; can batch multiple remix variants;
  compile/import draft only — no auto-export. Does NOT call
  creative_submit_workflow / direct_video / AI clip generation.
metadata:
  layer: L1-capability
  requires: []
  tags: [jianying, capcut, remix, transition, filter, animation, effect, font, subtitle, sticker, bgm, batch, local, draft, editor]
---

# Jianying Remix — 本机草稿导演

用户提供多段视频时，你是**智能混剪导演**；本机 `jianying-draft-compiler` 是**草稿编译器**；用户剪映是**特效渲染器**。

**成片交付（强制）**：流程止于 `compile` + `import`。**禁止**调用 `jy-compile export` / `export-check` / 任何 RPA·OCR 自动导出。导入成功后提醒用户：**退出并重开剪映 → 在「本地草稿」打开对应草稿预览 → 需要成片时自行点导出**。

**素材来源（强制）**：只用**用户提供的视频**（本地 path / 可下载 url / 上游 skill 已落盘的片段）。  
**禁止**：`creative_submit_workflow`、`direct_video`、`creative_image_to_video`、`creative_generate_video`、`creative_submit_batch_variants` 等任何 AI 出片。缺素材就请用户补视频，或改走 **product-image-to-jianying-remix**（那边负责图生片段）。

**接受的「批量生成」**：同一套用户视频 → 批量产出**多版混剪**（不同转场 / 特效 / 滤镜 / 动画 / BGM 组合），每版一份 Edit Plan → 编译/导入（见 §1.0）。

**资源尽量用满（强制方向）**：不只贴边框。按片段数量与内容，尽量覆盖：转场、场景特效、人物特效、滤镜、视频入出/组合动画、字体与文字动画（有字幕时）。选型见 §1.5 与 [effect-presets.md](references/effect-presets.md)。

**不做**：自研特效渲染、云端服务器导出成片、AI 生 JPG 假透明转场板、AI 生视频素材。

## 何时使用

- 用户已有多段本地/可下载视频，要「剪映级」转场/边框/胶片等模板感混剪
- 用户说时装混剪、撕纸边框、快切、CapCut 风格等
- 用户要加**字幕 / 标题字 / 贴纸**（按需）；**BGM 默认带上**（用户可关）
- 用户要对**同一批素材**批量出多版（不同转场/特效/BGM）混剪草稿或成片

## 何时不用

| 需求 | 改走 |
|------|------|
| 无剪映、只要快速拼接成片 | 其它 remix / ffmpeg / creative-agent 成片链路 |
| 只有产品图、还没有视频片段 | **product-image-to-jianying-remix**（图生片段后再回本 skill） |
| 要 AI 文生/图生视频 | `creative-direct` / script2film / L2 产品图流水线 — **不要**在本 skill 里调 `direct_video` |
| 只要云端 MP4、不打开本机剪映 | 不要用本 skill 承诺自动成片（本 skill 只写草稿） |

## 前置探测（每次必做）

```bash
export PATH="$HOME/.vidau/bin:$PATH"
# Windows CMD: set PATH=%USERPROFILE%\.vidau\bin;%PATH%

command -v jy-compile >/dev/null || bash <repo>/tools/install-jy-compile.sh
jy-compile where
```

Compiler 来源与安装：同仓 `tools/jianying-draft-compiler/`，见 [references/install-compiler.md](references/install-compiler.md)。  
（`references/windows-export.md` 仅为历史/手工调试文档；**本 skill 默认不跑自动导出**。）

## 工作流

### 1. 收素材与意图

- **必须先有视频**：本地 path 优先；画幅默认 `9:16`
- 无视频、只有图 → **停止本 skill 的 AI 出片尝试**，引导 **product-image-to-jianying-remix**
- Preset 只是**素材池**，不是整片套一层：[references/effect-presets.md](references/effect-presets.md)
- 默认 `allow_vip=false`（转场 / 特效 / 文字动画只用非 VIP）
- **VIP 提醒（必做）**：若用户想用 VIP 转场/特效，或 Plan 中将写入 `is_vip=true` 项，须先明确提醒：
  > 将使用剪映 VIP 素材；请确认本机剪映已登录**有效的剪映 VIP 账号**，否则预览/导出可能水印、无法应用或弹窗打断。若有 VIP，请告知，我再改用 VIP 素材；没有则继续用免费效果。
  仅当用户确认「有剪映 VIP / 可以用 VIP」后，才设 `allow_vip=true` 并选用 VIP 项；未确认一律免费。
- 询问或识别：字幕/贴纸是否需要；BGM **默认要加**（有用户文件优先，否则 `creative_generate_bgm`；用户明确说不要配乐则跳过）
- 用户要**多版混剪** → §1.0；只要一版 → 跳过 §1.0，直接 §1.5

### 1.0 批量混剪变体（接受 · 仅用户视频）

对**同一组用户提供的 clips**，批量生成多版「不同转场 / 特效 / 滤镜 / 动画 / BGM」的剪映草稿。  
**不是**批量 AI 生成视频；**不**自动导出 MP4。

| 参数 | 默认 | 说明 |
|------|------|------|
| `variant_count` | `3` | 1–5 版；过多则拆次确认 |
| `clips` | 用户提供 | 各版共用同一 `clips[]` |
| 差异维度 | 转场 + 特效/滤镜 + 视频动画策略 + BGM | 每版至少换两类；优先三类都换 |

**步骤：**

1. 锁定共用 `clips[]`（path/url）；校验文件可读  
2. 规划 `variant_count` 套差异表，例如：

| 版 | 气质 | 转场 | 特效+滤镜 | 视频动画 | BGM |
|----|------|------|-----------|----------|-----|
| A | 清爽促销 | 闪白系 | 镭射边框 + `清新`/`日系奶油` | 多数 `渐显`/`渐隐` | 偏亮 |
| B | 胶片质感 | 溶解系 | 胶片框 + `Lofi II` | 1 段 `三分割`，余段轻入出 | 偏缓 |
| C | 潮流故障 | 故障系 | 轻故障 + `VHS III` | `动感放大`/`缩小` + 1 段 `抖入放大` | 电子感 |

3. **每一版**独立走 §1.5→§2→§3：单独 Edit Plan、`title`/`--name` 带后缀 `-v1`/`-v2`…  
4. 段内选型规则与单版相同（禁止一版内全片同一特效/同一转场）  
5. BGM：用户无文件时每版可各调一次 `creative_generate_bgm`（mood 不同）；有用户 BGM 则可同曲不同 `volume`/fade，或用户允许时再生成  
6. 交付时列表：`版本 | 草稿名 | 转场 | 特效/滤镜 | 动画 | BGM`（提醒用户到剪映本地草稿查看）

### 1.5 按片段内容智能选型（强制 · 尽量用满资源）

写 Plan 前必须先**看懂每段视频**（文件名/描述/能读帧则看画面），再为**每一段、每一条接缝**选型。  
完整表格见 [effect-presets.md](references/effect-presets.md)（含按 clip 数的满配强度）。

**每段 clip 应尽量覆盖（按内容取舍，不是全空），且遵守数量上限：**

| 层 | Plan 字段 | 每段上限 | 查法 |
|----|-----------|----------|------|
| 滤镜 | `clips[].filter` + `filter_intensity` | **1** | `catalog --type filters --free` |
| 视频入出 | `clips[].intro` / `outro` | **1 套**（可同时有 intro+outro） | `catalog --type video-intros/outros` |
| 或组合动画 | `clips[].group_animation`（与 intro/outro **互斥**；全片最多 1–2 段） | **1**（与上互斥） | `catalog --type video-groups` |
| 人物特效 | `clips[].character_effect`（**画面有人即可挂**） | **1**（不要再用 character overlay 叠） | `catalog --type effects --kind character` |
| 场景特效 | `overlays` `type=effect`，时间窗=该段轴上区间 | **1**（禁止同段叠边框+漏光+闪烁） | `catalog --type effects --kind scene` |
| 蒙版 | `clips[].mask` | **0**（默认）；有则 ≤1 | `catalog --type masks` |
| 转场 | `junctions[].transition` | 接缝 1 个 | `catalog --type transitions` |
| 文字（若有） | `font` + 文字 `intro`/`outro`/`loop` | 标题短窗；勿堆满 | `fonts` / `text-intros` / `text-loops` |

同段允许组合示例：`filter` +（`intro`/`outro` 或 `group`）+ `character_effect` + **1 个**场景特效。  
同段禁止：多个 `type=effect` 盖同一段；`character_effect` 再加人物类 effect overlay。

**禁止：**

- 全片只用同一个 effect / 同一个 transition / 同一滤镜复制粘贴
- **同段堆特效**（场景 >1 或人物 >1）；validate 会报错
- 不看素材套「全程」模板；或只写边框、完全不用滤镜与视频动画
- **字段错位**（会导致剪映崩溃）：
  - 转场 → 只进 `junctions.transition`
  - 场景特效 → 只进 `overlays type=effect`
  - 人物特效 → 优先 `clips[].character_effect`（也可 effect + `effect_kind=character`）
  - 滤镜 → 只进 `clips[].filter`（**禁止**当 transition/effect）
  - 视频入出/组合 → 只进 `clips[].intro|outro|group_animation`
  - 文字入出/循环/字体 → 只进 text/subtitle overlays（**禁止**把文字 `渐显` 写进 clip 视频 intro）
  - 写完必须 `jy-compile validate`；`ok:false` 禁止 import

**要求：**

1. 为每段记内容标签（静物特写 / 走秀 / 口播 / 快运镜 / 暗调 / 明亮产品…）
2. 按 [effect-presets.md](references/effect-presets.md)「内容→*」表选滤镜、动画、特效、转场；选用前 `catalog --grep` 核对类别与免费
3. effect overlay **按段切时间窗**，不要整片一条盖满
4. 接缝按「前段尾 × 后段头」选转场；相邻接缝不重复
5. ≥3 段时至少一半片段有视频 intro/outro（或等价 group）；group 只作点睛
6. **有人物的片段**（口播 / 模特产品展示 / 试穿走秀等）尽量挂 `character_effect`；纯静物无人才默认不加；人物近景场景特效宜轻，避免厚边框挡脸/挡身
7. 交付简述：每段滤镜/动画/特效、每条接缝转场（各一句）

### 1.6 字幕与贴纸（按用户需求）

**默认不加。** 仅当用户明确要求（或提供了文案 / 贴纸图）时写入 overlays。**一旦加字，尽量用上字体与文字动画**（见下表）。

| 需求 | Plan |
|------|------|
| 底部说明 / 口播字幕 | `type: "subtitle"`，`text`，`font`（如 `思源中宋`/`抖音美好体`），`transform_y` 约 `-0.75` |
| 标题 / 角标大字 | `type: "text"`，`font`（英文促销优先 `Anton`；中文 `站酷酷黑体`/`抖音美好体`），字号更大，`transform_y` 约 `0.5~0.7` |
| 关键词高亮 | `keywords`/`keyword` + `keyword_color`/`keyword_font_size` |
| 文字入/出场 | overlays 的 `intro` / `outro`（文字目录，如 `渐显`/`弹入`）；`jy-compile catalog --type text-intros --free` |
| 文字循环 | 标题短窗可用 `loop`（如 `扫光`）；口播字幕默认不加 |
| 贴纸 / 装饰图 | `type: "sticker"` + 本地 `path`（或 `url`） |

规则：

- 文案要短、可读；避免挡脸 / 挡产品主体
- 字幕按片段或按句分段；不要一条盖全片除非只要总标题
- 标题类：字体 + 入场（`弹入`/`渐显`）+ 可选 `扫光`；出场可选
- 贴纸优先用户透明 PNG；不要伪造内置 `resource_id`
- 字段见 [references/edit-plan.md](references/edit-plan.md)

### 1.7 BGM（默认开启）

**默认写入 `bgm`。** 仅当用户明确说「不要配乐 / 不要 BGM / 保留原声即可」时省略。

音源优先级（**暂时不走曲库选型** `creative_select_bgm`）：

1. 用户提供的本地 `path` 或 `url`
2. 否则调用 MCP **`creative_generate_bgm`**（生成配乐，扣积分）：按题材写 `prompt`/`mood`，时长贴近成片；用返回的音频 `url` 写入 Plan
3. 生成失败：warnings 说明，草稿可导入；请用户补文件或在剪映里加乐

```json
"bgm": {
  "url": "https://…/generated.mp3",
  "volume": 0.35,
  "fade_in_ms": 400,
  "fade_out_ms": 800,
  "loop": true
}
```

规则：

- 只用纯音频 URL/文件；不要把视频当 BGM
- 默认 `volume` 约 `0.3–0.4`
- **有 BGM 时原视频默认静音**（编译器自动；不必手写 `mute_original_audio`）。用户明确要「原声+配乐」时才设 `"mute_original_audio": false`
- `loop: true`（默认）铺满成片
- 不要自己拼平台曲库 HTTP；无用户文件时直接 `creative_generate_bgm`

### 2. 写 Edit Plan

见 [references/edit-plan.md](references/edit-plan.md)。写入临时 JSON；overlays / junctions 体现分段差异；字幕/贴纸按需；**BGM 默认写入**。

### 3. 校验 → 编译 → 导入

```bash
jy-compile validate /tmp/vidau-edit-plan.json
jy-compile compile /tmp/vidau-edit-plan.json
jy-compile import "<draft_dir>" --name "<短横线英文名>"
```

### 4. 提醒用户在剪映中查看（禁止自动导出）

**禁止**执行 `jy-compile export`、`jy-compile export-check`，以及任何 UIA/OCR/pyautogui 自动导出。

导入成功后必须明确告知用户：

1. **完全退出并重新打开剪映**（否则首页可能看不到新草稿）  
2. 在首页 **「本地草稿」** 中找到草稿名 `<name>`（多版则为 `-v1` / `-v2`…）  
3. 打开草稿预览转场/特效/BGM  
4. 需要成片时，在剪映内自行点 **导出**

若用户追问自动导出：说明当前 skill **已关闭自动导出**，请在剪映草稿箱操作；不要擅自再跑 export。

## 失败处理

| 现象 | 处理 |
|------|------|
| `jy-compile` 不存在 | install-compiler；阻塞 |
| `where` 失败 | 装剪映或设 `JIANYING_DRAFT_ROOT` |
| 链接媒体 / 暂无访问权限 | 必须用 `import`（路径改写） |
| `validate`/`compile` 报目录错位 | 按 errors 改槽位：转场→junction；场景特效→overlay effect；人物→`character_effect`；滤镜→`filter`；视频动画→clip intro/outro/group；文字动画/字体→text overlay；改完再 validate |
| 报「同段场景/人物特效过多」 | 该段只留 **1** 个场景特效、**1** 个人物特效；删掉重叠时间窗上的多余 overlay |
| 首页看不到草稿 | 请用户退出重开剪映；核对 `--name` 与本地草稿列表 |
| VIP 特效无法应用 / 弹窗 | 确认是否有剪映 VIP；无则换免费 preset 并重编；有则请用户登录 VIP 后重开剪映 |
| 贴纸图打不开 | 检查 path/url；改 PNG；或去掉 sticker overlay |
| BGM 失败 / 无声音 | 确认是纯音频；看 compile warnings；生成失败则请用户补文件后重编；路径经 import 改写 |
| 用户要 AI 出片 | 拒绝在本 skill 调 `direct_video`；改 **product-image-to-jianying-remix** 或 creative-direct |
| 批量变体部分失败 | 已成功版本照常交付；失败版单独重编 |
| 用户要自动导出 MP4 | 拒绝跑 export；引导在剪映本地草稿打开并手动导出 |

## 交付话术

> 已写入剪映草稿 `<name>`（默认已配 BGM，除非你要求不要）。分段：滤镜/视频动画/特效…；接缝转场：…；人物特效/字体动画：…（若有）；BGM：…。效果均为免费项 / 已按你的剪映 VIP 使用 VIP 素材（二选一如实说明）。  
> 请**退出并重开剪映**，在「本地草稿」打开该草稿预览；需要成片时在剪映内自行导出。本流程不自动导出 MP4。
