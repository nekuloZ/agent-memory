# Agent Memory System

一个为 AI Agent 设计的四层记忆系统，支持渐进式加载、RAG 语义搜索、Obsidian 集成和多 Agent 协作。

## 核心概念

```
L0 - Working Layer    (短期记忆 - 当前对话)
L1 - Episodic Layer   (长期记忆 - 历史记录)
L2 - Procedural Layer (AI记忆 - 技能/协议)
L3 - User Layer       (第二大脑 - 主题/洞察)
```

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/agent-memory.git
cd agent-memory
```

### 2. 安装依赖

```bash
# Python 3.9+
pip install -r requirements.txt

# Obsidian (推荐)
# 下载 Obsidian 并打开 memory 目录作为 Vault
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入你的 API 密钥
```

### 4. 启动

```bash
# 初始化目录结构
python scripts/init.py

# 启动 RAG 服务（可选）
python tools/memory_search/setup_env.ps1  # Windows
python tools/memory_search/setup_env.sh   # macOS/Linux
```

## 目录结构

```
agent-memory/
├── memory/           # 记忆存储目录（Obsidian Vault）
│   ├── L0_Working/         # 工作层：今日待办、当前任务
│   ├── L1_Episodic/        # 长期层：日报、项目、人际关系
│   ├── L2_Procedural/      # AI层：技能文档、参考协议
│   └── L3_User/            # 用户层：主题洞察、学习记录
├── .claude/skills/         # Claude Code Skills
├── tools/                  # 工具脚本
└── docs/                   # 详细文档
```

## 核心功能

| 功能 | 说明 | 触发词 |
|------|------|--------|
| **Session Startup** | 会话启动时加载上下文 | "早上好" / "hey jarvis" |
| **Daily Review** | 日归档 + RAG索引 | "复盘" / "Archive" |
| **Weekly Review** | 周归档 + 习惯统计 | "周归档" / "WeeklyArchive" |
| **Memory Loader** | 渐进式记忆加载 | 自动触发 |
| **RAG Search** | 语义搜索历史 | "之前..." / "上次..." |

## 文档导航

- [架构设计](docs/ARCHITECTURE.md) - 四层记忆系统详解
- [安装配置](docs/SETUP.md) - 详细安装步骤
- [日常使用](docs/WORKFLOW.md) - 日/周工作流程
- [跨平台适配](docs/CROSS_PLATFORM.md) - Windows/macOS/Linux
- [多Agent协作](docs/MULTI_AGENT.md) - OpenClaw 兼容

## 技术栈

- **存储**: Markdown + JSON (Obsidian 兼容)
- **RAG**: Gemini Embedding + Supabase/pgvector
- **Skills**: Claude Code Skill 框架
- **搜索**: 关键词 + 语义混合搜索

## 许可证

MIT
