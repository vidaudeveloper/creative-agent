---
name: creative-narrative-router
description: Use before script2film to pick narrative_structure beats
metadata:
  layer: L0-foundation
  requires: []
  tags: [foundation, narrative, script, routing, storyboard, i18n, playbook, ecommerce]
  hermes:
    related_skills: [product-url-to-video, creative-script2film, viral-ad-rewrite]
---

# Creative Narrative Router

Before **`creative_generate_script`**, pick a **`narrative_structure`**, **Read** the matching file under `references/`, then inject beats, constraints, and scene rhythm into `brief.narrative`.

For **ecommerce / product ads**, also resolve a commerce **industry playbook** (美妆 / 服饰 / 食品) and inject hook menu + sell-point order + CTA — see `references/commerce-playbook-index.md`.

Do **not** use one universal HOOK→CLIMAX template for every video. Structure follows user intent; details live in references (loaded on demand).

## Language & locale

| Rule | Detail |
|------|--------|
| **Skill docs** | English (this file + references) |
| **User conversation** | Match the user's language (EN, ES, JP, ZH, …) |
| **Script output** | `creative_generate_script` sets **Output Language** from `creative_request` / `brief.locale` — do not force Chinese |
| **Platforms** | TikTok, Instagram Reels, YouTube Shorts, YouTube, LinkedIn, Amazon, Shopify, etc. — not CN-only platforms unless the user asks |

## When to run

| Scenario | Router |
|----------|--------|
| `creative-script2film` / `-keyframes` — generate script | **Required** |
| `product-url-to-video` — before submit | **Required** |
| `creative-direct` — single clip ≤15s | Optional |
| User pasted full Final Video Spec | Skip router → submit |

## Flow (4 steps)

### Step 1 — Parse intent

From user message + `brief`:

| Field | Meaning |
|-------|---------|
| `content_goal` | sell / brand / story / promo / mood / explain |
| `has_concrete_product` | named SKU, product refs, or `brief.product` |
| `platform` | TikTok, Reels, YouTube, LinkedIn, … |
| `target_duration_sec` | 16–120, default 30 |
| `voiceover` | default `false` |
| `user_explicit_structure` | user named a type (“brand film”, “story-led”, “pain-point ad”) |
| `industry` | `beauty_skincare` / `fashion_accessories` / `food_beverage` / `unknown` |

Resolve `industry` per **`references/commerce-playbook-index.md`**. Low confidence → ask or offer 2 structure options; **never invent** niche industry jargon.

### Step 2 — Choose `narrative_structure`

**Priority** (high → low):

1. User explicitly chose a structure
2. Keyword inference (table below) — works in **English and other languages**; prefer explicit `brief.narrative_structure` when unsure
3. Low confidence → show **2–3 options** with **different** structures; wait for choice
4. Still unclear → `product_ad` if product/SKU present, else `problem_solution` if pain described

#### Available structures

| `narrative_structure` | User signals (EN examples) | Inference hints | Reference |
|----------------------|----------------------------|-----------------|-----------|
| `product_ad` | “product ad”, “features”, “SKU”, “UGC sell” | `brief.product`, product ref images | `references/product-ad.md` |
| `story_narrative` | “story”, “mini film”, “emotional”, “not hard sell” | story intent without sell-only goal | `references/story-narrative.md` |
| `problem_solution` | “pain point”, “before/after”, “save time”, “frustration” | problem + solution in brief | `references/problem-solution.md` |
| `brand_film` | “brand film”, “brand story”, “values”, “manifesto” | brand tone, weak CTA | `references/brand-film.md` |
| `event_promo` | “sale”, “launch”, “Black Friday”, “limited offer” | promo / discount / event | `references/event-promo.md` |
| `mood_film` | “mood”, “aesthetic”, “sensory”, “minimal copy” | vibe-led, weak script | `references/mood-film.md` |
| `knowledge_explainer` | “explainer”, “how it works”, “tutorial”, “educational” | teach / explain topic | `references/knowledge-explainer.md` |
| `character_showcase` | “character showcase”, “model”, “lookbook”, “turnaround” | person-led, no SKU focus | `references/character-showcase.md` |

> **Server:** `creative_generate_script` reads `brief.narrative_structure` and injects beats; if omitted, server infers with the same EN/ZH keyword rules. Response includes `narrative_structure` / `secondary_narrative_structure`.

#### Combining structures

Commerce often uses **`product_ad` + `problem_solution`**: pain hook → product reveal.  
Set primary `product_ad`, `secondary_structure: problem_solution`, Read **both** references.

### Step 3 — Load structure + commerce playbook

1. **Read** the reference file for the chosen structure (paths relative to this `SKILL.md`)
2. If ecommerce / `has_concrete_product` / `product-url-to-video`:
   - **Read** `references/commerce-playbook-index.md`
   - If industry known → **Read** matching `references/playbooks/*.md`
   - Default commerce shape: **Hook → Pitch → CTA** (maps onto `product_ad` beats)
3. Merge structure beats + playbook hook/sellpoint/CTA into `brief.narrative`

### Step 4 — Call MCP

Call **`creative_generate_script`** with enriched brief:

```json
{
  "creative_request": "30s vertical TikTok ad for vitamin C serum — glow texture focus",
  "brief": {
    "product": "Vitamin C serum",
    "audience": "US office workers with dull skin",
    "platform": "TikTok",
    "locale": "en",
    "industry": "beauty_skincare",
    "narrative_structure": "product_ad",
    "secondary_structure": "problem_solution",
    "narrative": {
      "beats": ["hook", "hero_product", "pitch", "cta"],
      "hook_type": "texture_asmr",
      "sellpoint_order": ["scenario", "benefit", "feature", "experience"],
      "cta_style": "soft_routine",
      "video_form": "product_demo",
      "constraints": ["No invented clinical claims", "No invented SKUs"],
      "scene_types_hint": ["texture_closeup", "hero_product", "routine_lifestyle", "cta_card"]
    }
  },
  "target_duration_sec": 30,
  "aspect_ratio": "9:16",
  "voiceover": false
}
```

**Agent:** **Narrative Driver** in the spec must follow the beat map; each shot in **Scene overview** should map to a beat (label beats in parentheses when helpful). For beauty/fashion/food, script must show **industry hook type + sell-point order**, not a generic “introduce the product” line.

## Multi-option pitch (low confidence)

Each row must use a **different** `narrative_structure`:

```markdown
| Option | Structure | One-line pitch | Why |
| A | product_ad | 30s vertical, 3 features fast | Product refs + clear SKU |
| B | problem_solution | Commute noise → ANC earbuds | User stressed pain points |
| C | story_narrative | Day-in-the-life, earbuds appear naturally | User wants soft sell |
```

After selection → Read reference → `creative_generate_script`.

## Alignment with vidau-editor ad formats

| `narrative_structure` | `choice_ad_format` |
|----------------------|-------------------|
| `product_ad` | `product_ad` |
| `story_narrative` | `story_narrative` |
| `brand_film` | `brand_film` |
| `event_promo` | `event_promo` |
| `mood_film` | `mood_film` |
| `knowledge_explainer` | `knowledge_explainer` |
| `character_showcase` | `character_showcase` |
| `problem_solution` | Often secondary to `product_ad`; can stand alone without SKU |

## Do not invent products

If the user gave **no** product name and **no** product reference images:

- Do **not** pick `product_ad` and invent watches, phones, etc.
- Prefer `story_narrative`, `problem_solution`, or `character_showcase` with placeholders
- Or ask: “Do you have a product name or reference images?”

## Downstream skills

- **creative-script2film** / **creative-script2film-keyframes** — require this skill before script generation
- **product-url-to-video** — usually `product_ad` (+ optional `problem_solution`) + commerce playbook
- **viral-ad-rewrite** — may reuse playbook for pitch/CTA after structure brief is confirmed
