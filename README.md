# VidAU Creative Agent Skills

VidAU Creative Agent 的 Skill 包，配合 [creative-agent](https://github.com/vidaudeveloper/creative-agent) MCP 服务使用。

**一键安装全部 Skill**：复制 [docs/SKILLS_SETUP.md](./docs/SKILLS_SETUP.md) 中的话术到 Agent 对话即可。

## Skill 分层

| 层级 | 说明 | Skill |
|------|------|-------|
| **L0-foundation** | 通用基础 | `creative-platform`、`creative-job-runner` |
| **L1-capability** | 制作能力链路 | `creative-direct`、`creative-script2film`、`creative-script2film-keyframes`、`creative-batch-orchestrator` |
| **L2-vertical** | 垂类场景 | `trend-viral-short`、`product-url-to-video` |

依赖关系见 [`_manifest.yaml`](./_manifest.yaml)。

## MCP 配置

```yaml
mcp_servers:
  vidau-creative:
    url: https://creative.vidau.info/mcp
    enabled: true
    connect_timeout: 60
    timeout: 300
```

## 安装

复制 [docs/SKILLS_SETUP.md](./docs/SKILLS_SETUP.md) 中的话术到 Agent 对话，或在本仓库执行：

```bash
pnpm skills:install
```

## 维护

```bash
pnpm skills:validate
pnpm skills:build
```

更详细的 MCP 工具对照见 [SKILLS.md](./SKILLS.md)。
