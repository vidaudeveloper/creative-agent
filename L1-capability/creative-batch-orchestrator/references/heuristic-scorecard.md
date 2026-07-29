# Heuristic creative scorecard

Dialogue-only report after a batch finishes. **Not** real ads performance. No account pause/write.

## When required

| Condition | Action |
|-----------|--------|
| ≥5 successful variants in one batch | **Must** output scorecard after result table |
| trend-viral-short / product-url-to-video hook batches | Default on when N≥5 |
| User asks “哪个优先测” | Output even if N<5 |
| User asks to pause/stop low performers | Refuse write; explain read-only |

## Dimensions (fixed customer wording)

Score each successful item **1–5** qualitatively from the creative (prompt + visible artifact), then rank:

| Dimension (对客) | Look for |
|------------------|----------|
| 钩子强度 Hook strength | First-glance stop power; clear opening idea |
| 产品识别度 Product recognition | Can you tell the SKU/pack quickly? |
| 信息清晰度 Message clarity | Benefit readable without clutter |
| 变体差异度 Variant diversity | Distinct vs siblings (penalize near-duplicates) |
| 合规风险提示 Risk note (light) | Obvious sensitive/misleading risk — **not** full policy lint |

Do **not** invent CTR, CPA, ROAS, or letter grades tied to spend.

## Output template

```markdown
## 创意评分卡（启发式 · 非投放效果）

> 依据开头冲击力、产品露出、文案/信息清晰度、变体差异度等**创意启发式**排序，**不是**账户真实投放数据。

### 优先测（Top N）
| 排名 | label | 综合启发 | 一句话理由 |
|------|-------|----------|------------|
| 1 | … | 高 | … |
| 2 | … | 高 | … |

### 观察中档
| label | 综合启发 | 一句话理由 |
|-------|----------|------------|
| … | 中 | … |

### 建议重做或延后
| label | 原因 |
|-------|------|
| … | 差异度不足 / 产品难识别 / … |

### 下一步
- 建议先拿 Top 1–2 去测；中档可备轮换
- 若要停投放侧计划，请到投放工具操作 —— **本能力只建议、不代操作**
```

## Forbidden claims

- “A 级素材 ROAS 更高”
- “按 CPA 自动暂停”
- Fake account benchmarks or fatigue percentages

## Optional rehearsal

If user wants to see the report shape without a real batch, show the template filled with clearly labeled **示例** rows and state no jobs were run.
