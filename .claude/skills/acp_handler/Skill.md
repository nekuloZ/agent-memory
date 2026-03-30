---
name: acp-handler
description: Use when receiving ACP (Agent Communication Protocol) messages from Director (OpenClaw), or when user forwards agent task results with /acp or specific keywords.
version: v2.0
last_updated: 2026-03-23
---

> **变更历史:** [CHANGELOG.json](./CHANGELOG.json)
> **模式归属:** 🤖 assist
> **系统:** Jarvis ↔ Director Team
> **数据层:** Supabase (acp_tasks / worker_tasks / task_events)

---

## 触发条件

**显式触发:**
- 用户输入 `/acp` 或 `/acp-handler`
- 用户消息包含 "来自 Director"
- 用户消息包含 "任务完成通知"

**隐式触发:**
- 检测到 ACP 消息格式（包含任务ID `acp-`、执行结果等字段）

---

## Supabase 配置

```
URL:      https://bvaykseswlcysfqgxldz.supabase.co
ANON_KEY: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ2YXlrc2Vzd2xjeXNmcWd4bGR6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjkxNDAxOTUsImV4cCI6MjA4NDcxNjE5NX0.UcwduJhBy0kmumv9DCvl-3uUZ7fKCpWY7uLFTbexxww
```

**Jarvis 直接使用 Supabase MCP 工具**（`mcp__supabase__execute_sql`），无需 HTTP 调用。

---

## 状态机

```
acp_tasks:
  pending → in_progress → awaiting_confirmation → confirmed → archived
                ↓                  ↓
            blocked            in_progress（Jarvis 要求修改）
```

---

## 场景 1: 查看待确认任务

**触发:** 用户说 `/acp`，或 Director 通知有任务完成

### Step 1: 查询待确认任务

```sql
SELECT task_id, title, result_status, result_summary,
       deliverables, completed_at
FROM acp_tasks
WHERE status = 'awaiting_confirmation'
ORDER BY completed_at DESC;
```

### Step 2: 如果有待确认任务，展示摘要

```
📬 有 {N} 个任务等待确认

━━━━━━━━━━━━━━━━━━━━━━━━
[1] {task_id} · {title}
    状态: ✅ 成功 / ⚠️ 部分完成 / ❌ 失败
    完成时间: {completed_at}
    交付物: {deliverables}
    摘要: {result_summary}
━━━━━━━━━━━━━━━━━━━━━━━━

操作: [确认归档] [要求修改] [查看详情]
```

### Step 3: 等待用户操作

**用户说"确认"或"归档":**

```sql
-- 1. 确认
UPDATE acp_tasks
SET status = 'confirmed'
WHERE task_id = '{task_id}';

-- 2. 写事件
INSERT INTO task_events (acp_task_id, actor, action, from_status, to_status, message)
SELECT id, 'jarvis', 'confirmed', 'awaiting_confirmation', 'confirmed', '用户确认完成'
FROM acp_tasks WHERE task_id = '{task_id}';

-- 3. 归档
UPDATE acp_tasks
SET status = 'archived'
WHERE task_id = '{task_id}';

INSERT INTO task_events (acp_task_id, actor, action, from_status, to_status)
SELECT id, 'jarvis', 'archived', 'confirmed', 'archived'
FROM acp_tasks WHERE task_id = '{task_id}';
```

**用户说"要求修改"并说明原因:**

```sql
UPDATE acp_tasks
SET status = 'in_progress'
WHERE task_id = '{task_id}';

INSERT INTO task_events (acp_task_id, actor, action, from_status, to_status, message)
SELECT id, 'jarvis', 'revision_requested', 'awaiting_confirmation', 'in_progress', '{用户说明的修改原因}'
FROM acp_tasks WHERE task_id = '{task_id}';
```

回复: `✅ 已退回，Director 会看到任务重新变为 in_progress 状态。`

---

## 场景 2: Jarvis 提交新任务给 Director

**触发:** 用户描述一个要交给 Director 执行的任务

### Step 1: 生成任务 ID

```sql
-- 查询今天的最大序号
SELECT task_id
FROM acp_tasks
WHERE task_id LIKE 'acp-{YYYYMMDD}-%'
ORDER BY task_id DESC
LIMIT 1;
```

新序号 = 最大序号 + 1，格式化为 3 位：`acp-{YYYYMMDD}-{NNN}`

### Step 2: 确认任务信息

向用户确认以下字段（未提供的可询问）：
- `title` - 任务名称（必填）
- `description` - 任务描述（必填）
- `priority` - P0 / P1 / P2（默认 P1）
- `requirements` - 验收标准/交付物列表
- `background` - 背景信息（可选）
- `estimated_hours` - 预计耗时（可选）

### Step 3: 写入数据库

```sql
INSERT INTO acp_tasks (
  task_id, title, description, background,
  requirements, priority, estimated_hours
) VALUES (
  '{task_id}',
  '{title}',
  '{description}',
  '{background}',
  '{requirements_json}',   -- [{"item": "交付物1", "done": false}]
  '{priority}',
  {estimated_hours}
);

INSERT INTO task_events (acp_task_id, actor, action, to_status, message)
SELECT id, 'jarvis', 'created', 'pending', '任务已提交给 Director'
FROM acp_tasks WHERE task_id = '{task_id}';
```

### Step 4: 确认回复

```
✅ 任务已提交

任务ID: {task_id}
标题: {title}
优先级: {priority}
状态: pending（等待 Director 接取）

Director 会在下次 HEARTBEAT 时读取并开始处理。
```

---

## 场景 3: 查询任务状态

**触发:** 用户问"任务进展怎样"、"XX任务做完了吗"

```sql
-- 查所有活跃任务
SELECT task_id, title, status, priority, updated_at
FROM acp_tasks
WHERE status NOT IN ('archived')
ORDER BY
  CASE priority WHEN 'P0' THEN 0 WHEN 'P1' THEN 1 ELSE 2 END,
  updated_at DESC;
```

```sql
-- 查某个任务的完整事件流
SELECT e.created_at, e.actor, e.action, e.from_status, e.to_status, e.message
FROM task_events e
JOIN acp_tasks t ON t.id = e.acp_task_id
WHERE t.task_id = '{task_id}'
ORDER BY e.created_at ASC;
```

展示格式：
```
📋 任务状态

{task_id} · {title}
状态: {status_emoji} {status}
优先级: {priority}
最后更新: {updated_at}

事件流:
→ {time} [{actor}] {action}: {message}
→ ...
```

---

## Director/Worker 的 HTTP 调用参考

Director 和 Worker 通过 REST API 操作数据库（在各自的 SOUL.md 中配置）：

```bash
# Director 接取任务（pending → in_progress）
curl -X PATCH "{SUPABASE_URL}/rest/v1/acp_tasks?task_id=eq.{task_id}" \
  -H "apikey: {ANON_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"status": "in_progress"}'

# Director 汇报完成（in_progress → awaiting_confirmation）
curl -X PATCH "{SUPABASE_URL}/rest/v1/acp_tasks?task_id=eq.{task_id}" \
  -H "apikey: {ANON_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "awaiting_confirmation",
    "result_status": "success",
    "result_summary": "...",
    "deliverables": ["path/to/file"]
  }'

# Worker 查询待处理任务
curl "{SUPABASE_URL}/rest/v1/worker_tasks?worker=eq.worker-dev&status=eq.pending" \
  -H "apikey: {ANON_KEY}"

# Worker 更新进度
curl -X PATCH "{SUPABASE_URL}/rest/v1/worker_tasks?task_id=eq.{task_id}" \
  -H "apikey: {ANON_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"status": "in_progress", "progress_pct": 60}'

# 写事件日志
curl -X POST "{SUPABASE_URL}/rest/v1/task_events" \
  -H "apikey: {ANON_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"acp_task_id": "{uuid}", "actor": "director", "action": "started", ...}'
```

---

## 相关资源

- **数据库表:** `acp_tasks` / `worker_tasks` / `task_events`
- **Supabase 项目:** https://bvaykseswlcysfqgxldz.supabase.co
- **Director SOUL:** `E:/AI_program/Jarvis/.openclaw/Director/SOUL.md`
