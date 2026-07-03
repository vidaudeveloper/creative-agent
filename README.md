# VidAU Creative Agent Skills

Hermes 可安装的 **Skill 包**，配合 [creative-agent](https://github.com/vidaudeveloper/creative-agent) MCP 服务使用。

本仓库为 Skill 文档的**独立源**，便于用户单独安装、Fork 或托管到 CDN。

## Skill 分层

| 层级 | 说明 | Skill |
|------|------|-------|
| **L0-foundation** | 通用基础 | `creative-platform`、`creative-job-runner` |
| **L1-capability** | 制作能力链路 | `creative-direct`、`creative-script2film`、`creative-script2film-keyframes`、`creative-batch-orchestrator` |
| **L2-vertical** | 垂类场景 | `trend-viral-short`、`product-url-to-video` |

完整清单见 [`_manifest.yaml`](./_manifest.yaml)。

---

## 快速集成（Hermes 用户）

### 1. 注册 MCP（生图/生视频）

在 `~/.hermes/config.yaml`：

```yaml
mcp_servers:
  vidau-creative:
    url: https://creative.vidau.info/mcp
    headers:
      Authorization: Bearer ${VIDAU_TOKEN}
```

登录 VidAU：`hermes vidau login`

### 2. 远程安装 Skill（推荐）

**已发布测试服**：`https://creative.vidau.info`

```bash
BASE=https://creative.vidau.info

# 浏览可用 Skill
hermes skills search "$BASE" --source well-known

# 预览单个 Skill
hermes skills inspect "well-known:${BASE}/.well-known/skills/creative-direct"

# 安装单个
hermes skills install "well-known:${BASE}/.well-known/skills/creative-direct" --force

# 一次安装全部（本仓库根目录）
git clone https://github.com/vidaudeveloper/creative-agent-skill.git
cd creative-agent-skill
pnpm skills:install
```

### 3. 本地软链（开发 / 自定义）

```bash
git clone https://github.com/vidaudeveloper/creative-agent-skill.git
ln -sf "$(pwd)/creative-agent-skill/L0-foundation/creative-platform" \
  ~/.hermes/skills/vidau-creative/creative-platform
# 其他 skill 同理，或复制整个 L0/L1/L2 目录
```

---

## 与本仓库配合的 creative-agent

[creative-agent](https://github.com/vidaudeveloper/creative-agent) 运行时通过 `SKILLS_DIR` 读取本仓库内容，并暴露 Hermes 标准端点：

| URL | 说明 |
|-----|------|
| `GET /.well-known/skills/index.json` | Skill 目录索引 |
| `GET /.well-known/skills/{name}/SKILL.md` | 单个 Skill 正文 |

在 creative-agent 中以 **git submodule** 引用本仓库：

```bash
cd creative-agent
git submodule add https://github.com/vidaudeveloper/creative-agent-skill.git skills
# .env.local: SKILLS_DIR=./skills
```

---

## 静态托管（CDN / GitHub Pages）

不跑 Node 服务也可托管 Skill：

```bash
pnpm skills:validate   # 校验 frontmatter
pnpm skills:build      # 生成 public/.well-known/skills/
```

将 `public/` 挂到 CDN 或 nginx，然后用：

```bash
hermes skills install "well-known:https://your-cdn.example.com/.well-known/skills/creative-direct" --force
```

---

## 目录结构

```
creative-agent-skill/
├── _manifest.yaml          # 包元数据 + 依赖关系
├── L0-foundation/
│   ├── creative-job-runner/
│   └── creative-platform/
├── L1-capability/
│   ├── creative-batch-orchestrator/
│   ├── creative-direct/
│   ├── creative-script2film/
│   └── creative-script2film-keyframes/
├── L2-vertical/
│   ├── product-url-to-video/
│   └── trend-viral-short/
├── scripts/
│   ├── validate-skills.mjs
│   ├── build-well-known-skills.mjs
│   └── install-hermes-skills.mjs
└── SKILLS.md               # 详细安装与 MCP 对照说明
```

---

## MCP Tools 对照

| Tool | 说明 |
|------|------|
| `platform_get_credits` | 查积分 |
| `platform_check_entitlement` | 查权益 |
| `creative_get_upload_instructions` | 参考素材本地上传 API 说明 |
| `creative_upload_reference` | 【兜底】经 MCP 代传参考图 |
| `creative_estimate` | 估积分/耗时 |
| `creative_generate_image` | 同步生图 |
| `creative_generate_video` | 同步生视频 |
| `creative_image_to_video` | 参考图生视频 |
| `creative_first_frame_to_video` | 首帧/首尾帧生视频 |
| `creative_submit_workflow` | 通用异步提交 |
| `creative_generate_script` | 生成 Final Video Spec 脚本 |
| `creative_submit_script2film` | 脚本→成片（reference） |
| `creative_submit_script2film_keyframes` | 脚本→成片（首尾帧） |
| `creative_submit_batch_variants` | 批量变体 |
| `creative_get_job` | 查任务 |
| `creative_list_jobs` | 列出我的任务 |
| `creative_cancel_job` | 取消任务 |
| `creative_list_models` | 模型列表 |

更多细节见 [SKILLS.md](./SKILLS.md)。

---

## 维护

```bash
pnpm skills:validate
pnpm skills:build
SKILLS_BASE_URL=http://localhost:3100 pnpm skills:install   # 联调 creative-agent 本地实例
```

本地联调时 Hermes 默认阻止 `localhost`（SSRF 防护），需在 `~/.hermes/config.yaml` 临时设置：

```yaml
security:
  allow_private_urls: true
```
