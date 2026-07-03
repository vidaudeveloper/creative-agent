---
name: creative-platform
description: VidAU Creative 参考素材上传与生成前置说明
metadata:
  layer: L0-foundation
  requires: []
  tags: [foundation, platform, upload]
---

# Creative Platform Gateway

当前测试环境**无需积分/权益校验**，可直接调用生成类 MCP 工具。

## 流程

1. 调用 `creative_estimate` 了解预估耗时（可选）
2. 直接调用 `creative_generate_*` / `creative_submit_*` 等工具

## 参考图本地上传（推荐）

生图/生视频 MCP 工具只接受 **HTTPS URL**（`reference_urls`），不传文件字节。

**有本机终端的环境：**

1. `creative_get_upload_instructions` — 获取 S3 预签名 PUT 上传 URL 与 curl 示例
2. 在**用户本机**用 `terminal` / curl PUT 文件（`Content-Type` 见返回说明）
3. 上传成功后使用返回的 `upload.file_url`
4. 填入 `creative_generate_image.reference_urls` 或 `creative_image_to_video.reference_image_urls`

**不要**对远程 MCP 使用 `local_path`（会 ENOENT）。**不要**默认把大图 base64 经 MCP 代传；仅无本机终端时用 `creative_upload_reference` 兜底。

## 注意

- 单张参考图上限约 25 MB；支持 jpg/png/webp/gif/bmp
