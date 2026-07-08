# VidAU Creative Agent Skills

Skill package for VidAU Creative Agent, used with the [creative-agent](https://github.com/vidaudeveloper/creative-agent) MCP server.

**One-click install (MCP + Skills)**: copy the prompt from [docs/SETUP.md](./docs/SETUP.md) into your Agent chat.

## Skill layers

| Layer | Purpose | Skills |
|-------|---------|--------|
| **L0-foundation** | Shared foundation | `creative-platform`, `creative-job-runner`, `creative-narrative-router`, `creative-seedance2-prompt`, `creative-gpt-image2-prompt` |
| **L1-capability** | Production workflows | `creative-direct`, `creative-script2film`, `creative-script2film-keyframes`, `creative-batch-orchestrator` |
| **L2-vertical** | Vertical scenarios | `trend-viral-short`, `product-url-to-video` |

See [`_manifest.yaml`](./_manifest.yaml) for dependencies.

## MCP config

```yaml
mcp_servers:
  vidau-creative:
    url: https://creative.vidau.ai/mcp
    enabled: true
    connect_timeout: 60
    timeout: 300
```

## Install

Copy [docs/SETUP.md](./docs/SETUP.md) into Agent chat, or install locally (no `raw.githubusercontent.com` — avoids 429):

```bash
pnpm skills:install          # copies from this repo into ~/.hermes/skills/vidau-creative/
pnpm skills:install --remote # fallback: install via GitHub Contents API
```

## Maintenance

```bash
pnpm skills:validate
pnpm skills:build
```

MCP tool reference: [SKILLS.md](./SKILLS.md).
