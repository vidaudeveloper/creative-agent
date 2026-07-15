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

### End-to-end: product image → Jianying film

Use L2 skill **`product-image-to-jianying-remix`**: upload one product image → async `creative_submit_workflow` ×5 (`direct_video`, 4s scenes) → poll every 15s → **jianying-remix**.

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
| `creative_generate_image` | Sync image generation |
| `creative_generate_video` | Async text-to-video (`direct_video` job) |
| `creative_image_to_video` | Async reference image to video (`direct_video` job) |
| `creative_first_frame_to_video` | Async first / first-last frame to video (`direct_video` job) |
| `creative_submit_workflow` | Generic async workflow submit |
| `creative_generate_script` | Generate Final Video Spec Markdown from brief |
| `creative_submit_script2film` | Script → video (reference mode) |
| `creative_submit_script2film_keyframes` | Script → video (first/last frame) |
| `creative_submit_batch_variants` | Batch image variants |
| `creative_get_job` | Get job status |
| `creative_list_jobs` | List jobs |
| `creative_cancel_job` | Cancel job |
| `creative_select_bgm` | 从 VidAU 曲库按题材选 BGM（返回 url，不扣积分） |
| `creative_generate_bgm` | AI 生成 BGM |
| `creative_mux_bgm_into_video` | 将 BGM 混入视频 |
| `creative_list_models` | List models |

## Local tools (jianying-remix)

**Git source (same skill repo):** `https://github.com/vidaudeveloper/creative-agent` → `tools/jianying-draft-compiler/`

Installed automatically by `scripts/install-skills.mjs` (see [docs/SETUP.md](./docs/SETUP.md)). Manual:

```bash
bash tools/install-jy-compile.sh
export PATH="$HOME/.vidau/bin:$PATH"
```

| CLI | Description |
|-----|-------------|
| `jy-compile where` | Detect Jianying draft root |
| `jy-compile validate` | Validate Edit Plan JSON |
| `jy-compile compile` | Edit Plan → draft folder + zip |
| `jy-compile import` | Copy draft into Jianying + rewrite media paths |
| `jy-compile export-check` | Whether Windows RPA export is available |
| `jy-compile export` | Windows only: export imported draft → MP4 via Jianying UI |

Install details: `L1-capability/jianying-remix/references/install-compiler.md`.
