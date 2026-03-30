# L1 - Episodic Layer (Long-term Memory)

## Purpose

The episodic layer stores historical records organized by time and topic. This is your personal history.

## Directory Structure

```
L1_Episodic/
├── 00-L1-MOC.md              # L1 index and navigation
├── 01-Daily/                 # Daily logs (time-based)
│   ├── 01-Daily-MOC.md       # Daily log index
│   └── YYYY-MM-DD.md         # Individual daily logs
├── 02-Projects/              # Project documents
│   ├── 02-Projects-MOC.md    # Projects index
│   ├── MOC-Dev.md            # Development projects
│   ├── MOC-Learning.md       # Learning projects
│   └── {project-name}.md     # Individual project files
├── 03-Relationships/         # People and relationships
│   └── {person-name}.md      # Individual person files
├── 04-Weekly/                # Weekly reviews
│   └── YYYY-WXX.md           # Individual weekly reviews
├── 05-Essays/                # Essays and articles
├── 06-Financial/             # Financial records
└── 99-Archive/               # Historical archives
```

## 01-Daily/ - Daily Logs

**Purpose**: Archive of each day's activities and outcomes

**Format**: `YYYY-MM-DD.md`

**Template**:
```markdown
---
type: daily_log
title: "YYYY-MM-DD | Weekday"
date: YYYY-MM-DD
weekday: "Monday"
---

## What Did You Discover Today

## What Did You Decide Today

## Project Progress
- [[Project Name]]: Specific progress

## Today's Data
| Metric | Value |
|--------|-------|
| Sleep | X hours |
| Energy | High/Medium/Low |
```

## 02-Projects/ - Project Documents

**Purpose**: Long-running project documentation

**Format**: `{project-name}.md`

**Structure**:
```markdown
# Project Name

## Project Goal

## Project Log

### YYYY-MM-DD
**[Time] Activity**

- **Project Loop:**
  - **Hypothesis:** What was assumed
  - **Reality:** What actually happened
  - **Insight:** Key learning

**Completed:**
- ✅ Task A

**Next:**
- ⏳ Task B
```

## Loading Strategy

| Directory | Preload Trigger |
|-----------|-----------------|
| 01-Daily | "Yesterday", date mentions |
| 02-Projects | Project name mentions |
| 03-Relationships | Person name mentions |
| 04-Weekly | Week number mentions |

## Retention Policy

- Active (last 30 days): 01-Daily/, active projects
- Reference (30-90 days): All accessible
- Archive (90+ days): Move to 99-Archive/

## RAG Indexing

Not all content goes to RAG. Only index:
- Project decisions and reasons
- Technical solutions
- Key insights
- Important commitments
