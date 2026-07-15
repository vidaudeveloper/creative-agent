# Seedance 2.0 Platform Specs (VidAU)

## Input limits

| Type | Max | Formats | Size |
|------|-----|---------|------|
| Images | 9 | jpeg, png, webp, bmp, tiff, gif | < 30 MB each |
| Videos | 3 | mp4, mov | < 50 MB each, 2–15s total |
| Audio | 3 | mp3, wav | < 15 MB each, ≤ 15s total |
| Text | Natural language | — | — |
| **Total files** | **12** | — | — |

## Output

- Duration: **4–15 seconds** per generation
- Resolution: ~480p–720p (platform); VidAU may upscale/rehost
- Native audio: model can emit in-shot SFX; VidAU script2film adds BGM separately

## Hard blocks

- **No identifiable real human faces** in reference inputs
- Copyright / IP likeness (characters, logos, celebrities) — rewrite abstractly
- Privacy-sensitive input images

## VidAU MCP mapping

| MCP tool | Prompt field | Ref fields |
|----------|--------------|------------|
| `creative_generate_video` | `prompt` | optional refs — **async** `job_id` |
| `creative_image_to_video` | `prompt` | `reference_image_urls` / `reference_image_url` — **async** |
| `creative_first_frame_to_video` | `prompt` | `first_frame_url`, optional `last_frame_url` — **async** |
| `creative_submit_workflow` (`direct_video`) | `input.prompt` | same fields under `input` — **async** |
| `creative_submit_workflow` (`direct_video`) | `input.prompt` | per mode table in creative-direct |

## Audio policy (VidAU script2film)

When `voiceover_enabled` or server sets `generate_audio=false`:

- Prompt may include: footsteps, fabric, product clicks, ambient room tone
- Prompt must **not** include: BGM, soundtrack, background music, song, humming, lyrics

When direct single clip with `generate_audio=true`:

- In-shot SFX OK; avoid requesting full musical score (conflicts with optional `creative_generate_bgm`)

## Language

- **Chinese prompts** generally perform best on 即梦 / Seedance
- Match user conversation locale unless user asks for English prompt text
- Keep on-screen display text in quotes with exact copy
