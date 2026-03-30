---
name: favorites-manager
description: 链接收藏夹智能管理，支持查找、添加、批量操作收藏链接。触发词："找链接"、"添加收藏"、"收藏这个"、"搜索链接"
version: v1.0
last_updated: 2026-03-13
---

# 收藏夹管理器

链接收藏夹智能管理，自动读取 `jarvis-memory/html-tools/链接保存/favorites导航_YYYY-MM-DD.json`，支持查找、添加、批量操作。

## 快速使用

```javascript
const fm = require('./favorites.js');

// 查找
const results = fm.findLinks({ keyword: "chatgpt" });

// 添加
fm.addLink({
  title: "Claude",
  url: "https://claude.ai",
  category: "⚙️ AI工作空间",
  tags: ["AI", "对话"]
});

// 统计
const stats = fm.getStats();
```

## 用户意图识别

当用户说以下话时，使用此 Skill：

### 🔍 查找类
- "帮我找ChatGPT相关链接"
- "稍后阅读里有哪些链接"
- "AI分类下有什么"
- "搜索关键词 XXX"

**Action**: `findLinks()` 或 `smartSearch()`

### ➕ 添加类
- "添加这个链接"
- "收藏 https://example.com"
- "把这个加到AI工具分类"
- "批量添加以下链接：..."

**Action**: `addLink()` 或 `batchAddLinks()`

### 📝 整理类
- "把稍后阅读的移到AI分类"
- "给这些链接打上标签"
- "删除重复链接"
- "批量修改分类"

**Action**: `batchUpdate()` 或 `updateLink()`

### 📊 统计类
- "我有多少链接"
- "整理情况如何"
- "有哪些分类"

**Action**: `getStats()`

## 完整 API

### 读取数据
```javascript
const links = fm.readData();
// 返回: Link[] 数组
```

### 查找链接
```javascript
// 精确查找
fm.findLinks({
  keyword: "搜索词",      // 模糊匹配标题/URL/别名/描述
  category: "分类名",     // 精确匹配分类
  tag: "标签",           // 匹配标签（支持数组）
  status: "unread",      // 状态：unread/important/todo
  starred: true          // 是否收藏
});

// 智能搜索（带相关度排序）
fm.smartSearch("搜索词", 10);  // 返回前10个最相关
```

### 添加链接
```javascript
// 单个添加
fm.addLink({
  title: "标题",           // 必填
  url: "https://...",      // 必填
  category: "分类",        // 可选，空则进稍后阅读
  tags: ["标签1", "标签2"], // 可选
  description: "描述",     // 可选
  status: "unread"         // 可选，unread/important/todo
});

// 批量添加
fm.batchAddLinks([
  { title: "链接1", url: "...", category: "..." },
  { title: "链接2", url: "...", category: "..." }
]);
```

### 更新链接
```javascript
// 单个更新
fm.updateLink("链接ID", {
  category: "新分类",
  tags: ["新标签"]
});

// 批量更新
fm.batchUpdate(
  link => link.status === "unread",  // 筛选条件
  { category: "⚙️ AI工作空间" }       // 更新内容
);
```

### 删除链接
```javascript
fm.deleteLink("链接ID");
```

### 获取统计
```javascript
fm.getStats();
// 返回:
// {
//   total: 500,           // 总数
//   categories: [["分类名", 数量], ...],
//   tags: [["标签", 数量], ...],
//   unread: 12,           // 待整理
//   starred: 20           // 收藏
// }
```

## 典型工作流

### 工作流1：日常添加链接

```
用户：添加 https://claude.ai，AI对话工具

AI:
1. fm.readData() 读取当前数据
2. fm.addLink({
     title: "Claude",
     url: "https://claude.ai",
     category: "⚙️ AI工作空间",
     tags: ["AI", "对话"]
   })
3. 返回结果给用户
```

### 工作流2：整理稍后阅读

```
用户：把稍后阅读里AI相关的移到AI工作空间

AI:
1. fm.readData()
2. const aiLinks = fm.findLinks({ 
     status: "unread",
     keyword: "AI"
   })
3. fm.batchUpdate(
     link => aiLinks.includes(link),
     { category: "⚙️ AI工作空间", status: null }
   )
4. 报告移动了多少个
```

### 工作流3：批量导入

```
用户：添加以下链接：
- ChatGPT https://chatgpt.com
- Claude https://claude.ai  
- Midjourney https://midjourney.com

AI:
1. fm.batchAddLinks([
     { title: "ChatGPT", url: "...", category: "AI", tags: ["免费"] },
     { title: "Claude", url: "...", category: "AI", tags: ["付费"] },
     { title: "Midjourney", url: "...", category: "AI", tags: ["绘画"] }
   ])
2. 报告成功/失败数量
```

## 数据格式

```typescript
interface Link {
  id: string;              // 时间戳唯一ID
  title: string;           // 标题
  url: string;             // 链接地址
  category: string;        // 分类（空=稍后阅读）
  subCategory?: string;    // 子分类
  description?: string;    // 描述
  alias?: string;          // 搜索别名
  status?: "unread" | "important" | "todo";
  tags: string[];          // 标签数组
  starred?: boolean;       // 是否收藏
  count?: number;          // 打开次数
  lastOpened?: number;     // 最后打开时间戳
}
```

## 文件位置

自动读取目录下最新文件：
```
jarvis-memory/html-tools/链接保存/
  ├── favorites导航_2026-02-03.json  ← 最新，使用这个
  ├── favorites导航_2026-02-02.json
  └── favorites导航_2026-02-01.json
```

保存时自动生成新文件（保留历史）。

## 注意事项

1. **自动备份**：每次修改生成新文件，历史数据保留
2. **重复检测**：添加前自动检查URL是否已存在
3. **编码**：UTF-8，支持中文
4. **并发**：单文件操作，同一时间只能有一个写入

## 集成其他 Skill

配合以下 Skill 使用效果更佳：

- **obsidian-markdown**: 将收藏夹统计写入每日笔记
- **daily_review_archiver**: 每日自动提示待整理链接数量
- **theme_insight_tracker**: 分析收藏标签，发现兴趣趋势
