---
name: viral-ad-rewrite
description: Use when borrow viral ad structure; NOT copy brand/pack
metadata:
  layer: L2-vertical
  requires:
    [
      creative-task-runner,
      creative-platform,
      creative-seedance2-prompt,
      creative-gpt-image2-prompt,
      creative-narrative-router,
      creative-script2film,
      creative-direct,
    ]
  tags: [ecommerce, viral, rewrite, structure, reference, script2film]
  hermes:
    related_skills: [product-url-to-video, trend-viral-short, creative-script2film]
---

# Viral Ad Rewrite（爆款结构复刻）

Borrow a **reference ad’s structure** (hook / pacing / shot order / CTA style) and remake it for the user’s **own product**. Product truth comes from the **product image**, never from the template brand.

> **Prompt gate**: Image MCP → **creative-gpt-image2-prompt**. Video MCP / visual enrichment → **creative-seedance2-prompt**.

> **NOT for**: copying another brand’s pack copy, subtitles, or claims; paste-product-URL-only flows → **product-url-to-video**; trend hook stills A/B → **trend-viral-short**.

## Dual input roles (say this first)

| Role | Source | What you may borrow / use |
|------|--------|---------------------------|
| **Template video** | Reference ad (user URL/file or our example) | Rhythm, hook pattern, shot order, camera pacing, CTA *style* |
| **Product image** | User’s product hero (preferred: no clear real human face) | Appearance, packaging, visible sell points — **source of truth** |

Hard rule: **structure可借、产品不可偷** — template brand / pack text / subtitles / specific claims must appear on the **forbidden inherit** list.

## State machine (hard gates)

Treat the dialogue as states. **Never** ask for generation confirm or call generate MCP before `BRIEF_READY` + user confirm.

| State | Agent does | Forbidden |
|-------|------------|-----------|
| `START_OPENING` | Explain dual roles; offer **rehearsal** vs **real**; collect inputs | “确认生成”、estimate、any generate MCP |
| `INPUTS_READY` | Classify template profile; draft rewrite plan | Submit generate |
| `BRIEF_READY` | Show compact brief (≥3 borrow + ≥3 forbid); offer detail / edit / confirm | Generate without confirm |
| `DETAIL_VIEW` | Full breakdown if asked; return to edit/confirm | Skip confirm |
| `REHEARSAL` | Walk example brief + fake result; **zero** paid MCP | Real `creative_submit_*` |
| `GENERATION_CONFIRMED` | Estimate → submit → track | Generating before this state |
| `DELIVERED` | Video + restate borrowed vs forbidden | Claim “same as template brand” |

Read `references/brief-template.md`, `references/template-profiles.md`, `references/rehearsal.md` on demand.

## When to trigger

User says / implies: 借爆款、结构复刻、参考这个广告做我们的产品、rewrite this viral for my SKU、borrow this ad’s structure.

## Default output

- Aspect: **9:16** short ad
- Path: **creative-script2film** with product image as `reference_image_urls` (locks product identity)
- Single ≤15s clip only if user asks → **creative-direct** `image_to_video`
- Prefer product images **without clear real human faces** (stability + risk). If face-heavy, explain and ask for pack/product-only hero.

## Flow

### 1. Opening (`START_OPENING`)

Match user language. Cover:

1. Template = structure; product image = truth
2. Choice: **无成本彩排** / **正式分析**
3. Collect: template video (or “用示例模板”), product image(s), optional direction (audience / tone / CTA)

Do **not** show a final “确认生成” button yet.

### 2. Collect inputs

- Template: local path / URL the Agent can inspect, or built-in example for rehearsal
- Product: ≥1 clear product image (upload via **creative-platform** if needed)
- Optional: market, locale, duration (default 15–30s)

### 3. Rehearsal path (optional)

If user chooses rehearsal → load **`references/rehearsal.md`**.

- Full brief + detail option + example “result” narrative
- **No** `creative_estimate` / **no** submit / **no** credit burn
- After rehearsal, offer to switch to real path with their media

### 4. Analyze → compact brief (`BRIEF_READY`)

Using template profile (`references/template-profiles.md`), output compact brief via **`references/brief-template.md`**:

Must include:

- What we **borrow** (≥3 bullets)
- **Forbidden inherit** (≥3 bullets) — brand, pack copy, subtitles, claims, face identity…
- Product anchors from the image
- Hook / shot rhythm / how product enters frame
- Editable: audience, tone, CTA

Wait for: confirm / edit / “查看详细分析”.

**Hard gate:** If user has not confirmed the brief → **do not** call any generate MCP.

### 5. Confirm → generate (`GENERATION_CONFIRMED`)

1. Optional: **creative-narrative-router** + commerce playbook for pitch/CTA wording (product side)
2. Build script / prompts that encode borrowed structure + product anchors; strip forbidden items
3. `creative_estimate` → show credits/ETA
4. Submit default:

```
creative_submit_script2film:
  script: "<rewrite script>"
  reference_image_urls: ["<product image>", ...]
  brief:
    product: "<from image/user>"
    audience: "<confirmed>"
    locale: "<locale>"
    narrative_structure: "product_ad"
    rewrite:
      template_profile: "<visual_product_texture|human_demo|human_voiceover|platform_cta|mixed>"
      borrowed: ["...", "...", "..."]
      forbidden_inherit: ["...", "...", "..."]
  aspect_ratio: "9:16"
  target_duration_sec: 30
  client_request_id: "<uuid>"
```

5. **creative-task-runner** — notify + background poll → end turn

### 6. Deliver

- Video URL + short note: **借了结构、换了产品**
- Restate ≥3 borrowed + ≥3 forbidden (same lists as confirmed brief)
- Asset pack lite: hook used, audience, 1 next A/B angle

## Notes

- Never copy template pack text into overlays or VO
- Never claim the result is “the same ad” as the template brand
- No TikTok Ads account write / pause / budget from this skill
- If only a product URL is given (no reference ad) → route to **product-url-to-video**
