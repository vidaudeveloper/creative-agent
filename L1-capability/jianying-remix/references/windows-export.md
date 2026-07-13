# Windows 自动导出（RPA）

> **Skill 状态**：`jianying-remix` / `product-image-to-jianying-remix` **默认不调用**自动导出。  
> Agent 应在 `import` 后提醒用户到剪映「本地草稿」预览并手动导出。下文仅供人工调试 `jy-compile export`。

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
rem 剪映 10.9 UIA 空树时，直接用视觉 OCR：
jy-compile export mens-vest-remix -o %USERPROFILE%\Videos\out.mp4 --driver vision --timeout 600
rem 或 auto：先 UIA，失败再 OCR
jy-compile export mens-vest-remix -o %USERPROFILE%\Videos\out.mp4 --profile v10 --driver auto
```

PowerShell:

```powershell
$env:PATH = "$env:USERPROFILE\.vidau\bin;$env:PATH"
# $env:JY_EXPORT_DRIVER = "vision"
jy-compile export mens-vest-remix -o "$env:USERPROFILE\Videos\out.mp4" --driver vision
```

| `--driver` | 说明 |
|------------|------|
| `auto`（默认） | 先 UIA；控件树空 / 找不到草稿 / 找不到导出按钮 → 回退 OCR 点击 |
| `uia` | 仅 UIAutomation |
| `vision` | 仅屏幕 OCR + pyautogui 点击（适合 10.9 GetChildren=0） |

| `--profile` | 适用（仅 uia/auto 的 UIA 段） |
|-------------|------|
| `auto`（默认） | 先试 ≤6 AutomationId，再回退 10.9 中文按钮名 |
| `legacy` | 剪映 6 及以下 |
| `v10` | 剪映 **10.9** 中文专业版 |

## Skill 流程（Windows）

1. validate → compile → import  
2. 确认剪映在首页  
3. `jy-compile export <name> -o <mp4> --driver vision`（10.9 推荐）或 `--driver auto`  
4. 向用户交付本地 mp4 路径  

若 export 失败：把完整错误 JSON 发回；**最省时仍是剪映里手动导出**。10.9 截图结论见 [uia-10.9-from-screenshots.md](uia-10.9-from-screenshots.md)。

## 已知失败层（自动导出）

| 层 | 现象 | 处理 |
|----|------|------|
| 依赖 | `No module named 'src'` | 已改为 vendor 内 `win_utils`（勿再依赖 capcut-mate `src.utils`） |
| 草稿名空 | `draft_info.name == ""`，首页搜不到 | compile/import 会写入 `name`（与 `--name` / `plan.title` 一致） |
| UIA 空树 | 日志 `uia_children=0` | 用 `--driver vision`（OCR 点草稿名 / 导出 / 关闭） |
| 标题截断 | 卡片显示 `mens-ve…mix` | UIA/OCR 均支持省略号/前缀模糊；草稿名建议 ≤20 字符 |
| OCR 误点 | 点到错误「导出」 | vision 用屏幕区域约束（顶栏 vs 底栏）；保持窗口最大化、缩放稳定 |

视觉导出会在 `%USERPROFILE%\Videos` 等目录找**导出开始后最新**的 mp4 再挪到 `-o` 路径；请勿在导出期间往 Videos 扔别的大视频。

## 风险

- 10.9 适配按截图用中文 Name 匹配，**须实机验证**；控件树若与截图不一致需再改  
- OCR 依赖清晰可见的中文按钮；锁屏 / 远程桌面最小化会失败  
- SVIP「立即续费」、黄气泡「知道了」会挡点击  
- vision 模式暂不改分辨率/帧率（用剪映当前默认，多为「原始」）  
- 同时只能跑一个导出任务  
- 系统缩放 150% 时依赖截图像素坐标与 pyautogui 一致  
- 远程桌面最小化 / 锁屏时 UIA 常返回空控件树  

## 依赖（手动）

```bat
cd %USERPROFILE%\.vidau\jianying-draft-compiler
uv sync --extra windows
```

需包含：`uiautomation` `pyautogui` `pywin32` `Pillow` `numpy` `rapidocr-onnxruntime`。

改完 controller / vision 后请在本机重装/同步 `jy-compile`（或 `uv sync` 后指向最新 vendor）。
