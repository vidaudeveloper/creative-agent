# Persona by vertical (text brief only)

Output a **persona brief** for image + Seedance prompts. Do **not** call external persona libraries / IDs.

## Trust signals

| Vertical | Ideal persona | Why |
|----------|---------------|-----|
| Healthcare / supplements | 30–50, clean, trustworthy | Credibility |
| Beauty / skincare | 20–35, polished but peer-like | Peer recommend |
| Tech / gadgets | 25–40, casual-pro | Approachable expertise |
| Finance | 35–55, neat, calm authority | Stability |
| Fitness | 25–35, athletic energy | Aspiration |
| Food / beverage | 25–45, warm, home kitchen | Lifestyle |
| Education | 30–50, friendly teacher | Soft authority |
| General DTC | 20–35, casual UGC | Peer recommend |

## Brief template (fill and paste into `brief.persona`)

```text
Age band: …
Gender presentation: … (or unstated)
Vibe: … (warm / energetic / calm expert)
Wardrobe: … (casual tee / athleisure / …)
Setting: … (home desk / kitchen / balcony — natural light)
Handheld / wear style: phone-selfie feel; product already in hand OR worn on body (never empty-handed)
Face: stylized AI model — NOT a real celebrity or real photo likeness
TTS voice lock: … (fill from voiceover-timing.md table — one id for whole film)
```
Note: persona text feeds the **handheld still** prompt — still must composite persona + product before Hint.  
TTS: pick **one** voice from the gender row and lock it for all shots (see voiceover-timing § Voice lock).


## Diversity

- Match market locale when user targets a region
- Prefer "looks like the customer OR who they trust"
- A/B gender only if user asks for variants — don't assume

## Compliance

- Never use a user's private photo of a real person as Seedance face ref
- Never request celebrity lookalikes
