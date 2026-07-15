# Handheld + product Seedance constraints

Load with **creative-seedance2-prompt**. Apply to every speaking / handheld shot.

## Hard rules

1. **Product lock**: Match reference product shape, color, logo, materials exactly — no SKU drift
2. **Product visibility**: Product occupies ~15–30%+ of frame when claimed "handheld"
3. **Action**: Hold / present / tilt / point — not face-only talking head
4. **UGC**: Mild handheld motion, natural light, home/street set (see ugc-authenticity.md)
5. **Talent**: Stylized AI face consistent with talent still; no real-person / celebrity likeness
6. **Lipsync shots**: Face clearly visible; avoid extreme head turns; follow reference audio phonemes
7. **No**: competitor brands, fake UI screenshots as proof, readable personal PII

## Prompt fragments (EN — weave into shot lines)

```
Mid-shot UGC selfie style, talent holding the exact product from reference,
product logo readable, soft natural window light, slight handheld camera,
speaking to camera with natural lip motion matching the reference audio,
keep face and product both in frame.
```

Close-up B-roll (**opt-in only** — user asked for 展示/特写):

```
Macro product detail matching reference packaging, slow tilt, fingers optional,
no face required, natural desk light.
```

## Mode reminder

| Shot type | When | Prefer |
|-----------|------|--------|
| Talking + face + product in hand | **Default every shot** | `reference_audio_urls` lipsync |
| Product-only B-roll | **Only if user requested** | optional TTS / no face |

## Continuity

- Same talent still + product ref on all talking shots
- Hard cuts OK; cut on VO pauses
- Optional cinematic bridges → creative-script2film-keyframes (usually skip for talking shots)
