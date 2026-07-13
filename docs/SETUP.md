# VidAU Creative Agent — One-Click Setup

Please complete the full Creative Agent setup in the following order:

1. **MCP**: Check whether `creative-agent` is already connected and working. If not, configure the MCP server `creative-agent` to point to `https://creative.vidau.ai/mcp`. Reload MCP and verify the connection is healthy.

2. **Skills + local Jianying compiler**: Install **all** Skills from `https://github.com/vidaudeveloper/creative-agent` (branch `main`). **Do not** use `raw.githubusercontent.com` URLs for the skill list — they often return HTTP 429. The skill list is defined in `_manifest.yaml` — never hardcode skill names.

   `install-skills.mjs` will:
   - copy every skill in `_manifest.yaml` into `~/.hermes/skills/vidau-creative/`
   - **also install** `tools/jianying-draft-compiler` → CLI `jy-compile` under `~/.vidau/bin/` (needed by **jianying-remix**)

   Prerequisites for the compiler step: **git**, **uv** ([install](https://docs.astral.sh/uv/getting-started/installation/)), Python **3.11+**.  
   On **Windows**, the installer also tries `uv sync --extra windows` (uiautomation / pyautogui) so `jy-compile export` can RPA-export MP4.  
   To skip compiler only: `node …/install-skills.mjs --force --skip-compiler`.

   **Preferred (one shallow clone, zero raw CDN requests):**

   ```bash
   git clone --depth 1 https://github.com/vidaudeveloper/creative-agent.git /tmp/creative-agent-skill
   node /tmp/creative-agent-skill/scripts/install-skills.mjs --force
   export PATH="$HOME/.vidau/bin:$PATH"
   jy-compile where   # optional check — should print Jianying draft root
   ```

   The script reads local `_manifest.yaml`, then copies every `skills[].path` (including `references/`) into `~/.hermes/skills/vidau-creative/`, then runs `tools/install-jy-compile.sh`.

   **Fallback A (no local copy, but git available):**

   ```bash
   git clone --depth 1 https://github.com/vidaudeveloper/creative-agent.git /tmp/creative-agent-skill
   node /tmp/creative-agent-skill/scripts/install-skills.mjs --remote --force
   export PATH="$HOME/.vidau/bin:$PATH"
   ```

   **Fallback B (no git):** fetch `_manifest.yaml` via GitHub Contents API (not raw CDN), parse every `skills[].path` in manifest order, and for each path run:

   ```bash
   skills install vidaudeveloper/creative-agent/<path> --force --yes --category vidau-creative
   ```

   Manifest URL: `https://api.github.com/repos/vidaudeveloper/creative-agent/contents/_manifest.yaml?ref=main` (decode the `content` field from base64).

   Or run the install script with API-fetched manifest (download script via the same Contents API if needed):

   ```bash
   node install-skills.mjs --from-github --force
   ```

   Note: Fallback B / `--from-github` without a full clone still installs skills via Hermes, then **git-clones** the same repo into `~/.vidau/cache/creative-agent` to install `jy-compile` (avoids raw CDN for the compiler tree).

   After installation, verify that the installed skill list matches every `skills[].id` in `_manifest.yaml`, and that `jy-compile where` works (unless `--skip-compiler`).

3. **Apply changes**: Run `/reset` (or `/new`) to restart the session so MCP and Skills all take effect. Ensure the user shell / agent environment has `PATH` including `$HOME/.vidau/bin` when using **jianying-remix**.
