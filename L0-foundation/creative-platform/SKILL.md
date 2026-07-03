---
name: creative-platform
description: VidAU 平台积分、会员权益与参考素材本地上传
metadata:
  layer: L0-foundation
  requires: []
  tags: [foundation, billing, platform, upload]
---

# Creative Platform Gateway

在执行任何扣费生成前，先确认用户积分与权益。

## 流程

1. `platform_check_entitlement` — 确认可使用 Creative Agent
2. `platform_get_credits` — 获取当前 `coin` 余额
3. 调用 `creative_estimate` 对比所需积分
4. 不足时明确告知差额，引导充值（VidAU VIP）

## 参考图本地上传（推荐）

生图/生视频 MCP 工具只接受 **HTTPS URL**（`reference_urls`），不传文件字节。

**Hermes Desktop / 有 `VIDAU_TOKEN` 的环境：**

1. `creative_get_upload_instructions` — 获取上传 URL、Header、curl 示例
2. 在**用户本机**用 `terminal` / curl POST multipart（字段名 `file`）
3. 取响应 `data.fileUrl`
4. 填入 `creative_generate_image.reference_urls` 或 `creative_image_to_video.reference_image_urls`

**不要**对远程 MCP 使用 `local_path`（会 ENOENT）。**不要**默认把大图 base64 经 MCP 代传；仅无本机 token 时用 `creative_upload_reference` 兜底。

## 注意

- 所有 MCP 请求需携带用户 `VidAu-Token`（MCP HTTP Header）；本地上传同样用 `VIDAU_TOKEN`
- 单张参考图上限约 25 MB；支持 jpg/png/webp/gif/bmp
- 失败生成按平台规则不重复扣费（以服务端为准）
