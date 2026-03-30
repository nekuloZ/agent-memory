---
name: shadowing_manager
description: This skill should be used when the user says "添加跟读文本", "影子跟读", "生成填空", "填空练习" to manage shadowing texts and exercises
version: v1.2
last_updated: 2026-03-12
---

> **变更历史:** [CHANGELOG.json](./CHANGELOG.json)
> **模式归属:** 📚 learn (学习模式)

# 影子跟读管理器

保存跟读文本、生成填空练习。

---

## 触发词

- "添加跟读文本"
- "影子跟读"
- "生成填空"
- "填空练习"

---

## 关键规则

1. **JSON 格式必须符合标准**（见下方）
2. **必须调用 record skill** 记录操作
3. **媒体文件和 JSON 同名**才能自动关联

---

## 文件路径

- **文本文件:** `jarvis-memory/L3_Semantic/language/shadowing/`
- **练习文件:** `jarvis-memory/L3_Semantic/language/exercises/`
- **索引文件:** `shadowing_index.json`

---

## 标准 JSON 格式

```json
{
  "title": "文本标题",
  "type": "tv/movie/podcast/talk/music/news/documentary",
  "source": "来源",
  "difficulty": "easy/medium/hard 或 A1/A2/B1/B2/C1/C2",
  "tags": ["标签1", "标签2"],
  "subtitles": [
    {
      "start": 0,
      "end": 3.2,
      "text": "英文原文",
      "translation": "中文翻译"
    }
  ]
}
```

**命名规范:** `{type}-{标题}-{子标题}.json`

示例: `tv-老友记-The_One_with_the_Embryos.json`

---

## 功能

### 1. 添加跟读文本

**步骤:**
1. 询问标题、内容/字幕、来源、难度
2. 生成标准 JSON
3. 保存到 shadowing/ 目录
4. 更新索引
5. 调用 record

**输出示例:**
```
✅ 已保存影子跟读文本

标题：The Road Not Taken
来源：Robert Frost
难度：medium

保存位置：
jarvis-memory/L3_Semantic/language/shadowing/
```

### 2. 生成填空练习

**步骤:**
1. 读取文本文件
2. 按 ratio（默认20%）挖空
3. 生成练习 JSON
4. 保存到 exercises/ 目录

**输出示例:**
```
📝 填空练习已生成

原文：The Road Not Taken
挖空比例：20% (15个空)

Two roads ______ in a yellow wood,
And sorry I could not ______ both...

答案：
1. diverged (动词，表示分岔)
2. travel (动词，表示行走)
```

### 3. 文件处理（批量）

**用户放置文件后:**
1. 扫描临时目录
2. 验证 JSON 格式
3. 标准化命名
4. 移动到主目录
5. 更新索引

**输出:**
```
✅ 文件已处理

📁 位置：jarvis-memory/L3_Semantic/language/shadowing/
已处理：
  ├─ 📄 tv-老友记-The_One_with_the_Embryos.json
  ├─ 🎬 tv-老友记-The_One_with_the_Embryos.mp4
  └─ 📄 podcast-The_Daily-A_New_Chapter.json

💡 下一步：
   打开 Shadowing Studio，点击"📁 导入内容"按钮
```

---

## 禁止

- ❌ 不验证格式就保存 JSON
- ❌ 不更新索引
- ❌ 不调用 record

---

## 快捷检查

完成前确认：
1. JSON 格式正确？
2. 文件名符合规范？
3. 调用 record 了吗？
