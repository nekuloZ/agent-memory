#!/usr/bin/env python3
"""
Agent Memory System Initialization Script

Usage:
    python scripts/init.py
"""

import os
import json
from pathlib import Path
from datetime import datetime


def get_memory_path():
    """Get memory system root path"""
    env_path = os.getenv("AGENT_MEMORY_PATH")
    if env_path:
        return Path(env_path)

    # Default: ~/agent-memory
    return Path.home() / "agent-memory"


def create_directory_structure(base_path):
    """Create L0-L4 directory structure"""

    directories = [
        # L0 - Working
        "memory/L0_Working",

        # L1 - Episodic
        "memory/L1_Episodic/01-Daily/.data",
        "memory/L1_Episodic/02-Projects",
        "memory/L1_Episodic/03-Relationships",
        "memory/L1_Episodic/04-Weekly",
        "memory/L1_Episodic/05-Essays",
        "memory/L1_Episodic/06-Financial",
        "memory/L1_Episodic/99-Archive",

        # L2 - Procedural
        "memory/L2_Procedural/core",
        "memory/L2_Procedural/reference/docs",
        "memory/L2_Procedural/reference/protocols",
        "memory/L2_Procedural/reference/templates",

        # L3 - User
        "memory/L3_User/01-Identity/99-Templates",
        "memory/L3_User/02-Themes",
        "memory/L3_User/03-Learning/Language/en",
        "memory/L3_User/03-Learning/Language/jp",
        "memory/L3_User/03-Learning/Skills",
        "memory/L3_User/04-Definitions",

        # Tools
        "tools/memory_search",
    ]

    for dir_path in directories:
        full_path = base_path / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"[OK] Created: {dir_path}")


def create_initial_files(base_path):
    """Create initial template files"""

    today = datetime.now().strftime("%Y-%m-%d")

    # L0: scratchpad.md
    scratchpad_content = f"""# AI Short-term Memory - {today}

> **Yesterday Archive:** -
> **Week Archive:** -

> **Purpose:** Claude's short-term memory, record observations and insights
> **Archive:** Daily review appends summary, weekly review clears

---

## Quick Overview

| Dimension | Status |
|-----------|--------|
| **Date** | {today} |
| **Weekday** | {datetime.now().strftime("%A")} |
| **Session Time** | - |
| **Sleep** | - |
| **Energy** | - |
| **Today's Focus** | - |

---

## Core Insights

(Waiting to record)

---

## Today's Decisions

(Waiting to record)

---

## Unclosed Items

- [ ] Initialize Agent Memory System

---

## Today's Conversation Summary

(Waiting to record)

---

## Daily Archive Marker
"""

    scratchpad_path = base_path / "memory/L0_Working/scratchpad.md"
    if not scratchpad_path.exists():
        scratchpad_path.write_text(scratchpad_content, encoding="utf-8")
        print(f"[OK] Created: scratchpad.md")

    # L0: habit_data.json
    habit_data = {
        "metadata": {"version": "1.0", "last_updated": today},
        "targets": {"sleep": "22:30", "wake": "06:00", "sleep_hours": 7.5},
        "today": {"date": today},
        "history": [],
        "last_shower_date": ""
    }

    habit_path = base_path / "memory/L0_Working/habit_data.json"
    if not habit_path.exists():
        habit_path.write_text(json.dumps(habit_data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[OK] Created: habit_data.json")

    # L0: next_actions_kanban.md
    kanban_content = """# Next Actions Kanban

## In Progress
- [ ] Initialize Agent Memory System

## Todo

## Done

---

Last updated: """ + today + "\n"

    kanban_path = base_path / "memory/L0_Working/next_actions_kanban.md"
    if not kanban_path.exists():
        kanban_path.write_text(kanban_content, encoding="utf-8")
        print(f"[OK] Created: next_actions_kanban.md")

    # L0: .current_task.json
    current_task = {
        "active_tasks": [],
        "completed_today": [],
        "day_count": 0,
        "last_session": ""
    }

    task_path = base_path / "memory/L0_Working/.current_task.json"
    if not task_path.exists():
        task_path.write_text(json.dumps(current_task, indent=2), encoding="utf-8")
        print(f"[OK] Created: .current_task.json")


def create_moc_files(base_path):
    """Create Map of Content (MOC) index files"""

    # 00-Memory-MOC.md
    memory_moc = """---
title: Agent Memory System Overview
type: moc
---

# Memory System Navigation

## Layer Overview
- [[L0_Working/README]] - Short-term Memory (Today)
- [[L1_Episodic/README]] - Long-term Memory (History)
- [[L2_Procedural/README]] - AI Memory (Skills/Protocols)
- [[L3_User/README]] - Second Brain (Personal Knowledge)

## Quick Access
- [[L0_Working/scratchpad]] - Today's Workspace
- [[L0_Working/next_actions_kanban]] - Todo Board

## Recent Updates
- Initialize Agent Memory System

---

> **Tip**: Use Obsidian backlinks [[like this]] to connect ideas.
"""

    moc_path = base_path / "memory/00-Memory-MOC.md"
    if not moc_path.exists():
        moc_path.write_text(memory_moc, encoding="utf-8")
        print(f"[OK] Created: 00-Memory-MOC.md")


def check_env_file(base_path):
    """Check if .env file exists"""

    env_path = base_path / ".env"
    env_example = base_path / ".env.example"

    if not env_path.exists() and env_example.exists():
        print(f"[WARN] .env file not found")
        print(f"[INFO] Please copy .env.example to .env and configure your API keys")


def main():
    print("=" * 60)
    print("Agent Memory System - Initialization")
    print("=" * 60)

    base_path = get_memory_path()
    print(f"\nMemory Path: {base_path}")
    print()

    # Create directories
    print("Creating directory structure...")
    create_directory_structure(base_path)
    print()

    # Create initial files
    print("Creating initial files...")
    create_initial_files(base_path)
    print()

    # Create MOC files
    print("Creating MOC index files...")
    create_moc_files(base_path)
    print()

    # Check env
    check_env_file(base_path)
    print()

    print("=" * 60)
    print("Initialization Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Configure .env file with your API keys")
    print("2. Open memory folder in Obsidian")
    print("3. Say 'hey jarvis' to start using the system")
    print()


if __name__ == "__main__":
    main()
