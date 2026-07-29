---
name: trend-viral-short
description: Use when trend hooks or batch TikTok IMAGE A/B; NOT URL film
metadata:
  layer: L2-vertical
  requires: [creative-task-runner, creative-platform, creative-gpt-image2-prompt, creative-seedance2-prompt, creative-batch-orchestrator, creative-script2film, creative-script2film-keyframes, creative-direct]
  tags: [trend, batch, ecommerce, image]
  hermes:
    related_skills: [creative-batch-orchestrator, product-url-to-video, viral-ad-rewrite]
---

# Trend Viral Short

Ride trends; produce **actionable creative directions**, then batch vertical **image** variants (or route to video when asked).

> **Prompt gate**: Load **creative-gpt-image2-prompt** — craft **one distinct prompt per variant**. For video paths, load **creative-seedance2-prompt** before video MCP.  
> **Submit path**: ≥2 images → **creative-batch-orchestrator** as N× `creative-direct-image`. **Do not** reuse one prompt with a count.  
> **After batch (≥5)**: always run orchestrator **heuristic scorecard**.

## Product principles

1. Trends suggestions must be **executable** (2–3 directions that can generate).
2. **No fake performance data** — no “你的素材已严重疲劳” without account metrics.
3. Confirm direction before burning credits on a batch.
4. User asks for **video** → do **not** silently stay on image-only batch.

## When to use

- “最近什么趋势适合我们这款” / “素材疲了帮我换方向” / trend chasing
- Same product, multiple opening-hook tests (**image** variants)
- MCN daily drops with trend tags

## When not to use

- Product URL → full multi-shot film → **product-url-to-video**
- Borrow a specific reference ad’s structure → **viral-ad-rewrite**

---

## Flow overview

```
0. Trend advice (situation → reasons → 2–3 directions)  ← NEW required front step
1. User picks a direction (or edits)
2. Route: batch images (default) OR video skill
3. Confirm-before-generate → batch / submit
4. Deliver + scorecard (if ≥5 image variants)
```

---

## 0. Trend advice (required front step)

No external hot-list MCP this week. Ground on: **user trend words** + category common sense + optional known tag names the user provides. Label source honestly (“基于你提供的趋势词 + 品类常识，非实时热榜”).

### 0.1 Collect minimum info

Ask only what’s missing:

| Field | Required? | Notes |
|-------|-----------|-------|
| `category` / product | Yes | SKU or category |
| `market` | Yes if unknown | US / UK / SEA / CN … |
| `in_flight` | Nice | Currently advertising? yes / no / unknown |
| `past_winner_clue` | Optional | Any past hook that worked (qualitative) |
| `trend_tags` | Optional | User-supplied trend words / sounds / formats |

### 0.2 Situation label (qualitative only)

Pick one — **never** claim measured fatigue without data:

| Situation | When to use | Tone |
|-----------|-------------|------|
| `new_advertiser` | Not yet running / just starting | Explore 2–3 distinct hooks |
| `active_possible_fatigue` | In-flight + user *feels* creative tired | Suggest refresh directions; **no** “已严重疲劳” absolute |
| `silent_restart` | Was live, paused, coming back | Re-entry angles + trend tie-in |
| `unknown` | Missing signals | Stay modest; ask one clarifying Q |

### 0.3 Three-part output (fixed shape)

```markdown
## 趋势建议（非实时热榜）

### 1. 处境判断
- Label: <new_advertiser | active_possible_fatigue | silent_restart | unknown>
- 依据：…（诚实；无投放数据则写明）

### 2. 推荐理由
- 为何这些方向贴合品类 / 用户趋势词：…

### 3. 可执行方向（2–3 条）
| # | 方向名 | 钩子 | 场景 | 跟趋势的关系 | 默认产物 |
|---|--------|------|------|--------------|----------|
| 1 | … | … | … | … | 钩子图批量 / 短视频 |
| 2 | … | … | … | … | … |
| 3 | … | … | … | … | … |

请选择方向编号，或告诉我要改的点。选好后我再生成。
```

Each direction must be generatable (hook + scene clear enough for prompts).

### 0.4 Forbidden phrases (no data)

- “你的素材已严重疲劳 / CTR 暴跌 / ROAS 崩了”
- Fake rankings (“今日 TikTok 热榜第 3”)
- Absolute fatigue scores

OK: “如果你在投且感觉重复，可以优先测差异更大的方向 #2”

---

## 1. After user picks a direction — route table

| User intent | Skill / path | MCP |
|-------------|--------------|-----|
| Default / “出几张钩子图” / A/B stills | This skill → **creative-batch-orchestrator** | N× `direct_image` |
| Explicit **video** / 短视频 / 成片 | **creative-script2film** (product ref) or **creative-direct** (≤15s) | `creative_submit_script2film` / `creative_generate_video` … |
| Multi-shot + transitions | **creative-script2film-keyframes** | `creative_submit_script2film_keyframes` |
| Borrow a concrete reference ad | **viral-ad-rewrite** | (handoff) |

**Hard rule:** If user clearly wants video, **do not** submit a pure image batch.

Confirm intent + N (default **5**, cap **10**) + aspect `9:16` before submit.

---

## 2. Image variant flow (default)

1. Brief from chosen direction: `product`, `trend_tags`, `hook_idea`
2. Decide `N` (default 5, hard cap 10)
3. **Load creative-gpt-image2-prompt** — **N distinct** prompts (different hooks/scenes; not “variant 1/2/3” suffixes)
4. Hand off to **creative-batch-orchestrator**:

```yaml
batch_label: "Trend hooks — <product> — <direction>"
items:
  - label: "Hook A — <scene>"
    skill: creative-direct-image
    input:
      prompt: "<prompt from gpt-image2 skill>"
      aspect_ratio: "9:16"
      reference_urls: ["https://..."]
  # … up to N
```

5. Batch submits via `creative_submit_generate` (`type=image`) → task-runner tracking
6. Deliver table by label → **heuristic scorecard** (orchestrator `references/heuristic-scorecard.md`) when N≥5 (also OK to show for N≥2 if useful; **required** for ≥5)

## Preset constraints (trend_viral_v1)

- Strong hook in first 3 seconds (visual)
- Product close-up ≤ 40% of frame
- No infringing trends, sensitive content

## Technique injection

When orchestrating, read preset file: `presets/trend_viral_v1.json` (if present).
