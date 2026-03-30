# 视频分析工作流程

> 最后更新：2026-03-05
> 支持平台：B站(bilibili.com) + 抖音(douyin.com)

---

## 前置准备

### 1. 安装依赖

```bash
# Python依赖
pip install yt-dlp openai-whisper playwright

# Playwright浏览器
playwright install chromium

# 系统依赖（Windows）
winget install Gyan.FFmpeg
```

### 2. 配置Cookie

#### B站（使用Firefox）
1. 安装Firefox浏览器
2. 访问 https://www.bilibili.com 并登录账号
3. 保持Firefox打开（脚本会自动读取cookie）

#### 抖音（扫码登录）
```bash
cd cookie_refresher
python douyin_qrcode_login.py
```
按提示用抖音APP扫码，cookie自动保存到 `douyin_cookies.json`

---

## 完整流程

### Step 1: 准备视频链接

创建 `video_urls.txt` 文件，每行一个链接：

```
# B站视频
https://www.bilibili.com/video/BV1xx411c7mD

# 抖音视频（支持短链接和长链接）
https://v.douyin.com/FLvzH1WUnt8/
https://www.douyin.com/video/1234567890
```

---

### Step 2: 下载视频

#### 方式A：统一版（自动识别平台）

```bash
python video_analyzer_unified.py
```

- 自动识别B站/抖音链接
- B站：使用yt-dlp + Firefox cookie
- 抖音：使用Playwright直接下载

#### 方式B：抖音专用下载器

```bash
python douyin_downloader.py
```

仅处理 `video_urls.txt` 中的抖音链接。

**输出目录：**
```
video_analysis/
├── 01_douyin_xxxx/          # 抖音视频
│   ├── metadata.json        # 元数据
│   ├── info.md              # 可读信息
│   ├── xxxx.mp4             # 视频文件
│   └── transcript.txt       # 页面提取的文案（仅标题/标签）
└── 02_bilibili_BVxx/
    ├── metadata.json
    ├── info.md
    ├── BVxx.mp4
    └── transcript.txt
```

---

### Step 3: 提取字幕/转录（Whisper）

```bash
# 基本用法
python -m whisper video_analysis/01_douyin_xxx/video.mp4 --model medium --language Chinese

# 指定输出目录和格式
python -m whisper video_analysis/01_douyin_xxx/video.mp4 \
  --model medium \
  --language Chinese \
  --output_dir video_analysis/01_douyin_xxx/ \
  --output_format txt
```

**模型选择：**
| 模型 | 速度 | 质量 | 适用场景 |
|------|------|------|---------|
| tiny | 最快 | 一般 | 快速测试 |
| base | 快 | 尚可 | 实时场景 |
| small | 中等 | 好 | 平衡选择 |
| **medium** | 中等 | **很好** | **推荐** |
| large | 慢 | 最好 | 高质量需求 |

**输出文件：**
- `video.txt` - 纯文本（带时间戳）
- `video.srt` - 字幕格式
- `video.vtt` - WebVTT格式

---

### Step 4: 整理与校对

#### 4.1 阅读原始转录

```bash
cat video_analysis/01_douyin_xxx/video.txt
```

#### 4.2 常见转录错误类型

| 类型 | 示例 | 修正 |
|------|------|------|
| 同音字错误 | "四部像" | "四不像" |
| 专业术语 | "全重" | "权重" |
| 技术词汇 | "偷拍的视频" | "超分的视频" |
| 人名/地名 | "约瑟分贵地" | "约瑟芬跪地" |
| 成语/惯用语 | "小金汉" | "短小精悍" |

#### 4.3 整理成Markdown

创建 `transcript_corrected.md`，建议结构：

```markdown
# 视频标题

## 视频信息
- **平台**: 抖音/B站
- **主题**: xxx
- **核心内容**: xxx

---

## 第一部分：xxx

### 小节标题

内容段落...

> 引用/重点标注

| 表格 | 说明 |
|------|------|
| xxx | xxx |

---

## 关键概念速查

| 术语 | 解释 |
|------|------|
| xxx | xxx |
```

---

## 故障排除

### Q: 抖音下载提示 "Fresh cookies needed"
**A:** Cookie已过期，重新扫码登录：
```bash
cd cookie_refresher
python douyin_qrcode_login.py
```

### Q: B站视频下载失败 "Requested format is not available"
**A:**
1. 检查Firefox是否已登录B站
2. 关闭Firefox后重试
3. 可能是地区限制或视频已删除

### Q: Whisper转录中文显示乱码
**A:** Windows终端编码问题，不影响输出文件。直接读取生成的 `.txt` 文件即可：
```bash
cat video_analysis/xxx/video.txt
```

### Q: 抖音视频文件名是 `.mp4`（没有ID）
**A:** 短链接导致的正常现象。如需重命名：
```bash
cd video_analysis/01_douyin_xxx
mv .mp4 actual_video_id.mp4
```

---

## 脚本文件说明

| 文件 | 用途 | 版本 | 支持平台 |
|------|------|------|----------|
| `video_analyzer_unified.py` | 批量分析（统一版） | **v3.0 (推荐)** | B站 + 抖音 |
| `douyin_downloader.py` | 抖音专用下载器 | v1.0 | 仅抖音 |
| `video_analyzer_v2.py` | B站专用（视频版） | v2.0 | 仅B站 |
| `video_analyzer.py` | B站专用（音频版） | v1.0 | 仅B站 |
| `get_videos.py` | 获取UP主视频列表 | v1.0 | 仅B站 |
| `generate_summary.py` | 生成汇总报告 | v1.0 | - |

---

## 更新记录

- **2026-03-05** - 添加抖音Playwright下载器 + Whisper转录流程
- **2026-03-05** - 统一版支持B站+抖音双平台
- **2026-02-27** - B站视频下载功能（Firefox Cookie）

---

## 快捷命令参考

```bash
# 完整流程（单条命令）
cd E:/AI_program/Jarvis

# 1. 下载
python video_analyzer_unified.py

# 2. 转录（替换路径为实际视频）
python -m whisper video_analysis/01_douyin_xxx/video.mp4 \
  --model medium --language Chinese \
  --output_dir video_analysis/01_douyin_xxx/

# 3. 查看转录结果
cat video_analysis/01_douyin_xxx/video.txt
```
