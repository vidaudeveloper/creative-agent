# Edit Plan schema

导演输出；编译器输入。JSON，UTF-8。

## 字段

```json
{
  "title": "my-remix",
  "aspect": "9:16",
  "clips": [
    { "path": "/abs/a.mp4", "in_ms": 0, "out_ms": 3000 },
    { "path": "/abs/b.mp4", "in_ms": 0, "out_ms": 3000 },
    { "path": "/abs/c.mp4", "in_ms": 0, "out_ms": 2800 }
  ],
  "junctions": [
    { "after_clip": 0, "transition": "竖向模糊", "duration_ms": 500 },
    { "after_clip": 1, "transition": "闪白", "duration_ms": 400 }
  ],
  "overlays": [
    { "type": "effect", "name": "撕纸涂鸦边框", "start_ms": 0, "end_ms": 3000 },
    { "type": "effect", "name": "胶片框 III", "start_ms": 3000, "end_ms": 6000 },
    { "type": "effect", "name": "细闪", "start_ms": 6000, "end_ms": 8800 },
    {
      "type": "subtitle",
      "text": "本季主推 · 轻薄风衣",
      "start_ms": 0,
      "end_ms": 3000,
      "font_size": 8,
      "align": 1,
      "transform_y": -0.75,
      "keywords": "轻薄风衣",
      "keyword_color": "#ff7100",
      "keyword_font_size": 10,
      "intro": "渐显",
      "outro": "渐隐"
    },
    {
      "type": "text",
      "text": "五个快乐到死的顶级思维",
      "start_ms": 3000,
      "end_ms": 4500,
      "font_size": 11,
      "bold": true,
      "transform_y": 0.55,
      "keyword": "快乐|顶级思维",
      "keyword_color": "#ff7100",
      "keyword_font_size": 15,
      "intro": "弹入",
      "outro": "弹出"
    },
    {
      "type": "sticker",
      "path": "/abs/stickers/star.png",
      "start_ms": 6000,
      "end_ms": 8800,
      "scale": 0.35,
      "transform_x": 0.55,
      "transform_y": 0.65
    }
  ],
  "bgm": {
    "path": "/abs/music/bgm.mp3",
    "volume": 0.35,
    "fade_in_ms": 400,
    "fade_out_ms": 800,
    "loop": true
  }
}
```

有 `bgm` 时编译器**默认静音原片**（等价 `mute_original_audio` 自动为 true）。若要原声+BGM 混音，显式设 `"mute_original_audio": false`。

| 字段 | 说明 |
|------|------|
| `aspect` | `9:16` \| `16:9` \| `1:1`；或显式 `width`/`height` |
| `clips[].path` / `url` | 二选一；优先 path |
| `in_ms` / `out_ms` | 源内裁剪；`out_ms` 可省略=用到片尾 |
| `junctions` | 转场挂在 `after_clip` 那段**结尾**；`transition` **必须**是转场目录名（`jy-compile transitions`）；**禁止**填特效名 |
| `overlays` | `effect` / `text` / `subtitle` / `sticker`；时间窗按段切分；`type=effect` 的 `name` **必须**是特效目录名（`jy-compile effects`）；**禁止**填转场名 |

## 目录槽位（强制 · 防崩溃）

| Plan 字段 | 允许目录 | 查法 | 反例（禁止） |
|-----------|----------|------|--------------|
| `junctions[].transition` | 仅转场 | `jy-compile transitions` | `撕纸涂鸦边框`、`胶片框 III`、`细闪`、`渐显` |
| `overlays[].name`（`type=effect`） | 仅画面特效 | `jy-compile effects --grep …` | `竖向模糊`、`色彩溶解`（纯转场名） |
| `overlays[].intro` / `outro` | 文字动画 | `jy-compile text-animations` | 转场名 / 边框特效名 |

写完后务必：

```bash
jy-compile validate /tmp/vidau-edit-plan.json
```

`ok: false` 时按 `errors` 改字段，**不要** compile/import 错位 Plan（剪映可能直接崩溃）。
| `bgm` | 可选；本地/URL 背景音乐，见下 |
| `mute_original_audio` | 可选；`null`/省略=有 BGM 则静音原片；`false`=保留原声；`true`=强制静音 |

## overlays 类型

### `effect`（场景特效）

- 必填：`name`（目录名，如 `撕纸涂鸦边框`）
- `start_ms` / `end_ms`

### `subtitle` / `text`（字幕 / 花字文案）

- 必填：`text`
- 推荐：`subtitle` 底部说明；`text` 标题/角标
- 可选：`font_size`（字幕约 7–9，标题约 10–14）、`color` `[r,g,b]` 0–1、`bold`、`align`（0 左 / 1 中 / 2 右）、`transform_x` / `transform_y`（半画布单位；字幕默认 `transform_y=-0.75`）、`border`（默认 true 描边）

**关键词高亮**（对齐简创 `add_text_style`，编译进剪映富文本 `styles`）：

| 字段 | 说明 |
|------|------|
| `keywords` / `keyword` | 高亮词；`"快乐\|顶级思维"` 或 `["快乐","顶级思维"]`；长词优先匹配 |
| `keyword_color` | `#RRGGBB` 或 `[r,g,b]`；默认 `#ff7100` |
| `keyword_font_size` | 关键词字号；默认约 `font_size+2` |

**文字动画**（本机目录，非云端模板）：

| 字段 | 说明 |
|------|------|
| `intro` | 入场名，如 `渐显` / `弹入` / `打字机 I` |
| `outro` | 出场名，如 `渐隐` / `弹出` |
| `intro_duration_ms` / `outro_duration_ms` | 可选覆盖时长 |

```bash
jy-compile text-animations --kind intro --free --limit 30
jy-compile text-animations --kind outro --grep 渐 --free
```

默认只用非 VIP。不确定时先查目录再写入。若改用 VIP 素材，须先提醒用户确认本机有**剪映 VIP 账号**。

### `sticker`（贴纸）

优先本地透明图：

- `path` 或 `url`：png / webp / jpg / gif
- 或 `resource_id`：剪映内置贴纸 ID（少用，需已知 ID）
- 可选：`scale`（默认 0.45）、`transform_x` / `transform_y`（角标常用 `0.55, 0.65`）

**仅当用户明确要求字幕/贴纸时才写入**；不要默认堆满字。

## `bgm`（背景音乐 · 默认开启）

**默认应写入。** 仅用户明确不要配乐时省略。

音源：用户 `path`/`url` 优先；否则 MCP **`creative_generate_bgm`**（暂时不用曲库 `creative_select_bgm`）。禁止 skill 直连平台曲库 HTTP。

| 字段 | 说明 |
|------|------|
| `path` / `url` | 二选一；mp3 / wav / m4a 等纯音频（不要用带画面的视频当 BGM） |
| `in_ms` / `out_ms` | 音频文件内裁剪 |
| `start_ms` / `end_ms` | 时间轴区间；默认盖满成片 |
| `volume` | 默认 `0.35`（相对原音）；口播场景可再低 |
| `fade_in_ms` / `fade_out_ms` | 默认 400 / 800 |
| `loop` | 默认 `true`；BGM 短于成片时循环铺满 |

配合：有 `bgm` 时**默认静音原片**；仅当用户要保留原声混音时写 `"mute_original_audio": false`。

## 时间

- Plan 用**毫秒**；引擎内部转微秒
- 片段在时间轴上**顺序拼接**（按 trim 后时长累加）
- overlay 的 `end_ms` 超过总时长会被 clamp
- 计算某 clip 的轴上区间：前面各 clip 的 `(out_ms - in_ms)` 之和 → 该段 `start_ms`；再加本段时长 → `end_ms`

## 命名

```bash
jy-compile transitions --limit 50
jy-compile effects --grep 边框 --limit 30
jy-compile text-animations --kind intro --free --limit 40
```

默认只用非 VIP。不确定时先 `effects --grep` / `text-animations` 再写入 Plan。选型规则见 [effect-presets.md](effect-presets.md)。改用 VIP 前须提醒用户确认有**剪映 VIP 账号**。

## 校验

```bash
jy-compile validate plan.json
```
