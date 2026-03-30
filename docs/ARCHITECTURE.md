# Agent Memory System 架构设计

## 四层记忆模型

```
┌─────────────────────────────────────────────────────────────┐
│  L3 - User Layer (第二大脑)                                  │
│  用户定义的知识、价值观、长期洞察                             │
│  memory/L3_User/                                     │
├─────────────────────────────────────────────────────────────┤
│  L2 - Procedural Layer (AI记忆)                              │
│  AI的程序性知识、技能协议、参考文档                           │
│  memory/L2_Procedural/ + .claude/skills/             │
├─────────────────────────────────────────────────────────────┤
│  L1 - Episodic Layer (长期记忆)                              │
│  情景记忆、项目历史、人际关系、日报                           │
│  memory/L1_Episodic/                                 │
├─────────────────────────────────────────────────────────────┤
│  L0 - Working Layer (短期记忆)                               │
│  短期记忆、当前任务、习惯数据、待办看板                       │
│  memory/L0_Working/                                  │
└─────────────────────────────────────────────────────────────┘
```

## 各层详细说明

### L0 - Working Layer (工作层)

**访问频率**: 每次对话
**存储位置**: `memory/L0_Working/`
**文件类型**: Markdown, JSON

| 文件 | 用途 | 更新频率 |
|------|------|----------|
| `scratchpad.md` | 今日对话摘要、核心洞察、未闭环事项 | 实时 |
| `next_actions_kanban.md` | 待办看板（原子动作级别） | 实时 |
| `habit_data.json` | 习惯追踪数据（睡眠、洗澡等） | 每日 |
| `.current_task.json` | 当前活跃任务上下文 | 任务切换时 |

**加载策略**: SessionStart 时必载

### L1 - Episodic Layer (长期层)

**访问频率**: 按需加载
**存储位置**: `memory/L1_Episodic/`
**组织方式**: MOCs (Map of Content) + 时间序列

| 目录 | 内容类型 | 预加载策略 |
|------|----------|------------|
| `01-Daily/` | 每日归档日志 | 最近7天 + 提及日期 |
| `02-Projects/` | 项目文档（按类型分子MOC） | 活跃项目 + 提及项目名 |
| `03-Relationships/` | 人际关系档案 | 提及人名匹配 |
| `04-Weekly/` | 周归档 | 本周 + 提及周数 |
| `05-Essays/` | 随笔/文章 | 手动加载 |
| `06-Financial/` | 财务记录 | 手动加载 |
| `99-Archive/` | 历史归档 | 不预加载 |

**加载策略**: 关键词匹配 + 时间衰减

### L2 - Procedural Layer (AI层)

**访问频率**: 启动时 + 触发时
**存储位置**:
- `memory/L2_Procedural/`
- `.claude/skills/`

| 目录 | 内容 | 用途 |
|------|------|------|
| `core/` | 核心机制文档 | 记忆系统协议 |
| `reference/docs/` | 参考文档 | 技术方案、决策记录 |
| `reference/protocols/` | 协议规范 | Agent 行为准则 |
| `reference/templates/` | 模板文件 | 日报/周报模板 |

**Skills 目录** (`.claude/skills/`):
- `memory_loader/` - 渐进式记忆加载
- `session_startup/` - 会话启动处理
- `daily_review_archiver/` - 日归档
- `weekly_review_archiver/` - 周归档
- `theme_insight_tracker/` - 主题洞察追踪

### L3 - User Layer (第二大脑)

**访问频率**: 会话开始时
**存储位置**: `memory/L3_User/`
**特点**: 用户自己维护，AI 可建议但需透明记录

| 目录 | 内容 | AI权限 |
|------|------|--------|
| `01-Identity/` | 自我认知、设备清单、重要关系 | 建议，需确认 |
| `02-Themes/` | 主题洞察（拖延、健康、学习等） | 可自动更新 |
| `03-Learning/` | 学习记录（语言、技能） | 可自动更新 |
| `04-Definitions/` | 术语定义 | 可添加 |

**L3 修改记录规范**: 每次修改必须记录到 `L0_Working/scratchpad.md`

## 渐进式加载机制

```
用户请求
    │
    ▼
[Stage 0] L0 自动加载（必载）
    │ - scratchpad.md
    │ - next_actions_kanban.md
    │ - habit_data.json
    │
    ▼
[Stage 1] 意图识别 → 确定加载范围
    │ - 分析用户 query 关键词
    │ - 匹配预定义加载规则
    │
    ▼
[Stage 2] 提及层加载（关键词匹配）
    │ - 根据文件夹路径预加载相关文档
    │ - 利用 Obsidian 双链预加载关联笔记
    │
    ▼ 质量足够？
    ├── 是 → 直接回复 ✅
    │
    └── 否 → [Stage 3] 语义搜索补充
               - Gemini Embedding 向量搜索
               - 补充召回相关历史记录
```

## 关键词预加载规则

| 用户 Query 包含 | 预加载文件夹 |
|----------------|-------------|
| "项目..."、"Project..." | `L1_Episodic/02-Projects/` |
| "昨天..."、"上周..." | `L1_Episodic/01-Daily/` |
| "张三..."、"李四..." | `L1_Episodic/03-Relationships/` |
| "课题..."、"主题..." | `L3_User/02-Themes/` |

## 上下文优先级标记

- **P0 (主上下文)**: 用户直接提及的文件
- **P1 (关联上下文)**: 通过 Obsidian 双链关联的文件
- **P2 (背景上下文)**: 语义搜索召回的文件

## RAG 语义搜索

### 存储范围

**应该进 RAG**:
- 项目决策和原因
- 技术方案选型
- 关键洞察（"我发现..."）
- 重要约定

**不应该进 RAG**:
- 日常流水账
- 已完成的临时任务
- 纯数据记录（睡眠几点等）

### 触发时机

| 场景 | 触发条件 |
|------|----------|
| 自动触发 | 用户问"之前..."、"上次..." |
| 手动触发 | 用户说"搜索记忆" |
| 归档时 | 日归档后自动同步高价值内容 |

### 分层搜索策略

```
Stage 1: 关键词搜索 (~200ms)
    ↓ 质量不足？
Stage 2: Gemini 语义搜索 (~1.2s)
```

## Obsidian 集成

### MOCs 组织方式

```
memory/
├── 00-Memory-MOC.md          # 记忆系统总入口
├── L0_Working/
├── L1_Episodic/
│   ├── 00-L1-MOC.md          # L1 总索引
│   ├── 01-Daily/
│   │   ├── 01-Daily-MOC.md   # 日报索引
│   │   └── YYYY-MM-DD.md
│   └── 02-Projects/
│       ├── 02-Projects-MOC.md
│       ├── MOC-Dev.md        # 开发类项目
│       └── MOC-Learning.md   # 学习类项目
└── L3_User/
    ├── 00-L3-MOC.md
    └── 02-Themes/
        └── 02-Themes-MOC.md
```

### 双链预加载

读取文件时自动提取 `[[wikilinks]]`，预加载关联笔记：

```python
# 伪代码
file_content = read("L1_Episodic/02-Projects/ai-video.md")
links = extract_wikilinks(file_content)  # [[Seedance]], [[Kling]]
for link in links:
    preload_with_lower_priority(link)
```

## 数据流图

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  用户输入    │────▶│ 意图识别     │────▶│ 记忆加载器   │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                                │
                       ┌────────────────────────┼────────────────────────┐
                       │                        │                        │
                       ▼                        ▼                        ▼
               ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
               │ L0 Working   │      │ L1 Episodic  │      │ L2/L3 Layer  │
               │ (自动加载)    │      │ (按需加载)    │      │ (搜索加载)    │
               └──────────────┘      └──────────────┘      └──────────────┘
                       │                        │                        │
                       └────────────────────────┼────────────────────────┘
                                                │
                                                ▼
                                       ┌─────────────┐
                                       │  RAG 语义搜索 │
                                       │ (兜底补充)   │
                                       └─────────────┘
```
