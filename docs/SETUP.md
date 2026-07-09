# VidAU Creative Agent — One-Click Setup

Please complete the full Creative Agent setup in the following order:

1. **MCP**: Check whether `creative-agent` is already connected and working. If not, configure the MCP server `creative-agent` to point to `https://creative.vidau.ai/mcp`. Reload MCP and verify the connection is healthy.

2. **Skills**: Install **all** Skills from `https://github.com/vidaudeveloper/creative-agent` (branch `main`). **Do not** use `raw.githubusercontent.com` URLs — they often return HTTP 429. The skill list is defined in `_manifest.yaml` — never hardcode skill names.

   **Preferred (one shallow clone, zero raw CDN requests):**

   ```bash
   git clone --depth 1 https://github.com/vidaudeveloper/creative-agent.git /tmp/creative-agent-skill
   node /tmp/creative-agent-skill/scripts/install-skills.mjs --force
   ```

   The script reads local `_manifest.yaml`, then copies every `skills[].path` (including `references/`) into `~/.hermes/skills/vidau-creative/`.

   **Fallback A (no local copy, but git available):**

   ```bash
   git clone --depth 1 https://github.com/vidaudeveloper/creative-agent.git /tmp/creative-agent-skill
   node /tmp/creative-agent-skill/scripts/install-skills.mjs --remote --force
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

   After installation, verify that the installed skill list matches every `skills[].id` in `_manifest.yaml`.

3. **Apply changes**: Run `/reset` (or `/new`) to restart the session so MCP and Skills all take effect.
