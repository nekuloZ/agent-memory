---
name: RTSC画面监控管理器
description: Use when user says "/rtsc", "截图", "画面监控", "OBS截图" to capture RTSP stream screenshot via FFmpeg
version: v1.1
last_updated: 2026-02-25
platform: [win32]
tools_required: [ffmpeg, obs]
---

> **变更历史:** [CHANGELOG.json](./CHANGELOG.json)

---
  - v1.1 (2026-02-25): 新增常驻监控脚本 - 1秒1截，自动清理
  - v1.0 (2026-02-25): 初始版本 - RTSP实时画面监控与截图
---

# RTSC画面监控管理器 Skill

通过 FFmpeg 捕获 OBS RTSP 推流画面，实现实时截图功能。

**两种模式：**
- **单次截图** - 立即截图并返回
- **常驻监控** - 后台运行，1秒1截，保留最近50张

## 触发条件

| 触发词 | 示例 |
|--------|------|
| `/rtsc` | `/rtsc` 或 `/rtsc 截图` |
| `截图` | "截个图", "截图看看" |
| `画面监控` | "看一下画面", "监控画面" |
| `OBS截图` | "OBS画面截图" |

---

## 配置参数

### OBS RTSP 推流设置

```
推流地址：rtsp://localhost:8554/live
推流密钥：（任意，如 obs）
```

### FFmpeg 截图命令

```bash
# 基础截图（默认分辨率）
ffmpeg -i rtsp://localhost:8554/live -ss 00:00:01 -vframes 1 -q:v 2 output.jpg

# 指定分辨率截图
ffmpeg -i rtsp://localhost:8554/live -ss 00:00:01 -vframes 1 -s 1920x1080 -q:v 2 output.jpg

# 快速截图（降低延迟）
ffmpeg -rtsp_transport tcp -i rtsp://localhost:8554/live -ss 00:00:00.5 -vframes 1 -q:v 2 output.jpg
```

### Windows PowerShell 命令

```powershell
# 带时间戳的截图
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
ffmpeg -i rtsp://localhost:8554/live -ss 00:00:01 -vframes 1 -q:v 2 "screenshot_$timestamp.jpg"
```

---

## 执行步骤

### Step 1: 检查 FFmpeg

```powershell
# 验证 FFmpeg 是否可用
ffmpeg -version | Select-Object -First 1
```

### Step 2: 捕获截图

```powershell
# 生成带时间戳的文件名
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$outputPath = "E:\AI_program\Jarvis\jarvis-memory\assets\rtsc\screenshot_$timestamp.jpg"

# 执行截图
ffmpeg -rtsp_transport tcp -i rtsp://localhost:8554/live -ss 00:00:01 -vframes 1 -q:v 2 "$outputPath"
```

### Step 3: 验证截图成功

- 检查文件是否存在
- 检查文件大小（应 > 0）
- 使用 Read 工具查看图片内容

### Step 4: 记录到 scratchpad

```
record(
  type = "工具使用",
  topic = "RTSC画面截图",
  content = "截图时间: $timestamp\n文件路径: $outputPath\n画面状态: [成功/失败]"
)
```

---

## 常驻监控模式

后台持续运行，每秒自动截图，保留最近50张。

### 文件位置

```
scripts/
├── rtsc_monitor.py      # 主监控脚本
├── rtsc_start.bat       # 启动监控（后台）
├── rtsc_stop.bat        # 停止监控
└── rtsc_status.bat      # 查看状态
```

### 使用方法

**启动监控：**
```powershell
# 方式1：直接运行脚本
python scripts/rtsc_monitor.py start

# 方式2：使用批处理（后台运行，无窗口）
scripts/rtsc_start.bat
```

**停止监控：**
```powershell
# 方式1：Python脚本
python scripts/rtsc_monitor.py stop

# 方式2：批处理
scripts/rtsc_stop.bat
```

**查看状态：**
```powershell
# 显示运行状态和截图统计
scripts/rtsc_status.bat
```

### 配置参数

```python
# rtsc_monitor.py 配置项
RTSP_URL = "rtsp://localhost:8554/live"   # RTSP流地址（本地OBS推流）
OUTPUT_DIR = "jarvis-memory/assets/rtsc"   # 截图保存路径
INTERVAL = 1                               # 截图间隔（秒）
KEEP_COUNT = 50                            # 保留最近N张
```

### 技术实现

```python
# FFmpeg 命令（脚本内部使用）
ffmpeg -y -rtsp_transport tcp -i tcp://5.tcp.cpolar.cn:10793 \
       -ss 00:00:00.5 -vframes 1 -q:v 2 output.jpg

# 参数说明：
# -y          覆盖已有文件
# -rtsp_transport tcp  使用TCP传输（更稳定）
# -ss 00:00:00.5      0.5秒后开始截图（降低延迟）
# -vframes 1          只截取1帧
# -q:v 2              图片质量（2=高质量）
```

### 自动清理机制

- 每次截图后自动清理旧文件
- 只保留最新的50张截图
- 防止磁盘空间无限增长

### 进程管理

- 使用 PID 文件跟踪监控进程
- 支持异常退出清理（PID文件自动删除）
- 可重复查询状态，自动修复残留PID

---

## 使用流程

### 场景1：日常截图

```
用户：/rtsc
AI：
1. 等待1秒（确保获取最新截图）
2. 读取最新图片文件
3. 描述画面内容
4. 记录使用日志
```

### 场景2：游戏画面检查

```
用户：截图看看游戏画面
AI：
1. 等待1秒（确保获取最新截图）
2. 读取最新图片文件
3. 分析游戏状态
4. 给出建议
```

---

## 常见问题

### Q1: FFmpeg 未安装

**解决：**
```powershell
# 安装 FFmpeg（通过 chocolatey）
choco install ffmpeg

# 或下载解压到固定路径
# 路径：C:\tools\ffmpeg\bin\ffmpeg.exe
```

### Q2: RTSP 连接失败

**排查：**
1. 检查 OBS 是否正在推流
2. 检查 RTSP 服务器是否运行（如 mediamtx）
3. 检查端口 8554 是否被占用

### Q3: 截图延迟高

**优化：**
```bash
# 使用 TCP 传输 + 减少缓冲区
ffmpeg -rtsp_transport tcp -buffer_size 1024000 -i rtsp://localhost:8554/live -ss 00:00:00.5 -vframes 1 output.jpg
```

---

## 文件存储

**截图保存路径：**
```
jarvis-memory/assets/rtsc/
├── screenshot_20260225_103000.jpg
├── screenshot_20260225_103500.jpg
└── ...
```

**保留策略：**
- 日归档时清理 7 天前的截图
- 重要截图手动归档到项目文件夹

---

## 关联文件

- **OBS配置：** `TOOLS.md` - 推流设置
- **截图存储：** `jarvis-memory/assets/rtsc/`
- **项目日志：** `L1_Episodic/Projects/游戏项目.md`

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.1 | 2026-02-25 | 新增常驻监控脚本 - 1秒1截，自动清理，支持 start/stop/status |
| v1.0 | 2026-02-25 | 初始版本 - RTSP实时画面监控与截图 |
