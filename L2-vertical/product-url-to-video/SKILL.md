---
name: product-url-to-video
description: 商品链接→抓取产品信息→生成带货短视频/广告图（独立站与主流电商）
metadata:
  layer: L2-vertical
  requires: [creative-job-runner, creative-platform, creative-script2film, creative-script2film-keyframes]
  tags: [ecommerce, product, url, scrape, script2film, bgm, one-click]
---

# 商品链接 → 视频（Product URL to Video）

用户粘贴**商品页链接**时启用。先用 Hermes 内置网页能力抓取产品信息，再调用 **vidau-creative** MCP 生成广告素材。

> **适用**：Shopify 独立站、Amazon、TikTok Shop、Temu 等任意可访问的商品页。  
> **不适用**：纯社媒主页、网盘、YouTube/Bilibili 视频链接 — 按普通对话处理。

## 生视频 Skill 选型（L2 必读）

提交成片前，根据用户需求选择 **L1 生视频 Skill**：

| 用户意图 / 场景 | 加载 Skill | MCP 入口 |
|----------------|------------|----------|
| 带货短片，产品外观必须与主图一致（**默认**） | **creative-script2film** | `creative_submit_script2film` |
| 强调镜头切换、运镜过渡、电影感 | **creative-script2film-keyframes** | `creative_submit_script2film_keyframes` |
| 只要单段 5–15s 演示，不要多镜 | **creative-direct** | `creative_image_to_video` 或 `creative_first_frame_to_video` |
| A/B 测试多条钩子**图片** | **trend-viral-short** | `creative_submit_batch_variants` |

**决策口诀**：
- 有产品主图、要「像这个商品」→ **reference**（creative-script2film）
- 要「顺滑转场 / 故事感运镜」→ **首尾帧**（creative-script2film-keyframes）
- 用户未说明时，电商带货默认 **creative-script2film**

## 何时触发

消息中含 `https://` 且像商品页（含 `product`、`/p/`、`/dp/`、`shop`、`store` 等路径，或用户明确说「这个链接的产品」）。

## 流程概览

```
1. 抓取产品信息（Hermes 工具）
2. 向用户展示摘要并确认
3. 估积分 + 提交生成（MCP）
4. creative-job-runner — 提交后立即发送 `tracking.user_message`，**禁止** sleep / 轮询
```

---

## 1. 抓取产品信息

按优先级尝试，**前一步成功即停止**：

### A. `web_extract`（首选）

```
web_extract(urls=["<商品页 URL>"], format="markdown")
```

从返回内容提取：`product_name`、`brand`、`price`、`description`、主图 URL（`og:image` / 最大商品图）。

### B. `execute_code`（结构化解析）

`web_extract` 信息不足或失败时使用。优先解析 **JSON-LD**（`@type: Product`）、**Open Graph**、`application/ld+json`：

```python
import urllib.request, json, re

url = "<商品页 URL>"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")

# JSON-LD Product
for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
    try:
        data = json.loads(block)
        # 递归查找 @type == Product
        ...
    except: pass

# Open Graph fallback
og = lambda prop: re.search(rf'property="og:{prop}" content="([^"]+)"', html)
name = og("title") or og("product:title")
image = og("image")
desc = og("description")
print(json.dumps({"name": name, "image": image, "description": desc}, ensure_ascii=False))
```

**必须提取的字段**：

| 字段 | 说明 |
|------|------|
| `product_name` | 商品标题 |
| `product_description` | 卖点/描述（可截断至 500 字） |
| `product_images` | 主图 URL 列表（最多 8 张，优先高清） |
| `price` | 可选，展示用 |
| `brand` | 可选 |

### C. `terminal` + curl（轻量兜底）

仅当 A/B 均失败：

```
curl -sL -A "Mozilla/5.0" "<URL>" | head -c 200000
```

再用 `execute_code` 或自行 regex 提取 og/meta。

### D. `browser`（JS 渲染页）

页面需登录、或 A–C 返回空壳 HTML 时使用 browser 工具打开 URL，再重复 B 的解析逻辑。

### 抓取失败

明确告知用户：「无法从该链接解析产品信息」，请手动上传产品图并补充名称/卖点。不要强行提交 MCP。

---

## 2. 向用户确认

抓取成功后，**先展示摘要再生成**：

- 产品名称、品牌、价格（若有）
- 主图预览（Markdown 图片或 URL）
- 卖点摘要（2–3 句）

询问用户：

1. **生成类型**：短视频成片（默认）/ 批量钩子变体 / 单张广告图
2. **画幅**：默认 `9:16`（TikTok/Reels）
3. **时长**：默认 30 秒（script2film）
4. **参考图**：默认使用抓取到的主图（最多 3 张）

用户仅贴链接未说明意图时，默认走 **script2film 30s 竖版带货短片**。

---

## 3. 生成脚本（LLM 自写）

根据抓取结果撰写 **30–60 秒竖版带货脚本**（分镜感、口播感），结构：

1. 前 3 秒钩子（痛点/场景）
2. 产品亮相 + 核心卖点 × 2–3
3. CTA（限时/下单引导）

脚本语言与用户对话语言一致（中文用户 → 中文脚本）。

---

## 4. MCP 提交

### 前置（必做）

1. `platform_check_entitlement`
2. `platform_get_credits`
3. `creative_estimate` — 按选定 workflow 估积分

### 默认：script2film 成片（reference）

```
creative_submit_script2film:
  script: "<上一步脚本>"
  reference_image_urls: ["<主图 URL>", ...]
  brief:
    product: "<product_name>"
    product_description: "<卖点>"
    product_url: "<原始链接>"
    reference_image_urls: ["<主图 URL>", ...]
    audience: "<推断受众>"
  aspect_ratio: "9:16"
  target_duration_sec: 30
  shot_duration_sec: 5
  client_request_id: "<uuid>"
```

**参考图用法**：生图 + 生视频均走 **reference** 模式。

### 备选：首尾帧 script2film 成片

用户要电影感转场、不强调 reference 锁产品时：

```
creative_submit_script2film_keyframes:
  script: "<上一步脚本>"
  reference_image_urls: ["<主图 URL>"]   # 仅生图阶段约束产品
  video_mode: "first_last_frame"         # 可省略，为此工具默认
  aspect_ratio: "9:16"
  target_duration_sec: 30
  shot_duration_sec: 5
  client_request_id: "<uuid>"
```

### 备选：批量钩子变体

用户要 A/B 测试多条开头时，改走 **trend-viral-short** 或：

```
creative_submit_batch_variants:
  prompt: "<产品名 + 卖点 + 热点钩子，英文更佳>"
  count: 5
  aspect_ratio: "9:16"
```

### 备选：单图/单视频

走 **creative-direct**：

- 生图：`creative_generate_image` + `reference_urls: [<主图>]`
- 参考生视频：`creative_image_to_video` + `reference_image_urls: [<主图>]`
- 首尾帧生视频：`creative_first_frame_to_video` + `first_frame_url` / `last_frame_url`

---

## 5. 任务追踪

提交后立即加载 **creative-job-runner**：

- 发送 `tracking.user_message`，告知用户可在本对话中随时询问任务进度
- **禁止** sleep / 循环 `creative_get_job`；用户主动追问时再单次查询
- 用户主动追问某任务时，可单次 `creative_get_job` 后交付成片 URL + 本地落盘提示（**script2film 默认已含 BGM**）

---

## 注意事项

- **图片 URL**：抓取到的外链可直接传入 `reference_urls` / `reference_image_url`；若 MCP 报下载失败，告知用户手动上传图片后重试。
- **合规**：遵守目标站 robots.txt；抓取失败不反复 brute-force。
- **主流平台**：Amazon/TikTok Shop 等若页面复杂，优先 `web_extract` 或 `browser`。
- **多链接**：一次最多处理 **3 个**商品链接；多产品时分别抓取、分别确认。
- **不要**在抓取阶段调用 vidau-creative MCP；抓取纯靠 Hermes 本地工具，生成才走 MCP。
