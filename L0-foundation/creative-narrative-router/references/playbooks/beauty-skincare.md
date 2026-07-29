# Playbook — Beauty & Skincare (`beauty_skincare`)

> Commerce vertical. Pair with `product_ad` (optional `problem_solution` for skin concerns).

## One-line formula

**Hook (skin moment / result tease) → Pitch (texture + benefit + proof) → CTA (try / shop / shade).**

## Hook type menu (pick 1)

| Hook type | Pattern | Example angle |
|-----------|---------|---------------|
| `curiosity_question` | Ask a skin/makeup question | “Still patchy by noon?” |
| `pain_warning` | Name a frustration fast | “Maskne after long meetings” |
| `before_after_tease` | Hint transformation (no fake clinical %) | Dry → dewy look in routine |
| `texture_asmr` | Sensory first (swipe, glow, pour) | Glass-skin close-up |
| `ugc_confession` | Personal “I switched because…” | “I stopped buying 5 serums” |

## Sell-point order (Pitch)

Prefer this order (skip missing ones; **do not invent**):

1. **Scenario** — morning routine / makeup base / travel
2. **Target audience** — oily / dry / busy / first-time makeup
3. **Benefit** — look/feel outcome in plain language
4. **Feature** — texture, key ingredients (only if in brief)
5. **Proof** — UGC-style reaction, before/after look (no unverified clinical %)
6. **Experience** — how it feels on skin
7. **Offer** — only if user provided discount / bundle

## CTA examples

- Soft: “Try it in your next AM routine”
- Direct: “Shop the shade that matches you”
- Offer-backed: “Grab the set while it’s listed” (only if real offer in brief)

## Recommended video forms

| Form | When | Audio hint |
|------|------|------------|
| `product_demo` | Texture / application hero | VO or soft BGM |
| `ugc_testimonial` | Trust / “switched to…” | VO |
| `scenario_story` | Routine-in-context | VO + light BGM |
| `effectiveness_show` | Visible look change | VO (objective tone) |

Default for URL→video: `product_demo` + Hook→Pitch→CTA.

## Beat hints (30s)

| Beat | Role |
|------|------|
| `hook` 0–3s | Face/skin moment or product texture hit |
| `hero_product` | Pack + product readable |
| `pitch` | 2–3 sell points in order above |
| `cta` | Pack + soft CTA card |

## Forbidden

- Invented clinical claims, “cures acne”, medical advice
- Fake “dermatologist recommended” / lab % without brief source
- Shame-based body/skin language
- Opening with “In this video I will review…”

## `brief.narrative` inject example

```json
{
  "beats": ["hook", "hero_product", "pitch", "cta"],
  "hook_type": "texture_asmr",
  "sellpoint_order": ["scenario", "benefit", "feature", "experience"],
  "cta_style": "soft_routine",
  "video_form": "product_demo",
  "constraints": ["No invented clinical claims", "Show real product pack from refs"],
  "scene_types_hint": ["texture_closeup", "hero_product", "routine_lifestyle", "cta_card"]
}
```
