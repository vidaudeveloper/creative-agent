# Voiceover timing · lipsync vs mux

## Mode choice (this skill default)

Handheld **default render** = batch direct video (see [batch-direct-video.md](batch-direct-video.md)), **not** script2film mux/lipsync flags.

| Need | Path |
|------|------|
| On-camera lip sync (default) | Per-shot `reference_audio_urls` + direct_video / image_to_video |
| Off-camera VO only | Still batch direct video **or** hand off script2film `voiceover_mode=mux` |

## Voice lock（硬门禁 — 整片同一音色）

多镜口播 **必须** 使用 **同一个** MiniMax `voice` + 同一个 `language_boost`。  
音色不一致（甚至性别跳变）几乎总是因为：逐镜漏传 / 换传 `voice`，或省略后落到服务端英文默认声。

### 锁定时机

Hint 确认后、**第一声 TTS 之前**，按下方 **匹配顺序** 选定一次，写入 agent 记忆：

```yaml
tts_voice: "<MiniMax voice id>"
tts_language_boost: "zh"   # or en
tts_voice_reason: "<vertical + gender + vibe → why this id>"
```

之后每一镜 `creative_generate_tts` **原样复用** `tts_voice` / `tts_language_boost`。用户未改口要求换声前，**禁止**改 ID。

### 匹配顺序（必做）

1. **用户指定音色 ID** → 整片用该 ID（仍须每镜显式传入）  
2. 否则看 **口播语言**（中文 / English）+ **persona 性别**  
3. 再按 **垂类 / 职业角色 / vibe** 从下表选最贴合的一条（优先 vertical；无表项则用 vibe 关键词）  
4. 仍无法判断 → 用该语言+性别的 **fallback**

音色须与画面人物一致：女声配女性形象、男声配男性形象；职业感贴近（医美≠电台综艺腔、金融≠甜妹音）。

### 中文 · 按垂类 / 职业（先选这里）

| Vertical / 职业角色 | 女 `voice` | 男 `voice` | 匹配要点 |
|---------------------|------------|------------|----------|
| Beauty / skincare / 美妆达人 | `Chinese (Mandarin)_Warm_Bestie` | `Chinese (Mandarin)_Gentle_Youth` | 闺蜜安利、轻柔亲近 |
| Healthcare / supplements / 健康顾问 | `Chinese (Mandarin)_Wise_Women` | `Chinese (Mandarin)_Gentleman` | 可信、沉稳、勿过于甜 |
| Tech / gadgets / 数码测评 | `Chinese (Mandarin)_IntellectualGirl` | `Chinese (Mandarin)_Straightforward_Boy` | 清晰、直接、略专业 |
| Finance / 理财顾问 | `Chinese (Mandarin)_News_Anchor` | `Chinese (Mandarin)_Reliable_Executive` | 权威、稳、少口语嬉皮 |
| Fitness / 教练 | `Chinese (Mandarin)_Crisp_Girl` | `Chinese (Mandarin)_Unrestrained_Young_Man` | 有劲、鼓励感 |
| Food / beverage / 美食博主 | `Chinese (Mandarin)_Warm_Girl` | `Chinese (Mandarin)_Southern_Young_Man` | 烟火气、生活感 |
| Education / 老师 / 知识分享 | `Chinese (Mandarin)_Wise_Women` | `Chinese (Mandarin)_Gentle_Youth` | 讲解感、耐心 |
| General DTC / UGC 素人 | `Chinese (Mandarin)_Warm_Girl` | `Chinese (Mandarin)_Radio_Host` | 同龄安利、自然口播 |
| 空乘 / 礼仪服务感 | `Chinese (Mandarin)_HK_Flight_Attendant` | `Chinese (Mandarin)_Male_Announcer` | 礼貌、播报清晰 |
| 成熟御姐 / 高冷种草 | `Chinese (Mandarin)_Mature_Woman` | `Chinese (Mandarin)_Reliable_Executive` | 气场、少奶气 |
| 邻家 / 真诚种草 | `Chinese (Mandarin)_Sweet_Lady` | `Chinese (Mandarin)_Sincere_Adult` | 真诚、不夸张 |

`language_boost`: 中文口播一律 `zh`。

### English · by vertical / role

| Vertical / role | Female `voice` | Male `voice` |
|-----------------|----------------|--------------|
| Beauty / skincare | `English_Soft-spokenGirl` | `English_Gentle-voiced_man` |
| Healthcare / supplements | `English_SereneWoman` | `English_Trustworth_Man` |
| Tech / gadgets | `English_ConfidentWoman` | `English_Diligent_Man` |
| Finance | `English_Graceful_Lady` | `English_Trustworth_Man` |
| Fitness | `English_Upbeat_Woman` | `English_PassionateWarrior` |
| Food / lifestyle | `English_Upbeat_Woman` | `English_Jovialman` |
| Education | `English_SereneWoman` | `English_PatientMan` |
| General DTC / UGC | `English_Upbeat_Woman` | `English_Trustworth_Man` |

`language_boost`: `en`（或省略）。

> 注：官方男声 ID 为 `English_Trustworth_Man`（拼写无 y）；勿写成 Trustworthy。

### Vibe 关键词补强（vertical 模糊时）

| Persona vibe / 特点 | 偏女 | 偏男 |
|---------------------|------|------|
| warm / peer / 闺蜜安利 | Warm_Bestie / Warm_Girl | Southern_Young_Man / Sincere_Adult |
| calm expert / 专业沉稳 | Wise_Women / News_Anchor | Gentleman / Reliable_Executive |
| energetic / 活力种草 | Crisp_Girl / Warm_Girl | Unrestrained_Young_Man / Radio_Host |
| soft / gentle / 柔和 | Soft_Girl / Sweet_Lady | Gentle_Youth / Gentleman |
| authoritative / 权威 | News_Anchor / Mature_Woman | Reliable_Executive / Male_Announcer |

（中文 ID 前缀均为 `Chinese (Mandarin)_`；英文见上表完整 ID。）

### Fallback（仅当 vertical + vibe 都对不上）

| 口播语言 | 性别 | `voice` |
|----------|------|---------|
| 中文 | 女 / 未指定 | `Chinese (Mandarin)_Warm_Girl` |
| 中文 | 男 | `Chinese (Mandarin)_Radio_Host` |
| English | female / unstated | `English_Upbeat_Woman` |
| English | male | `English_Trustworth_Man` |

### 规则

- 用户指定音色 ID → 整片用用户指定的（仍须每镜显式传入）  
- 换声仅当用户明确说「换成男声/女声/某某音色」或「更专业/更甜」→ 按表重选后 **整批重跑 TTS**  
- **Forbidden**: 逐镜换 ID；省略 `voice`；音色性别与画面人物明显冲突；金融/医疗却用过甜综艺音（除非用户点名）

### MCP 调用模板（每镜相同 voice）

```json
{
  "text": "<shot VO line>",
  "voice": "<LOCKED tts_voice>",
  "language_boost": "<LOCKED tts_language_boost>"
}
```

服务端默认（省略 `voice` 时）= `English_Upbeat_Woman` — **中文口播切勿省略**。

---

## Per-shot pipeline

1. Parse `## Voiceover Copy` (one line per shot, ordered)
2. **Lock voice**（上节）→ then TTS each line via `creative_generate_tts` with the **same** `voice` + `language_boost`
3. Duration:
   ```bash
   ffprobe -v error -show_entries format=duration -of csv=p=0 vo-NN.mp3
   ```
4. `duration_sec = clamp(ceil(measured + 0.4), 4, 12)`
5. Plan entry:

```json
{
  "index": 1,
  "text": "…",
  "duration_sec": 6,
  "audio_url": "https://…/vo-01.mp3",
  "voice": "<same locked id>"
}
```

`audio_url` **required for predictable lipsync** (server can auto-TTS if omitted, but prefer client URLs — and server TTS also needs a single `tts_voice` if used).

## Word / char budgets (guide)

Aim so TTS ≈ target shot length before clamp:

| Shot target | EN words (conversational) | ZH chars (approx) |
|-------------|---------------------------|-------------------|
| 5s | 12–15 | 18–22 |
| 8s | 20–24 | 28–36 |
| 12s | 30–36 | 42–54 |

If sum of `duration_sec` differs from `target_duration_sec` by **>3s**, rewrite copy or re-TTS **with the same locked voice** before submit.

## ≤15s single shot

One line TTS → async `creative_image_to_video` / `direct_video` with `reference_audio_urls: [audio_url]` + product/talent refs. Skip script2film.
