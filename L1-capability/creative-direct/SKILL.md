---
name: creative-direct
description: Use when ≤15s clip/image; NOT multi-shot or product URL
metadata:
  layer: L1-capability
  requires: [creative-platform, creative-task-runner, creative-seedance2-prompt, creative-gpt-image2-prompt]
  tags: [image, video, async, one-click]
---

# Creative Direct — Image / Video / BGM (all async)

All generation returns **`task_id`** immediately. Follow **creative-task-runner** (foreground reply + background ETA → 20s poll).

> **Preferred MCP**: `creative_submit_generate` with `items: [{ type, input }, ...]`（1–10 条，一次返回多个 `task_id`）。  
> Convenience aliases still work: `creative_generate_image` / `creative_generate_video` / `creative_image_to_video` / `creative_first_frame_to_video` / `creative_generate_bgm`.

> **Prompt gate (required)**: Before any MCP call below, load **creative-gpt-image2-prompt** (images) or **creative-seedance2-prompt** (video), output a paste-ready prompt, then pass it as MCP `prompt`. Never use raw user text.

> **Duration routing**: User wants **>15s** / 30s / 60s / multi-shot / storyboard → use **creative-script2film** or **handheld-product-avatar** batch; **do not** force long-form through this skill.

> **Task tracking**: Load **creative-task-runner** before any generation call.

## Video skill selection

| Need | Skill | MCP |
|------|-------|-----|
| Reference images, product consistency | **creative-script2film** | `creative_submit_script2film` |
| First/last-frame transitions, controlled camera | **creative-script2film-keyframes** | `creative_submit_script2film_keyframes` |
| Single short clip | **This skill** | `creative_submit_generate` `type=video` (or convenience video tools) |
| Multi-shot parallel | **creative-batch-orchestrator** | 一次 `creative_submit_generate` `items[]`（≤10）或多次 `creative_submit_workflow` |

## Image generation (async)

1. **Load creative-gpt-image2-prompt** — craft production-grade `prompt`
2. Local/attached refs → `creative_get_upload_instructions` (prefer) or `creative_upload_reference`
3. Submit:

```json
{
  "items": [
    {
      "type": "image",
      "input": {
        "prompt": "<from gpt-image2 skill>",
        "aspect_ratio": "9:16",
        "reference_urls": ["https://..."]
      },
      "client_request_id": "<uuid>"
    }
  ]
}
```

MCP: `creative_submit_generate`（返回 `tasks[]`；单条时也有顶层 `task_id`）。多图一次最多 10 条 `items`。Alias：`creative_generate_image`（单条 flat fields）。
4. Follow **creative-task-runner**; on wake save to conversation **产物** + show download URL.

## Video generation (async)

1. **Load creative-seedance2-prompt**
2. Prefer `creative_submit_generate`:

| Case | `items[].input` highlights |
|------|-------------------|
| Text-to-video | `prompt`, `duration_sec`, `aspect_ratio` |
| Reference | above + `video_mode: "reference"`, `reference_image_urls` |
| First frame | `video_mode: "first_frame"`, `first_frame_url` |
| First/last | `video_mode: "first_last_frame"`, `first_frame_url`, `last_frame_url` |

Aliases: `creative_generate_video` / `creative_image_to_video` / `creative_first_frame_to_video`.
3. Response is **`tasks[]` / `task_id` + tracking** — follow **creative-task-runner**.

## Optional: BGM (async)

After video task completes:

```json
{
  "items": [
    {
      "type": "bgm",
      "input": {
        "prompt": "...",
        "duration_sec": 30,
        "instrumental": true
      }
    }
  ]
}
```

Or alias `creative_generate_bgm`. On wake → `creative_mux_bgm_into_video` with video + BGM URLs.

## Defaults

- Vertical short: `aspect_ratio=9:16`, video `duration_sec=5`, BGM `duration_sec=30`
- **Audio on** for video: `generate_audio=true` (default); in-shot SFX from Seedance
