# Handheld + product constraints

## Confirmation still（Hint 用 — 硬门禁）

Load **creative-gpt-image2-prompt** before `creative_generate_image`.  
This still is what the user confirms — **must** show person **already holding or wearing** the product.

### Hard rules (still)

1. `reference_urls` **must include the product image** (first or clearly indexed)
2. If user provided a talent photo → include it too; keep face identity, **add** product interaction
3. Choose interaction by product form:
   - Bottle / box / device / food pack → **holding** in hand, product logo readable
   - Watch / jewelry / glasses / hat / apparel → **wearing** correctly on body
4. Vertical **9:16**, mid-shot or selfie framing; **face + product both in frame**
5. Product shape/color/logo match reference — no SKU drift
6. Stylized AI talent OK; no celebrity / real-person lookalike unless user uploaded their own face and accepted risk
7. **Forbidden for Hint**: face-only headshot, product floating beside person, product only in background, “will hold later” empty hands

### Prompt fragments (EN — still)

Handheld (default for most SKUs):

```
Vertical 9:16 UGC selfie mid-shot. Same person as Image N (if talent ref).
Holding the exact product from Image 1 in hand toward camera,
product packaging shape color and logo match reference, readable,
natural window light, casual home setting, both face and product clearly visible,
empty hands forbidden.
```

Wearable:

```
Vertical 9:16 UGC selfie mid-shot. Same person as Image N (if talent ref).
Wearing the exact product from Image 1 correctly on body (watch on wrist /
necklace on neck / …), product appearance matches reference,
natural light, face and product both clearly visible.
```

Index refs in prompt, e.g. `Image 1: product — lock appearance. Image 2: talent face/wardrobe — keep identity.`

---

## Seedance video constraints

Load with **creative-seedance2-prompt**. Apply to every speaking / handheld shot.

### Hard rules (video)

1. **Product lock**: Match reference product shape, color, logo, materials exactly — no SKU drift
2. **Product visibility**: Product occupies ~15–30%+ of frame when claimed "handheld"
3. **Action**: Hold / present / tilt / point — not face-only talking head
4. **UGC**: Mild handheld motion, natural light, home/street set (see ugc-authenticity.md)
5. **Talent**: Consistent with confirmed **handheld still**; no real-person / celebrity likeness
6. **Lipsync 口播（硬门禁）**: Face clearly visible; mouth moves with `reference_audio`; **on-camera speech** — NOT 旁白 / off-screen narration
7. **No**: competitor brands, fake UI screenshots as proof, readable personal PII

### 口播 vs 旁白（写 prompt 时必守）

| ✅ 口播 lipsync（本 skill 默认） | ❌ 旁白 / mux 感（禁止用于默认镜） |
|--------------------------------|----------------------------------|
| Talent **speaks to camera** / 出镜说话 | Voiceover / narration / 画外音 / 旁白 |
| Lip motion matches reference audio | Silent face + audio layered as VO |
| `reference_audio_urls` = this shot TTS | Audio described as BGM / soundtrack / 解说 |

**Mandatory EN suffix**（每镜 Seedance prompt 末尾追加）+ MCP 传 `reference_audio_role: "lipsync"`（服务端仅在此 role 下再保险追加一次）:

```
The on-screen person speaks on camera in sync with the reference audio (lip-sync talking-head).
This is spoken dialogue from the visible talent — NOT off-screen narration, NOT voiceover over a silent face.
Match lip movements and facial performance to the speech phonemes.
Keep the face clearly visible; avoid extreme head turns that break lip sync.
Mouth must move with the reference audio; do not invent different dialogue.
```

**Forbidden prompt words**（默认 talking 镜）: `voiceover`, `narration`, `off-screen`, `旁白`, `画外音`, `解说`, `配音盖画面`

### Prompt fragments (EN — weave into shot lines)

```
Mid-shot UGC selfie style, talent holding the exact product from reference,
product logo readable, soft natural window light, slight handheld camera,
the talent speaks on camera to the viewer with natural lip motion matching the reference audio,
keep face and product both in frame — on-camera dialogue, not narration.
```

Close-up B-roll (**opt-in only** — user asked for 展示/特写):

```
Macro product detail matching reference packaging, slow tilt, fingers optional,
no face required, natural desk light.
```

### Mode reminder

| Shot type | When | Prefer |
|-----------|------|--------|
| Talking + face + product in hand | **Default every shot** | `reference_audio_urls` lipsync |
| Product-only B-roll | **Only if user requested** | optional TTS / no face |

### Continuity

- Same **handheld still** + product ref on all talking shots
- Hard cuts OK; cut on VO pauses
- Optional cinematic bridges → creative-script2film-keyframes (usually skip for talking shots)
