# Commerce industry playbooks — index

Load **after** choosing a narrative structure (usually `product_ad` ± `problem_solution`). Inject industry hooks / sell-point order / CTA into `brief.narrative` — do **not** replace the beat map.

## Supported industries (this week)

| `industry` id | Signals (EN / ZH examples) | Reference |
|---------------|----------------------------|-----------|
| `beauty_skincare` | skincare, makeup, serum, moisturizer, lipstick, 美妆, 护肤, 面膜 | `playbooks/beauty-skincare.md` |
| `fashion_accessories` | apparel, dress, sneakers, jewelry, bag, 服饰, 穿搭, 鞋包, 配件 | `playbooks/fashion-accessories.md` |
| `food_beverage` | snack, drink, coffee, supplement food, 零食, 饮料, 食品 | `playbooks/food-beverage.md` |
| `unknown` | unclear / multi-category / non-commerce | Do **not** invent niche jargon — see Low confidence |

## Resolve `industry`

Priority:

1. User states category (“这是美妆”, “fashion brand”)
2. Product title / description / URL path keywords
3. Hero image obvious category (cosmetic bottle, apparel on hanger, food pack) — medium confidence only
4. Else → `unknown`

Set `brief.industry` and optionally `brief.industry_confidence`: `high` | `medium` | `low`.

## Low confidence

When `unknown` or `low`:

- Ask one short question: “这更偏美妆 / 服饰 / 食品，还是其他？”
- Or offer **two structure options** (e.g. demo-led `product_ad` vs pain-hook `problem_solution`) **without** fake industry-specific claims
- Never invent medical claims, “dermatologist-approved”, or niche sub-vertical scripts you cannot ground

## Inject into `brief.narrative`

After Reading the playbook file, merge:

```json
{
  "beats": ["hook", "pitch", "cta"],
  "hook_type": "<from playbook menu>",
  "sellpoint_order": ["scenario", "benefit", "feature", "proof"],
  "cta_style": "<from playbook>",
  "video_form": "<demo|ugc_testimonial|scenario_story|...>",
  "constraints": ["No invented clinical claims", "...playbook forbidden..."],
  "scene_types_hint": ["..."]
}
```

Script shape for commerce: **Hook → Pitch (sell points in order) → CTA**.
