# L0 - Working Layer (Short-term Memory)

## Purpose

The working layer contains ephemeral, session-level context that changes frequently throughout the day.

## Files

| File | Purpose | Update Frequency |
|------|---------|------------------|
| `scratchpad.md` | Today's conversation summary, core insights, unclosed items | Real-time |
| `next_actions_kanban.md` | Todo kanban board (atomic action level) | Real-time |
| `habit_data.json` | Habit tracking data (sleep, shower, etc.) | Daily |
| `.current_task.json` | Current active task context | On task switch |

## scratchpad.md Structure

```markdown
# AI Short-term Memory - YYYY-MM-DD

## Quick Overview
| Dimension | Status |
|-----------|--------|
| Date | YYYY-MM-DD |
| Weekday | Monday |
| Session Time | 09:57 - |
| Sleep | - |
| Energy | - |
| Today's Focus | - |

## Core Insights
(Record key discoveries today)

## Today's Decisions
(Record important decisions made)

## Unclosed Items
- [ ] Task A (status)
- [ ] Task B (status)

## Today's Conversation Summary

1. **[Topic]** Time
   - Action: What was done
   - Result: Outcome

## Daily Archive Marker
<!-- Archive marker will be appended here -->
```

## habit_data.json Structure

```json
{
  "metadata": {
    "version": "1.0",
    "last_updated": "YYYY-MM-DD"
  },
  "targets": {
    "sleep": "22:30",
    "wake": "06:00",
    "sleep_hours": 7.5
  },
  "today": {
    "date": "YYYY-MM-DD",
    "actual_sleep": "HH:MM",
    "actual_wake": "HH:MM",
    "sleep_duration_hours": 7.0,
    "predicted_energy": "high"
  },
  "history": [],
  "last_shower_date": "YYYY-MM-DD"
}
```

## Loading Strategy

- **Session Start**: Always auto-loaded (Stage 0)
- **Priority**: P0 (Primary Context)
- **Retention**: Weekly cleanup

## Workflow

1. Throughout day: AI updates based on conversation
2. End of day: "Archive" command moves summary to L1
3. Weekly: Scratchpad is cleared
