---
name: daily-report
description: 生成主播业绩日报，包含飞书数据导出、AI点评分析、上传飞书文档、发送通知。触发词："生成主播业绩日报"、"日报"、"/streaming_report"
version: v1.1
last_updated: 2026-03-18
---

> **变更历史:** [CHANGELOG.json](./CHANGELOG.json)
> **模式归属:** 📊 ops (运营模式)
> **斜杠命令:** `/report`

# 直播业绩日报系统

自动生成主播业绩日报并上传到飞书，支持发送消息通知。

---

## 完整工作流

```
┌─────────────────────────────────────────────────────────────────┐
│  步骤 1: 导出飞书数据                                           │
│  → 调用飞书 API 导出多维表格为 xlsx                             │
│  → 输出: jarvis-memory/data/直播每日数据.xlsx                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  步骤 2: 生成日报                                               │
│  → 读取 Excel 数据，计算各项指标                                 │
│  → 输出: jarvis-memory/L0_Working/reports/主播业绩日报_{日期}.md │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  步骤 3: AI 点评分析                                             │
│  → 使用 report_insight skill 分析日报并追加点评建议              │
│  → 更新: jarvis-memory/L0_Working/reports/主播业绩日报_{日期}.md │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  步骤 4: 上传并转文档                                           │
│  → 上传 Markdown 文件                                           │
│  → 创建导入任务转为飞书在线文档                                  │
│  → 输出: 飞书 docx 链接                                         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  步骤 5: 发送通知                                               │
│  → 发送文档链接给指定用户（小松、胡总）                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 使用方式

### 手动执行（完整流程）

**命令：** `/streaming_report` 或 "生成主播业绩日报"

```
生成主播业绩日报，发送给小松和胡总。
```

Claude 会自动执行：
1. 运行 `scripts/generate_report.py` 导出数据并生成日报（内置飞书导出功能）
2. 使用 `report_insight` skill 进行 AI 点评分析
3. 运行 `scripts/upload_to_feishu.py` 上传飞书
4. 运行 `scripts/send_notification.py` 发送通知给小松和胡总

### 单独执行某一步骤

```bash
# 只生成日报（不含 AI 点评）
python .claude/skills/daily_report/scripts/generate_report.py

# 只上传飞书
python .claude/skills/daily_report/scripts/upload_to_feishu.py

# 发送通知
python .claude/skills/daily_report/scripts/send_notification.py <用户> <链接>
```

---

## 自动触发检测（v1.1 新增）

本 Skill 支持智能场景路由自动检测。

### 检测逻辑

启动时检查 `.claude/.pending_signal.json`：

1. **文件存在且 timestamp 在 5 分钟内？**
2. **scene 匹配 "operation"？**
3. **符合条件 → 按 scene-router 配置预加载记忆**
4. **清理 signal 文件，进入正常执行流程**

### 预加载内容

当检测到运营场景信号时，自动预加载：
- L0: `scratchpad.md`（今日工作记录）
- `jarvis-memory/data/` 数据目录
- `jarvis-memory/L0_Working/reports/` 历史日报

### 触发示例

```
用户: "生成今天的主播日报"
    ↓ Signal Hook 检测到 operation 场景 (confidence: 0.9)
    ↓ 写入 .pending_signal.json
    ↓ daily_report 启动
    ↓ 检测到信号，预加载相关记忆
    ↓ 执行日报生成流程
```

### 手动触发（无信号时）

如果信号不存在或过期，按原有触发词逻辑执行：
- "生成主播业绩日报"
- "日报"
- "/streaming_report"

---

## 定时任务设置

### Windows 任务计划程序

1. **打开任务计划程序**
   - Win+R 输入 `taskschd.msc` 回车

2. **创建基本任务**
   - 名称: `主播业绩日报`
   - 触发器: 每天 08:00（或其他时间）
   - 操作: "启动程序"
     - 程序/脚本: `claude`
     - 添加参数: `-p "生成主播业绩日报，发送给小松和胡总" -d E:\AI_program\Jarvis`

---

## 配置文件

### `.claude/agents/config/feishu-config.md`

```yaml
## API 凭证
app_id: "cli_a917cdf0b5399cd2"
app_secret: "BGvGSt5mZ6ra6gWM2uw82ciILheQJB0g"

## 文件夹
FOLDER_TOKEN: "A3tWfWzyxlESe5dOrSsczwHJnwf"  # 日报文件夹

## 用户 open_id
胡总: "ou_59475f003ce0fe225a5be09615a72925"
小松: "ou_560b1ed72f8280eced3527b689f44cd4"

## 多维表格：直播每日数据
app_token: "FOjMbU3oEaiH9DskfvEclydBnkf"
table_id: "tblRBXvqOVu6wHEr"
```

---

## 日报结构

| 章节 | 内容 |
|------|------|
| 一、整体汇总 | 14项指标 + 环比 |
| 二、主播排名 | 14项维度排名 |
| 三、主播时段细分 | 每时段详细数据 |
| 四、最佳时段分析 | GMV/ROI/转化率最高 |
| 五、基准对比 | 7日/30日双基准 |
| 六、点评与建议 | AI 分析建议（通过 report_insight skill） |

---

## 关键计算公式

```
利润 = GMV × (1 - 退款率) - GMV × (1 - 退款率) × (43/66) - 千川消耗
ROI = GMV / 千川消耗
单位时长GMV = GMV / 时长
```

---

## 评级说明

| 符号 | 含义 |
|------|------|
| 🟢 | 超基准 +10% 以上 |
| ➡️ | 基准 ±10% 以内 |
| ⚠️ | 低于基准 -10%~-20% |
| 🔴 | 低于基准 -20% 以下 |

---

## 文件目录结构

```
jarvis-memory/
├── data/
│   └── 直播每日数据.xlsx          # 飞书导出的原始数据
└── L0_Working/
    └── reports/
        └── 主播业绩日报_*.md      # 生成的日报文件

.claude/skills/daily_report/scripts/
├── generate_report.py            # 日报生成脚本
├── upload_to_feishu.py           # 上传脚本
├── send_notification.py          # 通知脚本
└── feishu_token.py               # Token管理
```

---

## 清理规则

**自动管理：**
- 数据文件：`jarvis-memory/data/直播每日数据.xlsx` - 每次导出自动覆盖
- 日报文件：`jarvis-memory/L0_Working/reports/主播业绩日报_*.md` - 按日期生成

**归档建议：**
- 历史日报可定期归档到 `jarvis-memory/L1_Episodic/Reports/`
- 旧数据文件无需保留，源数据在飞书多维表格中
