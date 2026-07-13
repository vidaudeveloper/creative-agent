# jianying-draft-compiler（P0）

> **Canonical location**: shipped inside the skill monorepo  
> `https://github.com/vidaudeveloper/creative-agent/tree/main/tools/jianying-draft-compiler`

VidAU **导演 + 草稿编译器**：把 Edit Plan 编译成剪映/CapCut 草稿包。  
**不**实现转场/特效渲染；用户本机剪映打开草稿即可预览。

引擎：vendored `pyJianYingDraft`（源自 capcut-mate）。

## 用户安装

```bash
curl -fsSL https://raw.githubusercontent.com/vidaudeveloper/creative-agent/main/tools/install-jy-compile.sh | bash
export PATH="$HOME/.vidau/bin:$PATH"
jy-compile where
```


## Edit Plan

```json
{
  "aspect": "9:16",
  "clips": [
    { "path": "/abs/a.mp4", "in_ms": 0, "out_ms": 3000 },
    { "url": "https://…/b.mp4", "in_ms": 0, "out_ms": 3000 }
  ],
  "junctions": [
    { "after_clip": 0, "transition": "竖向模糊", "duration_ms": 500 }
  ],
  "overlays": [
    { "type": "effect", "name": "撕纸涂鸦边框", "start_ms": 0, "end_ms": 6000 }
  ]
}
```

- 时间单位：**毫秒**（编译时转微秒）
- `junctions[].after_clip`：转场挂在该索引片段尾部（接缝前一段）
- 名称必须与剪映目录一致：`jy-compile transitions` / `jy-compile effects --grep 撕纸`

## HTTP API（可选）

```bash
uv run uvicorn jianying_draft_compiler.api:app --reload --port 3100
# POST /edit-plan/compile
# GET  /catalog/transitions
# GET  /catalog/effects?q=撕纸
```

## 目录

```
vendor/pyJianYingDraft/   # 从 capcut-mate 同步
vendor/template_default2/
src/jianying_draft_compiler/
  models.py    # EditPlan
  compile.py   # 核心编译
  catalog.py   # 转场/特效名解析
  api.py       # FastAPI
  cli.py       # jy-compile
examples/p0_demo.json
scripts/sync_vendor.sh
```

同步上游引擎：

```bash
./scripts/sync_vendor.sh
# 或 CAPCUT_MATE_ROOT=/path/to/capcut-mate ./scripts/sync_vendor.sh
```

## Windows 自动导出

```bat
jy-compile export-check
jy-compile export <草稿名> -o %USERPROFILE%\Videos\out.mp4
```

依赖：`uv sync --extra windows`。剪映须打开且在首页。macOS 不支持 RPA，仅 import + 手动导出。

## P0 范围 / 非目标

| 做 | 不做 |
|----|------|
| Plan → draft 目录 + zip | 云端导出 MP4 |
| 转场 + 场景特效写入草稿 | 自研 453/1097 渲染 |
| 字幕 / 标题字 / 本地贴纸图 / BGM | Mac 自动导出 |
| 本地 path / HTTP url 素材 | 保证全版本 UI 兼容 |
| Windows RPA 导出（剪映 UI） | 伪造剪映内置贴纸 ID 目录 |

## 许可注意

`vendor/pyJianYingDraft` 源自 capcut-mate / 上游项目，请遵守其 Apache-2.0 等许可；本仓库仅作 VidAU 集成骨架。
