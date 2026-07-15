# Hint 确认模式（文案 + 形象）

口播文案与人物形象图就绪后进入本模式；**未确认前禁止** TTS / 生视频 / 拼接。

## Enter

After:

1. Per-shot VO lines ready  
2. Talent still ready (user-uploaded **or** `creative_generate_image`)

Show the user in one message:

- Full script by shot (`01`…`N` + spoken text)  
- Talent image URL / preview  
- Persona one-liner (age/style) if relevant  
- Ask: 可改文案、改形象，或回复「确认 / 可以生成」继续  

Then **end the turn** and wait.

## Loop (user may repeat)

| User intent | Action | Stay in Hint? |
|-------------|--------|----------------|
| 改某镜文案 / 整段重写 | Edit lines; re-show full script | ✅ Yes |
| 语气/时长/卖点调整 | Revise script; re-show | ✅ Yes |
| 换人物 / 更年轻 / 换穿搭 | Regenerate talent still (`creative-gpt-image2-prompt` + `creative_generate_image`) or accept new upload; re-show image | ✅ Yes |
| 用户上传新形象图/视频 | Replace refs; re-show | ✅ Yes |
| 「确认」「OK」「可以生成」「开始出片」 | Exit Hint → TTS (§5) | ❌ Exit |
| 取消 | Stop; no TTS/video | — |

Rules:

- **Do not** call `creative_generate_tts` or any video submit while in Hint  
- After each edit, show the **updated** script and/or image again and wait  
- Prefer small edits over full regenerate unless user asks  
- If only script changes → keep same talent URL; if only talent changes → keep same script  

## Exit criteria (all required)

- User **explicitly** confirms (not silence / vague “嗯”)  
- Final shot list + talent refs locked in agent memory for TTS/video  

Then proceed: TTS → batch direct video → Wait-then-poll → concat.
