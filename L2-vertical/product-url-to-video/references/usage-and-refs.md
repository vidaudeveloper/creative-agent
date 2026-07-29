# Correct usage + multi-image references

Hard requirement for **product-url-to-video**: selling points alone are not enough. The video must show the product **used the way the page describes**, grounded in **multiple page images** — not only the hero packshot.

## 1. Deep-read the page (do not stop at og:meta)

After a thin `web_extract` / OG parse, **continue reading**:

| Source on page | What to pull |
|----------------|--------------|
| How to use / Directions / Application / 使用方法 / 用法用量 | Ordered **usage steps** |
| FAQ / Ingredients / Specs tabs | Constraints (amount, frequency, wet/dry, left-on vs rinse) |
| A+ / detail HTML below fold | Extra steps, warnings, demo captions |
| Image gallery + alt / captions | Which frame is pack vs in-hand vs step demo |
| Review photos (if public) | Optional real-use cues — **never invent** medical claims |

Prefer full markdown from `web_extract`, then `browser` scroll for accordion tabs (“How to use”, “Directions”). Do **not** treat the first 500 chars of description as complete.

### `usage` object (required when page has any how-to)

```yaml
usage:
  summary: "1–2 sentences of correct use"
  steps:           # ordered, 2–8 steps, grounded in page text only
    - "…"
  frequency: "…"   # if stated
  amount_or_dose: "…"  # if stated
  constraints:     # wet hair / clean face / shake well / not for X
    - "…"
  source_quote: "short quote or section title from page proving steps"
  confidence: high | medium | low
```

If the page has **no** how-to:

- Set `usage.confidence: low` and `usage.steps: []`
- In confirm card: ask user for 2–4 correct steps, **or** mark demo shots as “pack / lifestyle only — no invented application”
- **Forbidden**: inventing massage / swallow / inject / apply-to-eye rituals not on the page

### Usage → script / shot binding (hard)

When writing the Final Video Spec / script2film scenes:

1. At least **one mid-video demo beat** must follow `usage.steps` order (or state “no demo — pack only” if low confidence).
2. Do **not** show contradictory use (e.g. drinking a topical serum, rubbing a drink on skin, wearing a food item).
3. Put `usage.steps` into `brief.product_usage` and mention them in `brief.narrative.constraints`.

---

## 2. Multi-image gallery (never hero-only)

**Forbidden default**: only `og:image` / first gallery tile as the sole reference for the whole film.

Collect up to **8** URLs, then pick **4–6** for generation, covering roles:

| Role | Purpose | Typical page signal |
|------|---------|---------------------|
| `hero_pack` | SKU identity, color, logo | Main PDP image |
| `angle_detail` | Shape / texture / nozzle / fabric | Gallery 2–3, zoom |
| `in_context` | Size in hand / on shelf / worn | Lifestyle tile |
| `usage_demo` | Correct application / pour / wear | “How to” images, step graphics |
| `before_after` | Only if page shows real B/A | Labeled gallery |

Rules:

1. Always include ≥1 `hero_pack` **and** try ≥1 `usage_demo` or `in_context` when available.
2. If gallery is pack-only, say so in confirm card and ask user to upload a use-demo photo when possible.
3. Pass **diverse** `reference_image_urls` into script2film (not 3 crops of the same hero).
4. In prompts / Narrative Driver: map shots to roles — e.g. open on pack (`hero_pack`), demo follows `usage.steps` with `usage_demo` refs, close on pack CTA.

### `product_images` enriched shape

```yaml
product_images:
  - url: "https://…"
    role: hero_pack | angle_detail | in_context | usage_demo | before_after | other
    note: "optional caption from alt"
```

Submit MCP with 3–6 URLs mixing roles; put the role list into `brief.reference_image_roles` so later shots stay consistent.
