# 安装配置指南

## 环境要求

- **Python**: 3.9+
- **Obsidian** (推荐): 最新版
- **Claude Code**: 最新版
- **Git**: 用于版本控制

## 快速安装

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/agent-memory.git
cd agent-memory
```

### 2. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# === Gemini API (用于 RAG 嵌入) ===
GEMINI_API_KEY=your_gemini_api_key_here

# === Supabase (用于向量数据库) ===
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here

# === 可选: OpenClaw 配置 ===
OPENCLAW_BASE_URL=http://localhost:18789
OPENCLAW_API_KEY=your_openclaw_key_here

# === 可选: 飞书配置 ===
FEISHU_APP_ID=your_feishu_app_id
FEISHU_APP_SECRET=your_feishu_app_secret
```

### 4. 初始化目录结构

```bash
# Windows
python scripts/init.py

# macOS/Linux
python3 scripts/init.py
```

### 5. 配置 Claude Code Skills

#### Windows

```powershell
# 复制 Skills 到 Claude Code 目录
copy .claude\skills\* %USERPROFILE%\.claude\skills\ /Y

# 或者创建符号链接（推荐，方便更新）
mklink /D %USERPROFILE%\.claude\skills\agent-memory "%CD%\.claude\skills"
```

#### macOS/Linux

```bash
# 复制 Skills
mkdir -p ~/.claude/skills
cp -r .claude/skills/* ~/.claude/skills/

# 或者创建符号链接（推荐）
ln -s "$(pwd)/.claude/skills" ~/.claude/skills/agent-memory
```

### 6. 配置 Obsidian

1. 打开 Obsidian
2. 选择 "Open folder as vault"
3. 选择 `agent-memory/memory` 目录
4. 安装推荐插件：
   - **Calendar** - 日历视图
   - **Dataview** - 数据查询
   - **Templater** - 模板系统
   - **Periodic Notes** - 周期性笔记

## 详细配置

### Supabase 向量数据库设置

1. 注册 [Supabase](https://supabase.com)
2. 创建新项目
3. 启用 **Vector** 扩展
4. 创建表：

```sql
-- 启用向量扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 创建记忆向量表
CREATE TABLE memory_vectors (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    content TEXT NOT NULL,
    embedding VECTOR(768),  -- Gemini Embedding 维度
    source_file TEXT,
    source_type TEXT CHECK (source_type IN ('project', 'scratchpad', 'daily_log')),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 创建向量索引
CREATE INDEX idx_memory_vectors_embedding ON memory_vectors USING ivfflat (embedding vector_cosine_ops);
```

5. 部署 Edge Function：

```bash
cd tools/memory_search/supabase-functions
supabase functions deploy embed-and-store
```

### Gemini API 配置

1. 访问 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 创建 API Key
3. 添加到 `.env` 文件

### 跨平台配置

#### Windows 特定配置

```powershell
# PowerShell 配置
# 添加到 $PROFILE

# 设置环境变量
$env:GEMINI_API_KEY = "your_key"
$env:SUPABASE_URL = "your_url"

# 快捷命令
function archive { python "$env:AGENT_MEMORY_PATH\tools\memory_search\process_logs.py" --daily-logs }
function search-rag { python "$env:AGENT_MEMORY_PATH\tools\memory_search\smart_search.py" $args }
```

#### macOS 特定配置

```bash
# ~/.zshrc 或 ~/.bash_profile

# 环境变量
export AGENT_MEMORY_PATH="$HOME/agent-memory"
export GEMINI_API_KEY="your_key"
export SUPABASE_URL="your_url"

# 快捷命令
alias archive='python $AGENT_MEMORY_PATH/tools/memory_search/process_logs.py --daily-logs'
alias search-rag='python $AGENT_MEMORY_PATH/tools/memory_search/smart_search.py'
```

## 验证安装

```bash
# 1. 测试 Python 环境
python --version  # 应显示 3.9+

# 2. 测试依赖
python -c "import requests; print('OK')"

# 3. 测试 RAG 连接
python tools/memory_search/smart_search.py "test"

# 4. 测试 Skills 加载
# 在 Claude Code 中输入：
# "早上好" 或 "hey jarvis"
# 应触发 session_startup skill
```

## 故障排除

### 问题：Skills 不触发

**检查清单：**
1. Skills 文件是否在 `.claude/skills/` 目录下
2. `Skill.md` 文件是否有正确的 frontmatter
3. Claude Code 是否重启

### 问题：RAG 搜索失败

**检查清单：**
1. `.env` 文件中的 API 密钥是否正确
2. Supabase 项目是否运行
3. Edge Function 是否部署成功

### 问题：Obsidian 无法打开

**检查清单：**
1. `memory` 目录是否存在
2. 是否有读写权限
3. 路径中是否有中文或特殊字符

## 下一步

- [日常使用指南](WORKFLOW.md) - 学习日/周工作流程
- [多 Agent 配置](MULTI_AGENT.md) - 配置 OpenClaw 协作
