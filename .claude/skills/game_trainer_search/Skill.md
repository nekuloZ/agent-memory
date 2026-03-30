---
name: game_trainer_search
description: 搜索、下载和管理游戏修改器（Trainer）。支持FLiNG、小幸等多数据源，中英关键词互译。触发词："找修改器"、"下载修改器"、"搜索trainer"、"找游戏作弊器"。
version: 1.0.0
author: nekulo
tags: [game, trainer, cheat, search, download]
---

# 游戏修改器搜索 Skill

集成 `trainer_search_cli` 工具，提供游戏修改器的搜索、下载和管理功能。

## 触发词

| 触发词 | 示例 |
|--------|------|
| "找修改器" | "找艾尔登法环修改器" |
| "下载修改器" | "下载黑神话悟空修改器" |
| "搜索trainer" | "搜索 Elden Ring trainer" |
| "找游戏作弊器" | "找赛博朋克2077作弊器" |
| "安装修改器" | "帮我安装只狼修改器" |

## 使用方法

### 1. 搜索修改器

用户说："找艾尔登法环修改器"

执行：
```bash
cd trainer_search_cli
python trainer_search.py search "艾尔登法环"
```

输出示例：
```
找到 5 个结果:

ID   游戏名                     来源            版本       大小
--------------------------------------------------------------------------------
1    Elden Ring                 FLiNG           v1.12      -
2    Elden Ring                 FLiNG Archive   v1.10      -
3    艾尔登法环                 小幸            v1.12      12.5MB
...
```

向用户展示结果，并询问要下载哪一个。

### 2. 下载指定修改器

用户说："下载第1个" 或 "下载ID 1"

执行：
```bash
cd trainer_search_cli
python trainer_search.py download 1
```

### 3. 搜索并直接下载

用户说："直接下载黑神话悟空修改器"

执行：
```bash
cd trainer_search_cli
python trainer_search.py get "黑神话悟空"
```

### 4. 查看已安装的修改器

用户说："查看已安装的修改器" 或 "列出我的修改器"

执行：
```bash
cd trainer_search_cli
python trainer_search.py installed
```

## 工作流程

```
用户请求 → 解析游戏名 → 执行搜索 → 展示结果 → 确认下载 → 执行下载 → 反馈结果
```

### 详细流程

1. **解析游戏名**
   - 从用户输入中提取游戏名称
   - 支持中文、英文、别名（如"老头环"→"艾尔登法环"）

2. **执行搜索**
   - 调用 `trainer_search.py search`
   - 多数据源并发查询
   - 缓存结果 24 小时

3. **展示结果**
   - 格式化表格显示
   - 显示来源、版本、大小

4. **确认下载**
   - 询问用户下载哪一个
   - 或让用户提供具体ID

5. **执行下载**
   - 调用 `trainer_search.py download`
   - 流式下载 + 自动解压

6. **反馈结果**
   - 显示下载路径
   - 显示可执行文件位置

## 工具路径

```
{project_root}/trainer_search_cli/trainer_search.py
```

## 数据结构

### 搜索结果
```json
{
  "id": 1,
  "game_name": "Elden Ring",
  "trainer_name": "艾尔登法环 修改器",
  "source": "fling_main",
  "source_name": "FLiNG",
  "url": "https://...",
  "version": "v1.12",
  "download_url": null,
  "size": null
}
```

### 下载结果
```json
{
  "success": true,
  "file_path": "C:/Users/xxx/.trainer_search/downloads/Elden Ring/xxx.zip",
  "extracted": true,
  "game_dir": "C:/Users/xxx/.trainer_search/downloads/Elden Ring",
  "executable": "C:/Users/xxx/.trainer_search/downloads/Elden Ring/EldenRing_Trainer.exe",
  "metadata": {...}
}
```

## 数据源

| 数据源 | 名称 | 特点 |
|--------|------|------|
| fling_main | FLiNG | 风灵月影，更新快 |
| fling_archive | FLiNG Archive | 历史版本 |
| xiaoxing | 小幸 | 中文支持好 |

## 存储位置

下载的修改器存放在：
```
~/.trainer_search/downloads/
├── Elden Ring/
│   ├── EldenRing_Trainer.exe
│   └── gcm_info.json
├── Black Myth Wukong/
│   └── ...
```

## 错误处理

| 场景 | 处理方式 |
|------|----------|
| 未找到结果 | 提示"未找到XX的修改器，尝试用英文搜索？" |
| 下载链接失效 | 提示"该修改器链接失效，尝试其他来源？" |
| 7z未安装 | 提示"需要安装7-Zip才能解压修改器" |
| 网络超时 | 重试或提示"网络连接失败，请检查网络" |

## 别名映射

常见游戏别名自动识别：

| 别名 | 正式名称 |
|------|----------|
| 老头环 | 艾尔登法环 |
| 黑猴 | 黑神话：悟空 |
| 老滚5 | 上古卷轴5 |
| 只狼 | 只狼：影逝二度 |
| 2077 | 赛博朋克2077 |

## 注意事项

1. **仅支持Windows** - 修改器主要是Windows程序
2. **需要7-Zip** - 用于解压修改器压缩包
3. **网盘链接** - 部分来源返回网盘链接，需要手动处理
4. **反病毒软件** - 修改器可能被杀毒软件误报，需用户自行判断
5. **单机游戏使用** - 提醒用户修改器仅适用于单机模式

## 依赖

确保已安装：
```bash
cd trainer_search_cli
pip install -r requirements.txt
```

并安装 [7-Zip](https://www.7-zip.org/)

## 示例对话

### 示例1：完整流程

**用户：** 找艾尔登法环修改器

**Claude：**
```
正在搜索"艾尔登法环"的修改器...

找到 3 个结果:

ID   游戏名                     来源            版本       大小
--------------------------------------------------------------------------------
1    Elden Ring                 FLiNG           v1.12      -
2    Elden Ring                 FLiNG Archive   v1.10      -
3    艾尔登法环                 小幸            v1.12      15.2MB

要下载哪一个？输入ID（如：1）
```

**用户：** 1

**Claude：**
```
正在下载 FLiNG v1.12 版本...
[下载] Elden Ring Trainer v1.12
[进度] 45.2% (2.1 MB / 4.6 MB)
...
[解压] 完成
[元数据] 已保存

✓ 下载完成！
  目录: C:\Users\nekulo\.trainer_search\downloads\Elden Ring
  可执行文件: EldenRing_Trainer_x64.exe

提示：修改器可能会被杀毒软件误报，请添加到信任列表。
```

### 示例2：直接下载

**用户：** 直接下载黑神话悟空修改器

**Claude：**
```
正在搜索并下载"黑神话悟空"的修改器...
找到 2 个结果，下载第一个...

[下载] 黑神话：悟空 修改器 v1.0
...
✓ 下载完成！
  目录: C:\Users\nekulo\.trainer_search\downloads\Black Myth Wukong
```

### 示例3：查看已安装

**用户：** 查看我已安装的修改器

**Claude：**
```
已安装 2 个修改器:

游戏名                     版本       安装日期             可执行文件
---------------------------------------------------------------------------------------------------
Elden Ring                 v1.12      2026-02-28T11:30:00  EldenRing_Trainer_x64.exe
Black Myth Wukong          v1.0       2026-02-28T10:15:00  Wukong_Trainer.exe
```
