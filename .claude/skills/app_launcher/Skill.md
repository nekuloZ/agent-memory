---
name: app_launcher
description: ALWAYS use when user wants to launch apps with "打开XXX", "启动XXX", "运行XXX", "开启XXX", "开一下XXX" or query app locations with "XXX在哪里", "XXX路径", "找到XXX". Includes "查看所有软件" and "添加软件到清单".
version: v1.2
last_updated: 2026-03-30
platform: [win32, darwin]
tools_required:
  - node
---

> **变更历史:** [CHANGELOG.json](./CHANGELOG.json)
> **模式归属:** 🤖 assist (助手模式)

---

# 应用启动器 Skill

智能管理应用启动，支持查询路径、直接打开、渐进式学习主程序名称。跨平台支持 Windows 和 macOS。

## 🎯 核心机制

**渐进式学习：**
1. **首次使用** - 返回安装目录，询问主程序名
2. **记录学习** - 用户确认后更新到数据库
3. **后续使用** - 直接打开应用，无需再次询问

**优点：**
- ✅ 只记录常用应用的主程序
- ✅ 不常用的应用保持原状（只返回目录）
- ✅ 避免猜测错误，保证准确性

---

## ⚡ 触发方式

### 1. 直接打开
- "打开XXX"
- "启动XXX"
- "运行XXX"

### 2. 查询路径
- "XXX在哪里"
- "XXX路径"
- "找到XXX"

---

## 📝 执行步骤

### Step 1: 解析软件名称

从用户表达中提取软件名称：

**示例：**
```
用户："打开飞书"
→ 软件名称：飞书

用户："暴雪战网在哪里"
→ 软件名称：暴雪战网
```

**模糊匹配处理：**
- 如果找不到精确匹配 → 尝试模糊搜索
- 搜索 `software_name`、`alias`、`comment` 字段

---

### Step 2: 查询数据库

```sql
SELECT
  id,
  software_name,
  install_directory,
  executable_name,
  alias
FROM windows_software_list
WHERE software_name LIKE '%软件名%'
   OR alias LIKE '%软件名%'
ORDER BY
  CASE WHEN software_name = '软件名' THEN 1 ELSE 2 END;
```

---

### Step 3: 判断处理方式

#### 情况A：有 executable_name ✅

**直接打开应用（跨平台）：**

**Windows:**
```powershell
# 构建完整路径
full_path = install_directory + "\" + executable_name

# 启动应用
Start-Process -FilePath $full_path
```

**macOS:**
```bash
# macOS 应用通常在 /Applications/ 下
open -a "应用名"
# 或直接打开路径
open "/Applications/应用名.app"
```

**响应：**
```
✅ 正在打开 [软件名称]...
已启动！
```

---

#### 情况B：无 executable_name，但有 install_directory ⚠️

**返回安装目录，询问主程序名：**
```
找到 [软件名称]！
安装目录：[install_directory]

但我还不知道主程序名，能帮我找一下吗？
（比如：Feishu.exe, lark.exe, launcher.exe）
```

**用户提供后：**
1. 更新数据库
2. 直接打开应用

---

#### 情况C：完全找不到 ❌

**响应：**
```
❌ 没找到 [软件名称]

可能的原因：
1. 软件清单里没有这个软件
2. 名称可能不一样

要查看所有软件吗？或者添加到清单？
```

---

### Step 4: 更新数据库（当用户提供executable_name时）

```sql
UPDATE windows_software_list
SET executable_name = '用户提供的主程序名.exe'
WHERE id = [记录ID];
```

**然后直接打开（跨平台）：**

**Windows:**
```powershell
Start-Process -FilePath $full_path
```

**macOS:**
```bash
open "$install_dir/$executable_name"
```

**响应：**
```
✅ 已记录！正在打开 [软件名称]...
下次就可以直接打开了！
```

---

## 📖 示例对话

### 示例1：已记录主程序（首次使用后）

**用户：** 打开暴雪战网
**AI：**
```
✅ 正在打开暴雪战网...
已启动！
```

---

### 示例2：首次使用（无executable_name）

**用户：** 打开飞书
**AI：**
```
找到飞书！
安装目录：D:\Software\Feishu

但我还不知道主程序名，能帮我找一下吗？
（比如：Feishu.exe, lark.exe, launcher.exe）
```

**用户：** Feishu.exe
**AI：**
```
✅ 已记录！正在打开飞书...
下次就可以直接打开了！
```

---

### 示例3：查询路径

**用户：** 企业微信在哪里？
**AI：**
```
找到企业微信！
安装目录：D:\Software\WXWork
主程序：WXWork.exe

完整路径：D:\Software\WXWork\WXWork.exe
```

---

### 示例4：软件不存在

**用户：** 打开微信
**AI：**
```
❌ 没找到微信

可能的原因：
1. 软件清单里没有这个软件
2. 名称可能不一样

要查看所有软件吗？或者添加到清单？
```

---

## 🔧 辅助功能

### 查询所有软件

**触发：** "查看所有软件"、"软件清单"

**响应格式：**
```
📋 Windows软件清单（共104条）

常用工具：
- 飞书
- 企业微信
- Bandizip
- ...

开发工具：
- CLion
- PhpStorm
- ...

要查看完整列表吗？
```

### 添加新软件

**触发：** "添加XXX到清单"

**收集信息：**
1. 软件名称
2. 安装目录
3. 主程序名（可选）
4. 别名（可选）

---

## ⚠️ 注意事项

1. **路径安全** - 只启动用户明确指定的应用
2. **编码问题** - Windows路径使用双反斜杠 `\\`
3. **错误处理** - 启动失败时提示用户检查路径
4. **渐进式学习** - 不强制要求所有软件都有executable_name
5. **模糊匹配** - 优先精确匹配，其次模糊搜索

---

## 🎯 设计哲学

**为什么采用渐进式学习？**

1. **避免错误猜测** - 不自动猜测主程序，避免启动错误
2. **只记录常用** - 不常用的应用不需要精确路径
3. **用户主导** - 用户决定哪些应用需要直接启动
4. **自然演进** - 随着使用逐渐完善数据库

**vs 传统方案的对比：**

| 方案 | 优点 | 缺点 |
|------|------|------|
| **一次性扫描** | 全面 | 耗时长，可能猜错 |
| **启发式规则** | 自动化 | 仍可能出错 |
| **渐进式学习** ✅ | 准确、灵活 | 首次需要询问 |
