# L3 - User Layer (Second Brain)

## Purpose

The user layer is your personal knowledge space. This is your "second brain" where you define who you are, what you value, and what you're learning.

**Important**: This is YOUR space. AI can suggest changes but must be transparent and get your confirmation.

## Directory Structure

```
L3_User/
├── 00-L3-MOC.md              # L3 index and navigation
├── 01-Identity/              # Self-knowledge
│   ├── 01-Identity-MOC.md
│   ├── USER.md               # Your self-definition
│   ├── contacts.json         # Important relationships
│   ├── devices.json          # Device inventory
│   └── 99-Templates/         # Personal templates
├── 02-Themes/                # Theme insights
│   ├── 02-Themes-MOC.md
│   ├── procrastination.md    # Example: overcoming procrastination
│   ├── health.md             # Example: health management
│   └── ...                   # Your themes
├── 03-Learning/              # Learning and growth
│   ├── 03-Learning-MOC.md
│   ├── Language/
│   │   ├── en/               # English learning
│   │   └── jp/               # Japanese learning
│   └── Skills/               # Other skills
└── 04-Definitions/           # Term definitions
    └── definitions.md
```

## 01-Identity/ - Self-Knowledge

**Purpose**: Who you are, how you work, what matters to you

**Files**:
- `USER.md`: Self-profile, routines, preferences
- `contacts.json`: Important people in your life
- `devices.json`: Your tech setup

**AI Permission**: Suggest only, require confirmation

## 02-Themes/ - Theme Insights

**Purpose**: Recurring patterns, ongoing investigations, personal insights

**Example Themes**:
- `procrastination.md`: Understanding and overcoming procrastination
- `health.md`: Health management strategies
- `productivity.md`: Personal productivity system
- `decision-making.md`: How you make decisions

**Format**:
```markdown
# Theme: Procrastination

## Core Insight
Root cause is perfectionism, not laziness.

## Strategies
1. Break tasks into 2-minute starts
2. Focus on progress, not perfection
3. Track obstacles

## Related
- [[productivity]]
- [[decision-making]]

## History
- 2026-01-15: First identified perfectionism link
- 2026-02-20: 2-minute rule proved effective
```

**AI Permission**: Can auto-update based on conversations, but must log changes

## 03-Learning/ - Learning & Growth

**Purpose**: Skill acquisition tracking

**Language Learning** (`Language/`):
- `en/`: English vocabulary, phrases, shadowing texts
- `jp/`: Japanese vocabulary, grammar notes

**Other Skills** (`Skills/`):
- Programming languages
- Professional skills
- Hobbies

**AI Permission**: Can auto-update progress

## 04-Definitions/ - Term Definitions

**Purpose**: Your personal dictionary

**Format**:
```markdown
# Definitions

## Project Loop
**Meaning**: Hypothesis → Reality → Insight cycle
**Source**: Personal framework
**Related**: [[decision-making]]

## MCP
**Meaning**: Model Context Protocol
**Source**: Anthropic
**Context**: AI tool integration standard
```

**AI Permission**: Can add new terms

## Modification Log

Every change to L3 is logged in `L0_Working/scratchpad.md`:

```markdown
## 📋 L3 Memory Update - 2026-03-16 15:20

**Location:** `L3_User/02-Themes/procrastination.md`
**Type:** New Insight
**Trigger:** User said "I realized..."

**Changes:**
+ [New] Added: "Perfectionism is the root cause"
```

## User Control

- **Review**: Daily review shows all L3 changes
- **Confirm**: Batch confirm during daily review
- **Rollback**: Can revert from change log
- **Read-only**: Add `ai_readonly: true` to file frontmatter
