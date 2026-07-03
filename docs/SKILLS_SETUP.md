# VidAU Creative Agent — Skill 一键安装

请帮我从 GitHub 远程安装 Creative Agent 仓库中的**全部** Skill（**无需本地 clone**，直接从 GitHub 拉取）。Skill 仓库：`https://github.com/vidaudeveloper/creative-agent.git`（分支 `main`）。

先读取 `https://raw.githubusercontent.com/vidaudeveloper/creative-agent/main/_manifest.yaml`，按其中 `skills[].path` 列出全部 skill（按 L0-foundation → L1-capability → L2-vertical 顺序）；对每个 path 执行 `skills install https://raw.githubusercontent.com/vidaudeveloper/creative-agent/main/<path>/SKILL.md --force --yes --category vidau-creative`。装完后验收已安装列表与 manifest 一致。若 MCP 未配置，请先配置 `creative-agent` 指向 `https://creative.vidau.info/mcp`。
