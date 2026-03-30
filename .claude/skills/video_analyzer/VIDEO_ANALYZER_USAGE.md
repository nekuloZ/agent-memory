# 视频分析工具使用指南

> 支持平台：B站(bilibili.com) + 抖音(douyin.com)

---

## 快速开始

### 1. 准备视频链接

创建 `video_urls.txt` 文件，每行一个链接：

```
# B站视频
https://www.bilibili.com/video/BV1xx411c7mD

# 抖音视频（支持短链接和长链接）
https://v.douyin.com/FLvzH1WUnt8/
https://www.douyin.com/video/1234567890
```

### 2. 运行分析

```bash
# 统一版（自动识别平台）
python video_analyzer_unified.py

# 或单独运行抖音下载器
python douyin_downloader.py
```

### 3. 查看结果

输出目录：`video_analysis/`

```
video_analysis/
├── 01_bilibili_BVxxx/          # B站视频
│   ├── metadata.json           # 元数据
│   ├── info.md                 # 可读信息
│   ├── BVxxx.mp4               # 视频文件（720p）
│   ├── transcript.txt          # 字幕/转录文本
│   └── screenshots/            # 视频截图
├── 02_douyin_xxxxxx/           # 抖音视频
│   ├── metadata.json
│   ├── info.md
│   ├── xxxxxx.mp4              # 视频文件
│   └── transcript.txt          # 视频文案
└── video_analysis_report.md    # 汇总报告
```

---

## Cookie 获取流程

### B站 Cookie（使用 Firefox）

**前提条件：**
- 安装 Firefox 浏览器
- Firefox 已登录 B站账号

**步骤：**
1. 打开 Firefox，访问 https://www.bilibili.com
2. 登录你的B站账号
3. 保持Firefox打开（脚本会自动读取cookie）

**注意：**
- Windows上Chrome/Edge的cookie被加密，无法使用
- Firefox的cookie未加密，yt-dlp可以直接读取
- 如果下载失败，尝试关闭Firefox再运行脚本

---

### 抖音 Cookie（扫码登录）

**步骤：**

```bash
# 1. 进入cookie刷新目录
cd cookie_refresher

# 2. 运行扫码登录脚本
python douyin_qrcode_login.py

# 3. 按提示操作：
#    - 脚本会自动打开浏览器访问抖音登录页
#    - 当前目录生成 douyin_qrcode.png（二维码图片）
#    - 用抖音APP扫码
#    - 手机上确认登录
#    - 登录成功后按 Ctrl+C 退出

# 4. 检查cookie是否生成
ls douyin_cookies.json  # 文件时间应为当前时间

# 5. 复制到根目录（如果不在的话）
cp douyin_cookies.json ..
cd ..
```

**Cookie有效期：**
- 通常能维持几天到几周
- 如果发现下载失败提示 "Fresh cookies needed"，需要重新登录
- 建议每次大批量下载前先检查一下

---

## 各平台特性

| 特性 | B站 | 抖音 |
|------|-----|------|
| **视频下载** | ✅ yt-dlp + Firefox cookie | ✅ Playwright + 扫码cookie |
| **元数据** | ✅ 完整（标题/作者/播放/点赞） | ✅ 完整（标题/作者/文案） |
| **字幕提取** | ✅ 优先下载CC字幕 | ❌ 无字幕功能 |
| **语音转录** | ✅ Whisper转录 | ❌ 直接提取文案 |
| **视频截图** | ✅ ffmpeg提取关键帧 | ❌ 暂不支持 |
| **短链接** | ✅ 自动跳转 | ✅ 自动跳转 |

---

## 常见问题

### Q: B站视频下载失败 "Requested format is not available"
**A:**
- 检查Firefox是否已登录B站
- 关闭Firefox后重试
- 可能是地区限制或视频已删除

### Q: 抖音下载提示 "Fresh cookies needed"
**A:** Cookie已过期，需要重新扫码登录：
```bash
cd cookie_refresher
python douyin_qrcode_login.py
```

### Q: 抖音视频文件名是 `.mp4`（没有ID）
**A:** 这是短链接导致的正常现象，不影响使用。如需重命名：
```bash
cd video_analysis/01_douyin_xxx
mv .mp4 actual_video_id.mp4
```

### Q: 如何只下载特定平台的视频？
**A:**
- 只下载B站：使用 `video_analyzer_unified.py`，自动过滤
- 只下载抖音：使用 `douyin_downloader.py`

---

## 依赖安装

```bash
# Python依赖
pip install yt-dlp openai-whisper playwright

# Playwright浏览器
playwright install chromium

# 系统依赖（Windows）
winget install Gyan.FFmpeg
```

---

## 脚本文件说明

| 文件 | 用途 | 版本 |
|------|------|------|
| `video_analyzer_unified.py` | 统一版分析工具（推荐） | v3.0 |
| `douyin_downloader.py` | 抖音专用下载器 | v1.0 |
| `video_analyzer_v2.py` | B站专用（视频版） | v2.0 |
| `video_analyzer.py` | B站专用（音频版） | v1.0 |

---

## 更新记录

- **2026-03-05** - 添加抖音Playwright下载器
- **2026-03-05** - 统一版支持B站+抖音双平台
- **2026-02-27** - B站视频下载功能（Firefox Cookie）

---

**提示：** Cookie过期是正常现象，重新登录即可。建议将本文件收藏，方便下次查阅流程。
