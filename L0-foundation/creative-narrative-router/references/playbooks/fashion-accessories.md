# Playbook — Fashion & Accessories (`fashion_accessories`)

> Commerce vertical. Pair with `product_ad` (optional `mood_film` secondary for aesthetic-led).

## One-line formula

**Hook (outfit problem / fit flex) → Pitch (look + fabric/fit + occasion) → CTA (size / shop the look).**

## Hook type menu (pick 1)

| Hook type | Pattern | Example angle |
|-----------|---------|---------------|
| `curiosity_question` | Style dilemma | “One bag for work and weekend?” |
| `pain_warning` | Fit / comfort pain | “Blisters by lunch?” |
| `outfit_transform` | Before plain → styled | Same tee, new jacket |
| `detail_flex` | Hardware / stitch / sole close-up | Metal clasp macro |
| `personal_story` | “I wore this to…” | Wedding guest / commute |

## Sell-point order (Pitch)

1. **Scenario** — work / date / travel / season
2. **Target audience** — size range, gender-neutral if true, lifestyle
3. **Benefit** — confidence, comfort, versatility
4. **Feature** — material, fit cut, waterproof, weight (from brief only)
5. **Experience** — try-on / movement / pocket test
6. **Proof** — styling shots, real-model fit (no fake celebrity)
7. **Offer** — only if user provided

## CTA examples

- “Shop the look — sizes listed on page”
- “Add to cart in your usual size”
- “Complete the set with …” (only if SKU exists in brief)

## Recommended video forms

| Form | When | Audio hint |
|------|------|------------|
| `lookbook_demo` | Silhouette / colorways | BGM or light VO |
| `try_on_ugc` | Fit / comfort | VO |
| `scenario_story` | Occasion-led | VO + BGM |
| `detail_showcase` | Craft / hardware hero | ASMR / BGM |

Default for URL→video: `lookbook_demo` or `try_on_ugc` if apparel on body; still-life product → `detail_showcase`.

## Beat hints (30s)

| Beat | Role |
|------|------|
| `hook` 0–3s | Outfit problem or detail flex |
| `hero_product` | Full garment / accessory readable |
| `pitch` | Occasion + fit/material + benefit |
| `cta` | Packshot / soft shop CTA |

## Forbidden

- Body-shaming or unrealistic size claims
- Invented fabric tech / “celebrity worn”
- Ignoring provided colorway / SKU refs
- “In this haul…” cold open without hook

## `brief.narrative` inject example

```json
{
  "beats": ["hook", "hero_product", "pitch", "cta"],
  "hook_type": "outfit_transform",
  "sellpoint_order": ["scenario", "benefit", "feature", "experience"],
  "cta_style": "shop_the_look",
  "video_form": "lookbook_demo",
  "constraints": ["Match reference colorway", "No body-shaming"],
  "scene_types_hint": ["detail_closeup", "full_look", "lifestyle_occasion", "cta_card"]
}
```
