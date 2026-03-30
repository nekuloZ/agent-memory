---
name: tts-reader
description: 英语/中文文字朗读工具，支持复读、调速、情绪控制。触发词："读这个"、"发音"、"怎么读"、"读一遍"、"慢速读"
version: v2.2
last_updated: 2026-03-30
platform: [win32, darwin]
tools_required: [python, node]
---

# 文字朗读工具

基于 MiniMax Speech-2.8 的文字朗读，支持英语/中文、复读、调速、情绪控制。

---

## 触发方式

**自然语言触发:**
- "读这个单词" / "发音" / "怎么读"
- "读一遍" / "读三遍"
- "慢速读" / "快速读"
- "跟读"

**命令行:**
```bash
python tts_reader.py "hello world"
python tts_reader.py "hello world" --repeat 3
python tts_reader.py "hello world" --rate slow
python tts_reader.py -i  # 交互模式
```

---

## 功能

### 1. 基础朗读

```bash
# 自动检测语言并选择语音
python tts_reader.py "hello"
python tts_reader.py "你好"

# 指定语音
python tts_reader.py "hello" --voice en-uk-ryan  # 英式男声
python tts_reader.py "你好" --voice zh-yunxi     # 中文男声
```

### 2. 复读模式

```bash
# 复读3次
python tts_reader.py "pronunciation" --repeat 3

# 交互式复读
python tts_reader.py -i
> /r 5 hello  # 复读5次
```

### 3. 调速

```bash
# 慢速（-30%）
python tts_reader.py "hello" --rate slow

# 快速（+30%）
python tts_reader.py "hello" --rate fast
```

---

## 可用语音

| 名称 | 语言 | 性别 | MiniMax voice_id |
|------|------|------|-----------------|
| zh-xiaoxiao | 中文 | 女 | Chinese (Mandarin)_Female_Assistant |
| zh-xiaoyi | 中文 | 女 | Chinese (Mandarin)_Female_Educational |
| zh-yunxi | 中文 | 男 | Chinese (Mandarin)_Male_Young |
| zh-yunyang | 中文 | 男 | Chinese (Mandarin)_Male_Mature |
| zh-ning | 中文 | 女 | Chinese (Mandarin)_Female_Standard |
| en-jenny | 英语(美) | 女 | English (US)_Female_Conversational |
| en-guy | 英语(美) | 男 | English (US)_Male_News |
| en-aria | 英语(美) | 女 | English (US)_Female_Expressive |
| en-ryan | 英语(英) | 男 | English (UK)_Male_Formal |
| en-emma | 英语(英) | 女 | English (UK)_Female_Natural |

---

## 情绪控制

MiniMax Speech-2.8 支持情绪标签：

| 情绪 | 说明 |
|------|------|
| happy | 开心 |
| sad | 悲伤 |
| angry | 生气 |
| anxious | 焦虑 |
| disgusted | 厌恶 |
| surprised | 惊讶 |

**使用方式：**
```bash
python tts_reader.py "你好" --emotion happy
```

**交互模式：**
```
> /happy 你好   # 开心语气
> /sad 你好     # 悲伤语气
```

---

## API 配置

需要设置环境变量 `MINIMAX_SPEECH_API_KEY`（**注意：与 Anthropic 代理用的 key 不同**）：

```bash
# Windows PowerShell
$env:MINIMAX_SPEECH_API_KEY = "your_speech_api_key"

# Linux/macOS
export MINIMAX_SPEECH_API_KEY="your_speech_api_key"
```

**获取 Speech API Key：**
1. 登录 https://platform.minimaxi.com
2. 进入 **用户中心 → API Key 管理**
3. 创建或查看 API Key（Speech 服务专用）

⚠️ **重要**：MiniMax 控制台的 API Key 有两种用途：
- **Chat API (Anthropic 代理)**：你在 `.claude/env.minimax.json` 里用的
- **Speech API**：需要单独创建，用于语音合成

两者不同！

---

## 与语言学习 Skills 集成

### vocabulary_manager

查单词时自动发音:
```python
# 在 vocabulary_manager 中添加
from tts_reader import speak_text
import asyncio

# 查询单词后
asyncio.run(speak_text(word, voice="en-jenny"))
```

### shadowing_manager

跟读文本生成音频:
```python
# 生成跟读音频（慢速）
asyncio.run(speak_text(text, voice="en-jenny", rate="slow", output_file="shadowing.mp3"))
```

---

## 交互模式命令

```bash
python tts_reader.py -i

> hello world          # 朗读
> /r 3 hello           # 复读3次
> /slow hello          # 慢速读
> /fast hello          # 快速读
> /quit                # 退出
```

---

## 完整流程示例

```bash
# 1. 生成单词发音
python tts_reader.py "pronunciation" --repeat 3 --rate slow

# 2. 生成句子（保存文件）
python tts_reader.py "How are you today?" -o practice.mp3

# 3. 播放（跨平台）
# Windows:
ffplay -nodisp -autoexit practice.mp3
# macOS:
afplay practice.mp3
```
