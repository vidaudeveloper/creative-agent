# VidAU Creative Agent Skills

> **独立仓库**：[creative-agent-skill](https://github.com/vidaudeveloper/creative-agent-skill)  
> MCP 服务：[creative-agent](https://github.com/vidaudeveloper/creative-agent)

Hermes 可安装的 Skill 包。分层：

- **L0-foundation**：通用基础（job-runner、platform）
- **L1-capability**：能力链路（script2film、batch）
- **L2-vertical**：垂类场景（热点、公益、电商等）

## 远程安装（Well-Known，推荐）

`creative-agent` 启动后会暴露 Hermes 标准端点：

| URL | 说明 |
|-----|------|
| `GET /.well-known/skills/index.json` | Skill 目录索引 |
| `GET /.well-known/skills/{name}/SKILL.md` | 单个 Skill 正文 |

**已发布测试服**（推荐）：`https://creative.vidau.info`  
**本地开发**：`http://localhost:3100`

```bash
# 测试服
curl https://creative.vidau.info/.well-known/skills/index.json
curl https://creative.vidau.info/.well-known/skills/creative-direct/SKILL.md
```

### Hermes CLI 安装

```bash
BASE=https://creative.vidau.info

# 搜索该站点下所有 Skill
hermes skills search "$BASE" --source well-known

# 预览
hermes skills inspect "well-known:${BASE}/.well-known/skills/creative-direct"

# 安装（可加 --force 跳过社区源确认）
hermes skills install "well-known:${BASE}/.well-known/skills/creative-direct" --force

# 一次安装全部（在本仓库根目录执行；默认从 creative.vidau.info 拉取）
pnpm skills:install

# 本地 creative-agent 联调
SKILLS_BASE_URL=http://localhost:3100 pnpm skills:install
```

**本地调试 Hermes 远程安装**：Hermes 默认阻止访问 `localhost`（SSRF 防护）。本地联调时在 `~/.hermes/config.yaml` 临时开启：

```yaml
security:
  allow_private_urls: true
```

然后再执行 `hermes skills install well-known:http://localhost:3100/.well-known/skills/creative-direct --force`。

### 与 MCP 配合

1. **MCP**（生图/生视频）：`mcp_servers.vidau-creative.url` → `https://creative.vidau.info/mcp`
2. **Skill**（工作流）：`hermes skills install well-known:https://creative.vidau.info/.well-known/skills/...`

Skill 安装到 `~/.hermes/skills/`，MCP 仍走 HTTP 远程调用。

### Hermes 自动任务追踪（推荐）

在 `~/.hermes/SOUL.md` 追加（或通过 `creative-job-runner` Skill 生效）：

```markdown
## VidAU Creative 任务追踪
- 调用任何 vidau-creative MCP 生图/生视频工具后，必须读取响应中的 `tracking` 字段。
- `creative_submit_*` 返回后：立即向用户发送 `tracking.user_message`，**禁止** sleep / 自动轮询 `creative_get_job`。
- 告知用户可在本对话中随时询问任务进度；用户主动追问时再单次 `creative_get_job`。
- 同步工具（creative_generate_*）调用前先告知预估耗时，完成后交付 artifacts + tracking.user_message。
```

安装/更新 Skill：`pnpm skills:install`（默认从 `https://creative.vidau.info` 安装）

## 静态导出（CDN / nginx）

不跑 Node 也可托管 Skill 文件：

```bash
pnpm skills:build
# 输出 → public/.well-known/skills/
```

将 `public/` 挂到 CDN 或 nginx 的 web root 即可。

## 本地开发（软链，可选）

```bash
ln -sf "$(pwd)/L0-foundation/creative-platform" ~/.hermes/skills/vidau-creative/creative-platform
# ... 其他 skill 同理
```

## 维护

```bash
pnpm skills:validate   # 检查 frontmatter
pnpm skills:build      # 生成静态 well-known 目录
```

## 目录

```
skills/
├── _manifest.yaml
├── L0-foundation/
│   ├── creative-job-runner/
│   └── creative-platform/
├── L1-capability/
│   ├── creative-batch-orchestrator/
│   ├── creative-direct/
│   ├── creative-script2film/
│   └── creative-script2film-keyframes/
└── L2-vertical/
    ├── trend-viral-short/
    └── product-url-to-video/
```

## MCP Tools 对照

| Tool | 说明 |
|------|------|
| `platform_get_credits` | 查积分 |
| `platform_check_entitlement` | 查权益 |
| `creative_get_upload_instructions` | 参考素材本地上传 API 说明（不传图） |
| `creative_upload_reference` | 【兜底】经 MCP 代传参考图 → CDN URL |
| `creative_estimate` | 估积分/耗时 |
| `creative_generate_image` | 同步生图 |
| `creative_generate_video` | 同步生视频 |
| `creative_image_to_video` | 参考图生视频 |
| `creative_first_frame_to_video` | 首帧/首尾帧生视频 |
| `creative_submit_workflow` | 通用异步提交 |
| `creative_generate_script` | 从创意/brief 生成 Final Video Spec Markdown 脚本 |
| `creative_submit_script2film` | 脚本→成片（reference） |
| `creative_submit_script2film_keyframes` | 脚本→成片（首尾帧） |
| `creative_submit_batch_variants` | 批量变体 |
| `creative_get_job` | 查任务 |
| `creative_list_jobs` | 列出我的任务（含 tracking） |
| `creative_cancel_job` | 取消任务 |
| `creative_list_models` | 模型列表 |
