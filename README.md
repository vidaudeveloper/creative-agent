# VidAU Creative Agent Skills

VidAU Creative Agent 的 Hermes Skill 包，配合 [creative-agent](https://github.com/vidaudeveloper/creative-agent) MCP 服务使用。

本仓库为 **Skill 文档独立源**，供桌面端打包时拉取并内置到安装包。

## Skill 分层

| 层级 | 说明 | Skill |
|------|------|-------|
| **L0-foundation** | 通用基础 | `creative-platform`、`creative-job-runner` |
| **L1-capability** | 制作能力链路 | `creative-direct`、`creative-script2film`、`creative-script2film-keyframes`、`creative-batch-orchestrator` |
| **L2-vertical** | 垂类场景 | `trend-viral-short`、`product-url-to-video` |

依赖关系见 [`_manifest.yaml`](./_manifest.yaml)。

---

## 桌面端接入（推荐）

最常见的做法：打包前从本仓库复制 Skill 文件，**展平**为 `{skill-name}/SKILL.md` 目录结构，打进应用资源目录。

### 1. 引用本仓库

```bash
# 方式 A：git submodule（推荐，版本可 pin）
git submodule add https://github.com/vidaudeveloper/creative-agent-skill.git vendor/creative-agent-skill
git submodule update --init --recursive

# 方式 B：CI 临时 clone
git clone --depth 1 https://github.com/vidaudeveloper/creative-agent-skill.git /tmp/creative-agent-skill
```

### 2. 打包脚本同步 Skill

将 L0 / L1 / L2 三层展平复制到目标目录（示例输出 `resources/skills/`）：

```bash
SKILL_SRC="vendor/creative-agent-skill"   # 或 /tmp/creative-agent-skill
SKILL_DEST="resources/skills"             # 改成你项目的内置路径

rm -rf "$SKILL_DEST"
mkdir -p "$SKILL_DEST"

for layer in L0-foundation L1-capability L2-vertical; do
  layer_dir="$SKILL_SRC/$layer"
  [[ -d "$layer_dir" ]] || continue
  for skill_dir in "$layer_dir"/*/; do
    [[ -f "${skill_dir}SKILL.md" ]] || continue
    cp -R "$skill_dir" "$SKILL_DEST/$(basename "$skill_dir")"
  done
done

echo "已同步 $(find "$SKILL_DEST" -name SKILL.md | wc -l | tr -d ' ') 个 Skill"
```

同步后的目录结构：

```
resources/skills/
├── creative-platform/SKILL.md
├── creative-job-runner/SKILL.md
├── creative-direct/SKILL.md
├── creative-script2film/SKILL.md
├── creative-script2film-keyframes/SKILL.md
├── creative-batch-orchestrator/SKILL.md
├── trend-viral-short/SKILL.md
└── product-url-to-video/SKILL.md
```

### 3. 配置 MCP

桌面端 Agent 还需连接 creative-agent MCP（生图 / 生视频 / 异步任务）：

```yaml
mcp_servers:
  vidau-creative:
    url: https://creative.vidau.info/mcp
    headers:
      Authorization: Bearer ${VIDAU_TOKEN}
```

Skill 告诉 Agent **怎么用** MCP 工具；MCP 负责 **实际调用**。

---

## 其他接入方式

### 静态 well-known 托管

适合 CDN / GitHub Pages，不跑 Node 服务：

```bash
pnpm skills:validate
pnpm skills:build
# 输出 → public/.well-known/skills/
```

客户端按 `/.well-known/skills/index.json` 发现并拉取各 Skill。

### Hermes CLI 远程安装

已有 Hermes 环境的开发者，可在线安装：

```bash
git clone https://github.com/vidaudeveloper/creative-agent-skill.git
cd creative-agent-skill
pnpm skills:install
```

默认从 `https://creative.vidau.info` 拉取全部 Skill 到 `~/.hermes/skills/`。

---

## 维护

```bash
pnpm skills:validate   # 校验 SKILL.md frontmatter
pnpm skills:build      # 生成 well-known 静态目录
```

更详细的 MCP 工具对照与安装说明见 [SKILLS.md](./SKILLS.md)。
