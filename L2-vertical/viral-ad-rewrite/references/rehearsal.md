# No-cost rehearsal

Walk the **same UI structure** as the real path without calling any paid generation MCP (`creative_submit_*`, `creative_generate_*` for video/image that burns credits).

## When to use

- User chooses 彩排 / rehearsal / “先走一遍看看”
- First-time users unsure about confirm gates

## Script (match user language)

1. **Opening** — dual roles + “本段为零成本彩排，不会扣积分”
2. **Example inputs** — describe a built-in style example (e.g. texture drink pour template + generic serum bottle product). No need for real files if user has none.
3. **Compact brief** — use the same sections as `brief-template.md` with example borrow/forbid lists (≥3 each)
4. **Offer** — 查看详细分析 / 改方向 / （彩排）查看示例结果
5. **Example result** — narrate what a finished clip would show; optional placeholder thumbnail URL only if already public; **do not** submit Seedance/script2film
6. **Handoff** — “要用你的参考片和商品图正式跑，回复「正式分析」”

## Parity rules

| Must match real path | May differ |
|----------------------|------------|
| Brief sections & confirm/edit options | Cost/provider wording (“示例 / 不扣分”) |
| ≥3 borrow + ≥3 forbid | Artifact is illustrative, not a real render |
| Forbidden: generate MCP | — |

## Forbidden in rehearsal

- `creative_estimate` framed as a real charge (optional educational “正式大约会估 X 分” is OK if clearly hypothetical)
- `creative_submit_script2film` / `creative_submit_generate` / image or video generate tools
- Claiming the example video is the user’s finished ad
