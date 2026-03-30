---
name: continuous-learning
description: Use when user says "/instinct-status", "/evolve", "/promote", "查看学习状态", "技能进化", "提升技能优先级", or asks about learning patterns and skill evolution.
trigger:
  - /instinct-status
  - /evolve
  - /promote
  - "查看学习状态"
  - "技能进化"
  - "提升技能优先级"
  - "学习本能"
version: "1.0"
---

> **变更历史:** [CHANGELOG.json](./CHANGELOG.json)
> **模式归属:** 🤖 assist

# Continuous Learning v2 - 持续学习系统

基于 ECC 的 instinct-based learning，自动检测技能使用模式，建议进化方向。

---

## 核心概念

### 学习本能 (Instincts)

| 本能 | 说明 |
|------|------|
| **技能使用模式** | 检测高频使用的技能 |
| **时间敏感任务** | 检测特定时间触发的任务 |
| **模式切换模式** | 预测用户的模式切换行为 |

### 技能状态

| 状态 | 说明 |
|------|------|
| **learning** | 学习中，收集使用数据 |
| **stable** | 稳定，已验证可靠 |
| **evolved** | 已进化，优先级提升 |

---

## 命令

### /instinct-status - 查看学习本能状态

**触发词：**
- "/instinct-status"
- "查看学习状态"
- "学习本能"

**执行：**
```bash
node scripts/learning.js status
```

**输出示例：**
```
╔══════════════════════════════════════════════════════════╗
║           🧠 Jarvis 学习本能状态 v1.0                    ║
╠══════════════════════════════════════════════════════════╣
║ 📊 技能使用统计:                                         ║
║   task_completion    12次 ████████                       ║
║   habit_tracker       8次 █████                          ║
║   mode-switcher       5次 ███                            ║
╠══════════════════════════════════════════════════════════╣
║ 🌟 进化候选 (使用≥5次):                                  ║
║   • mode-switcher - 建议提升优先级                       ║
╠══════════════════════════════════════════════════════════╣
║ 🔍 学习本能:                                             ║
║   ○ 技能使用模式 (置信度: 60%)                           ║
║   ○ 时间敏感任务 (置信度: 40%)                           ║
║   ○ 模式切换模式 (置信度: 50%)                           ║
╚══════════════════════════════════════════════════════════╝
```

---

### /evolve - 技能进化

**触发词：**
- "/evolve"
- "技能进化"
- "进化技能"

**执行：**
```bash
node scripts/learning.js evolve
```

**进化条件：**
- 技能使用次数 ≥ 5
- 当前状态为 "learning"

**进化效果：**
- 优先级提升（P3→P2→P1）
- 状态变为 "stable"
- 置信度 +20%

---

### /promote - 提升技能优先级

**触发词：**
- "/promote [skill-name]"
- "提升 [skill-name] 优先级"

**执行：**
```bash
node scripts/learning.js promote <skill-name>
```

**示例：**
```bash
node scripts/learning.js promote habit_tracker
```

---

## 数据结构

### 存储位置

```
.claude/learning/
├── instincts.json      # 学习本能定义
└── skill-usage.json    # 技能使用记录
```

### skill-usage.json 格式

```json
{
  "skills": {
    "skill_name": {
      "count": 10,
      "last_used": "2026-03-18T15:30:00Z",
      "priority": "P1",
      "confidence": 0.8,
      "status": "stable",
      "evolution_history": []
    }
  }
}
```

---

## 集成

### 自动记录

其他 skills 应在触发后记录使用：

```bash
node scripts/learning.js record <skill-name>
```

### 与 mode-switcher 集成

切换模式时自动分析模式切换模式：
- 记录切换时间
- 检测切换规律
- 预测下次切换

---

## 设计理念

**为什么需要持续学习？**

| 问题 | 解决方案 |
|------|---------|
| 技能优先级固定 | 根据实际使用动态调整 |
| 无法识别用户习惯 | 学习模式，主动预测 |
| 新技能难以推广 | 进化机制，逐步提升优先级 |

---

> **Related:** [mode-switcher](../mode-switcher/Skill.md) | scripts/learning.js
