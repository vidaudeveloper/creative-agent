# VidAU Creative Agent Skills

> **Repo**: [creative-agent](https://github.com/vidaudeveloper/creative-agent)  
> **MCP**: `https://creative.vidau.ai/mcp`

## Install

One-click: copy [docs/SETUP.md](./docs/SETUP.md) into Agent chat (MCP first, then Skills).

```bash
# or from repo root
pnpm skills:install
```

## Working with MCP

1. **MCP**: `https://creative.vidau.ai/mcp`
2. **Prompt skills** (required before generation): `creative-seedance2-prompt` (video), `creative-gpt-image2-prompt` (image)
3. **Skills** (workflows): see [SETUP.md](./docs/SETUP.md)

## Maintenance

```bash
pnpm skills:validate
pnpm skills:build
```

## MCP tools reference

| Tool | Description |
|------|-------------|
| `creative_get_upload_instructions` | S3 presigned PUT instructions for local reference upload |
| `creative_upload_reference` | Fallback — upload reference image via MCP → S3 URL |
| `creative_estimate` | Estimate credits / duration |
| `creative_submit_generate` | Unified async generate: `items[]` (1–10), returns `tasks[]` |
| `creative_generate_image` | Async image (`direct_image` alias) |
| `creative_generate_video` | Async text-to-video (`direct_video` alias) |
| `creative_image_to_video` | Async reference image to video (`direct_video` alias) |
| `creative_first_frame_to_video` | Async first / first-last frame to video (`direct_video` alias) |
| `creative_submit_workflow` | Generic async workflow submit |
| `creative_generate_script` | Generate Final Video Spec Markdown from brief |
| `creative_submit_script2film` | Script → video (reference mode) |
| `creative_submit_script2film_keyframes` | Script → video (first/last frame) |
| `creative_generate_bgm` | Async BGM (`direct_bgm` alias) |
| `creative_get_task` | Get task status |
| `creative_list_tasks` | List tasks |
| `creative_cancel_task` | Cancel task |
| `creative_list_models` | List models |
