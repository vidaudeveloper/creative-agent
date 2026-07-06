# VidAU Creative Agent — One-Click Setup

Please complete the full Creative Agent setup in the following order:

1. **MCP**: Check whether `creative-agent` is already connected and working. If not, configure the MCP server `creative-agent` to point to `https://creative.vidau.info/mcp` (no Authorization required). Reload MCP and verify the connection is healthy.

2. **Vision (image understanding)**: Add the following YAML to the Agent configuration to analyze user-uploaded product images, reference images, and similar assets:

```yaml
auxiliary:
  vision:
    provider: custom:www.tokenware.ai
    model: gemini-3.1-flash-image-preview
```

3. **Skills**: Install **all** Skills from the GitHub repository (**no local clone required** — fetch directly from GitHub). Skill repository: `https://github.com/vidaudeveloper/creative-agent-skill` (branch `main`). Read `https://raw.githubusercontent.com/vidaudeveloper/creative-agent-skill/main/_manifest.yaml`, list every skill from `skills[].path` (in order: L0-foundation → L1-capability → L2-vertical, including **creative-seedance2-prompt** and **creative-gpt-image2-prompt**), and for each path run `skills install https://raw.githubusercontent.com/vidaudeveloper/creative-agent-skill/main/<path>/SKILL.md --force --yes --category vidau-creative`. After installation, verify that the installed list matches the manifest.

4. **Apply changes**: Run `/reset` (or `/new`) to restart the session so MCP, Vision, and Skills all take effect.
