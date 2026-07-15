# Persona by vertical (text brief only)

Output a **persona brief** for image + Seedance prompts. Do **not** call external persona libraries / IDs.

## Trust signals

| Vertical | Ideal persona | Why | 默认 TTS 方向（详见 voiceover-timing） |
|----------|---------------|-----|----------------------------------------|
| Healthcare / supplements | 30–50, clean, trustworthy | Credibility | Wise_Women / Gentleman |
| Beauty / skincare | 20–35, polished but peer-like | Peer recommend | Warm_Bestie / Gentle_Youth |
| Tech / gadgets | 25–40, casual-pro | Approachable expertise | IntellectualGirl / Straightforward_Boy |
| Finance | 35–55, neat, calm authority | Stability | News_Anchor / Reliable_Executive |
| Fitness | 25–35, athletic energy | Aspiration | Crisp_Girl / Unrestrained_Young_Man |
| Food / beverage | 25–45, warm, home kitchen | Lifestyle | Warm_Girl / Southern_Young_Man |
| Education | 30–50, friendly teacher | Soft authority | Wise_Women / Gentle_Youth |
| General DTC | 20–35, casual UGC | Peer recommend | Warm_Girl / Radio_Host |

## Brief template (fill and paste into `brief.persona`)

```text
Age band: …
Gender presentation: … (or unstated)
Role / profession: … (e.g. 美妆达人 / 健康顾问 / 数码测评 / 理财顾问 / 素人 UGC)
Vibe: … (warm / energetic / calm expert)
Wardrobe: … (casual tee / athleisure / …)
Setting: … (home desk / kitchen / balcony — natural light)
Handheld / wear style: phone-selfie feel; product already in hand OR worn on body (never empty-handed)
Face: stylized AI model — NOT a real celebrity or real photo likeness
TTS voice lock: … (from voiceover-timing: language + gender + vertical/role/vibe → one MiniMax id)
TTS voice reason: … (one line: why this id fits the role)
```
Note: persona text feeds the **handheld still** prompt — still must composite persona + product before Hint.  
TTS: match **职业/垂类/vibe + 性别 + 语言**，锁定 **一个** ID 给整片（见 voiceover-timing § Voice lock）。


## Diversity

- Match market locale when user targets a region
- Prefer "looks like the customer OR who they trust"
- A/B gender only if user asks for variants — don't assume

## Compliance

- Never use a user's private photo of a real person as Seedance face ref
- Never request celebrity lookalikes
