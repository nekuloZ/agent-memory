# 日常使用流程

## 核心使用模式

Agent Memory System 围绕三个核心流程设计：

1. **Session Startup** - 会话启动时加载上下文
2. **Daily Review** - 每日结束时归档和索引
3. **Weekly Review** - 每周结束时回顾和规划

## Session Startup (会话启动)

### 触发方式

- 自动触发：Claude Code SessionStart Hook
- 手动触发："早上好" / "中午好" / "晚上好" / "hey jarvis"

### 执行流程

```
用户：早上好
    ↓
[Step 1] 获取当前时间
    ↓
[Step 2] 加载意图矩阵
    ↓
[Step 3] 场景检测
    ├── 同一日多会话 → 加载 L0，延续话题
    ├── 新的一天首次 → 加载 L0 + 昨日日报
    └── /clear 恢复 → 加载 L0 + 上次断点
    ↓
[Step 4] 生成简报
    - 问候 + 状态一句话
    - 今日焦点（建议优先处理 + 预计耗时）
    - 其他待办
    - 主动询问支持
```

### 输出示例

```
早上好，昨晚 8 小时，状态应该在线。

【今日焦点】
昨天把 session_startup 和 OpenClaw 都收尾了，进度不错。
→ 建议优先：Seedance 视频测试（上班族迟到 12 镜）
→ 预计：1-2 小时可以出第一批视频
→ 下一步：确认分镜脚本，然后批量生成

【其他待办】
- Seedance2.0 Web 应用（搭建中，不急）
- 接入 Seedance 2.0 API（还在等官方开放）

需要我先帮你准备什么材料吗？
```

## Daily Review (日归档)

### 触发方式

- "复盘"
- "Archive"
- "总结今天"

### 执行流程

```
用户：Archive
    ↓
[Step 1] 读取 L0 数据
    - scratchpad.md
    - next_actions_kanban.md
    - habit_data.json
    - .current_task.json
    ↓
[Step 2] 展示计划（等待确认）
    显示：昨日产出、待办状态、习惯数据
    询问：确认执行吗？
    ↓
[Step 3] 用户确认后执行
    1. 生成 Daily Log (Markdown)
       路径：L1_Episodic/01-Daily/YYYY-MM-DD.md

    2. 生成 JSON (数据分析)
       路径：L1_Episodic/01-Daily/.data/YYYY-MM-DD.json

    3. 更新文件
       - .current_task.json
       - next_actions_kanban.md
       - habit_data.json

    4. 标记 scratchpad
       追加：## 📅 每日归档 - YYYY-MM-DD
    ↓
[Step 4] RAG 索引提取（可选）
    分析当日内容，提取高价值片段：
    - 项目决策
    - 主题洞察
    - 问题方案
    - 人际约定

    展示候选，用户确认后存入 RAG
```

### RAG 索引提取示例

```
══════════════════════════════════════════════════
RAG索引候选（可选）
══════════════════════════════════════════════════

[1] 项目决策 - Seedance
    内容: 改用Web方案绕过API限制...
    [Y/n]

[2] 主题洞察 - 克服拖延
    内容: 拖延根源是完美主义恐惧...
    [Y/n]

输入要跳过的编号，或回车全部确认：
>

[存储结果]
✓ 项目决策 → projects/Seedance
✓ 主题洞察 → themes/克服拖延
```

## Weekly Review (周归档)

### 触发方式

- "周归档"
- "WeeklyArchive"

### 执行流程

```
用户：WeeklyArchive
    ↓
[Step 1] 读取本周数据
    - 本周所有 Daily Logs
    - habit_data.json 历史
    - 项目进展
    ↓
[Step 2] 生成周报
    路径：L1_Episodic/04-Weekly/YYYY-WXX.md

    内容：
    - 本周完成的主要任务
    - 各项目进展
    - 习惯统计（平均睡眠、目标达成率）
    - 下周计划
    ↓
[Step 3] 更新系统
    - 清空 scratchpad（周清理）
    - 归档旧 Daily Logs
    - 更新项目状态
```

## 记忆检索流程

### 方式1: 关键词搜索（快速）

```
用户：之前说的那个项目...
    ↓
AI：根据关键词匹配 L1/L2/L3 层文件
    ↓
返回：直接读取相关文件内容
```

### 方式2: 语义搜索（精准）

```
用户：搜索记忆 "Seedance 为什么不用 API"
    ↓
AI：[Stage 1] 关键词搜索 → 无高质量结果
    ↓
AI：[Stage 2] RAG 语义搜索
    → 命中：projects/Seedance | decision
       "决策：改用Web方案绕过API限制"
    ↓
返回：精准答案
```

### 方式3: 渐进式加载（自动）

```
用户：关于拖延，我好像总结过方法
    ↓
AI：[Stage 0] 加载 L0
AI：[Stage 1] 意图识别 → 主题查询
AI：[Stage 2] 加载 L3_User/02-Themes/克服拖延.md
AI：[Stage 3] 评估质量 → 已找到相关内容
    ↓
返回：主题洞察内容
```

## 主题洞察追踪

### 触发方式

- "我发现..."
- "原来..."
- "意识到..."

### 执行流程

```
用户：我发现拖延不是因为懒，是完美主义导致的
    ↓
AI：识别为洞察表达
    ↓
[Step 1] 更新 L3_User/02-Themes/克服拖延.md
    添加新的洞察点
    ↓
[Step 2] 记录到 scratchpad
    核心洞察部分
    ↓
[Step 3] 提示用户
    "已记录到主题洞察（克服拖延），日复盘时可选入RAG索引"
```

## 习惯追踪

### 触发方式

- "昨晚X点睡Y点起"
- "今天洗澡了"
- "/habit"

### 数据结构

```json
{
  "metadata": { "version": "1.0", "last_updated": "YYYY-MM-DD" },
  "targets": { "sleep": "22:30", "wake": "06:00", "sleep_hours": 7.5 },
  "today": {
    "date": "YYYY-MM-DD",
    "actual_sleep": "HH:MM",
    "actual_wake": "HH:MM",
    "sleep_duration_hours": 7.0,
    "predicted_energy": "充沛"
  },
  "history": [],
  "last_shower_date": "YYYY-MM-DD"
}
```

## 最佳实践

### 每日流程

```
早上：
  → "早上好" 启动会话，查看简报

白天：
  → 完成任务后说 "完成了" 自动归档
  → 有洞察时说 "我发现..." 自动记录
  → 临时想法用 "要做..." 添加到看板

晚上：
  → "Archive" 执行日复盘
  → 确认 RAG 索引候选
```

### 每周流程

```
周日晚上：
  → "WeeklyArchive" 执行周归档
  → 回顾本周完成
  → 规划下周重点
```

### 提示词速查

| 你想... | 说... |
|---------|-------|
| 开始工作 | "早上好" / "hey jarvis" |
| 完成任务 | "完成了" / "搞定了" |
| 记录洞察 | "我发现..." / "意识到..." |
| 添加待办 | "要做..." / "记得..." |
| 日归档 | "Archive" / "复盘" |
| 周归档 | "WeeklyArchive" / "周归档" |
| 搜索记忆 | "搜索..." / "之前说的..." |
| 记录睡眠 | "昨晚X点睡Y点起" |
| 查看习惯 | "/habit" |

## 故障排除

### 记忆加载慢

- 检查 RAG 搜索结果是否过多
- 考虑减少 L1 层历史数据
- 定期归档旧日志到 99-Archive

### 搜索结果不准

- 使用更具体的关键词
- 确保内容已建立 RAG 索引
- 检查向量数据库连接

### Skills 不触发

- 检查触发词是否正确
- 查看 Claude Code 日志
- 确认 Skill 文件位置正确
