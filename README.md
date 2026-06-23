# Yichip AI 脚手架

开箱即用的 AI 辅助开发环境 —— VS Code + Kilo Code，免配置。

## 使用方式

### 方式 A：从这里开始新项目（推荐）

直接复制本仓库作为模板创建新项目

### 方式 B：给已有项目加上 AI 支持

将以下文件复制到你的项目根目录：
- `AGENTS.md`
- `.kilo/` 整个目录


### 首次配置

1. 安装 VS Code (https://code.visualstudio.com/thank-you?dv=win64user)
1. VS Code 扩展商店搜索安装 **Kilo Code**
2. Kilo Code 面板 → 齿轮(设置) → 提供商 → 查看更多 → Deepseek → 填入 API Key
3. 还没有 Key？联系葛嘉昊

## 环境检查

```powershell
.\check-env.ps1
```

检查项：VS Code 安装状态、Kilo Code 插件、API Key 配置、脚手架文件完整性。

## 文件结构

```
项目目录/
├── check-env.ps1            # 环境检查脚本（只读）
├── AGENTS.md                # AI 工作规范（数据红线、代码风格、嵌入式原则）
├── .kilo/
│   ├── kilo.jsonc           # 主配置（模型、权限、skill 路径）
│   ├── command/             # 自定义命令
│   │   ├── 使用指南.md       # /使用指南 — 新手入门
│   │   └── 报销指南.md       # /报销指南 — 费用报销流程
│   └── skills/              # 本地 skill（caveman、grill-me 等）
└── ...                      # 其余项目文件
```

## 常用命令

| 命令 | 说明 |
|------|------|
| `/使用指南` | 新手入门：AI 能做什么、怎么提问、省钱技巧、报错怎么办 |
| `/报销指南` | AI 费用报销流程（有票/无票、OA 操作步骤） |

## 经验分享

有效的 prompt / skill / 工作流 → 贡献到 `\\192.168.2.16\public\AI`，有价值产出有奖励。
