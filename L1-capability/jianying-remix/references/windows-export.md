# Windows 自动导出（RPA）

仅 **Windows + 剪映专业版**。macOS 无此能力。

## 前置

1. `jy-compile` 已安装（`skills:install` 会装；Windows 会尝试 `uv sync --extra windows`）
2. `jy-compile export-check` 返回 `"ok": true`
3. 草稿已 `jy-compile import … --name <draft_name>`
4. **剪映专业版已打开，停留在首页**（草稿列表可见 `<draft_name>`）
5. 本机可操作 UI（不要锁屏 / 远程桌面最小化导致 UI 自动化失败）
6. 关掉新手黄气泡「知道了」、VIP/更新弹窗

## 命令

```bat
set PATH=%USERPROFILE%\.vidau\bin;%PATH%
jy-compile export-check
rem 剪映 10.9 务必加 --profile v10
jy-compile export mens-vest-remix -o %USERPROFILE%\Videos\out.mp4 --resolution 1080P --timeout 600 --profile v10
```

PowerShell:

```powershell
$env:PATH = "$env:USERPROFILE\.vidau\bin;$env:PATH"
# 也可: $env:JY_UIA_PROFILE = "v10"
jy-compile export mens-vest-remix -o "$env:USERPROFILE\Videos\out.mp4" --profile v10
```

| `--profile` | 适用 |
|-------------|------|
| `auto`（默认） | 先试 ≤6 AutomationId，再回退 10.9 中文按钮名 |
| `legacy` | 剪映 6 及以下 |
| `v10` | 剪映 **10.9** 中文专业版（推荐） |

## Skill 流程（Windows）

1. validate → compile → import  
2. 确认剪映在首页  
3. `jy-compile export <name> -o <mp4> --profile v10`（10.9）  
4. 向用户交付本地 mp4 路径  

若 export 失败：把完整错误 JSON 发回；可先手动导出。10.9 截图结论见 [uia-10.9-from-screenshots.md](uia-10.9-from-screenshots.md)。

## 风险

- 10.9 适配按截图用中文 Name 匹配，**须实机验证**；控件树若与截图不一致需再改  
- SVIP「立即续费」、黄气泡「知道了」会挡点击  
- 分辨率在 10.9 常为「原始」；设 1080P 失败时会保留默认并继续导出  
- 同时只能跑一个导出任务  
- 系统缩放 150% 时依赖 UIA，不要写死坐标  

## 依赖（手动）

```bat
cd %USERPROFILE%\.vidau\jianying-draft-compiler
uv sync --extra windows
```

改完 controller 后请在本机重装/同步 `jy-compile`（或 `uv sync` 后指向最新 vendor）。
