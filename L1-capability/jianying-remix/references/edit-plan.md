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
      "transform_y": -0.75
    },
    {
      "type": "text",
      "text": "NEW IN",
      "start_ms": 3000,
      "end_ms": 4500,
      "font_size": 11,
      "bold": true,
      "transform_y": 0.55
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
  ]
}
```

| 字段 | 说明 |
|------|------|
| `aspect` | `9:16` \| `16:9` \| `1:1`；或显式 `width`/`height` |
| `clips[].path` / `url` | 二选一；优先 path |
| `in_ms` / `out_ms` | 源内裁剪；`out_ms` 可省略=用到片尾 |
| `junctions` | 转场挂在 `after_clip` 那段**结尾**；相邻接缝尽量换名 |
| `overlays` | `effect` / `text` / `subtitle` / `sticker`；时间窗按段切分 |

## overlays 类型

### `effect`（场景特效）

- 必填：`name`（目录名，如 `撕纸涂鸦边框`）
- `start_ms` / `end_ms`

### `subtitle` / `text`（字幕 / 花字文案）

- 必填：`text`
- 推荐：`subtitle` 底部说明；`text` 标题/角标
- 可选：`font_size`（字幕约 7–9，标题约 10–14）、`color` `[r,g,b]` 0–1、`bold`、`align`（0 左 / 1 中 / 2 右）、`transform_x` / `transform_y`（半画布单位；字幕默认 `transform_y=-0.75`）、`border`（默认 true 描边）

### `sticker`（贴纸）

优先本地透明图：

- `path` 或 `url`：png / webp / jpg / gif
- 或 `resource_id`：剪映内置贴纸 ID（少用，需已知 ID）
- 可选：`scale`（默认 0.45）、`transform_x` / `transform_y`（角标常用 `0.55, 0.65`）

**仅当用户明确要求字幕/贴纸时才写入**；不要默认堆满字。

## 时间

- Plan 用**毫秒**；引擎内部转微秒
- 片段在时间轴上**顺序拼接**（按 trim 后时长累加）
- overlay 的 `end_ms` 超过总时长会被 clamp
- 计算某 clip 的轴上区间：前面各 clip 的 `(out_ms - in_ms)` 之和 → 该段 `start_ms`；再加本段时长 → `end_ms`

## 命名

```bash
jy-compile transitions --limit 50
jy-compile effects --grep 边框 --limit 30
```

默认只用非 VIP。不确定时先 `effects --grep` 再写入 Plan。选型规则见 [effect-presets.md](effect-presets.md)。

## 校验

```bash
jy-compile validate plan.json
```
