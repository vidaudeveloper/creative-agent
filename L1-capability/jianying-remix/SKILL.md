---
name: jianying-remix
description: >-
  Local CapCut/Jianying remix director — per-clip content-aware effects/transitions,
  optional subtitles/stickers; BGM on by default (user file or MCP generate),
  compile draft via jianying-draft-compiler, import into user's Jianying;
  on Windows RPA-export MP4. Not for cloud MP4 or AI fake-alpha plates.
metadata:
  layer: L1-capability
  requires: []
  tags: [jianying, capcut, remix, transition, subtitle, sticker, bgm, local, draft, editor, windows-export]
---

# Jianying Remix — 本机草稿导演

用户提供多段视频时，你是**智能混剪导演**；本机 `jianying-draft-compiler` 是**草稿编译器**；用户剪映是**特效渲染器**（Windows 可 RPA 自动导出）。

**不做**：自研 453/1097 特效渲染、云端服务器导出成片、AI 生 JPG 假透明转场板。

## 何时使用

- 用户要「剪映级」转场/边框/胶片等模板感混剪
- 本机有（或可安装）剪映 + 多段本地/可下载视频
- 用户说时装混剪、撕纸边框、快切、CapCut 风格等
- 用户要加**字幕 / 标题字 / 贴纸**（按需）；**BGM 默认带上**（用户可关）

## 何时不用

| 需求 | 改走 |
|------|------|
| 无剪映、只要快速拼接成片 | 其它 remix / ffmpeg / creative-agent 成片链路 |
| 单镜头生成 | `creative-direct` / script2film |
| 只要云端 MP4、不打开本机剪映 | 不要用本 skill 承诺自动成片 |

## 前置探测（每次必做）

```bash
export PATH="$HOME/.vidau/bin:$PATH"
# Windows CMD: set PATH=%USERPROFILE%\.vidau\bin;%PATH%

command -v jy-compile >/dev/null || bash <repo>/tools/install-jy-compile.sh
jy-compile where
```

Compiler 来源与安装：同仓 `tools/jianying-draft-compiler/`，见 [references/install-compiler.md](references/install-compiler.md)。  
Windows 导出能力：`jy-compile export-check` + [references/windows-export.md](references/windows-export.md)。

## 工作流

### 1. 收素材与意图

- 本地 path 优先；画幅默认 `9:16`
- Preset 只是**素材池**，不是整片套一层：[references/effect-presets.md](references/effect-presets.md)
- 默认 `allow_vip=false`
- 询问或识别：字幕/贴纸是否需要；BGM **默认要加**（有用户文件优先，否则自动生成；用户明确说不要配乐则跳过）

### 1.5 按片段内容选型（强制）

写 Plan 前必须先**看懂每段视频**（读文件名/用户描述；能读帧或预览就看画面；否则根据题材推断），再为**每一段、每一条接缝**单独选特效与转场。

**禁止：**

- 全片只用同一个 `overlays[].name` 盖满时间轴
- 所有 `junctions` 用同一个 `transition`
- 不看素材直接套 preset「全程」模板

**要求：**

1. 为每段 clip 记 1 句内容标签（如：静物特写 / 全身走秀 / 人物口播 / 快速运镜 / 暗调氛围 / 明亮产品）
2. 按标签从 [effect-presets.md](references/effect-presets.md)「内容→效果」表选型；相邻段特效尽量不同
3. 每个 effect overlay 只盖**该段在时间轴上的区间**（`start_ms`/`end_ms` = 该 clip 起止），不要整片一条
4. 每条 junction 按「前段尾气质 × 后段头气质」选转场；相邻接缝不要重复同一转场
5. 全局可有**很轻**的统一气质（如偶发 `细闪`），但边框/胶片/故障类必须分段轮换

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

### 4. 导出（按平台）

**先探测 OS**（`uname` / `sys.platform` / 用户环境）。

#### Windows（完整自动）

1. `jy-compile export-check` → 必须 `ok: true`；否则装 `uv sync --extra windows` 并重试  
2. 确认**剪映专业版已打开且在首页**（能看到刚导入的草稿名）  
3. 执行：

```bat
jy-compile export <草稿名> -o %USERPROFILE%\Videos\<草稿名>.mp4 --resolution 1080P --timeout 600
```

4. 成功则交付 `output_mp4` 路径；失败则展示 error，并引导手动导出  

#### macOS / 非 Windows

- 请用户**退出并重开剪映**，打开草稿预览后**手动点导出**
- **不要**调用 `jy-compile export`（会直接失败）

## 失败处理

| 现象 | 处理 |
|------|------|
| `jy-compile` 不存在 | install-compiler；阻塞 |
| `where` 失败 | 装剪映或设 `JIANYING_DRAFT_ROOT` |
| 链接媒体 / 暂无访问权限 | 必须用 `import`（路径改写） |
| `export-check` 失败 | 装 windows extras；确认在 Windows |
| `export` 找不到草稿 | 剪映回首页；草稿名=文件夹名；robocopy/重启剪映 |
| `export` 超时 / 找不到按钮 | 版本 UI 不兼容或 VIP 弹窗；改手动导出 |
| VIP 特效 | 换免费 preset |
| 贴纸图打不开 | 检查 path/url；改 PNG；或去掉 sticker overlay |
| BGM 失败 / 无声音 | 确认是纯音频；看 compile warnings；生成失败则请用户补文件后重编；路径经 import 改写 |

## 交付话术

**Windows 自动导出成功：**

> 已完成混剪并导出：`<mp4路径>`。草稿名 `<name>`。分段特效：…；接缝转场：…；BGM：…；字幕/贴纸：…（若有）。

**macOS / 仅导入：**

> 已写入剪映草稿 `<name>`（默认已配 BGM，除非你要求不要）。分段特效与转场已按素材内容区分。请退出重开剪映后打开预览并手动导出。本机为 Mac，无法 RPA 自动导出。
