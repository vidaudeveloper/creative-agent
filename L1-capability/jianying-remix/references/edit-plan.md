# Edit Plan schema

导演输出；编译器输入。JSON，UTF-8。

## 字段

```json
{
  "title": "my-remix",
  "aspect": "9:16",
  "clips": [
    {
      "path": "/abs/a.mp4",
      "in_ms": 0,
      "out_ms": 3000,
      "filter": "日系奶油",
      "filter_intensity": 55,
      "intro": "渐显",
      "outro": "渐隐"
    },
    {
      "path": "/abs/b.mp4",
      "in_ms": 0,
      "out_ms": 3000,
      "group_animation": "三分割",
      "filter": "清新",
      "character_effect": "光环 I"
    },
    {
      "path": "/abs/c.mp4",
      "in_ms": 0,
      "out_ms": 2800,
      "intro": "轻微放大",
      "outro": "缩小",
      "filter": "冷白",
      "filter_intensity": 40
    }
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
      "font": "抖音美好体",
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
      "text": "NEW DROP",
      "start_ms": 3000,
      "end_ms": 4500,
      "font": "Anton",
      "font_size": 14,
      "bold": true,
      "transform_y": 0.55,
      "intro": "弹入",
      "loop": "扫光",
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

## clips[] 字段

| 字段 | 说明 |
|------|------|
| `path` / `url` | 二选一；优先 path |
| `in_ms` / `out_ms` | 源内裁剪；`out_ms` 可省略=用到片尾 |
| `intro` / `outro` | **视频**入/出场动画名（`jy-compile catalog --type video-intros/outros`）；与 `group_animation` **互斥** |
| `group_animation` | 视频组合动画（如 `三分割`）；设置后不要再写 intro/outro |
| `filter` | 滤镜名（`catalog --type filters`） |
| `filter_intensity` | 0–100，默认 80；时尚/口播建议 40–60 |
| `mask` | 蒙版名（`线性`/`圆形`/`矩形`/`爱心`/`星形`/`镜面`）；慎用，易裁切主体 |
| `character_effect` | **人物**特效挂在该 clip 上；画面有人即可用（口播/模特展示/走秀等），非仅口播（`catalog --type effects --kind character`） |

## 顶层与其它

| 字段 | 说明 |
|------|------|
| `aspect` | `9:16` \| `16:9` \| `1:1`；或显式 `width`/`height` |
| `junctions` | 转场挂在 `after_clip` 那段**结尾**；`transition` **必须**是转场目录名 |
| `overlays` | `effect` / `text` / `subtitle` / `sticker`；时间窗按段切分 |
| `bgm` | 可选；本地/URL 背景音乐 |
| `mute_original_audio` | 可选；`null`/省略=有 BGM 则静音原片；`false`=保留原声；`true`=强制静音 |

## 目录槽位（强制 · 防崩溃）

| Plan 字段 | 允许目录 | 查法 | 反例（禁止） |
|-----------|----------|------|--------------|
| `junctions[].transition` | 仅转场 | `jy-compile transitions` 或 `catalog --type transitions` | 边框/滤镜/视频动画名 |
| `overlays[].name`（`type=effect`） | 画面特效；**每段时间窗最多 1 个场景特效** | `catalog --type effects` | 转场/滤镜/视频 intro 名；同段叠多个 effect |
| `clips[].intro` / `outro` | 视频入/出场 | `catalog --type video-intros` / `video-outros` | 文字 `渐显`、转场名、特效边框 |
| `clips[].group_animation` | 视频组合动画 | `catalog --type video-groups` | 单入/单出动画名 |
| `clips[].filter` | 滤镜 | `catalog --type filters` | 特效/转场名 |
| `clips[].mask` | 蒙版 | `catalog --type masks` | — |
| `clips[].character_effect` | 人物特效；**每段最多 1 个**（勿再叠人物 overlay） | `catalog --type effects --kind character` | 场景边框特效；同段第二个人物特效 |
| `overlays[].intro` / `outro` | **文字**入/出场 | `text-animations` 或 `catalog --type text-intros/outros` | 视频 intro、转场 |
| `overlays[].loop` | 文字循环 | `catalog --type text-loops` | — |
| `overlays[].font` | 字体 | `catalog --type fonts` | — |

写完后务必：

```bash
jy-compile validate /tmp/vidau-edit-plan.json
```

`ok: false` 时按 `errors` 改字段，**不要** compile/import 错位 Plan（剪映可能直接崩溃）。

## overlays 类型

### `effect`（时间轴特效轨）

- 必填：`name`（场景/人物特效目录名）
- `start_ms` / `end_ms`
- 可选：`effect_kind`: `"auto"` \| `"scene"` \| `"character"`（默认 auto）
- **边框/胶片/闪烁**等盖画面 → 用本字段；人物美颜类更优先写在 `clips[].character_effect`

### `subtitle` / `text`（字幕 / 花字）

- 必填：`text`
- 推荐：`subtitle` 底部说明；`text` 标题/角标
- 可选：`font`（字体目录名）、`font_size`、`color`、`bold`、`align`、`transform_x/y`、`border`
- 关键词高亮：`keywords`/`keyword`、`keyword_color`、`keyword_font_size`
- 动画：`intro` / `outro` / `loop`（文字目录）；`intro_duration_ms` / `outro_duration_ms`

```bash
jy-compile catalog --type fonts --grep Anton --free
jy-compile catalog --type text-intros --free --limit 30
jy-compile catalog --type text-loops --free --grep 扫光
```

### `sticker`（贴纸）

- `path` / `url` 或 `resource_id`；可选 `scale`、`transform_x/y`
- **仅当用户明确要求**时写入

## `bgm`

**默认应写入。** 用户明确不要配乐时省略。

| 字段 | 说明 |
|------|------|
| `path` / `url` | 纯音频 |
| `volume` | 默认 `0.35` |
| `fade_in_ms` / `fade_out_ms` | 默认 400 / 800 |
| `loop` | 默认 `true` |

## 时间

- Plan 用**毫秒**；片段顺序拼接
- overlay 的 `end_ms` 超过总时长会被 clamp
- clip 轴上区间 = 前面各 clip trim 时长累加

## 命名查询（统一入口）

```bash
jy-compile catalog --type transitions --free --limit 50
jy-compile catalog --type effects --kind scene --grep 边框 --free
jy-compile catalog --type effects --kind character --free --limit 40
jy-compile catalog --type filters --free --grep 日系
jy-compile catalog --type video-intros --free --grep 渐
jy-compile catalog --type video-groups --free --limit 40
jy-compile catalog --type fonts --free --grep 站酷
jy-compile catalog --type text-loops --free
```

旧命令 `transitions` / `effects` / `text-animations` 仍可用。选型见 [effect-presets.md](effect-presets.md)。
