---
name: creative-direct
description: Use when ≤15s clip/image; NOT multi-shot or product URL
metadata:
  layer: L1-capability
  requires: [creative-platform, creative-job-runner, creative-seedance2-prompt, creative-gpt-image2-prompt]
  tags: [image, video, async, one-click]
---

# Creative Direct — Image sync / Video async

- **Image**: sync MCP (`creative_generate_image`) — returns artifacts in one call.
- **Video**: **always async** — submit returns `job_id`; never wait for the MP4 in the same MCP call (Seedance is too slow → timeouts).

> **Prompt gate (required)**: Before any MCP call below, load **creative-gpt-image2-prompt** (images) or **creative-seedance2-prompt** (video), output a paste-ready prompt, then pass it as MCP `prompt`. Never use raw user text.

> **Duration routing**: User wants **>15s** / 30s / 60s / multi-shot / storyboard → use **creative-script2film** or **handheld-product-avatar** batch; **do not** force long-form through this skill.

> **Job tracking**: Load **creative-job-runner** before any generation call.

## Video skill selection

| Need | Skill | MCP |
|------|-------|-----|
| Reference images, product consistency | **creative-script2film** | `creative_submit_script2film` |
| First/last-frame transitions, controlled camera | **creative-script2film-keyframes** | `creative_submit_script2film_keyframes` |
| Single short clip | **This skill** | `creative_image_to_video` / `creative_generate_video` / `creative_first_frame_to_video` (all → `direct_video` job) |
| Multi-shot parallel | **creative-batch-orchestrator** | `creative_submit_workflow` `direct_video` |

## Image generation

1. Tell user: "Generating image, ~1–2 minutes…"
2. **Load creative-gpt-image2-prompt** — craft production-grade `prompt` from user intent + references
3. **When user has local/attached reference images** (`@image`, etc.):
   - **Prefer** `creative_get_upload_instructions` → local curl/terminal PUT to S3 → use `upload.file_url`
   - Fallback (no local terminal): `creative_upload_reference` (`content_base64`)
4. `creative_generate_image`:
   - `prompt`: **output from creative-gpt-image2-prompt** (not raw user text)
   - `aspect_ratio`: `9:16` | `1:1` | `16:9`
   - `reference_urls`: optional — `file_url` from upload step (or existing HTTPS URLs)
5. Read `tracking.user_message`; return `artifacts[0].urls.download` + local save hint

## Video generation (async only)

1. Tell user: "Submitting video job, ~2–5 minutes; ask me for progress anytime."
2. **Load creative-seedance2-prompt** — craft production-grade `prompt`
3. With user reference images → **`creative_image_to_video`**:
   - `prompt`: Seedance prompt
   - `reference_image_urls` (max 9) or `reference_image_url`
   - optional `reference_audio_urls` / `reference_video_urls`
4. Without refs → `creative_generate_video` (text-to-video)
5. First/last frame → `creative_first_frame_to_video`
6. Response is **`job_id` + tracking** — **not** artifacts. Follow **creative-job-runner**: reply immediately; poll only when user asks.

Equivalent: `creative_submit_workflow` with `workflow_type=direct_video` and the same fields under `input`.

## Optional: BGM

For a single short clip with background music (after video job completes):

1. `creative_generate_bgm` (may pass `script` / `brief` / `bgm_hint` for auto prompt)
2. `creative_mux_bgm_into_video` — mux `video_url` + `bgm_url`

## Defaults

- Vertical short: `aspect_ratio=9:16`, `duration_sec=5`
- **Audio on**: `generate_audio=true` (default); in-shot SFX from Seedance
