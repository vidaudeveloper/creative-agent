# VidAU Creative Agent — One-Click Skill Install

Please install **all** Skills from the Creative Agent repository on GitHub (**no local clone required** — fetch directly from GitHub). Skill repository: `https://github.com/vidaudeveloper/creative-agent.git` (branch `main`).

First, read `https://raw.githubusercontent.com/vidaudeveloper/creative-agent/main/_manifest.yaml` and list every skill from `skills[].path` (in order: L0-foundation → L1-capability → L2-vertical). For each path, run `skills install https://raw.githubusercontent.com/vidaudeveloper/creative-agent/main/<path>/SKILL.md --force --yes --category vidau-creative`. After installation, verify that the installed list matches the manifest. If MCP is not configured yet, configure `creative-agent` to point to `https://creative.vidau.info/mcp` first.
