---
name: product-url-to-video
description: Use when user pastes product page URL to make ad video
metadata:
  layer: L2-vertical
  requires: [creative-task-runner, creative-platform, creative-seedance2-prompt, creative-gpt-image2-prompt, creative-narrative-router, creative-script2film, creative-script2film-keyframes]
  tags: [ecommerce, product, url, scrape, script2film, bgm, one-click]
  hermes:
    related_skills: [trend-viral-short, viral-ad-rewrite, handheld-product-avatar, creative-batch-orchestrator]
---

# Product URL → Video

Enable when the user pastes a **product page URL**. Scrape product info with Agent web tools, then call **vidau-creative** MCP to generate ad assets.

> **Prompt gate**: Before any image MCP → **creative-gpt-image2-prompt**. Before any video MCP or script visual enrichment → **creative-seedance2-prompt**.

> **Applies to**: Shopify DTC, Amazon, TikTok Shop, Temu, any reachable product page.  
> **Not for**: social profile pages, cloud drives, YouTube/Bilibili video links, collection/category pages — **reject and guide** (see Gate order).

## Product principles (hard)

1. **Confirm-before-generate** — never burn credits until the user confirms the creative summary (or chooses analyze-only).
2. **Gate order** — URL check → market/locale → scrape → confirm → estimate → submit.
3. **Default narrative** — Hook → Pitch → CTA (via **creative-narrative-router** + commerce playbook when industry is known).
4. **Delivery = video + asset pack** — not a bare download link.
5. **Correct usage from the page** — deep-read PDP for how-to / directions; demo shots must follow page steps — **never invent** application rituals. See `references/usage-and-refs.md`.
6. **Multi-image refs, not hero-only** — collect gallery roles (pack / detail / in-context / usage_demo); do **not** generate the whole film from `og:image` alone.

## Video skill selection (L2 required reading)

Before submitting final render, pick **L1 video skill** from user intent:

| User intent / scenario | Load skill | MCP entry |
|------------------------|------------|-----------|
| Product short; hero must match main image (**default**) | **creative-script2film** | `creative_submit_script2film` |
| Emphasis on shot transitions, camera motion, cinematic feel | **creative-script2film-keyframes** | `creative_submit_script2film_keyframes` |
| Single 5–15s demo clip only, no multi-shot | **creative-direct** | `creative_image_to_video` or `creative_first_frame_to_video` |
| Handheld talking-head / 口播数字人 + product in hand | **handheld-product-avatar** | `creative_generate_tts` + lipsync path |
| A/B test multiple hook **images** | **trend-viral-short** → **creative-batch-orchestrator** | N× `direct_image` + scorecard |

**Decision shorthand**:
- Has product hero, must "look like this SKU" → **reference** (creative-script2film)
- Wants "smooth transitions / story camera" → **keyframes** (creative-script2film-keyframes)
- If unspecified, e-commerce default → **creative-script2film**

## When to trigger

Message contains `https://` and looks like a product page (`product`, `/p/`, `/dp/`, `shop`, `store`, etc.) or user says "this link's product" / "帮我做个 TT 广告".

## Flow overview

```
0. Gate: product-URL? → market/locale?
1. Deep-scrape: sell points + USAGE steps + multi-role gallery (not og:image only)
2. Show confirm summary (sell points + usage + refs + 3 hooks) — wait for user
2b. Analyze-only? → stop (no MCP generate)
3. Narrative router + commerce playbook → script with usage-bound demo beats
4. Estimate credits + submit (diverse reference_image_urls)
5. creative-task-runner — notify + background ETA/20s poll → end turn
6. Deliver video + asset pack (+ scorecard if batch hooks)
```

> **Read** `references/usage-and-refs.md` before scrape and before writing the script.

---

## 0. Gate order (fail-fast)

Run **before** scrape. Stop at first failure.

### 0.1 Product-page URL check

**Accept** (examples): Shopify product paths, Amazon `/dp/` or `/gp/product/`, TikTok Shop / Temu product pages, any page with clear single-SKU product signals.

**Reject immediately** (do **not** enter long scrape/generate flow):

| Reject type | Examples | Reply guidance |
|-------------|----------|----------------|
| Social / profile | Instagram/TikTok/X home, creator profiles | Ask for a **product page** URL or upload hero + name |
| Video / watch | YouTube, Bilibili, Douyin video links | Wrong skill for “paste video”; for structure rewrite → **viral-ad-rewrite** |
| Collection / category / search | `/collections/`, `/category/`, search result pages | Ask for a **single product** deep link |
| Drive / file share | Google Drive, Dropbox, raw file hosts | Ask user to upload images + paste name/sell points |

Rejection message must be explicit (match user language), e.g. ZH:「这不是商品详情页，请换一条带价格/加购的商品链接，或直接上传主图和卖点。」

### 0.2 Market / language

If user did **not** specify:

| Field | Default ask | Notes |
|-------|-------------|-------|
| `market` | e.g. US / UK / SEA / CN | Needed for CTA tone & currency display |
| `locale` / language | Match chat language if clear; else ask | Script + VO language |

**Do not scrape for generation** until market + language are known (or user says “use defaults: US + English” / 「默认美国英文」).

Analyze-only may still scrape after URL gate, but still ask market/locale when missing so hooks stay market-aware.

---

## 1. Scrape product info (deep-read)

**Goal**: sell points **and** correct **usage**, plus a **role-tagged image gallery**. Stopping at `og:title` + `og:image` is a hard fail for this skill.

Try tools in order; you may **combine** A+B+D until usage + multi-image are filled (do not “stop at first success” if usage/gallery are still empty).

### A. `web_extract` (preferred first pass)

```
web_extract(urls=["<product URL>"], format="markdown")
```

Extract from the **full** markdown, not only the fold:

- Identity: `product_name`, `brand`, `price`, description
- **Usage**: sections titled How to use / Directions / Application / 使用方法 / 用法 / 食用方法 / 穿戴说明 — → ordered `usage.steps`
- **Gallery**: all product image URLs in the page (not only first / og:image); keep alts/captions

### B. `execute_code` (structured + gallery)

When extract is thin. Prefer **JSON-LD** (`@type: Product` → `image` array), **Open Graph**, then HTML gallery / `srcset`:

```python
import urllib.request, json, re

url = "<product URL>"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")

# JSON-LD Product — name, description, image[] (all URLs)
# Open Graph — og:title, og:image (hero only; NOT sufficient alone)
# Regex gallery: product__media, data-zoom, srcset high-res candidates
# Text usage blocks: How to use|Directions|Application|使用方法|用法用量
```

### C. `terminal` + curl (light fallback)

Only if A/B fail body fetch:

```
curl -sL -A "Mozilla/5.0" "<URL>" | head -c 400000
```

Prefer **400KB+** so below-fold how-to HTML is included; then parse with `execute_code`.

### D. `browser` (required when usage is behind tabs)

Open the PDP, expand **How to use / Directions / FAQ** accordions, scroll A+ content, capture:

- Visible usage steps text
- Extra gallery tiles not in initial HTML

JS-heavy Shopify/Amazon pages often hide usage until click — **do this before** inventing demo shots.

### Required scrape fields

| Field | Meaning |
|-------|---------|
| `product_name` | Product title |
| `product_description` | Raw description (keep enough for claims; ~800–1500 chars OK) |
| `product_images` | **Role-tagged** list (max 8) — see below; **not** hero-only |
| `price` / `brand` | Optional |
| `selling_points` | **3–5** bullets from page facts |
| `usage` | **Required object** — summary + ordered steps + constraints + confidence (see `usage-and-refs.md`) |
| `hook_directions` | **3** distinct hook angles |

### Image roles (mandatory tagging)

Each image: `{ url, role, note? }` with `role` ∈ `hero_pack` | `angle_detail` | `in_context` | `usage_demo` | `before_after` | `other`.

| Minimum bar | Rule |
|-------------|------|
| ≥1 `hero_pack` | Always |
| ≥1 non-hero | `angle_detail` / `in_context` / `usage_demo` when gallery allows |
| Prefer `usage_demo` | When page shows application / pour / wear / eat steps visually |
| Generation set | Pass **3–6 diverse** URLs into MCP — **forbid** 1× og:image only |

### Scrape failure (degrade, do not abandon)

Tell user clearly what is missing. Offer **manual path**:

1. Upload **2–4** images (pack + detail + use-demo if possible)
2. Paste product name + 3–5 sell points + **correct usage steps** (2–4 lines)

Then continue at **§2 Confirm**. Do not force MCP submit.

---

## 2. Confirm with user (Confirm-before-generate)

After scrape (or manual fill), **show this summary and wait**. Do **not** call estimate/submit until the user confirms or edits.

### Confirm card (required fields)

```markdown
## Creative summary — please confirm

- **Product**: <name> · <brand>
- **Price**: <price or "n/a">
- **Market / language**: <market> / <locale>
- **Selling points** (edit freely):
  1. …
  2. …
  3. … (3–5)
- **Correct usage** (from page — edit if wrong; do not skip):
  - Summary: …
  - Steps:
    1. …
    2. …
  - Constraints: …
  - Confidence: high | medium | low
- **Reference images by role** (not hero-only):
  | role | preview |
  | hero_pack | ![](…) |
  | angle_detail | ![](…) |
  | in_context / usage_demo | ![](…) |
- **Hook directions** (pick or edit; default #1 for first render):
  1. …
  2. …
  3. …
- **Audience (one line)**: <inferred; editable>
```

Ask user:

1. **Mode**: `full video` (default) / **`analyze only`** / batch hook images / single ad image
2. **Aspect ratio**: default `9:16`
3. **Duration**: default 30s (script2film)
4. **Usage OK?** — if confidence low, ask user to correct steps before any demo shot
5. **Refs OK?** — confirm multi-role set; allow user to add a use-demo upload
6. Confirm or edit sell points / hooks / usage

If user only pasted URL + said “做广告”, after confirm defaults → **script2film 30s vertical**.

If user wants **handheld talking-head / 口播数字人** → load **handheld-product-avatar** (still pass usage steps into VO).

### Analyze-only branch

Triggers: “只分析”, “先别做视频”, “analyze only”, “hooks only”.

- Deliver sell points + **usage steps** + 3 hooks + audience line + image-role list
- **Stop**. No `creative_estimate` / no submit / no credit burn
- Offer: “确认后我可以按钩子 #N + 正确用法演示出片”

---

## 3. Generate script (after confirm)

1. Load **creative-narrative-router** (required)
2. Resolve commerce industry playbook when possible (`beauty_skincare` / `fashion_accessories` / `food_beverage`) — see router `references/commerce-playbook-index.md`
3. E-commerce default structure: **`product_ad`** (+ optional `problem_solution`); beats = **Hook → Pitch → CTA**
4. Inject chosen hook + sell-point order into `brief.narrative`
5. **Bind usage into the script** (hard):
   - Put confirmed `usage.steps` into `brief.product_usage`
   - At least one **demo / application** beat must follow those steps in order
   - Add constraints: `Follow product_usage steps exactly; no invented application`
   - If `usage.confidence: low` and user did not supply steps → pack/lifestyle only; **no fake how-to**
6. Call **`creative_generate_script`** with `creative_request` that mentions correct use (or write Final Video Spec with labeled demo shots)

Script language = `brief.locale` / user language.

Show script / Final Video Spec briefly — call out which shots are **usage demos** vs pack — revise **before** estimate+submit.

---

## 4. MCP submit

### Preflight (required)

1. User confirmed §2 (and script if shown)
2. `creative_estimate` for selected workflow
3. Show credit/ETA once; proceed on confirm (or if user already said “确认出片” in §2)

### Default: script2film deliverable (reference)

**`reference_image_urls`**: 3–6 URLs mixing roles (`hero_pack` + `angle_detail` / `in_context` / `usage_demo`). **Reject** submit prep if only a single hero URL is available and user did not confirm “pack-only OK”.

```
creative_submit_script2film:
  script: "<script from step 3 — includes usage-bound demo beats>"
  reference_image_urls: ["<hero_pack>", "<angle_or_detail>", "<usage_demo_or_context>", ...]
  brief:
    product: "<product_name>"
    product_description: "<selling points>"
    product_usage:
      summary: "<usage.summary>"
      steps: ["...", "..."]
      constraints: ["..."]
    product_url: "<original URL>"
    reference_image_urls: ["<same diverse set>"]
    reference_image_roles: ["hero_pack", "angle_detail", "usage_demo"]
    audience: "<audience one-liner>"
    locale: "<locale>"
    market: "<market>"
    narrative_structure: "product_ad"
    industry: "<beauty_skincare|fashion_accessories|food_beverage|unknown>"
    selected_hook: "<hook text>"
    narrative:
      constraints: ["Follow product_usage steps exactly", "No invented application"]
  aspect_ratio: "9:16"
  target_duration_sec: 30
  client_request_id: "<uuid>"
```

**Reference usage**: keyframe + video both use **reference** mode; demo shots should lean on `usage_demo` / `in_context` refs, pack lock on `hero_pack`.

### Alt: keyframes script2film

```
creative_submit_script2film_keyframes:
  script: "<script from step 3>"
  reference_image_urls: ["<hero_pack>", "<detail_or_usage>", ...]   # still multi-ref
  video_mode: "first_last_frame"
  aspect_ratio: "9:16"
  target_duration_sec: 30
  client_request_id: "<uuid>"
```

### Alt: batch hook variants

User wants A/B hook tests → **trend-viral-short** → **creative-batch-orchestrator**:

1. Use the 3 confirmed hooks (expand to N distinct prompts via **creative-gpt-image2-prompt**)
2. Submit N× `direct_image` with **shared multi-role** `reference_urls` (not hero alone); prompts that show use must follow `usage.steps`
3. On batch complete → **heuristic scorecard** (orchestrator reference)

### Alt: single image / single video

Use **creative-direct**:

- Image: `creative_submit_generate` type=image + multi `reference_urls` when available
- Reference video: `creative_image_to_video` + same diverse refs; prompt must not invent usage

---

## 5. Job tracking

Load **creative-task-runner** immediately after submit:

- Send `tracking.user_message`; arm background ETA → 20s poll; **end foreground turn**
- On background wake with `completed` → save to conversation **产物** + deliver (§6)
- User may ask mid-wait; answer once; keep the background schedule

---

## 6. Delivery — video + asset pack (required)

After successful video (or single clip), deliver **both**:

1. **Video** — download URL + duration/aspect
2. **Asset pack** (short, always):

```markdown
### Asset pack
- **Hook used**: …
- **Audience**: …
- **Usage shown**: <1-line summary of steps used in demo>
- **Length / ratio**: 30s · 9:16
- **Refs used**: hero_pack + … (roles)
- **Suggested A/B next hooks** (1–2, not used yet): …
- **How to test**: e.g. run Hook A vs Hook B for 24–48h; refresh if CTR/hooks fatigue (qualitative — no ROAS claims)
```

Do **not** promise TikTok Ads library sync or auto-posting.

If batch hook images (≥5) → also load **creative-batch-orchestrator** scorecard section.

---

## Notes

- **Image URLs**: scraped external URLs may go into `reference_urls`; if MCP download fails, ask user to upload **pack + use-demo** and retry.
- **Usage fidelity**: if the finished video invents wrong use, treat as content bug — regenerate after fixing `product_usage` / refs, do not “style away” the error.
- **Compliance**: respect target site robots.txt; don't brute-force repeated scrapes on failure.
- **Major platforms**: Amazon/TikTok Shop — use `browser` for how-to tabs; do not stop at OG tags.
- **Multiple URLs**: max **3** product links per turn; scrape and confirm separately.
- **Do not** call vidau-creative MCP during scrape; scrape = Agent local tools only, generation = MCP.
- **Do not** claim real ad performance or sync to ad accounts from this skill.
