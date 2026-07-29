# Playbook — Food & Beverage (`food_beverage`)

> Commerce vertical. Pair with `product_ad` (optional `problem_solution` for craving / convenience pain).

## One-line formula

**Hook (craving / pour / bite) → Pitch (taste + occasion + ingredient honesty) → CTA (try / stock up).**

## Hook type menu (pick 1)

| Hook type | Pattern | Example angle |
|-----------|---------|---------------|
| `curiosity_question` | Taste or ritual question | “Cold brew that isn’t bitter?” |
| `craving_hit` | Steam / pour / crunch in 1s | First sip condensation |
| `pain_warning` | Afternoon crash / boring snack | “3pm desk hunger again” |
| `ingredient_reveal` | Honest ingredient spotlight | Real fruit visible |
| `sharing_moment` | Party / family table | Pass-the-bowl UGC |

## Sell-point order (Pitch)

1. **Scenario** — breakfast / desk / gym / movie night
2. **Target audience** — busy pros, parents, flavor seekers
3. **Benefit** — taste, energy, convenience, shareability
4. **Feature** — ingredients, size, caffeine, dietary flags **only if in brief**
5. **Experience** — texture, aroma, ritual
6. **Proof** — reaction bite/sip (no fake lab health claims)
7. **Offer** — multipack / promo only if provided

## CTA examples

- “Try the flavor that fits your afternoon”
- “Stock the pantry — link in bio / shop now”
- “Grab the variety pack” (only if real SKU)

## Recommended video forms

| Form | When | Audio hint |
|------|------|------------|
| `product_demo` | Pour / unbox / prep | BGM or ASMR |
| `scenario_story` | Occasion + lifestyle | VO |
| `ugc_reaction` | First sip / crunch | VO / reaction |
| `ingredient_story` | Clean-label angle | VO |

Default for URL→video: `product_demo` (appetite visuals) + Hook→Pitch→CTA.

## Beat hints (30s)

| Beat | Role |
|------|------|
| `hook` 0–3s | Appetite visual or craving line |
| `hero_product` | Pack + product readable |
| `pitch` | Taste + occasion + 1–2 honest features |
| `cta` | Pack + soft shop CTA |

## Forbidden

- Unverified health / medical / weight-loss claims
- Fake “doctor recommended” / invented nutrition facts
- Misleading “organic / sugar-free” if not in brief
- Gross-out humor that hides the product

## `brief.narrative` inject example

```json
{
  "beats": ["hook", "hero_product", "pitch", "cta"],
  "hook_type": "craving_hit",
  "sellpoint_order": ["scenario", "benefit", "experience", "feature"],
  "cta_style": "try_flavor",
  "video_form": "product_demo",
  "constraints": ["No invented health claims", "Show pack from refs"],
  "scene_types_hint": ["pour_closeup", "hero_pack", "lifestyle_occasion", "cta_card"]
}
```
