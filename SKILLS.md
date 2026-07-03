# VidAU Creative Agent Skills

> **独立仓库**：[creative-agent-skill](https://github.com/vidaudeveloper/creative-agent-skill)  
> MCP 服务：[creative-agent](https://github.com/vidaudeveloper/creative-agent)

## 安装

一键安装：复制 [docs/SKILLS_SETUP.md](./docs/SKILLS_SETUP.md) 中的话术到 Agent 对话。

```bash
# 或在本仓库根目录
pnpm skills:install
```

## 与 MCP 配合

1. **MCP**（生图/生视频）：`mcp_servers.vidau-creative.url` → `https://creative.vidau.info/mcp`（见 [creative-agent MCP_SETUP.md](https://github.com/vidaudeveloper/creative-agent/blob/main/docs/MCP_SETUP.md)）
2. **Skill**（工作流）：[SKILLS_SETUP.md](./docs/SKILLS_SETUP.md)

## 维护

```bash
pnpm skills:validate
pnpm skills:build
```

## MCP Tools 对照

| Tool | 说明 |
|------|------|
| `creative_get_upload_instructions` | 参考素材本地上传 S3 预签名 PUT 说明 |
| `creative_upload_reference` | 【兜底】经 MCP 代传参考图 → S3 URL |
| `creative_estimate` | 估积分/耗时 |
| `creative_generate_image` | 同步生图 |
| `creative_generate_video` | 同步生视频 |
| `creative_image_to_video` | 参考图生视频 |
| `creative_first_frame_to_video` | 首帧/首尾帧生视频 |
| `creative_submit_workflow` | 通用异步提交 |
| `creative_generate_script` | 从创意/brief 生成 Final Video Spec Markdown 脚本 |
| `creative_submit_script2film` | 脚本→成片（reference） |
| `creative_submit_script2film_keyframes` | 脚本→成片（首尾帧） |
| `creative_submit_batch_variants` | 批量变体 |
| `creative_get_job` | 查任务 |
| `creative_list_jobs` | 列出任务 |
| `creative_cancel_job` | 取消任务 |
| `creative_list_models` | 模型列表 |
