# Hermes Skill 命中率优化

## Hermes 实际怎么选 Skill

1. **系统提示索引（主路径）**  
   `build_skills_system_prompt()` 把每个 skill 渲染成：
   ```
   - {name}: {description}
   ```
   其中 `description` 来自 `extract_skill_description()`，**超过 60 字符会被截断成 57 字符 + `...`**。  
   来源：`hermes-agent/agent/skill_utils.py` → `extract_skill_description`。

2. **Agent 指令**  
   索引前有强制文案：匹配或「部分相关」就必须 `skill_view(name)`。  
   模型几乎只靠 **name + 前 60 字 description** 做第一次命中。

3. **`skills_list` / `skill_view`**  
   - `skills_list`：返回完整 description（≤1024），但模型不一定会先调。  
   - `skill_view`：才加载全文 + `related_skills` + references。

4. **分类 DESCRIPTION.md**  
   渲染为 `vidau-creative: {category description}`，帮助模型先进入电商视频类目。

## 写作硬规则（本仓库强制）

| 规则 | 说明 |
|------|------|
| `description` ≤ **60** 字符 | 等于 Hermes 索引窗口；`validate-skills.mjs` 会拦 |
| 以 `Use when` 开头 | 触发类，不是能力说明书 |
| 前 60 字含区分词 | 如 `URL` / `≤15s` / `16–120s` / `IMAGE` / `hooks` |
| 易混 skill 加 `NOT …` | 在截断窗口内写清互斥 |
| 细节放 body / `references/` | 长流程、MCP 参数表不要塞进 description |
| 新风格 skill 谨慎加条目 | 宁做一个 `creative-style-pack` + `skill_view(..., path)`，也不要 10 个几乎同构的 L2 抢索引 |

## 推荐 description 模板

```text
Use when <触发信号>; NOT <易混替代>
```

示例（均 ≤60）：

```yaml
description: Use when user pastes product page URL to make ad video
description: Use when ≤15s clip/image; NOT multi-shot or product URL
description: Use when batch TikTok/Reels hook IMAGE variants to A/B
```

## 新增「导演/广告节奏」时的结构建议

为避免命中率再次下降：

1. **L0** `creative-director-styles` — 镜头 lens 库（description 只写「cinematic lens/style」）  
2. **L1** `creative-ad-rhythm` — Hook / beat sheet（只写「hooks/beat sheet/CTA」）  
3. **L2** 最多 2–4 个垂直入口，触发词互斥（UGC / luxury / neon / SaaS）  
4. 风格明细放 `references/`，用 `skill_view(name, "references/...")` 渐进加载  
5. `metadata.hermes.related_skills` 互相指向，便于二次跳转

## 安装注意

- Skills 装到 `~/.hermes/skills/vidau-creative/`  
- 同步安装本目录 `DESCRIPTION.md` → `vidau-creative/DESCRIPTION.md`  
- 改 description 后需 **新开会话**（skill 索引有缓存 / snapshot）  
- 清理根目录重复副本（`~/.hermes/skills/creative-*` 与 `vidau-creative/` 重名时以 category 下为准）

## 回归抽检

```bash
# 描述长度
node scripts/validate-skills.mjs
```

或在 Hermes：`hermes chat -q "用这个商品链接做带货短视频"`，确认先 `skill_view(product-url-to-video)`。
