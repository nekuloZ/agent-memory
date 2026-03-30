# 跨平台适配指南

Agent Memory System 支持 Windows、macOS 和 Linux 三大平台。

## 平台差异总览

| 功能 | Windows | macOS | Linux |
|------|---------|-------|-------|
| Claude Code | ✅ 原生支持 | ✅ 原生支持 | ✅ 原生支持 |
| Obsidian | ✅ 原生支持 | ✅ 原生支持 | ✅ 原生支持 |
| PowerShell 脚本 | ✅ | ❌ | ❌ |
| Bash 脚本 | ❌ (WSL可用) | ✅ | ✅ |
| 路径分隔符 | `\` | `/` | `/` |
| 环境变量配置 | 系统属性 | `.zshrc` | `.bashrc` |

## Windows 配置

### 环境变量设置

#### 方法1: PowerShell (推荐)

```powershell
# 临时设置（当前会话）
$env:GEMINI_API_KEY = "your_api_key"
$env:SUPABASE_URL = "https://your-project.supabase.co"
$env:SUPABASE_ANON_KEY = "your_anon_key"

# 永久设置（用户级）
[Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "your_api_key", "User")
[Environment]::SetEnvironmentVariable("SUPABASE_URL", "your_url", "User")

# 永久设置（系统级，需要管理员权限）
[Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "your_api_key", "Machine")
```

#### 方法2: 系统属性 GUI

1. Win + R → 输入 `sysdm.cpl` → 回车
2. "高级" 标签 → "环境变量"
3. "用户变量" → "新建"
4. 添加变量名和值

#### 方法3: .env 文件（推荐用于项目）

```powershell
# 在项目根目录创建 .env 文件
notepad .env
```

### PowerShell Profile 配置

```powershell
# 编辑 PowerShell 配置
notepad $PROFILE

# 如果文件不存在，先创建
if (!(Test-Path -Path $PROFILE)) {
    New-Item -ItemType File -Path $PROFILE -Force
}
```

在 `$PROFILE` 中添加：

```powershell
# Agent Memory System 配置
$env:AGENT_MEMORY_PATH = "C:\Users\$env:USERNAME\agent-memory"

# 加载 .env 文件
$envFile = "$env:AGENT_MEMORY_PATH\.env"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match "^([^#][^=]+)=(.+)$") {
            [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
        }
    }
}

# 快捷命令
function archive {
    python "$env:AGENT_MEMORY_PATH\tools\memory_search\process_logs.py" --daily-logs
}
function search-rag {
    param([string]$query)
    python "$env:AGENT_MEMORY_PATH\tools\memory_search\smart_search.py" $query
}
function habit {
    python "$env:AGENT_MEMORY_PATH\tools\habit_tracker.py" show
}

# 别名
Set-Alias -Name arc -Value archive
Set-Alias -Name srag -Value search-rag
```

### 路径处理

Windows 使用反斜杠 `\`，但在 Python 中建议用 `pathlib`：

```python
from pathlib import Path

# 跨平台路径
base_path = Path.home() / "agent-memory" / "memory"
# Windows: C:\Users\Name\agent-memory\memory
# macOS: /Users/Name/agent-memory/memory
```

### 定时任务（Windows Task Scheduler）

```powershell
# 创建每日归档任务
$action = New-ScheduledTaskAction -Execute "python" -Argument "$env:AGENT_MEMORY_PATH\tools\daily_reminder.py"
$trigger = New-ScheduledTaskTrigger -Daily -At "21:00"
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "AgentMemory-DailyReminder" -Description "Agent Memory System 每日提醒"
```

## macOS 配置

### 环境变量设置

#### 方法1: .zshrc (推荐，使用 zsh)

```bash
# 编辑 zsh 配置
nano ~/.zshrc

# 添加以下内容
export AGENT_MEMORY_PATH="$HOME/agent-memory"
export GEMINI_API_KEY="your_api_key"
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_ANON_KEY="your_anon_key"

# 快捷命令
alias archive='python $AGENT_MEMORY_PATH/tools/memory_search/process_logs.py --daily-logs'
alias search-rag='python $AGENT_MEMORY_PATH/tools/memory_search/smart_search.py'
alias habit='python $AGENT_MEMORY_PATH/tools/habit_tracker.py show'

# 重新加载配置
source ~/.zshrc
```

#### 方法2: .bash_profile (使用 bash)

```bash
# 编辑 bash 配置
nano ~/.bash_profile

# 添加相同内容（见上）

# 重新加载
source ~/.bash_profile
```

### launchd 定时任务

创建 `~/Library/LaunchAgents/com.agentmemory.daily.plist`：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.agentmemory.daily</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/Users/YOURNAME/agent-memory/tools/daily_reminder.py</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>21</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
</dict>
</plist>
```

加载任务：

```bash
launchctl load ~/Library/LaunchAgents/com.agentmemory.daily.plist
```

### 路径处理

```python
from pathlib import Path

base_path = Path.home() / "agent-memory" / "memory"
# /Users/Name/agent-memory/memory
```

## Linux 配置

### 环境变量设置

```bash
# 编辑 bash 配置
nano ~/.bashrc

# 或编辑 zsh 配置
nano ~/.zshrc

# 添加内容（同 macOS）
```

### Systemd 定时任务

创建 `~/.config/systemd/user/agent-memory-daily.timer`：

```ini
[Unit]
Description=Agent Memory Daily Reminder Timer

[Timer]
OnCalendar=*-*-* 21:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

创建 `~/.config/systemd/user/agent-memory-daily.service`：

```ini
[Unit]
Description=Agent Memory Daily Reminder

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 %h/agent-memory/tools/daily_reminder.py
```

启用：

```bash
systemctl --user daemon-reload
systemctl --user enable agent-memory-daily.timer
systemctl --user start agent-memory-daily.timer
```

## 跨平台脚本编写

### Python 脚本（推荐）

```python
#!/usr/bin/env python3
"""跨平台路径处理示例"""

import os
import platform
from pathlib import Path

def get_memory_path():
    """获取记忆系统根目录"""
    # 优先从环境变量读取
    env_path = os.getenv("AGENT_MEMORY_PATH")
    if env_path:
        return Path(env_path)

    # 默认路径
    home = Path.home()
    return home / "agent-memory"

def get_platform_info():
    """获取平台信息"""
    return {
        "system": platform.system(),  # Windows, Darwin, Linux
        "release": platform.release(),
        "user": os.getenv("USER") or os.getenv("USERNAME"),
    }

def setup_environment():
    """根据平台设置环境"""
    system = platform.system()

    if system == "Windows":
        # Windows 特定设置
        os.environ["PYTHONIOENCODING"] = "utf-8"
    elif system == "Darwin":
        # macOS 特定设置
        pass
    elif system == "Linux":
        # Linux 特定设置
        pass

if __name__ == "__main__":
    print(f"Memory path: {get_memory_path()}")
    print(f"Platform: {get_platform_info()}")
```

### Shell 脚本

```bash
#!/bin/bash
# cross-platform.sh

# 检测平台
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    PLATFORM="Windows"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="macOS"
else
    PLATFORM="Linux"
fi

echo "Detected platform: $PLATFORM"

# 设置路径
if [ "$PLATFORM" == "Windows" ]; then
    MEMORY_PATH="${USERPROFILE}/agent-memory"
else
    MEMORY_PATH="${HOME}/agent-memory"
fi

echo "Memory path: $MEMORY_PATH"
```

## API 配置矩阵

| API | Windows | macOS | Linux | 获取方式 |
|-----|---------|-------|-------|----------|
| **Gemini** | `setx GEMINI_API_KEY xxx` | `export GEMINI_API_KEY=xxx` | `export GEMINI_API_KEY=xxx` | [Google AI Studio](https://makersuite.google.com) |
| **Supabase** | `setx SUPABASE_URL xxx` | `export SUPABASE_URL=xxx` | `export SUPABASE_URL=xxx` | [Supabase Dashboard](https://app.supabase.io) |
| **OpenClaw** | `setx OPENCLAW_API_KEY xxx` | `export OPENCLAW_API_KEY=xxx` | `export OPENCLAW_API_KEY=xxx` | 自建实例 |
| **飞书** | `setx FEISHU_APP_ID xxx` | `export FEISHU_APP_ID=xxx` | `export FEISHU_APP_ID=xxx` | [飞书开放平台](https://open.feishu.cn) |

## Obsidian 跨平台配置

### Vault 路径

| 平台 | 默认 Vault 路径 |
|------|-----------------|
| Windows | `C:\Users\[Name]\agent-memory\memory` |
| macOS | `~/agent-memory/memory` |
| Linux | `~/agent-memory/memory` |

### 同步方案

#### 方案1: Obsidian Sync (官方)
- 跨平台同步
- 端到端加密
- 付费服务 ($4/月)

#### 方案2: Git + GitHub
```bash
# 在 memory 目录初始化 git
cd memory
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/username/obsidian-vault.git
git push -u origin main
```

#### 方案3: Syncthing (免费)
- 点对点同步
- 无需服务器
- 跨平台支持

## 常见问题

### Windows 中文显示乱码

```powershell
# 设置 UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# 或在系统设置中启用 Beta: Unicode UTF-8
```

### macOS Python 版本

```bash
# 安装 Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装 Python 3.9+
brew install python@3.11

# 设置别名
alias python3='/opt/homebrew/bin/python3.11'
```

### Linux 权限问题

```bash
# 确保脚本可执行
chmod +x tools/*.py

# 如果安装在系统目录，可能需要
sudo chown -R $USER:$USER ~/agent-memory
```
