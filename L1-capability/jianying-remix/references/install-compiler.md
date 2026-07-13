# 安装本机 jianying-draft-compiler

Skill 依赖本机 CLI：`jy-compile`。  
**来源**：与本 skill 同一 Git 仓库  
`https://github.com/vidaudeveloper/creative-agent`  
路径：`tools/jianying-draft-compiler/`

## 用户一键安装（推荐）

装 **全部 Skills** 时会**自动**装编译器（`scripts/install-skills.mjs` 末尾调用）：

```bash
git clone --depth 1 https://github.com/vidaudeveloper/creative-agent.git /tmp/creative-agent-skill
node /tmp/creative-agent-skill/scripts/install-skills.mjs --force
export PATH="$HOME/.vidau/bin:$PATH"
jy-compile where
```

详见 [docs/SETUP.md](../../../docs/SETUP.md)。

仅装编译器（不装 skill）：

```bash
# 需要：git、uv、Python 3.11+
bash tools/install-jy-compile.sh
# 或已 clone 后：
# bash creative-agent/tools/install-jy-compile.sh
export PATH="$HOME/.vidau/bin:$PATH"
jy-compile where
```

跳过编译器：`node scripts/install-skills.mjs --force --skip-compiler`

安装结果：

- 源码缓存：`~/.vidau/cache/creative-agent`（或本机已有 checkout）
- 稳定入口：`~/.vidau/jianying-draft-compiler` → 指向上述源码
- CLI：`~/.vidau/bin/jy-compile`

## Agent / 开发机

若 skill 已通过 `pnpm skills:install` 装到本机，优先跑：

```bash
bash <skill-root>/L1-capability/jianying-remix/scripts/ensure-compiler.sh
```

会优先用仓库内 `tools/jianying-draft-compiler`，没有再走 GitHub。

## 环境变量（可选）

| 变量 | 默认 | 作用 |
|------|------|------|
| `VIDAU_JY_COMPILER_REPO` | `https://github.com/vidaudeveloper/creative-agent.git` | 克隆地址 |
| `VIDAU_JY_COMPILER_REF` | `main` | 分支 |
| `VIDAU_JY_COMPILER_SUBPATH` | `tools/jianying-draft-compiler` | 仓内子路径 |
| `VIDAU_JY_COMPILER_SRC` | （空） | 强制用本地目录 |
| `VIDAU_JY_COMPILER_HOME` | `~/.vidau/jianying-draft-compiler` | 安装链接位置 |

## 依赖

- Python **3.11+**
- [uv](https://docs.astral.sh/uv/)：`curl -LsSf https://astral.sh/uv/install.sh | sh`
- git
- 已安装**剪映专业版**，并至少打开过一次

## 验证

```bash
export PATH="$HOME/.vidau/bin:$PATH"
jy-compile where
# 期望：.../Movies/JianyingPro/User Data/Projects/com.lveditor.draft
```

Windows 自动导出（可选、**非 skill 默认流程**）：

```bat
jy-compile export-check
:: 若 ok=false，在安装目录执行: uv sync --extra windows
```

详见 [windows-export.md](windows-export.md)。**jianying-remix skill 已屏蔽自动导出**，导入后请用户在剪映「本地草稿」查看并手动导出。

## 对用户话术

> 首次使用剪映混剪需安装本机草稿编译器（一次性，来自 VidAU skill 仓库）。执行：  
> `curl -fsSL https://raw.githubusercontent.com/vidaudeveloper/creative-agent/main/tools/install-jy-compile.sh | bash`  
> 装好后我会把混剪写入剪映草稿箱；请你**退出重开剪映**，在「本地草稿」打开预览，需要成片时自行导出。

**不要**在未验证 `jy-compile where` 成功时声称「已导入剪映」。
