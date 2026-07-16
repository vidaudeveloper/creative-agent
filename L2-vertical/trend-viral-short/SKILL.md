---
name: trend-viral-short
description: Use when batch TikTok/Reels hook IMAGE variants to A/B
metadata:
  layer: L2-vertical
  requires: [creative-task-runner, creative-platform, creative-gpt-image2-prompt, creative-seedance2-prompt, creative-batch-orchestrator, creative-script2film, creative-script2film-keyframes, creative-direct]
  tags: [trend, batch, ecommerce, image]
---

# Trend Viral Short

Ride trends; quickly produce multiple vertical **image** variants for A/B testing.

> **Prompt gate**: Load **creative-gpt-image2-prompt** — craft **one distinct prompt per variant** (different hook / scene / composition). For video paths, load **creative-seedance2-prompt** before video MCP.
> **Submit path**: ≥2 images → hand off to **creative-batch-orchestrator** as N× `creative-direct-image` jobs. **Do not** reuse one prompt with a count.

## When to use

- MCN daily drops, trend chasing
- Same product, multiple opening-hook tests (**image** variants)

## When user wants "video deliverable"

This skill defaults to **batch images**. For video, switch L1 skill by intent:

| Need | Skill | MCP |
|------|-------|-----|
| Multi-shot product short + reference | creative-script2film | `creative_submit_script2film` |
| Multi-shot + keyframe transitions | creative-script2film-keyframes | `creative_submit_script2film_keyframes` |
| Single trend short clip | creative-direct | `creative_generate_video` / `creative_first_frame_to_video` |

Confirm intent before submit — do not default to image batch for video requests.

## Flow (image variants)

1. Organize brief: `product`, `trend_tags` (trend keywords), `hook_idea` (optional)
2. Decide `N` (default **5**, hard cap **10** via batch orchestrator)
3. **Load creative-gpt-image2-prompt** — craft **N distinct** production-grade prompts (different hooks / angles / scenes; not "variant 1/2/3" suffixes)
4. Hand off to **creative-batch-orchestrator** with N items:

```yaml
batch_label: "Trend hooks — <product>"
items:
  - label: "Hook A — neon shelf UGC"
    skill: creative-direct-image
    input:
      prompt: "<prompt from gpt-image2 skill>"
      aspect_ratio: "9:16"
      reference_urls: ["https://..."]   # product refs when available
  - label: "Hook B — bathroom vanity"
    skill: creative-direct-image
    input:
      prompt: "<different prompt>"
      aspect_ratio: "9:16"
      reference_urls: ["https://..."]
  # … up to N
```

5. Batch skill handles estimate → parallel `creative_submit_workflow` (`direct_image`) → job-runner tracking → result table
6. List artifacts by label; suggest launch priority

## Preset constraints (trend_viral_v1)

- Strong hook in first 3 seconds (visual)
- Product close-up ≤ 40% of frame
- No infringing trends, sensitive content

## Technique injection

When orchestrating, read preset file: `presets/trend_viral_v1.json`
