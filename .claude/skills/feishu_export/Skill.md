---
name: feishu-export
description: 将飞书多维表格、文档等导出为本地文件（xlsx）。触发词："导出飞书表格"、"飞书导出"
version: v1.0
last_updated: 2026-03-13
---

> **变更历史:** [CHANGELOG.json](./CHANGELOG.json)
> **模式归属:** 📊 ops (运营模式)

# 飞书文件导出

将飞书多维表格、文档等导出为本地文件（xlsx 等）。

## 前置条件

1. 飞书应用已开通 `drive:export:readonly` 或 `docs:document:export` 权限
2. 配置文件存在：`.claude/agents/config/feishu-config.md`

## 工作流程（4 次 API 调用）

```
┌─────────────────────────────────────────────────────────────────┐
│  步骤 1: 获取 access_token                                      │
│  POST https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal
│  Body: {"app_id": "xxx", "app_secret": "xxx"}                   │
│  返回: tenant_access_token                                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  步骤 2: 创建导出任务                                            │
│  POST https://open.feishu.cn/open-apis/drive/v1/export_tasks/   │
│  Body: {                                                         │
│    "token": "app_token",      // 多维表格的 app_token            │
│    "type": "bitable",         // 类型：bitable/docx/sheet 等     │
│    "file_type": "xlsx",       // 导出格式：xlsx/pdf 等           │
│    "file_extension": "xlsx",  // ⚠️ 必填！                       │
│    "table_id": "tblxxxxx"     // 多维表格时必填                  │
│  }                                                              │
│  返回: { "ticket": "xxxxxxxx" }                                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  步骤 3: 轮询任务状态                                            │
│  GET https://open.feishu.cn/open-apis/drive/v1/export_tasks/{ticket}?token={app_token}
│  返回: {                                                         │
│    "job_status": 0,          // 0=成功, 1=进行中, 2=失败         │
│    "file_token": "xxxxxxxx",  // 下载用的 token                  │
│    "file_size": 123456                                       │
│  }                                                              │
│  ⚠️ 如果 job_status=1，等待后重试                                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  步骤 4: 下载文件                                                │
│  GET https://open.feishu.cn/open-apis/drive/v1/export_tasks/file/{file_token}/download
│  ⚠️ 正确端点：/drive/v1/export_tasks/file/{file_token}/download  │
│  ❌ 错误端点：/drive/v1/files/{file_token}/download (403)        │
└─────────────────────────────────────────────────────────────────┘
```

## API 参数说明

### 导出类型 (type)
| 值 | 说明 |
|----|------|
| `bitable` | 多维表格 |
| `docx` | 文档 |
| `sheet` | 电子表格 |
| `mindnote` | 思维导图 |

### 导出格式 (file_type)
| 值 | 说明 |
|----|------|
| `xlsx` | Excel 格式 |
| `pdf` | PDF 格式 |
| `docx` | Word 格式 |

### 任务状态 (job_status)
| 值 | 说明 |
|----|------|
| `0` | 导出成功 |
| `1` | 导出中，需轮询 |
| `2` | 导出失败 |

## 常见错误

| 错误 | 原因 | 解决方法 |
|------|------|----------|
| `99991672` Access denied | 缺少导出权限 | 开通 `drive:export:readonly` 权限 |
| `99992402` field validation | 缺少 `file_extension` | 添加 `file_extension` 参数 |
| `403` Forbidden | 下载端点错误 | 使用 `/drive/v1/export_tasks/file/{file_token}/download` |
| `404` Not Found | 端点路径错误 | 检查 URL 路径格式 |

## 配置文件格式

`.claude/agents/config/feishu-config.md`:

```yaml
## API 凭证
app_id: "cli_xxxxxxxxxxxxx"
app_secret: "xxxxxxxxxxxxxxxx"

## 多维表格
### 表格名
app_token: "xxxxxxxx"
table_id: "tblxxxxx"
```

## 使用示例

```
"帮我把飞书的直播数据表导出为 xlsx"
"导出飞书多维表格 tblRBXvqOVu6wHEr 到本地"
```

## 参数检查（执行前必做）

**⚠️ 开始导出前，必须确认以下参数，缺一不可：**

| 参数 | 说明 | 默认值 | 来源 |
|------|------|--------|------|
| `app_token` | 多维表格/文档的 token | 无 | 用户提供 或 配置文件 |
| `table_id` | 多维表格的 table_id | 无 | 用户提供 或 配置文件 |
| `file_type` | 导出格式 | `xlsx` | 用户指定 或 默认 |
| `type` | 文件类型 | `bitable` | 自动推断 |

**参数检查流程：**

```
┌─────────────────────────────────────────────────────────────┐
│  1. 读取配置文件                                              │
│     → 读取 .claude/agents/config/feishu-config.md            │
│     → 获取 app_id, app_secret（API 凭证）                    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  2. 确认导出目标                                              │
│     → 用户指定表格名称？→ 从配置查找 app_token + table_id    │
│     → 用户指定 app_token？→ 直接使用                         │
│     → 都没指定？→ 询问用户：                                   │
│       "要导出哪个表格？请提供表格名称或 app_token"            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  3. 确认 table_id（多维表格必需）                              │
│     → 配置中有？→ 使用                                       │
│     → 配置没有？→ 询问用户：                                   │
│       "请提供 table_id（表格 URL 中 table= 后面的部分）"      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  4. 确认导出格式                                              │
│     → 用户指定？→ 使用                                       │
│     → 未指定？→ 默认 xlsx，询问确认：                         │
│       "导出为 xlsx 格式，可以吗？"                            │
└─────────────────────────────────────────────────────────────┘
                              ↓
                      所有参数齐备，开始导出
```

**询问用户的话术模板：**

```
需要确认以下信息才能导出：

1. 表格名称（如"直播数据表"）或 app_token
2. table_id（如果配置文件中没有）
3. 导出格式（默认 xlsx，支持 pdf/docx）

请提供上述信息，或确认使用配置文件中的默认值。
```

## 执行步骤

1. **参数检查**：按上述流程确认所有必需参数
2. 读取配置文件获取 API 凭证（app_id, app_secret）
3. 获取 tenant_access_token
4. 创建导出任务，获取 ticket
5. 轮询任务状态直到 job_status=0
6. 下载文件到当前目录
7. 报告：文件名、大小、API 调用次数
