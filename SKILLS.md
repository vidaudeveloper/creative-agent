# VidAU Creative Agent Skills

> **Repo**: [creative-agent-skill](https://github.com/vidaudeveloper/creative-agent-skill)  
> **MCP server**: [creative-agent](https://github.com/vidaudeveloper/creative-agent)

## Install

One-click: copy [docs/SETUP.md](./docs/SETUP.md) into Agent chat (MCP first, then Skills).

```bash
# or from repo root
pnpm skills:install
```

## Working with MCP

1. **MCP** (image/video generation): `mcp_servers.vidau-creative.url` → `https://creative.vidau.info/mcp`, with `headers.Authorization: Bearer ${OPEN_VIDAU_API_KEY}`
2. **Prompt skills** (required before generation MCP): `creative-seedance2-prompt` (video), `creative-gpt-image2-prompt` (image)
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
| `creative_estimate` | Estimate duration (`eta_sec` / `eta_min`) |
| `creative_generate_image` | Sync image generation |
| `creative_generate_video` | Async video (direct_video job) |
| `creative_image_to_video` | Async video (direct_video job) |
| `creative_first_frame_to_video` | Async video (direct_video job) |
| `creative_image_to_video` | Reference image to video |
| `creative_first_frame_to_video` | First-frame / first-last-frame to video |
| `creative_submit_workflow` | Generic async workflow submit |
| `creative_generate_script` | Generate Final Video Spec Markdown from brief |
| `creative_submit_script2film` | Script → video (reference mode) |
| `creative_submit_script2film_keyframes` | Script → video (first/last frame) |
| `creative_submit_batch_variants` | Batch image variants |
| `creative_get_job` | Get job status |
| `creative_list_jobs` | List jobs |
| `creative_cancel_job` | Cancel job |
| `creative_list_models` | List models |
