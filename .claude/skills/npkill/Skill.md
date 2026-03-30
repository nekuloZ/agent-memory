---
name: npkill
description: Clean up node_modules and .next folders to free up disk space. Scans for build artifacts, shows sizes, and lets you selectively delete. Works in non-interactive environments.
---

# NPkill - Node.js and Next.js Build Artifact Cleaner

## Purpose

Clean up accumulated `node_modules` and `.next` folders that consume disk space. This skill works in non-interactive environments by scanning, showing sizes, and letting you choose what to delete.

## When to Use This Skill

- Disk space is running low
- Old projects need cleanup
- Before archiving inactive projects
- Regular development maintenance

## How It Works

### Step 1: Scan

Scans the current directory (or specified path) for:
- `node_modules` folders
- `.next` folders (Next.js build artifacts)

### Step 2: Display Results

Shows each folder with its size in MB/GB, sorted by size (largest first).

### Step 3: Select & Delete

You choose which folders to delete. The skill confirms before deleting.

## Usage

### Basic Usage (scan current directory)

```
/npkill
```

### Scan Specific Directory

```
/npkill E:\AI_program
```

### Target Only .next Folders

```
/npkill --target .next
```

### Target Only node_modules

```
/npkill --target node_modules
```

## Safety Features

- Shows sizes before any deletion
- Requires confirmation before deleting
- Only scans specified directory (not entire system)
- Dry-run by default - you must explicitly confirm deletions

## What Gets Deleted

When you confirm deletion, the skill removes:
- The selected `node_modules` folder (can restore with `npm install`)
- The selected `.next` folder (can rebuild with `npm run build`)

## Example Output

```
Found 6 node_modules folders:

Folder                              Size
-----                              ----
nano-banana-next-abandoned         520 MB
SillyTavern                        380 MB
Feishu Bitable AI Analyst          125 MB
autoplan                            45 MB
calculator                          23 MB
daliy                               12 MB

Total: 1.1 GB

Which folders would you like to delete?
```

## Tips

1. **Inactive projects**: Safe to delete - restore with `npm install` when needed
2. **Active projects**: Keep `node_modules` to avoid reinstall time
3. **Next.js projects**: `.next` folder is safe to delete - rebuilds on next `npm run dev`
4. **Before cleanup**: Make sure you have package.json if you plan to reinstall later
