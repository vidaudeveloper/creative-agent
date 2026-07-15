# Hint 确认模式（文案 + 手持/穿戴效果图）

口播文案与 **人物已手持/穿戴产品的效果图**就绪后进入本模式；**未确认前禁止** TTS / 生视频 / 拼接。

## Enter

After:

1. Per-shot VO lines ready  
2. **Handheld still** ready — 人物 + 产品同框（手持或穿戴），**不是**纯人物无产品图  
   - 来源：用户已上传「手持/穿戴该产品」图，**或** `creative_generate_image`（`reference_urls` 必含产品图）

Show the user in one message:

- Full script by shot (`01`…`N` + spoken text)  
- **Handheld still** URL / preview（用户应能直接看到产品已在手上/身上）  
- Persona one-liner (age/style) if relevant  
- Ask: 可改文案、改形象，或回复「确认 / 可以生成」继续  

Then **end the turn** and wait.

**Reject / regenerate before enter** if the still is face-only or product is missing/off-frame — do not ask user to confirm a product-less talent shot.

## Loop (user may repeat)

| User intent | Action | Stay in Hint? |
|-------------|--------|----------------|
| 改某镜文案 / 整段重写 | Edit lines; re-show full script | ✅ Yes |
| 语气/时长/卖点调整 | Revise script; re-show | ✅ Yes |
| 换人物 / 更年轻 / 换穿搭 | Regenerate **handheld still**（产品 ref 必带 + `creative-gpt-image2-prompt` + `creative_generate_image`）或接受新上传合图；re-show | ✅ Yes |
| 产品姿势不对 / 没拿稳 / 应改为穿戴 | Regenerate with clearer hold/wear instruction; keep persona; re-show | ✅ Yes |
| 用户上传新形象图/视频 | 若新图无产品 → 再合成手持/穿戴效果图；若已含产品 → 直接替换；re-show | ✅ Yes |
| 「确认」「OK」「可以生成」「开始出片」 | Exit Hint → TTS (§6) | ❌ Exit |
| 取消 | Stop; no TTS/video | — |

Rules:

- **Do not** call `creative_generate_tts` or any video submit while in Hint  
- After each edit, show the **updated** script and/or **handheld still** again and wait  
- Prefer small edits over full regenerate unless user asks  
- If only script changes → keep same handheld still URL; if only look changes → keep same script  
- Every regenerate **must** include product in `reference_urls` and in the visible result  

## Exit criteria (all required)

- User **explicitly** confirms (not silence / vague “嗯”)  
- Final shot list + **handheld still** (+ product URL) locked in agent memory for TTS/video  
- Confirmed still still shows product held or worn (visual check before exit)  

Then proceed: TTS → batch direct video → **§8 Wait-then-poll（强制 sleep）** → §9 concat.
