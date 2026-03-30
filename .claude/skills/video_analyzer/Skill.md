---
name: video-analyzer
description: 批量获取B站/抖音视频内容（标题、简介、视频下载、字幕/转录、元数据、截图）。触发词："分析视频"、"下载视频"、"批量分析UP主"
version: v3.1
last_updated: 2026-03-30
platform: [win32, darwin]
tools_required: [python, ffmpeg, yt-dlp]
---

# 视频批量分析工具

> **版本**: v3.0 (推荐)
> **用途**: 批量获取B站/抖音视频内容（标题、简介、**视频下载**、字幕/转录、元数据、视频截图）
>
> **📖 详细使用指南**: `VIDEO_ANALYZER_USAGE.md`
> **📋 操作流程**: `video_analysis_workflow.md` ← 完整的操作步骤记录
>
> **v3.0 更新**: 统一支持B站 + 抖音双平台
> **v2.0**: 支持使用 Firefox Cookie 下载视频文件和截图

---

## 触发方式

**自然语言触发:**
- "分析这个UP主的视频"
- "获取B站/抖音视频的标题和简介"
- "批量下载B站/抖音视频内容"
- "帮我分析灵剑2011的视频"
- "下载抖音视频并提取字幕"
- "分析B站和抖音的视频链接"

---

## 执行流程

### 阶段1：获取视频列表

```bash
python get_videos.py
```

**功能:**
- 使用 bilibili-api-python 获取UP主最新视频
- 生成 video_urls.txt（18个视频链接）

**依赖:**
```bash
pip install bilibili-api-python
```

---

### 阶段2：批量分析视频

#### 统一版（v3.0，推荐）- 支持B站+抖音
```bash
python video_analyzer_unified.py
```

**v3.0 新增功能:**
- ✅ 同时支持 **B站** 和 **抖音** 双平台
- ✅ 自动识别平台类型
- ✅ 使用各自平台的Cookie配置
- ✅ 统一的输出格式和报告

#### 视频版（v2.0）- 仅B站
```bash
python video_analyzer_v2.py
```

#### 音频版（v1.0）- 仅B站
```bash
python video_analyzer.py
```

**输出结构:**
```
jarvis-memory/tasks/video_analysis/
├── video_01_BVxxx/
│   ├── metadata.json    # 完整元数据
│   ├── info.md          # 易读格式
│   ├── BVxxx.mp4        # [v2.0] 视频文件
│   ├── BVxxx.txt        # 转录文本/字幕
│   └── screenshots/     # [v2.0] 视频截图
│       ├── shot_01_xxxs.jpg
│       ├── shot_02_xxxs.jpg
│       └── ...
├── video_02_.../
├── video_analysis_report.md  # 汇总报告
└── video_titles.txt          # 视频标题列表
```

---

### 阶段3：生成汇总报告

```bash
python generate_summary.py
```

**输出:**
- `jarvis-memory/tasks/video_analysis/video_analysis_report.md` - 完整分析报告
- `jarvis-memory/tasks/video_analysis/video_titles.txt` - 视频标题列表

---

## 脚本文件说明

| 文件 | 用途 | 版本 | 支持平台 |
|------|------|------|----------|
| `video_analyzer_unified.py` | 批量分析（统一版） | **v3.0 (推荐)** | B站 + 抖音 |
| `video_analyzer_v2.py` | 批量分析（视频下载版） | v2.0 | 仅B站 |
| `video_analyzer.py` | 批量分析（音频转录版） | v1.0 | 仅B站 |
| `douyin_downloader.py` | 抖音视频下载器 | v1.0 | 仅抖音 |
| `get_videos.py` | 获取视频列表 | v1.0 | 仅B站 |
| `generate_summary.py` | 生成汇总报告 | v1.0 | - |

**调用路径说明:**
所有脚本位于 `.claude/skills/video_analyzer/` 目录下。执行时需先进入 skill 目录：
```bash
cd .claude/skills/video_analyzer/
python video_analyzer_unified.py
```
或从项目根目录调用：
```bash
python .claude/skills/video_analyzer/video_analyzer_unified.py
```

---

## 完整数据路径

**任务输出目录:**
```
jarvis-memory/tasks/
├── transcripts/           # 纯转录文本（旧版本）
└── video_analysis/        # 完整分析结果
    ├── video_01_xxx/      # 单个视频文件夹
    ├── video_02_xxx/
    ├── ...
    ├── video_analysis_report.md
    └── video_titles.txt
```

---

## 依赖安装

```bash
# Python依赖
pip install bilibili-api-python yt-dlp openai-whisper

# 系统依赖
# Windows:
winget install Gyan.FFmpeg

# macOS:
brew install ffmpeg yt-dlp
```

---

## 视频下载前提条件

### v3.0 统一版配置

| 平台 | 配置方式 | 说明 |
|------|----------|------|
| **B站** | Firefox Cookie | 同v2.0，需安装Firefox并登录B站 |
| **抖音** | `douyin_cookies.json` | 需先扫码登录获取cookie |

**抖音Cookie获取步骤：**
```bash
# 方法1: 扫码登录（推荐）
cd cookie_refresher
python douyin_qrcode_login.py

# 按提示使用抖音APP扫码
# 登录成功后，cookie自动保存到 douyin_cookies.json
```

### B站配置（v2.0/v3.0）

**必须满足以下条件：**

1. **安装 Firefox 浏览器**
2. **Firefox 已登录 B 站账号**（必须登录才能下载720P+）
3. **运行脚本时 Firefox 完全关闭**（包括后台进程）

**Chrome/Edge 为什么不支持？**
- Windows 加密了 Chrome/Edge 的 cookie，yt-dlp 无法解密
- Firefox 的 cookie 未加密，可以被读取

---

## 注意事项

| 版本 | 限制 | 说明 |
|------|------|------|
| v1.0 | 仅音频转录 | B站限制，自动降级为音频+Whisper |
| v2.0 | 需要 Firefox | 使用 Firefox Cookie 可下载720P视频 |

1. **转录质量** - 取决于原视频音频清晰度，BGM过大可能影响识别
2. **耗时** - 18个视频约需30-90分钟（视频下载+转录）
3. **空间** - 每个视频约50-200MB（720p）+ 转录文本
4. **画质** - 默认下载720p，如需1080p修改脚本中的 `height<=720` 为 `height<=1080`

---

## 示例任务

### v3.0 统一版（推荐）- 支持B站+抖音

**准备视频链接列表：**
```bash
# 创建 video_urls.txt，每行一个链接
# 支持混合格式：
https://www.bilibili.com/video/BV1xx411c7mD
https://www.douyin.com/video/1234567890123456789
https://www.bilibili.com/video/BV2yy222d8eE
```

**运行分析：**
```bash
python video_analyzer_unified.py
```

**结果查看:**
- 详细分析: `video_analysis/video_analysis_report.md`
- 单个视频: `video_analysis/01_bilibili_BVxxx/` 或 `video_analysis/02_douyin_12345/`
  - `metadata.json` - 元数据（包含平台信息）
  - `info.md` - 易读信息
  - `BVxxx.mp4` / `12345.mp4` - 视频文件
  - `transcript.txt` - 字幕/转录文本
  - `screenshots/` - 视频截图

### v2.0 B站专用版

```bash
# 1. 获取视频列表
python get_videos.py

# 2. 批量分析（带视频下载）
python video_analyzer_v2.py

# 3. 生成报告
python generate_summary.py
```

---

## 更新日志

- v3.0 (2026-03-05) - 统一版，同时支持B站+抖音双平台，自动识别平台类型
- v2.0 (2026-02-27) - 新增视频下载功能（Firefox Cookie）、视频截图
- v1.0 (2026-02-27) - 初始版本，支持元数据提取、语音转录、汇总报告
