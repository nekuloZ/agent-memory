# 多 Agent 协作配置

Agent Memory System 支持多 Agent 协作，包括本地 Claude Code 和远程 OpenClaw 实例。

## 架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                    用户 (You)                                │
└──────────────┬──────────────────────────────┬───────────────┘
               │                              │
               ▼                              ▼
┌──────────────────────────┐    ┌──────────────────────────┐
│   Claude Code (本地)      │    │   OpenClaw (VPS远程)      │
│   - 日常开发协作          │    │   - Discord Bot          │
│   - 文件操作              │    │   - 定时任务             │
│   - 本地工具集成          │    │   - 后台服务             │
└──────┬───────────────────┘    └──────┬───────────────────┘
       │                               │
       └──────────────┬────────────────┘
                      │
                      ▼
        ┌─────────────────────────┐
        │   共享记忆层            │
        │   - Supabase (RAG)     │
        │   - GitHub (文档同步)   │
        │   - 飞书 (通知)        │
        └─────────────────────────┘
```

## 全局 Agent 协议

### 配置文件

`.claude/skills/global_agent_protocol/config.json`:

```json
{
  "agent_id": "claude_local|openclaw_vps|mobile_client",
  "agent_name": "Claude Local",
  "user_id": "your_user_id",
  "supabase": {
    "project_url": "https://xxxx.supabase.co",
    "anon_key": "sb_publishable_xxx"
  },
  "sync_interval_minutes": 10,
  "active_hours": {
    "start": "08:00",
    "end": "23:00"
  }
}
```

### 跨 Agent 同步规则

| 时机 | 行为 | 目标 |
|------|------|------|
| 会话启动 | 读取其他 Agent 状态 | Supabase |
| 任务开始 | 标记 active | Supabase + 本地 |
| 任务进展 | 每10分钟或对话结束 | Supabase |
| 任务完成 | 写入历史 | Supabase + 本地 |

### 简报生成规范

每个 Agent 汇报时必须包含：

```
早上好。

【昨日进展】
- 我的领域：在[任务]上花了[X]分钟，卡在[问题]

【其他Agent动态】
- [Agent名]：处理了[任务]，[状态]

【建议】
基于全局视角...
```

## OpenClaw 集成

### 部署架构

```
VPS (Ubuntu 22.04)
├── OpenClaw Docker
│   ├── Dashboard (127.0.0.1:18789)
│   ├── Discord Bot
│   └── API Server
├── SearXNG (搜索服务)
└── SSH 隧道 (AutoSSH)

本地 Windows
├── WSL (Ubuntu)
│   └── AutoSSH 隧道
└── 浏览器 → localhost:18789 (隧道)
```

### VPS 部署步骤

1. **创建 VPS** (推荐 2核4G+)

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 安装 Docker Compose
sudo apt install docker-compose-plugin
```

2. **部署 OpenClaw**

```bash
mkdir -p ~/openclaw && cd ~/openclaw

# 创建 docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  openclaw:
    image: ghcr.io/yourusername/openclaw:latest
    container_name: openclaw
    restart: unless-stopped
    ports:
      - "127.0.0.1:18789:18789"  # 仅本地访问
    environment:
      - DISCORD_BOT_TOKEN=${DISCORD_BOT_TOKEN}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - CLAUDE_API_KEY=${CLAUDE_API_KEY}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
EOF

# 启动
docker compose up -d
```

3. **配置 SSH 隧道**

本地 WSL：

```bash
# 安装 AutoSSH
sudo apt install autossh

# 创建隧道脚本
cat > ~/openclaw-tunnel.sh << 'EOF'
#!/bin/bash
export AUTOSSH_POLL=60
export AUTOSSH_GATETIME=30
autossh -M 20000 -N \
  -L 18789:localhost:18789 \
  -i ~/.ssh/openclaw.pem \
  user@vps-ip \
  -o ServerAliveInterval=60 \
  -o ServerAliveCountMax=3
EOF

chmod +x ~/openclaw-tunnel.sh

# Windows 任务计划：开机启动 WSL 脚本
# schtasks /create /tn "OpenClaw-Tunnel" /tr "wsl -d Ubuntu ~/openclaw-tunnel.sh" /sc onlogon
```

### 多账户路由

OpenClaw 支持多飞书账号并行：

```yaml
# openclaw-config.yml
accounts:
  default:
    app_id: cli_xxx
    app_secret: xxx
    encrypt_key: xxx
    verification_token: xxx

  agent-1:
    app_id: cli_yyy
    app_secret: yyy
    encrypt_key: yyy
    verification_token: yyy

  agent-2:
    app_id: cli_zzz
    app_secret: zzz
    encrypt_key: zzz
    verification_token: zzz

routing:
  default: default
  by_group:
    "直播运营群": agent-1
    "数据监控群": agent-2
```

## 记忆同步策略

### 同步范围

| 数据类型 | 本地 Claude | OpenClaw | 同步方式 |
|----------|-------------|----------|----------|
| L0 Working | ✅ 主写 | ❌ 只读 | 实时 API |
| L1 Episodic | ✅ 主写 | ✅ 只读 | Git 同步 |
| L2 Procedural | ✅ 共享 | ✅ 共享 | Git 同步 |
| L3 User | ✅ 主写 | ❌ 只读 | 定时同步 |
| RAG 向量 | ✅ 共享 | ✅ 共享 | Supabase |

### Git 同步工作流

```bash
# 1. 初始化中央仓库
git init --bare agent-memory-sync.git

# 2. 本地配置
cd ~/agent-memory
git remote add sync ssh://vps/agent-memory-sync.git

# 3. 定时同步脚本 (cron/任务计划)
#!/bin/bash
cd ~/agent-memory || exit 1
git add -A
git commit -m "Auto sync: $(date '+%Y-%m-%d %H:%M')" || true
git pull sync main --rebase || true
git push sync main || true
```

### 冲突解决策略

```python
# conflict_resolver.py
def resolve_conflict(local_content, remote_content, file_path):
    """
    根据文件类型选择冲突解决策略
    """
    if "L0_Working" in file_path:
        # 本地优先
        return local_content
    elif "L1_Episodic" in file_path:
        # 合并（按时间排序）
        return merge_by_time(local_content, remote_content)
    elif "L2_Procedural" in file_path:
        # 手动解决提示
        return create_conflict_marker(local_content, remote_content)
    else:
        # 最新时间戳优先
        return local_content if is_newer(local_content) else remote_content
```

## Agent 间通信

### 通过共享 RAG

```python
# Agent A 写入
def notify_other_agents(message, target_agent=None):
    store_to_rag(
        content=message,
        item_type="notification",
        domain="system",
        metadata={
            "from": current_agent_id,
            "to": target_agent or "all",
            "priority": "normal"
        }
    )

# Agent B 读取
def check_notifications():
    results = search_rag(
        query="notification",
        filter={"metadata.from": {"$ne": current_agent_id}}
    )
    return results
```

### 通过飞书消息

```python
# 发送跨 Agent 通知
async def send_to_agent(target_agent, message):
    feishu = FeishuClient()

    # 查找目标 Agent 的接收群
    group_map = {
        "claude_local": "本地开发群",
        "openclaw_vps": "VPS监控群"
    }

    group = group_map.get(target_agent)
    if group:
        await feishu.send_message(group, f"[{current_agent}] {message}")
```

## 使用场景示例

### 场景1: 本地开发，远程监控

```
用户 (本地 Claude):
  "帮我部署这个服务到 VPS"
    ↓
  生成部署脚本
  通过 SSH 执行
    ↓
  OpenClaw (VPS):
  监控服务状态
  异常时 Discord 通知
```

### 场景2: 跨 Agent 任务接力

```
用户 (手机 Discord):
  "@openclaw 帮我查一下昨天的数据"
    ↓
  OpenClaw:
  查询需要本地文件
  发送接力请求到 Claude
    ↓
  Claude Code (本地):
  读取本地文件
  分析并返回结果
  同步到共享 RAG
    ↓
  OpenClaw:
  从 RAG 获取结果
  回复用户
```

### 场景3: 分布式记忆

```
Claude (本地):
  "我发现了一个很好的视频生成方案"
  记录到 L3_User/02-Themes/AI视频.md
  同步到 Git
    ↓
OpenClaw (读取 Git):
  "用户之前提到过视频生成方案"
  从共享记忆获取上下文
  提供更精准的建议
```

## 配置检查清单

### 本地 Claude Code

- [ ] `.claude/skills/` 已配置
- [ ] `global_agent_protocol/config.json` 已创建
- [ ] SSH 密钥可访问 VPS
- [ ] Git 可推送中央仓库

### VPS OpenClaw

- [ ] Docker 运行正常
- [ ] Discord Bot 已连接
- [ ] 可访问共享 RAG (Supabase)
- [ ] 定时任务已配置

### 共享基础设施

- [ ] Supabase 项目运行中
- [ ] Git 中央仓库可访问
- [ ] 飞书应用已配置（如需要）

## 故障排除

### 问题：Agent 间记忆不同步

**检查：**
1. Git 同步是否正常运行
2. Supabase 连接是否正常
3. 时间戳是否一致

**解决：**
```bash
# 强制同步
git fetch origin
git reset --hard origin/main
python tools/resync_rag.py  # 重新同步向量库
```

### 问题：OpenClaw 无法访问本地文件

**原因：** OpenClaw 在 VPS，无法直接访问本地文件系统

**解决：**
- 需要本地文件时，使用 SSH/SCP 传输
- 或使用共享存储（如 S3、网盘）

### 问题：多个 Agent 同时修改冲突

**解决：**
- L0 层：本地优先
- L1/L3 层：合并策略
- L2 层：版本控制，手动解决

## 安全建议

1. **API 密钥分离**
   - 每个 Agent 使用独立的 API Key
   - 定期轮换密钥

2. **SSH 隧道**
   - 使用密钥而非密码
   - 限制 VPS 端口暴露

3. **数据隔离**
   - L0 层不共享敏感信息
   - RAG 索引前脱敏处理

4. **访问控制**
   - Supabase RLS 策略
   - Git 分支保护
