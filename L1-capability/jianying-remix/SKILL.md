---
name: jianying-remix
description: >-
  Local CapCut/Jianying remix director for user-provided videos only —
  per-clip effects/transitions, optional subtitles/stickers; BGM on by default;
  can batch-output multiple remix variants (different transitions/effects/BGM)
  from the same clips; compile/import draft only — no auto-export; user opens
  Jianying to preview/export. Does NOT call creative_submit_workflow /
  direct_video / AI clip generation.
metadata:
  layer: L1-capability
  requires: []
  tags: [jianying, capcut, remix, transition, subtitle, sticker, bgm, batch, local, draft, editor]
---

# Jianying Remix — 本机草稿导演

用户提供多段视频时，你是**智能混剪导演**；本机 `jianying-draft-compiler` 是**草稿编译器**；用户剪映是**特效渲染器**。

**成片交付（强制）**：流程止于 `compile` + `import`。**禁止**调用 `jy-compile export` / `export-check` / 任何 RPA·OCR 自动导出。导入成功后提醒用户：**退出并重开剪映 → 在「本地草稿」打开对应草稿预览 → 需要成片时自行点导出**。

**素材来源（强制）**：只用**用户提供的视频**（本地 path / 可下载 url / 上游 skill 已落盘的片段）。  
**禁止**：`creative_submit_workflow`、`direct_video`、`creative_image_to_video`、`creative_generate_video`、`creative_submit_batch_variants` 等任何 AI 出片。缺素材就请用户补视频，或改走 **product-image-to-jianying-remix**（那边负责图生片段）。

**接受的「批量生成」**：同一套用户视频 → 批量产出**多版混剪**（不同转场 / 特效 / BGM 组合），每版一份 Edit Plan → 编译/导入（见 §1.0）。

**不做**：自研 453/1097 特效渲染、云端服务器导出成片、AI 生 JPG 假透明转场板、AI 生视频素材。

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

对**同一组用户提供的 clips**，批量生成多版「不同转场 / 特效 / BGM」的剪映草稿。  
**不是**批量 AI 生成视频；**不**自动导出 MP4。

| 参数 | 默认 | 说明 |
|------|------|------|
| `variant_count` | `3` | 1–5 版；过多则拆次确认 |
| `clips` | 用户提供 | 各版共用同一 `clips[]` |
| 差异维度 | 转场 + 分段特效 + BGM | 每版至少换一类；优先三类都换 |

**步骤：**

1. 锁定共用 `clips[]`（path/url）；校验文件可读  
2. 规划 `variant_count` 套差异表，例如：

| 版 | 气质 | 转场策略 | 特效策略 | BGM |
|----|------|----------|----------|-----|
| A | 清爽促销 | 快切/闪白系 | 镭射边框 + 细闪轮换 | 偏亮节奏 |
| B | 胶片质感 | 溶解/模糊系 | 胶片框 + 漏光轮换 | 偏缓 |
| C | 潮流故障 | 故障/抖动接缝 | 轻故障 + 星光轮换 | 电子感 |

3. **每一版**独立走 §1.5→§2→§3：单独 Edit Plan、`title`/`--name` 带后缀 `-v1`/`-v2`…  
4. 段内选型规则与单版相同（禁止一版内全片同一特效/同一转场）  
5. BGM：用户无文件时每版可各调一次 `creative_generate_bgm`（mood 不同）；有用户 BGM 则可同曲不同 `volume`/fade，或用户允许时再生成  
6. 交付时列表：`版本 | 草稿名 | 转场要点 | 特效要点 | BGM`（提醒用户到剪映本地草稿查看）

### 1.5 按片段内容选型（强制）

写 Plan 前必须先**看懂每段视频**（读文件名/用户描述；能读帧或预览就看画面；否则根据题材推断），再为**每一段、每一条接缝**单独选特效与转场。

**禁止：**

- 全片只用同一个 `overlays[].name` 盖满时间轴
- 所有 `junctions` 用同一个 `transition`
- 不看素材直接套 preset「全程」模板
- **转场/特效字段错位**（会导致剪映打开草稿崩溃）：
  - `junctions[].transition` **只能**用 `jy-compile transitions` 目录名（如 `竖向模糊`、`闪白`、`色彩溶解`）
  - `overlays` 且 `type=effect` 的 `name` **只能**用 `jy-compile effects` 目录名（如 `撕纸涂鸦边框`、`胶片框 III`、`细闪`）
  - **禁止**把边框/胶片/闪烁等特效名写进 `transition`
  - **禁止**把转场名写进 `overlays[].name`（effect）
  - 文字入出场（`渐显` 等）只能写 `intro`/`outro`，不能当转场或画面特效
  - 写完 Plan 后必须 `jy-compile validate`；`ok:false` 则改名后重编，**禁止**带着 catalog errors 去 import

**要求：**

1. 为每段 clip 记 1 句内容标签（如：静物特写 / 全身走秀 / 人物口播 / 快速运镜 / 暗调氛围 / 明亮产品）
2. 按标签从 [effect-presets.md](references/effect-presets.md)「内容→效果」表选型；相邻段特效尽量不同；选用前用 `jy-compile effects --grep` / `transitions` 核对属于哪一类
3. 每个 effect overlay 只盖**该段在时间轴上的区间**（`start_ms`/`end_ms` = 该 clip 起止），不要整片一条
4. 每条 junction 按「前段尾气质 × 后段头气质」选转场；相邻接缝不要重复同一转场
5. 全局可有**很轻**的统一气质（如偶发 `细闪`），但边框/胶片/故障类必须分段轮换
6. 少数名字在转场与特效目录**都存在**（如 `故障`、`闪白`）：按**用途**放对字段——接缝用 `junctions.transition`，盖画面用 `overlays.effect`，不要混用语义

交付时简述：每段用了什么特效、每条接缝用了什么转场（各一句即可）。

### 1.6 字幕与贴纸（按用户需求）

**默认不加。** 仅当用户明确要求（或提供了文案 / 贴纸图）时写入 overlays。

| 需求 | Plan |
|------|------|
| 底部说明 / 口播字幕 | `type: "subtitle"`，`text`，`transform_y` 约 `-0.75`，按句或按段切时间窗 |
| 标题 / 角标大字 | `type: "text"`，字号更大，可放上方 `transform_y` 约 `0.5~0.7` |
| 关键词高亮 | `keywords`/`keyword` + 可选 `keyword_color`/`keyword_font_size`（简创式富文本） |
| 文字入/出场 | `intro` / `outro`（如 `渐显`/`渐隐`）；先 `jy-compile text-animations --free` |
| 贴纸 / 装饰图 | `type: "sticker"` + 本地 `path`（或 `url`）；角标可用 `transform_x/y` + `scale` |

规则：

- 文案要短、可读；避免挡脸 / 挡产品主体
- 字幕按片段或按句分段，不要一条字幕盖全片除非用户只要一条总标题
- 需要强调卖点/品牌词时写 `keywords`；不要无意义整句高亮
- 标题类可加轻入场（`渐显`/`弹入`）；出场可选；默认只用非 VIP
- 贴纸优先用户提供的透明 PNG；没有图时不要伪造剪映内置 `resource_id`
- 字段细节见 [references/edit-plan.md](references/edit-plan.md)

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
| `validate`/`compile` 报转场/特效错位 | 按 errors 改字段：特效名→`overlays.effect`，转场名→`junctions.transition`；改完再 validate |
| 首页看不到草稿 | 请用户退出重开剪映；核对 `--name` 与本地草稿列表 |
| VIP 特效无法应用 / 弹窗 | 确认是否有剪映 VIP；无则换免费 preset 并重编；有则请用户登录 VIP 后重开剪映 |
| 贴纸图打不开 | 检查 path/url；改 PNG；或去掉 sticker overlay |
| BGM 失败 / 无声音 | 确认是纯音频；看 compile warnings；生成失败则请用户补文件后重编；路径经 import 改写 |
| 用户要 AI 出片 | 拒绝在本 skill 调 `direct_video`；改 **product-image-to-jianying-remix** 或 creative-direct |
| 批量变体部分失败 | 已成功版本照常交付；失败版单独重编 |
| 用户要自动导出 MP4 | 拒绝跑 export；引导在剪映本地草稿打开并手动导出 |

## 交付话术

> 已写入剪映草稿 `<name>`（默认已配 BGM，除非你要求不要）。分段特效：…；接缝转场：…；BGM：…；字幕/贴纸：…（若有）。效果均为免费项 / 已按你的剪映 VIP 使用 VIP 素材（二选一如实说明）。  
> 请**退出并重开剪映**，在「本地草稿」打开该草稿预览；需要成片时在剪映内自行导出。本流程不自动导出 MP4。
