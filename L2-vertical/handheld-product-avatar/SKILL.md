---
name: handheld-product-avatar
description: Use when 人物口播/handheld product VO; NOT still-life
metadata:
  layer: L2-vertical
  requires:
    [
      creative-platform,
      creative-task-runner,
      creative-seedance2-prompt,
      creative-gpt-image2-prompt,
      creative-narrative-router,
      creative-direct,
      creative-batch-orchestrator,
    ]
  tags: [ecommerce, avatar, handheld, voiceover, ugc, lipsync]
  hermes:
    related_skills:
      - creative-direct
      - creative-batch-orchestrator
      - product-url-to-video
      - creative-narrative-router
---

# Handheld Product Talking Avatar

Turn **product image + selling points** into a vertical UGC-style ad: person **holding / showing the product** while speaking.

> **Default shot plan**: **全程人物手持产品口播**（每镜都是 talking-handheld + lipsync）。  
> **不要**默认插入产品特写 / 静物展示 / B-roll；仅当用户**明确要求**「产品展示片段 / 特写 / 开箱」时才加。  
> **Hint 确认**：口播文案 + **人物已手持/穿戴产品的效果图**出来后进入 **Hint 模式**，用户可反复改文案/形象；**明确确认后**才 TTS / 生视频。  
> **禁止**只出无产品的纯人物定妆图给用户确认 — 效果图必须已含产品。  
> **Default render path**: **batch direct video** (per-shot Seedance) — **not** `creative_submit_script2film`.  
> Pipeline: TTS per shot → parallel async `direct_video` → **§8 后台 Wait-then-poll（强制）** → **§9 ffmpeg concat**.  
> **Wait-then-poll 硬门禁**：视频 job 全部提交后，agent **必须**按 **creative-task-runner**：前台通知并结束回合 + **后台** `sleep(ETA)` → 查 job → 未完成再后台 `sleep 20s`，全部终态后**自动**进拼接。  
> **禁止**：只回复 job 表却不调度后台 waiter；或把跟进完全推给用户「随时问进度」。  
> Lip sync = Seedance `reference_audio` **出镜口播对口型**（not 旁白/画外音；prompt 禁止 narration/旁白措辞）.  
> **Never** upload recognizable real-face refs unless user accepts privacy risk.

## When to use

| Trigger | This skill |
|---------|------------|
| 手持产品口播、带货数字人、talking head + product | ✅ |
| Product image + on-camera VO | ✅ |
| Still-life / no talking person | ❌ → `product-url-to-video` / `creative-script2film` |
| Product **URL** scrape first | ❌ → `product-url-to-video`, then handoff here |
| Single ≤15s one shot | Same path with **1** video job (no concat) |

## Prompt gates

- **Hint 手持/穿戴效果图**: **creative-gpt-image2-prompt** + product in `reference_urls`（禁止纯人物无产品）
- Each shot video prompt: **creative-seedance2-prompt** + [handheld-prompt.md](references/handheld-prompt.md)

## References

| File | When |
|------|------|
| [script-templates.md](references/script-templates.md) | VO pacing / Hook→CTA |
| [persona-by-vertical.md](references/persona-by-vertical.md) | Persona brief |
| [multi-scene.md](references/multi-scene.md) | 15/30/60s grids |
| [ugc-authenticity.md](references/ugc-authenticity.md) | UGC look |
| [voiceover-timing.md](references/voiceover-timing.md) | TTS + **同音色锁定** + duration |
| [handheld-prompt.md](references/handheld-prompt.md) | Confirmation still + Seedance constraints |
| [batch-direct-video.md](references/batch-direct-video.md) | 并行提交 + **必做** Wait-then-poll + ffmpeg concat |
| [hint-mode.md](references/hint-mode.md) | 文案+手持/穿戴效果图确认环；确认前禁止 TTS/视频 |

---

## Agent flow

### 1. Collect inputs

- Product image → **creative-platform** upload → HTTPS URL  
- Selling points / brief  
- Defaults: duration **30s**, aspect **9:16**, locale = user language  
- If user attached **talent image/video** → use as identity refs for composing handheld still (and optional `reference_video_urls`); if the upload is **already** person holding/wearing this product, may skip regenerate  

### 2. Persona (text only)

Load [persona-by-vertical.md](references/persona-by-vertical.md) unless talent media already defines look.

### 3. Script → per-shot VO lines

Load [script-templates.md](references/script-templates.md) + [multi-scene.md](references/multi-scene.md).

- Spoken copy; **each shot ≤12s** after TTS  
- **Every shot default**: person on camera, product in hand, speaking (lipsync)  
- **No** product-only / macro / B-roll shots unless user asked for showcase  
- Optional: `creative_generate_script` (`voiceover: true`) then parse `## Voiceover Copy`  

### 4. 手持/穿戴效果图（Hint 用 — 硬门禁）

给用户确认的必须是 **人物 + 产品已合在同一画面**（手持或穿戴），**不是**纯人物大头/半身无产品。

生成规则（无现成「已手持产品」图时必跑）：

1. Load **creative-gpt-image2-prompt**
2. `creative_generate_image`：
   - `reference_urls`: **必须含产品图**；若用户有人物图也一并放入
   - `aspect_ratio`: `9:16`
   - `prompt`: 按产品形态写清 **holding**（瓶/盒/机）或 **wearing**（表/饰/衣帽等）；产品外观锁参考图；脸+产品同框；UGC 自拍感  
   - 细则：[handheld-prompt.md](references/handheld-prompt.md) § Confirmation still
3. 输出 = **handheld still**（手持/穿戴定妆图），供 Hint 展示与后续视频 `reference_image_urls`

| User has | Action |
|----------|--------|
| 已是「人物手持/穿戴该产品」的图 | 可直接作 handheld still（仍建议核对产品与 SKU 一致） |
| 仅人物图 / 人物视频 | **仍须** `creative_generate_image`：产品 ref + 人物 ref → 合成手持/穿戴效果图；视频可另作 `reference_video_urls` |
| 仅产品图 | `creative_generate_image`：产品 ref + persona brief → 生成手持/穿戴效果图 |
| 用户不要换脸、只要自己图且已含产品 | 跳过生图，用用户图 |

### 5. Hint 确认模式（硬门禁）

Load [hint-mode.md](references/hint-mode.md).

1. 展示完整分镜口播文案 + **手持/穿戴效果图**（及 persona 摘要）— 确认用户能看见产品已在手上/身上  
2. **结束本回合**，等用户反馈  
3. 用户可反复：**改文案** / **重生或换形象**（重生时仍须带产品 ref，出合图）→ 每次改完再展示 → 继续等  
4. **仅当**用户明确说「确认 / 可以生成 / 开始出片」等 → 锁定文案与效果图，进入 §6  
5. Hint 期间 **禁止** `creative_generate_tts`、任何视频 submit  

### 6. TTS (required before video) — **同音色硬门禁**

Load [voiceover-timing.md](references/voiceover-timing.md) + persona（[persona-by-vertical.md](references/persona-by-vertical.md)）。

1. **先锁定**本片唯一 `voice` + `language_boost`：按 **口播语言 + 性别 + 垂类/职业/vibe** 匹配（voiceover-timing § Voice lock）；写入 `tts_voice_reason`  
2. 每一镜 `creative_generate_tts` **必须传同一组** `voice` / `language_boost` — **禁止**省略、禁止逐镜换音色/换性别  
3. 汇总 `{ index, text, duration_sec, audio_url, voice }`；`voice` 写入记忆供复检  

若某镜漏传 `voice`，服务端会落到英文默认声 `English_Upbeat_Woman`，整片音色会乱套。  
音色须贴合人物职业特点（如金融/医疗偏沉稳，美妆偏闺蜜，勿一律甜妹音）。

### 7. Batch direct video (default — **no script2film**)

Load [batch-direct-video.md](references/batch-direct-video.md)（含 **Wait-then-poll**，与 §8 同级必读）+ **creative-batch-orchestrator** when ≥2 shots.

For **each shot** submit one job (parallel, unique `client_request_id`):

**Preferred (async, trackable):**

```json
{
  "workflow_type": "direct_video",
  "input": {
    "prompt": "<Seedance prompt: handheld + product + speak to camera>",
    "aspect_ratio": "9:16",
    "duration_sec": 6,
    "video_mode": "reference",
    "reference_image_urls": ["<product>", "<handheld_still>"],
    "reference_video_urls": ["<talent_video?>"],
    "reference_audio_urls": ["<this shot TTS audio_url>"],
    "reference_audio_role": "lipsync",
    "generate_audio": true
  },
  "client_request_id": "<uuid>"
}
```

MCP: `creative_submit_workflow` with above, **or** `creative_image_to_video` (also async → same `direct_video` job). Prefer batch submit for ≥2 shots.

**口播硬门禁（防旁白）**

- 每镜 **必须** 带本镜 TTS 的 `reference_audio_urls` + **`reference_audio_role: "lipsync"`**（服务端才追加对口型约束；其它 skill 用 `guide` 或不传即可做节拍/旁白引导）
- Prompt 经 **creative-seedance2-prompt** + [handheld-prompt.md](references/handheld-prompt.md)：写明 **出镜说话 / on-camera lip-sync**，并追加 lipsync suffix  
- **禁止** prompt 出现：旁白、画外音、voiceover、narration、解说（否则 Seedance 常把参考音频当画外旁白，嘴不动）  
- `generate_audio: true`（让模型保留人声轨与口型对齐）

**Do not** call `creative_submit_script2film` on this default path.

**提交完成后必须调度 §8 后台 waiter** — 前台可结束回合，但不得只回复 job 表并等用户来问。

### 8. Wait-then-poll（强制主步骤 — 后台对齐 job-runner，唤醒后拼接）

**必做，不是参考可选。** 遵循 **creative-task-runner**（前台回复 + 后台轮询），完成后**必须**进 §9。

全部镜头 job 提交成功后：

1. **前台**：告知用户 jobs 已提交 + `task_id` ↔ shot 表 + **max ETA**（各 submit 的 `estimate.eta_sec`，缺省 **180s**）→ 调度后台 waiter → **结束前台回合**
2. **后台**：`sleep(max_eta)`（勿在前台阻塞）→ 查询每个 `task_id`
3. 若 **全部** 终态（`completed` / `failed` / `cancelled`）：
   - 有失败 → 报告失败镜；问重试或用成功镜继续
   - 全部 `completed` → **立刻**进 **§9 Client concat**（不等人再 ping）
4. 若仍有 `queued`/`running` → 再调度后台 `sleep 20s` → 回步骤 2（总上限约 30 min；超时列出卡住的 job）
5. 轮询唤醒时每 1–2 轮可简短进度（如 `3/5 done`）；勿刷屏

**Forbidden（违反即流程错误）**

- 结束回合且**不**调度后台 waiter，只说「你可以随时问我进度」
- 只描述 Wait-then-poll 却不 arm 后台 sleep / 不查 job
- 在前台回合里多分钟 `sleep` 卡住对话
- 查完终态却不进入 §9

细节表见 [batch-direct-video.md](references/batch-direct-video.md) § Wait-then-poll — 与本节等效，**不可**因「写在 references」而跳过。

### 9. Client concat (no BGM)

When all shot videos succeeded:

1. Download shot MP4s in index order  
2. ffmpeg concat demuxer → `final.mp4`  
3. **No BGM** unless user asks (`creative_generate_bgm` + mux)  
4. Optional subtitles from VO lines  

Example concat list + command: [batch-direct-video.md](references/batch-direct-video.md).

### 10. When to fall back to script2film

Only if user wants **full storyboard identity boards / auto BGM / mux post VO** without providing talent media — then hand off to **creative-script2film**. Default handheld VO stays on batch direct video.

---

## Continuity

- Same product + **handheld still** (person already holding/wearing product) on **every** shot  
- Hard cuts OK; cut on VO pauses  
- Default: every shot has `reference_audio_urls` (lipsync handheld)  
- Showcase / product-only shot: **only if user requested**; then TTS optional / may omit `reference_audio_urls`  

## Compliance

- No Creatify API  
- No celebrity lookalikes / real-face training  
- Product must match reference SKU  
- Real-face refs may be Seedance privacy-blocked — tell user if so  
