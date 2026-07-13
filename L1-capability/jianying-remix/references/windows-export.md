# Windows 自动导出（RPA）

仅 **Windows + 剪映专业版**。macOS 无此能力。

## 前置

1. `jy-compile` 已安装（`skills:install` 会装；Windows 会尝试 `uv sync --extra windows`）
2. `jy-compile export-check` 返回 `"ok": true`
3. 草稿已 `jy-compile import … --name <draft_name>`
4. **剪映专业版已打开，停留在首页**（草稿列表可见 `<draft_name>`）
5. 本机可操作 UI（不要锁屏 / 远程桌面最小化导致 UI 自动化失败）

## 命令

```bat
set PATH=%USERPROFILE%\.vidau\bin;%PATH%
jy-compile export-check
jy-compile export fashion-5clip-rich -o %USERPROFILE%\Videos\fashion-out.mp4 --resolution 1080P --timeout 600
```

PowerShell:

```powershell
$env:PATH = "$env:USERPROFILE\.vidau\bin;$env:PATH"
jy-compile export fashion-5clip-rich -o "$env:USERPROFILE\Videos\fashion-out.mp4"
```

## Skill 流程（Windows）

1. validate → compile → import  
2. 确认剪映在首页  
3. `jy-compile export <name> -o <mp4>`  
4. 向用户交付本地 mp4 路径  

若 export 失败：引导用户在剪映内手动导出，并报告错误 JSON。

## 风险

- 上游控制器注释：**主要验证于剪映 6 及以下**；更高版本 UI 变更可能导致找不到按钮  
- VIP 弹窗可能导致卡住；需用户关闭弹窗后重试  
- 同时只能跑一个导出任务  

## 依赖（手动）

```bat
cd %USERPROFILE%\.vidau\jianying-draft-compiler
uv sync --extra windows
```
