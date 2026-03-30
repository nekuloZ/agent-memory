---
name: short-sentence-trainer
description: 短句合并训练器，基于"短句合并法"的语言学习工具。触发词："帮我练句子"、"拆分句子"、"短句训练"、"句子重组"
version: v1.0
last_updated: 2026-03-13
---

> **变更历史:** [CHANGELOG.json](./CHANGELOG.json)
> **模式归属:** 📚 learn (学习模式)

# 短句训练器

短句合并训练器 - 基于"短句合并法"的语言学习工具

---

## 触发词

| 触发词 | 示例 |
|--------|------|
| "帮我练句子" | "帮我练这个句子: I was wondering if you could help me." |
| "拆分句子" | "拆分这个句子: Despite the rain, we decided to go out." |
| "短句训练" | "短句训练: The book that I bought yesterday is very interesting." |
| "句子重组" | "句子重组练习" |

---

## 短句合并法

### 核心理念

将复杂长句拆分为**最短语义单元**，然后通过重组练习培养语感。

**最短语义单元：** 不能再拆分的基本意思单位
- ❌ "I was wondering"（可拆）
- ✅ "I wondered" / "I thought" / "I felt"
- ❌ "if you could help me"（可拆）
- ✅ "you could help me"

### 三步练习法

```
第1步：拆分
    原句 → 最短语义单元清单

第2步：口头重组
    用户用这些单元，按自己的理解重新组织

第3步：对比学习
    AI 提供 3 种变体供参考
```

---

## 工作流程

### 完整练习流程

**用户输入：** "帮我练这个句子: Despite the heavy rain, we decided to go out for a walk."

**步骤 1：分析拆分**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
原句
Despite the heavy rain, we decided to go out for a walk.

翻译：尽管下着大雨，我们还是决定出去散步。

拆分结果：
┌─────────────────────────────────────────────────────────┐
│  [介词短语]              [主语] [谓语]  [不定式]        │
│  Despite the heavy rain,  we   decided  to go out       │
│                                                         │
│  [介词短语]                                             │
│  for a walk                                             │
└─────────────────────────────────────────────────────────┘

最短语义单元：
1. "Despite the heavy rain" - 让步状语（介词短语）
2. "we decided" - 主谓核心
3. "to go out" - 决定的内容（不定式）
4. "for a walk" - 目的（介词短语）
```

**步骤 2：用户口头重组**

```
现在请用这些单元，按你自己的理解重新组织句子。
（在心里或口头尝试，不用打字）

单元清单：
- Despite the heavy rain
- we decided
- to go out
- for a walk
```

**步骤 3：AI 提供变体**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
参考变体（3种表达方式）：

变体 1（强调决定）
We decided to go out for a walk, despite the heavy rain.
【主谓核心】+ 【不定式】+ 【目的】+ 【让步状语后置】

变体 2（强调天气）
The heavy rain didn't stop us from going out for a walk.
【天气作主语】+ 否定结构 + stop...from...

变体 3（简洁版）
We went out for a walk despite the rain.
【简化主谓】+ 【目的】+ 【让步状语】

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**步骤 4：记录学习**

```
💾 已保存到词汇库：
- 原句：Despite the heavy rain, we decided to go out for a walk.
- 变体1：We decided to go out for a walk, despite the heavy rain.
- 变体2：The heavy rain didn't stop us from going out for a walk.
- 变体3：We went out for a walk despite the rain.

标签: #短句合并法 #句子重组
```

---

## 成分类型与颜色标注

| 类型 | 说明 | 颜色 |
|------|------|------|
| `subject` | 主语 | 🔵 蓝色 |
| `verb` | 谓语 | 🔴 红色 |
| `object` | 宾语 | 🟢 绿色 |
| `adverbial` | 状语 | 🟡 黄色 |
| `participle` | 分词短语 | 🟣 紫色 |
| `infinitive` | 不定式 | 🔵 天蓝 |
| `clause` | 从句 | 🟨 金色 |
| `prepositional` | 介词短语 | 🟠 橙色 |

---

## 核心方法

### analyze_sentence(sentence)

分析句子结构，拆分为最短语义单元。

**返回格式：**
```python
{
    "original": "Despite the heavy rain, we decided to go out for a walk.",
    "translation": "尽管下着大雨，我们还是决定出去散步。",
    "components": [
        {"text": "Despite the heavy rain", "type": "prepositional", "role": "让步状语"},
        {"text": "we", "type": "subject", "role": "主语"},
        {"text": "decided", "type": "verb", "role": "谓语"},
        {"text": "to go out", "type": "infinitive", "role": "宾语（不定式）"},
        {"text": "for a walk", "type": "prepositional", "role": "目的状语"}
    ],
    "units": [  # 最短语义单元
        {"text": "Despite the heavy rain", "can_move": true, "position": "flexible"},
        {"text": "we decided", "can_move": false, "position": "fixed"},
        {"text": "to go out", "can_move": false, "position": "fixed"},
        {"text": "for a walk", "can_move": true, "position": "flexible"}
    ]
}
```

### generate_variants(components, count=3)

基于句子成分生成重组变体。

**策略：**
1. **语序变化** - 移动状语位置（前置、后置）
2. **句式转换** - 主动变被动、肯定变双重否定
3. **词汇替换** - 同义词、近义词替换
4. **结构简化** - 复合句变简单句

### practice(sentence, source="", source_type="")

完整练习流程。

**执行步骤：**
1. 调用 `analyze_sentence()` 分析句子
2. 展示拆分结果，引导用户口头重组
3. 调用 `generate_variants()` 生成3种变体
4. 调用 `vocabulary_manager.add_sentence()` 保存原句和变体
5. 调用 `record` 记录到 scratchpad.md

---

## 与 vocabulary_manager 的协作

```
short_sentence_trainer.practice(sentence)
    ↓
analyze_sentence(sentence)  # 分析拆分
    ↓
generate_variants(components)  # 生成变体
    ↓
# 保存原句
vocabulary_manager.add_sentence(
    sentence=original,
    analysis=analysis,
    sentences_group=[...]
)
    ↓
# 保存每个变体
for variant in variants:
    vocabulary_manager.add_sentence(
        sentence=variant,
        tags=["短句合并法", "句子重组", "变体"]
    )
    ↓
record(skill="short_sentence_trainer", ...)  # 记录到 scratchpad
```

---

## 使用示例

### 示例 1：复杂从句

**输入：** "The book that I bought yesterday, which was recommended by my friend, is very interesting."

**拆分：**
```
最短语义单元：
1. "The book" - 主语（核心）
2. "that I bought yesterday" - 定语从句（修饰 book）
3. "which was recommended by my friend" - 非限定定语从句（补充说明）
4. "is very interesting" - 系表结构（谓语）
```

**变体：**
```
变体 1：合并从句
The book that I bought yesterday based on my friend's recommendation is very interesting.

变体 2：拆分为两句
My friend recommended a book. I bought it yesterday and it's very interesting.

变体 3：强调推荐
A friend recommended this book, and I bought it yesterday. It's very interesting.
```

### 示例 2：口语表达

**输入：** "I was wondering if you could help me with this problem."

**拆分：**
```
最短语义单元：
1. "I wondered" - 主谓（比 I was wondering 更简洁）
2. "if you could help me" - 宾语从句
3. "with this problem" - 介词短语
```

**变体：**
```
变体 1：直接表达
Could you help me with this problem?

变体 2：更礼貌
I wonder if you might be able to help me with this.

变体 3：强调问题
This problem is tricky. Could you help me?
```

---

## 学习建议

### 何时使用短句合并法

✅ **适合：**
- 长难句分析
- 写作表达多样化练习
- 口语组织能力提升
- 备考（雅思、托福写作）

❌ **不适合：**
- 初学者基础词汇学习
- 快速阅读场景
- 听力理解训练

### 练习频率

- **日常学习：** 每天 3-5 个句子
- **备考冲刺：** 每天 10-15 个句子
- **复习回顾：** 每周复习一次已练习的句子

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-02-13 | 初始版本，实现短句合并法核心功能 |
