# L2 - Procedural Layer (AI Memory)

## Purpose

The procedural layer contains AI's procedural knowledge, skills, protocols, and reference documents. This is the AI's "how-to" knowledge.

## Directory Structure

```
L2_Procedural/
├── core/                     # Core mechanisms
│   ├── memory_system_protocol.md
│   └── rag_indexing_rules.md
├── reference/
│   ├── docs/                 # Reference documents
│   │   ├── thinking_frameworks.md
│   │   ├── decision_templates.md
│   │   └── troubleshooting_guides.md
│   ├── protocols/            # Protocol specifications
│   │   ├── l3_modification_protocol.md
│   │   └── session_startup_protocol.md
│   └── templates/            # Templates
│       ├── daily_log_template.md
│       ├── weekly_log_template.md
│       └── l3_update_log_template.md
└── README.md
```

## Core Protocols

### L3 Modification Protocol

When AI modifies L3 (User Layer):
1. Must be transparent to user
2. Must log to `L0_Working/scratchpad.md`
3. User can review and rollback

```markdown
## 📋 L3 Memory Update - YYYY-MM-DD HH:mm

**Location:** `L3_User/02-Themes/{theme}.md`
**Type:** New Insight / Data Update / Add Link
**Trigger:** [What triggered this change]

**Changes:**
+ [New] Discovered new pattern: ...
+ [Update] Progress from X% → Y%
+ [Link] Linked to [[theme-name]]
```

### Session Startup Protocol

See `reference/protocols/session_startup_protocol.md`

## Reference Documents

### Available Frameworks

- **Project Loop**: Hypothesis → Reality → Insight
- **Decision Framework**: Options → Criteria → Decision → Reason
- **Troubleshooting**: Problem → Attempt → Solution → Prevention

## Usage

These documents are:
- Loaded when relevant skills trigger
- Referenced during complex tasks
- Updated as protocols evolve

## Modification Guidelines

- AI can update L2 to improve performance
- Changes should be logged in CHANGELOG.json
- Major changes require user confirmation
