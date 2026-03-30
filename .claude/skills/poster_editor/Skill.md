# 海报编辑器

快速修改海报文字，支持精确定位、字体匹配、批量处理。

---

## 触发词

| 场景 | 触发词 | 示例 |
|------|--------|------|
| 编辑海报 | "编辑海报"、"修改海报文字"、"改海报" | "编辑海报，把标题改成 xxx" |
| 单区域修改 | "改海报某处文字"、"替换海报文字" | "改海报标题" |
| 批量修改 | "批量修改海报"、"多处修改" | "批量修改海报上的公司名" |
| 添加底部信息 | "加上海报落款"、"海报底部加公司" | "海报底部加上公司信息" |

---

## 文件位置

**Skill 脚本目录:** `.claude/skills/poster_editor/scripts/`

| 脚本 | 用途 | 命令 |
|------|------|------|
| `edit_single.py` | 单区域修改 | `python scripts/edit_single.py` |
| `edit_multi.py` | 多区域批量 | `python scripts/edit_multi.py` |
| `add_footer.py` | 底部色块+文字 | `python scripts/add_footer.py` |

---

## 快速使用

### 方法 1：直接用脚本（推荐）

```python
# 1. 复制配置模板到工作目录
cp .claude/skills/poster_editor/scripts/edit_single.py ./my_edit.py

# 2. 修改 CONFIG 区域（坐标、文字、字体）
# 3. 运行
python my_edit.py
```

### 方法 2：交互式编辑

用户提供信息后，Claude 自动生成配置并执行：

```
用户：编辑海报，把标题 "旧标题" 改成 "新标题"
Claude：请提供原图路径，并告诉我标题区域的坐标
用户：原图是 poster.png，坐标大概是中间位置
Claude：请在 PS 或画图中获取精确坐标 (x1,y1,x2,y2)，或我先帮你标个大概位置？
```

---

## 坐标获取方法

### 方法 1：Photoshop（最精确）
1. 打开图片
2. 鼠标悬停在目标位置
3. 查看【信息】面板显示的 X,Y 坐标

### 方法 2：Windows 画图
1. 右键图片 → 打开方式 → 画图
2. 鼠标移动到目标位置
3. 查看左下角状态栏坐标

### 方法 3：QQ/微信截图
1. 按截图快捷键
2. 移动鼠标，看显示的坐标
3. 估算大致位置

---

## 配置参数说明

### 单区域配置 (edit_single.py)

```python
CONFIG = {
    "input": "原图.png",           # 输入文件
    "output": "结果.png",          # 输出文件
    "box": {
        "x1": 100, "y1": 200,     # 涂色区域左上角
        "x2": 500, "y2": 300      # 涂色区域右下角
    },
    "bg_color": (255, 254, 252),   # 背景色 RGB
    "text": "新文字",              # 新文字内容
    "font_name": "C:/Windows/Fonts/msyh.ttc",  # 字体路径
    "font_size": 34,               # 字号
    "text_color": (68, 68, 68),    # 字色 RGB
    "align": "center",             # 对齐: left/center/right
    "center_x": 300,               # 水平中心点
    "top_y": 210                   # 顶部 Y 坐标
}
```

### 常用字体

| 字体 | 路径 | 用途 |
|------|------|------|
| 微软雅黑常规 | `C:/Windows/Fonts/msyh.ttc` | 正文 |
| 微软雅黑粗体 | `C:/Windows/Fonts/msyhbd.ttc` | 标题 |
| 黑体 | `C:/Windows/Fonts/simhei.ttf` | 标题 |
| 阿里巴巴普惠体 | `AlibabaPuHuiTi-3-85-Bold` | 商业海报 |

### 常用颜色

| 颜色 | RGB | 用途 |
|------|-----|------|
| 深灰 | `(68, 68, 68)` | 正文 |
| 纯黑 | `(0, 0, 0)` | 标题 |
| 白色偏暖 | `(255, 254, 252)` | 背景 |
| 米黄 | `(254, 221, 173)` | 强调背景 |
| 红色 | `(237, 29, 0)` | 重点文字 |

---

## 工作流程

```
需求确认 → 坐标获取 → 配置脚本 → 生成测试 → 调整确认
```

### 最佳实践

1. **先涂色验证位置** - 先用明显颜色（红色）涂色，确认覆盖范围
2. **分版本迭代** - `poster-v1.png` → `poster-v2.png` → `poster-final.png`
3. **保存配置** - 同系列海报复用坐标参数

---

## 示例任务

### 任务：修改海报公司名

**需求：** 把海报底部的 "旧公司名" 改成 "中国联通"

**执行：**

1. 获取坐标（PS 或画图）：
   - 底部区域：`x1=937, y1=3038, x2=1517, y2=3288`

2. 修改 `edit_single.py` 的 CONFIG：
   ```python
   CONFIG = {
       "input": "poster.png",
       "output": "poster-new.png",
       "box": {"x1": 937, "y1": 3038, "x2": 1517, "y2": 3288},
       "bg_color": (254, 221, 173),  # 米黄色背景
       "text": "中国联通",
       "font_name": "C:/Windows/Fonts/msyhbd.ttc",
       "font_size": 42,
       "text_color": (237, 29, 0),  # 红色
       "align": "center",
       "center_x": 1228,
       "top_y": 3213
   }
   ```

3. 运行：`python edit_single.py`

---

## 注意事项

- 坐标是相对于整张图的绝对坐标
- 字体未安装会回退到默认字体
- 涂色区域要完全覆盖原文字，避免残留
- 最终输出为 PNG 格式

---

> **变更历史:** [CHANGELOG.json](./CHANGELOG.json)
