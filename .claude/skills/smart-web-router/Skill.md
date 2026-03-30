---
name: smart-web-router
description: |
  **必须**使用此skill当用户需要搜索信息、获取网页内容、浏览任何网页时。
  触发场景包括："获取/抓取/搜索/浏览/打开 [URL或关键词]"、"帮我查一下..."、"看看这个网站"、
  "找一下关于...的信息"、"研究xxx"、"分析这个网页"、"twitter/reddit/github上有什么新消息"等。
  此skill会自动决策使用 Tavily/SearXNG/opencli/MCP Router 等最佳工具，无需手动选择。
  即使是简单的"打开xxx看看"或"搜索一下xxx"，也应该使用此skill来确保选择正确的工具。
version: v3.0
last_updated: 2026-03-26
allowed-tools: Bash, Read, Write, Skill, Agent
compatibility: |
  Windows(主环境): PowerShell环境变量语法 $env:XXX
  macOS/Linux: export XXX 语法
  代理要求: Clash Verge Rev 或其他HTTP代理在 10808 端口
  可用工具: Tavily CLI, SearXNG (自建), opencli, MCP Router (Playwright), CDP Browser
---

> **变更历史:** [CHANGELOG.json](./CHANGELOG.json)

# Smart Web Router v3.0

智能网络工具路由系统 - 自动选择最佳工具，无需手动决策。

**核心升级 v3.0：**
- 新增 CDP Browser 浏览器自动化（类人浏览）
- 新增 Site Patterns 站点经验系统
- 新增 Parallel Research 并行研究机制
- 强化"像人一样浏览"哲学

## 核心哲学：像人一样浏览

**Browse Like a Human.**

1. **设定明确成功标准** — 在开始前明确你想从页面获取什么信息
2. **验证每步结果** — 检查操作是否符合预期，及时调整
3. **遇到障碍自适应** — 页面结构变化时，能识别并找到替代方案
4. **目标达成即停止** — 拿到需要的信息后不要继续操作

## 核心特性

- **三层路由**：规则引擎（快速）+ AI兜底（灵活）+ CDP兜底（动态）
- **自动代理判断**：根据URL自动配置代理
- **失败回退**：主工具失败自动尝试备选
- **站点经验积累**：特定网站的交互策略存储复用
- **并行研究**：独立目标委托子代理并行处理

## 使用方式

```bash
# 直接描述需求，系统自动路由
"获取 https://twitter.com/user 的最新推文"
"搜索 Claude Code 最新功能"
"打开 B站 查看热门视频"
"抓取 https://github.com/xxx 的README"
"研究 xxx 竞品推广策略"  # → 并行研究模式
"帮我登录 GitHub 看看 issues"  # → CDP 浏览器模式
```

## 执行流程（必须遵循）

当用户提出任何网络相关请求时，**立即**按以下步骤执行：

### Step 1: 解析意图
- 判断是**搜索查询**（关键词）还是**URL获取**（具体链接）
- 使用正则提取URL：`/(https?:\/\/[^\s]+)/i`
- 判断是否有"登录态"、"动态内容"、"需要交互"等隐含需求
- 判断是否**多个独立目标** → 触发并行研究

### Step 2: 规则匹配（Layer 1 - 快速路径）
- **关键词匹配**：`^(搜索|查找|查询|新闻PEc、最新|什么是|怎么样).*`
- **URL分类**：检查域名是否需要代理、是否有站点经验
- **交互需求**：是否需要登录、填表、点击等操作

如果匹配成功 → 直接按"工具优先级矩阵"选择工具

### Step 3: AI决策（Layer 2 - 兜底路径）
如果规则无法匹配：
1. 分析URL特征（域名后缀、路径结构）
2. 判断内容类型（文档站/社交媒体/视频平台）
3. 推测是否需要JavaScript渲染
4. 选择最合适的工具

### Step 4: 代理配置（关键步骤）
检查URL分类，**需要代理时必须先设置环境变量**：

```powershell
# Windows PowerShell
$env:HTTP_PROXY="http://127.0.0.1:10808"
$env:HTTPS_PROXY="http://127.0.0.1:10808"

# 如果是Node.js工具（如opencli）
$env:GLOBAL_AGENT_HTTP_PROXY="http://127.0.0.1:10808"
$env:GLOBAL_AGENT_HTTPS_PROXY="http://127.0.0.1:10808"
```

### Step 5: 执行与失败回退
1. 调用选定的主工具
2. 如果失败，按优先级尝试备选工具
3. 直到成功或耗尽选项

### Step 6: 返回结果
- 输出获取的内容
- 简要说明使用了什么工具（便于调试）
- 如果使用了代理，注明"[Via Proxy]"

## 工具优先级矩阵（v3.0 实测版）

| 场景 | 第一选择 | 备选1 | 备选2 | 代理需求 |
|------|---------|-------|-------|---------|
| **搜索查询** | Tavily CLI | SearXNG | - | ❌ |
| **深度研究** | Tavily Research | Tavily Search | - | ❌ |
| **静态页面(国内)** | Tavily Extract | opencli | CDP Browser | ❌ |
| **静态页面(国际)** | Tavily Extract | CDP Browser | defuddle | 可选 |
| **动态/登录页** | CDP Browser | MCP Router | opencli | ✅ |
| **需要交互操作** | CDP Browser | MCP Router | - | ✅ |
| **批量爬取** | Tavily Crawl | - | - | ❌ |
| **社交内容** | opencli | CDP Browser | MCP Router | 看平台 |

## 工具详解

### P1: Tavily CLI（推荐首选）

**安装状态：** ✅ 已安装
**用途：** 搜索查询、内容提取、深度研究、批量爬取
**命令：**
```bash
# 搜索（推荐）
PYTHONIOENCODING=utf-8 tvly search "关键词" --depth advanced --json

# 提取单个页面
PYTHONIOENCODING=utf-8 tvly extract "URL" --json

# 深度研究
PYTHONIOENCODING=utf-8 tvly research "主题" --json

# 爬取网站
PYTHONIOENCODING=utf-8 tvly crawl "URL" --json
```

**注意：** Windows下必须用 `PYTHONIOENCODING=utf-8` 避免GBK编码错误

### P2: SearXNG（自建搜索引擎）

**URL：** `http://159.75.92.235:8080/`
**用途：** 批量查询、研究调研、聚合搜索
**命令：**
```bash
# JSON格式搜索
curl "http://159.75.92.235:8080/search?q=关键词&format=json"

# 简单搜索（返回HTML）
curl "http://159.75.92.235:8080/search?q=关键词"
```

### P3: CDP Browser（类人浏览器自动化）⚡ NEW

**状态：** CDP Proxy 运行在 `http://127.0.0.1:3456`
**用途：** 动态页面、登录态、需要交互操作（填表、点击、上传文件）
**优势：** 连接用户已有的Chrome实例，继承登录状态

**工作流程：**
```
1. 获取标签页列表 → GET /targets
2. 创建/选择标签页 → POST /new 或 POST /activate
3. 导航 → POST /navigate
4. 执行操作 → POST /eval (执行JS) 或 POST /click
5. 截图 → GET /screenshot
6. 提取内容 → GET /snapshot
```

**命令：**
```bash
# 获取所有标签页
curl "http://127.0.0.1:3456/targets"

# 导航到URL
curl -X POST "http://127.0.0.1:3456/navigate?url=https://github.com"

# 执行JavaScript
curl -X POST -d '{"expression": "document.title"}' "http://127.0.0.1:3456/eval"

# 点击元素
curl -X POST -d '{"selector": "#login-button"}' "http://127.0.0.1:3456/click"

# 截图
curl "http://127.0.0.1:3456/screenshot" -o screenshot.png

# 设置文件上传
curl -X POST -d '{"selector": "input[type=file]", "value": "/path/to/file.pdf"}' "http://127.0.0.1:3456/upload"
```

**适用场景：**
- 小红书、微信公众号等需要登录的平台
- 需要点击"加载更多"才能获取全部内容
- 需要填表、登录后才能访问的内容
- 需要文件上传操作的场景

### P4: MCP Router Browser（动态内容）

**状态：** MCP Router已连接（Playwright）
**用途：** 动态页面、登录态、需要JS渲染的内容
**工具：** `mcp__mcp-router__browser_*`
```javascript
// 导航
mcp__mcp-router__browser_navigate({ url: "URL" })

// 截图
mcp__mcp-router__browser_take_screenshot({ type: "png" })

// 提取内容
mcp__mcp-router__browser_snapshot()
```

### P5: opencli（社交/内容平台）

**安装状态：** ✅ 已安装
**用途：** B站、知乎、Twitter/X、YouTube等内容平台
**命令：**
```bash
# Twitter
opencli twitter "用户名或搜索词"

# B站
opencli bilibili "关键词"

# YouTube
opencli youtube "关键词"
```

### P6: defuddle（净含量提取）

**用途：** 从网页提取干净的内容（去除广告、导航栏等）
**命令：**
```bash
defuddle "URL"
```

## Site Patterns 站点经验系统 ⚡ NEW

特定网站的交互策略，存储在 `references/site-patterns/` 目录。

**文件命名：** `{域名}.md`
**内容结构：** 验证过的策略 + 已知的坑

**示例 - github.com.md：**
```markdown
# GitHub Site Pattern

## 验证过的策略
- README获取：直接用 Tavily Extract 或 defuddle
- Issues列表：CDP Browser 点击 "New issue" 按钮需要登录
- 代码搜索：Tavily Extract 效果最好

## 已知坑
- 动态加载：需要滚动触发加载更多
- 登录提示：会弹出登录框但不影响内容获取

## 代理需求
无需代理，直连
```

**使用方式：**
1. 解析URL获取域名
2. 查找 `references/site-patterns/{域名}.md`
3. 如有经验，按其中策略执行
4. 如无，创建新文件并填充经验

## Parallel Research 并行研究 ⚡ NEW

当有**多个独立研究目标**时，委托子代理并行处理。

**触发条件：**
- 用户说"研究A和B和C"
- 多个URL需要并行获取
- 竞品分析等多主题研究

**执行方式：**
```javascript
Agent({
  prompt: "研究主题：{具体目标}\n请使用CDP Browser或Tavily提取内容",
  subagent_type: "general-purpose",
  run_in_background: true
})
```

**主代理接收摘要，不接收完整内容**（节省上下文）

## URL 分类表

### 直连域名（无需代理）
```yaml
direct:
  - github.com
  - bilibili.com
  - zhihu.com
  - juejin.cn
  - csdn.net
  - oschina.net
  - gitee.com
  - jianshu.com
  - weibo.com
  - baidu.com
  - google.com        # 视网络环境
  - stackoverflow.com
  - stackexchange.com
  - medium.com        # 视网络环境
  - dev.to
  - arxiv.org
```

### 代理域名（需要代理）
```yaml
proxy:
  - twitter.com
  - x.com
  - youtube.com
  - reddit.com
  - discord.com
  - instagram.com
  - facebook.com
  - tiktok.com
  - openai.com
  - anthropic.com
  - platform.openai.com
  - 小红书.com
  - weixin.qq.com
```

## 失败回退策略

| 工具 | 失败原因 | 回退到 |
|------|---------|--------|
| Tavily Search | API限制/网络 | SearXNG |
| Tavily Extract | 访问限制 | CDP Browser → defuddle → MCP Router |
| CDP Browser | 未启动/超时 | MCP Router → opencli |
| SearXNG | 服务不可用 | Tavily Search |
| opencli | Adapter失效 | CDP Browser → MCP Router |
| MCP Router | 未连接/超时 | CDP Browser → opencli |

## 路由决策流程

```
用户请求
    │
    ├── 多个独立目标？ ──→ [Parallel Research]
    │                       └── 委托子代理并行
    │
    ▼
[Layer 1: 规则引擎] ←── 80% 命中率
    │
    ├── 关键词匹配 → 搜索工具
    │   └── Tavily Search / SearXNG
    │
    ├── URL直连匹配 → 内容提取
    │   └── Tavily Extract / defuddle
    │
    ├── URL代理匹配 → 动态浏览器
    │   └── CDP Browser / MCP Router / opencli
    │
    └── 规则无法判断 ──→ [Layer 2: AI决策]
                            │
                            └── 分析URL特征
                                └── 选择最佳工具
```

## 使用示例

### 示例1：搜索信息
```
用户：搜索最新的AI编程助手对比

路由决策：
1. 关键词匹配 "搜索" → 搜索工具
2. 选择 Tavily Search（LLM优化，结构化）
3. 无需代理

执行：
PYTHONIOENCODING=utf-8 tvly search "AI编程助手对比 Claude Cursor Windsurf" --depth advanced --json
```

### 示例2：获取GitHub内容
```
用户：获取 https://github.com/jackwener/opencli 的README

路由决策：
1. URL匹配直连列表 → github.com
2. 检查 site-patterns/github.com.md → 有经验
3. 静态页面 → Tavily Extract（最快）
4. 无需代理

执行：
PYTHONIOENCODING=utf-8 tvly extract "https://github.com/jackwener/opencli"
```

### 示例3：需要登录的页面
```
用户：帮我登录GitHub看看我的issues

路由决策：
1. URL匹配代理列表 → github.com
2. 需要登录态+交互 → CDP Browser
3. 设置代理环境变量

执行：
设置代理 → CDP Browser 连接Chrome → 导航到 github.com/issues
→ 用户在浏览器手动登录 → 提取内容
```

### 示例4：并行研究（竞品分析）
```
用户：研究一下 Claude、Cursor、Windsurf 这三个产品的推广策略

路由决策：
1. 检测到多个独立目标
2. 触发 Parallel Research
3. 分解为3个子任务并行执行

执行：
- 子代理1: 研究 Claude 推广策略
- 子代理2: 研究 Cursor 推广策略
- 子代理3: 研究 Windsurf 推广策略
→ 汇总为竞品分析报告
```

### 示例5：复杂边界情况（AI兜底）
```
用户：帮我看看这个网站有什么内容 https://some-new-site.com

路由决策：
1. URL不在任何列表 → 规则无法匹配
2. 触发AI兜底决策
3. 分析：
   - 检查域名归属地
   - 判断内容类型
   - 选择最佳工具
4. 执行
```

## 快速参考

| 你说 | 系统响应 |
|------|---------|
| "搜索xxx" | → Tavily Search |
| "深度研究xxx" | → Tavily Research |
| "打开/浏览 [URL]" | → 根据URL智能选择工具 |
| "抓取/获取 [URL]" | → Tavily Extract / defuddle |
| "研究A和B和C" | → Parallel Research |
| "帮我登录xxx" | → CDP Browser |
| "需要交互/填表" | → CDP Browser |
| "B站/知乎/Twitter内容" | → opencli 或 CDP Browser |

## 故障排查

**问题1：Tavily报错未认证**
```bash
# 解决：检查API Key
tvly login --api-key tvly-YOUR_KEY
```

**问题2：Tavily输出乱码（Windows GBK）**
```bash
# 解决：使用UTF-8编码
PYTHONIOENCODING=utf-8 tvly search "关键词" --json
```

**问题3：SearXNG返回空**
```bash
# 解决：检查服务状态
curl "http://159.75.92.235:8080/health"
```

**问题4：CDP Browser 无法连接**
```bash
# 解决：检查CDP Proxy是否运行
curl "http://127.0.0.1:3456/targets"

# 如果未运行，启动CDP Proxy
cdp-proxy  # 或查看 references/cdp-api.md
```

**问题5：MCP Router未连接**
```bash
# 解决
1. 打开 MCP Router 应用
2. 确认 Playwright MCP 状态为绿色
3. 重试
```

## 依赖工具检查

```bash
# 检查Tavily
tvly --version

# 检查opencli
opencli --version

# 检查SearXNG
curl "http://159.75.92.235:8080" | head -5

# 检查CDP Proxy
curl "http://127.0.0.1:3456/targets"
```
