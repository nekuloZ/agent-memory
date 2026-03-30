---
name: vocabulary-manager
description: Jarvis 语言学习词汇管理器。触发词："记录单词"、"查询单词"、"记录句子"、"记录短语"、"我的单词"
version: v1.2
last_updated: 2026-03-18
---

> **变更历史:** [CHANGELOG.json](./CHANGELOG.json)
> **模式归属:** 📚 learn (学习模式)
> **斜杠命令:** `/word`

# 词汇管理器

Jarvis 语言学习词汇管理器 - 支持单词、短语、句子的记录与查询。

---

## 触发词

| 触发词 | 示例 |
|--------|------|
| "记录单词" | "记录单词: ephemeral，释义: 短暂的" |
| "查询单词" | "查询单词: serendipity" |
| "我的单词" | "列出我所有的单词" |
| "记录句子" | "记录句子: ..." |
| "记录短语" | "记录短语: make up one's mind" |

---

## 自动触发检测（v1.2 新增）

本 Skill 支持智能场景路由自动检测。

### 检测逻辑

启动时检查 `.claude/.pending_signal.json`：

1. **文件存在且 timestamp 在 5 分钟内？**
2. **scene 匹配 "learning"？**
3. **符合条件 → 按 scene-router 配置预加载记忆**
4. **清理 signal 文件，进入正常执行流程**

### 预加载内容

当检测到学习场景信号时，自动预加载：
- L0: `scratchpad.md`（今日学习记录）
- L3: `L3_User/03-Learning/Language/` 目录下的学习数据
- L3: `L3_Semantic/language/` 词汇数据

### 触发示例

```
用户: "记录单词: ephemeral"
    ↓ Signal Hook 检测到 learning 场景 (confidence: 0.85)
    ↓ 写入 .pending_signal.json
    ↓ vocabulary_manager 启动
    ↓ 检测到信号，预加载相关记忆
    ↓ 执行记录单词流程
```

### 手动触发（无信号时）

如果信号不存在或过期，按原有触发词逻辑执行：
- "记录单词: xxx"
- "查询单词: xxx"
- "记录句子: xxx"
- "记录短语: xxx"

---

## 功能

### 1. 词汇记录

#### add_word(word, definition, ...)

记录单词到 `jarvis-memory/L3_Semantic/language/vocabulary/en/words/{word}.json`

**完整参数：**
```python
add_word(
    word: str,                    # 单词（必需）
    definition: str = "",          # 释义
    phonetic: str = "",            # 音标（如 /səˈrendɪpɪti/）
    part_of_speech: str = "",      # 词性（noun/verb/adjective/adverb）
    example: str = "",             # 例句
    tags: List[str] = None,        # 标签列表
    notes: str = "",               # 笔记
    synonyms: List[str] = None,    # 同义词
    antonyms: List[str] = None,    # 反义词
    collocations: List[str] = None,# 常见搭配
    syllables: str = "",           # 音节划分（如 "ephem·er·al"）
    source: str = "",              # 来源（如 "《老友记》"）
    source_type: str = ""          # 来源类型（book/tv_show/game/other）
)
```

**数据格式：**
```json
{
  "word": "ephemeral",
  "phonetic": "/ɪˈfɛmərəl/",
  "syllables": "ephem·er·al",
  "part_of_speech": "adjective",
  "definition": "lasting for a very short time",
  "example": "Fashions are ephemeral.",
  "tags": ["文学", "高频"],
  "notes": "来自《Appointment with Death》",
  "synonyms": ["transient", "fleeting", "evanescent"],
  "antonyms": ["permanent", "eternal"],
  "collocations": ["ephemeral nature", "ephemeral beauty"],
  "source": "《Appointment with Death》",
  "source_type": "book",
  "created_at": "2026-02-13T10:30:00",
  "language": "en"
}
```

#### add_phrase(phrase, meaning, ...)

记录短语到 `jarvis-memory/L3_Semantic/language/vocabulary/en/phrases/`

**完整参数：**
```python
add_phrase(
    phrase: str,                  # 短语（必需）
    meaning: str = "",            # 含义
    usage: str = "",              # 用法说明
    examples: List[str] = None,   # 例句列表
    tags: List[str] = None,       # 标签
    notes: str = "",              # 笔记
    register: str = "",           # 语域（formal/informal/slang）
    source: str = "",             # 来源
    source_type: str = ""         # 来源类型
)
```

**文件名格式：** `{phrase前20字符}_{timestamp}.json`

#### add_sentence(sentence, translation, ...)

记录句子到 `jarvis-memory/L3_Semantic/language/vocabulary/en/sentences/`

**完整参数：**
```python
add_sentence(
    sentence: str,                    # 句子（必需）
    translation: str = "",            # 翻译
    analysis: str = "",               # 句子成分分析
    key_words: List[str] = None,      # 关键词汇
    grammar_points: List[str] = None, # 语法点
    tags: List[str] = None,           # 标签
    notes: str = "",                  # 笔记
    source: str = "",                 # 来源
    source_type: str = "",            # 来源类型
    context: str = "",                # 上下文
    sentences_group: List[Dict] = None # 句子组（成分标注）
)
```

**sentences_group 格式（由 short_sentence_trainer 生成）：**
```json
{
  "sentences_group": [
    {
      "text": "Frowning, he shut it decisively.",
      "components": [
        {"text": "Frowning", "type": "participle", "role": "伴随状语"},
        {"text": "he", "type": "subject", "role": "主语"},
        {"text": "shut", "type": "verb", "role": "谓语"},
        {"text": "it", "type": "object", "role": "宾语"},
        {"text": "decisively", "type": "adverbial", "role": "方式状语"}
      ],
      "analysis": "分词短语作伴随状语 + 主谓宾结构 + 方式状语"
    }
  ]
}
```

### 2. 去重与多来源

**单词去重：** 以单词为文件名（如 `ephemeral.json`），同一单词多来源时更新 `sources` 数组

**短语/句子去重：** 遍历目录检查内容，相同内容时更新来源

### 3. 查询功能

#### lookup(word)

查询本地词典获取音标和释义（需要 dictionary.py 支持）。

**返回格式：**
```python
{
    "word": "ephemeral",
    "phonetic": "/ɪˈfɛmərəl/",
    "definitions": [
        {"pos": "adjective", "text": "lasting for a very short time"}
    ],
    "examples": ["Fashions are ephemeral."],
    "synonyms": ["transient", "fleeting"],
    "antonyms": ["permanent", "eternal"]
}
```

#### list_words(tag=None)

列出所有单词，可选按标签过滤。

#### list_phrases(tag=None)

列出所有短语。

#### list_sentences(tag=None)

列出所有句子。

---

## 与 Jarvis 集成

### 数据联动

每次添加词汇后，自动调用 `record` skill 记录到 `scratchpad.md`：

```markdown
## 10:30 语言学习

- 记录单词: ephemeral /ɪˈfɛmərəl/ - lasting for a very short time
- 来源: 《Appointment with Death》
```

### 与 short_sentence_trainer 协作

```
short_sentence_trainer 拆分句子
    ↓
vocabulary_manager 保存原句+变体
    ↓
record 记录到 scratchpad
```

---

## Python 模块使用

```python
from jarvis_memory.language.vocabulary_manager import VocabularyManager

# 初始化管理器
manager = VocabularyManager(language='en')

# 添加单词
manager.add_word(
    word="ephemeral",
    definition="lasting for a very short time",
    source="《Appointment with Death》",
    source_type="book"
)

# 查询单词
info = manager.lookup("ephemeral")
print(info['phonetic'])  # /ɪˈfɛmərəl/

# 列出所有单词
words = manager.list_words()
```

---

## 文件路径

| 类型 | 路径 |
|------|------|
| 单词 | `jarvis-memory/L3_Semantic/language/vocabulary/en/words/{word}.json` |
| 短语 | `jarvis-memory/L3_Semantic/language/vocabulary/en/phrases/{phrase_prefix}_{timestamp}.json` |
| 句子 | `jarvis-memory/L3_Semantic/language/vocabulary/en/sentences/{timestamp}.json` |
| 影子跟读 | `jarvis-memory/L3_Semantic/language/shadowing/{title}_{timestamp}.json` |
| 练习题 | `jarvis-memory/L3_Semantic/language/exercises/{title}_{timestamp}.json` |

---

## 数据迁移说明

原 language-agent 数据已复制到：
- `jarvis-memory/L3_Semantic/language/vocabulary/en/`

数据来源：`E:\AI_program\language-agent\vocabulary\en\`

---

## 执行操作（当用户触发时）

**⚠️ 重要：此 skill 被调用时，必须执行实际的文件写入操作，不能仅提供文档说明。**

### 1. 记录单词 - 立即执行

**触发：** 用户说"记录单词: xxx"

**立即执行：**
```python
# 1. 提取单词和释义
word = "damned"  # 从用户输入提取
definition = "该死的"  # 从用户输入提取
source = "The Genesis Order"  # 从用户输入提取

# 2. 构建文件路径
base_path = "E:/AI_program/Jarvis/jarvis-memory/L3_Semantic/language/vocabulary/en"
file_path = f"{base_path}/words/{word.lower()}.json"

# 3. 检查是否已存在（去重）
如果文件存在:
  读取现有内容
  追加新来源到 sources 数组
否则:
  创建新文件

# 4. 写入 JSON 文件
{
  "word": word,
  "definition": definition,
  "source": source,
  "source_type": "game",
  "created_at": "当前时间ISO格式",
  "language": "en"
}
```

### 2. 记录句子 - 立即执行

**触发：** 用户说"记录句子: xxx"

**立即执行：**
```python
# 1. 提取句子、翻译、来源
sentence = "原句"
translation = "中文翻译"
source = "来源"

# 2. 生成文件名（时间戳）
from datetime import datetime
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
file_path = f"{base_path}/sentences/{timestamp}.json"

# 3. 写入 JSON 文件
{
  "sentence": sentence,
  "translation": translation,
  "source": source,
  "source_type": "game",
  "created_at": "当前时间ISO格式",
  "key_words": [],  # 可选：提取关键词
  "grammar_points": []  # 可选：标注语法点
}
```

### 3. 记录短语 - 立即执行

**触发：** 用户说"记录短语: xxx"

**立即执行：**
```python
# 1. 提取短语和释义
phrase = "短语"
meaning = "释义"

# 2. 生成文件名（短语前20字符 + 时间戳）
phrase_prefix = phrase[:20].replace(" ", "_")
file_path = f"{base_path}/phrases/{phrase_prefix}_{timestamp}.json"

# 3. 写入 JSON 文件
{
  "phrase": phrase,
  "meaning": meaning,
  "source": source,
  "created_at": "当前时间ISO格式"
}
```

### 4. 执行后反馈

每次写入完成后，必须向用户确认：
```
已记录到：
- 单词: {word} → words/{word}.json
- 句子: {sentence前30字符}... → sentences/{timestamp}.json
- 短语: {phrase} → phrases/{phrase_prefix}_{timestamp}.json
```

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-02-13 | 初始版本，从 language-agent 迁移 |
| v1.1 | 2026-02-23 | 补充执行操作说明，明确文件写入流程 |
