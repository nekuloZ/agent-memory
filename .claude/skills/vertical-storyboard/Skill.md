# 短视频竖屏分镜提示词生成器

基于 Nano Banana Pro 9格电影分镜提示词改造，专为短视频平台（抖音、快手、Instagram Reels、YouTube Shorts）设计的竖屏分镜生成器。

---

## 使用方式

**触发词：** "生成分镜"、"短视频分镜"、"竖屏分镜"

```
生成分镜：一个关于咖啡制作的15秒短视频
```

---

## 输出规格

### 分镜格式
- **画幅**: 9:16 竖屏（1080×1920）
- **格子数**: 9格 或 12格 可选
- **总时长**: 15-60秒（短视频标准）

### 每格包含信息
| 字段 | 说明 |
|------|------|
| 镜号 | 第几镜 |
| 时长 | 该镜头时长（秒） |
| 景别 | 特写/近景/中景/全景 |
| 运镜 | 推/拉/摇/移/跟/固定 |
| 画面描述 | 详细视觉内容 |
| 字幕/台词 | 画面文字或旁白 |
| BGM提示 | 音乐节奏点 |

---

## 核心提示词模板

### 9格竖屏短视频分镜模板

```
一个电影级竖屏短视频9格分镜脚本（9:16比例，1080×1920）。

**视频规格：**
- 画幅：9:16 竖屏
- 总时长：约15-30秒
- 风格：短视频平台风格（抖音/快手/Reels/Shorts）
- 节奏：快节奏，前3秒抓人眼球
- 视觉：高饱和度、强对比、竖屏构图

**分镜结构：**
第1镜（0-3秒）【黄金3秒/钩子】
- 景别：特写或近景
- 运镜：快速推入或晃动开场
- 画面：[强视觉冲击内容，制造悬念或好奇]
- 字幕：[大字号，占画面1/3，强烈情绪词]
- BGM：节奏点0，重拍入场

第2镜（3-5秒）【问题/冲突】
- 景别：中景
- 运镜：手持微晃或固定
- 画面：[展示问题或冲突场景]
- 字幕：[疑问句或痛点描述]
- BGM：节奏点1

第3镜（5-7秒）【转折/亮点预告】
- 景别：近景
- 运镜：快速切换或缩放
- 画面：[展示即将揭晓的亮点]
- 字幕：["看完你就懂了" 或 "最后有惊喜"]
- BGM：节奏点2， buildup

第4镜（7-10秒）【核心内容-步骤1】
- 景别：中景或特写
- 运镜：跟拍或固定
- 画面：[核心内容展示]
- 字幕：[步骤说明或知识点]
- BGM：节奏点3，drop

第5镜（10-12秒）【核心内容-步骤2】
- 景别：特写
- 运镜：微距推进
- 画面：[细节展示]
- 字幕：[强调关键信息]
- BGM：节奏点4

第6镜（12-14秒）【高潮/结果】
- 景别：近景或中景
- 运镜：慢动作或定格
- 画面：[成果展示或高潮时刻]
- 字幕：[成果描述或感叹词]
- BGM：节奏点5，高潮

第7镜（14-16秒）【反应/情绪】
- 景别：特写（表情）
- 运镜：轻微推进
- 画面：[人物反应或情绪表达]
- 字幕：[情绪符号或简短评论]
- BGM：节奏点6

第8镜（16-18秒）【总结/金句】
- 景别：中景
- 运镜：固定或轻微环绕
- 画面：[总结画面]
- 字幕：[金句或行动号召]
- BGM：节奏点7

第9镜（18-20秒）【结尾/CTA】
- 景别：特写或logo
- 运镜：淡出或定格
- 画面：[关注引导或品牌露出]
- 字幕：["关注看更多" / "点赞收藏"]
- BGM：节奏点8，淡出

**视觉风格要求：**
- 竖屏构图：主体位于画面上1/3处
- 字幕样式：粗体、描边、高对比色
- 转场：快切、闪白、缩放、模糊
- 色彩：高饱和、暖色调或冷色调统一
- 质感：电影级调色，适度颗粒感

**叙事节奏：**
- 0-3秒：必须出现视觉钩子
- 3-15秒：信息密度高，快速推进
- 15-20秒：情绪高点 + 行动引导
```

---

### 12格竖屏短视频分镜模板（更长版本）

```
一个电影级竖屏短视频12格分镜脚本（9:16比例，1080×1920）。

**视频规格：**
- 画幅：9:16 竖屏
- 总时长：约30-45秒
- 风格：短视频平台风格（抖音/快手/Reels/Shorts）
- 节奏：前3秒抓人，中段展开，结尾强化

**分镜结构：**

第1镜（0-3秒）【黄金3秒钩子】
- 景别：特写
- 运镜：快速推进或晃动
- 画面：[最具冲击力的开场画面]
- 字幕：[大号字体，情绪强烈]
- BGM：重拍开场

第2镜（3-5秒）【背景铺垫】
- 景别：中景
- 运镜：固定或缓慢移动
- 画面：[场景建立]
- 字幕：[简短背景]

第3镜（5-7秒）【问题呈现】
- 景别：近景
- 运镜：手持晃动
- 画面：[展示问题或困境]
- 字幕：[痛点描述]

第4镜（7-9秒）【转折预告】
- 景别：特写
- 运镜：快速缩放
- 画面：[制造期待感]
- 字幕：["但是..." / "直到我发现"]

第5镜（9-11秒）【解决方案-引入】
- 景别：中景
- 运镜：跟拍
- 画面：[方案展示开始]
- 字幕：[方法名称]

第6镜（11-13秒）【解决方案-步骤1】
- 景别：特写
- 运镜：微距推进
- 画面：[详细步骤]
- 字幕：[步骤1说明]

第7镜（13-15秒）【解决方案-步骤2】
- 景别：近景
- 运镜：侧面跟随
- 画面：[继续展示]
- 字幕：[步骤2说明]

第8镜（15-17秒）【解决方案-步骤3】
- 景别：特写
- 运镜：固定
- 画面：[关键细节]
- 字幕：[步骤3说明]

第9镜（17-20秒）【成果展示】
- 景别：中景
- 运镜：环绕或推进
- 画面：[最终成果]
- 字幕：[成果描述]

第10镜（20-23秒）【对比/ Before-After】
- 景别：分屏或切换
- 运镜：固定
- 画面：[前后对比]
- 字幕：[对比文字]

第11镜（23-26秒）【总结/金句】
- 景别：近景
- 运镜：轻微推进
- 画面：[人物总结]
- 字幕：[核心金句]

第12镜（26-30秒）【结尾CTA】
- 景别：特写或logo
- 运镜：淡出
- 画面：[关注引导]
- 字幕：["关注我" / "评论区见"]
```

---

## 使用示例

### 输入
```
生成分镜："一个关于早起自律的励志短视频，9格"
```

### 输出

**短视频分镜脚本：早起自律（9格，9:16竖屏）**

| 镜号 | 时长 | 景别 | 运镜 | 画面描述 | 字幕 | BGM |
|------|------|------|------|----------|------|-----|
| 1 | 0-3s | 特写 | 快速推入 | 闹钟6:00响，手猛地关掉 | "早起的人赢一天" | 重拍入场 |
| 2 | 3-5s | 中景 | 手持晃动 | 床上挣扎的你，天还没亮 | "被窝太舒服了..." | 节奏点1 |
| 3 | 5-7s | 近景 | 快速切换 | 掀开被子起身的动作 | "但我选择改变" | 节奏点2 |
| 4 | 7-10s | 中景 | 跟拍 | 走向窗边拉开窗帘，阳光涌入 | "Day 1" | Drop |
| 5 | 10-12s | 特写 | 微距 | 手冲咖啡，热气升腾 | "从一杯咖啡开始" | 节奏点4 |
| 6 | 12-14s | 近景 | 环绕 | 书桌前阅读/工作的背影 | "每天进步1%" | 节奏点5 |
| 7 | 14-16s | 特写 | 推进 | 手表显示7:00，已完成多项任务 | "7点，别人刚醒" | 节奏点6 |
| 8 | 16-18s | 中景 | 固定 | 对着镜头自信微笑 | "你也可以做到" | 节奏点7 |
| 9 | 18-20s | 特写 | 淡出 | 关注按钮+头像 | "关注我，一起变好" | 淡出 |

---

## 快捷指令

### 生成分镜
```
生成分镜：[视频主题]，[9格/12格]

示例：
- "生成分镜：咖啡制作教程，9格"
- "生成分镜：职场干货分享，12格"
- "生成分镜：产品种草视频，9格"
```

### 分镜转 Nano Banana 提示词
```
把分镜转为 Nano Banana 提示词：[粘贴分镜内容]
```

**重要**：生成 Nano Banana 提示词时，必须先阅读并遵循《提示词编写指南》的规范（见下方"Nano Banana 提示词编写规范"章节）。

---

## 提示词特点

| 特点 | 说明 |
|------|------|
| **竖屏优先** | 9:16构图，主体放在上1/3 |
| **前3秒法则** | 第一镜必须是强视觉钩子 |
| **节奏感强** | 每2-3秒一个节奏点，配合BGM |
| **字幕友好** | 预留字幕空间，大号粗体 |
| **平台适配** | 适配抖音、快手、Reels、Shorts |

---

## 进阶用法

### 指定风格
```
生成分镜：美妆教程，9格，风格要高级ins风
```

### 指定BGM类型
```
生成分镜：健身激励视频，9格，BGM用电子音乐卡点
```

### 指定情绪
```
生成分镜：治愈系Vlog，12格，情绪要温暖舒缓
```

---

## 参考来源

- 基于 Nano Banana Pro 9格电影分镜提示词改造
- 适配短视频平台竖屏内容创作需求
- 针对移动端观看习惯优化构图和节奏

---

## Nano Banana 提示词编写规范（CRITICAL）

> **核心理念**：提示词是"约束"而非"建议"。模糊的描述会被 AI 忽略或用"平均解"填充，必须用强制性的、空间化的、可验证的描述。

### 1. 手部描述规范（critical）

**标准公式**：
```
[手指] + [位置] + [动作] + [禁止事项]
```

**正确示例**：
```
✅ "Four fingers (index, middle, ring, pinky) wrapped around the LOWER HANDLE
     below the two silver buttons, thumb resting on the side"

✅ "Natural relaxed grip - NOT tense, NOT clenched, fingers evenly spaced"

✅ "Palm facing slightly upward in a presenting gesture, hand at chest level"
```

**关键检查点**：
- [ ] 手指数量 = 5（ anatomically correct hands, proper finger count）
- [ ] 握持位置在下柄（lower handle below buttons）
- [ ] 手指没有穿过物体
- [ ] 没有挡住按钮等关键部位
- [ ] 手腕角度自然（wrist straight, not bent）

---

### 2. 产品朝向规范（critical）

**戴森吹风机类产品描述公式**：
```
[部件] + [方向] + [相对位置] + [禁止朝向]
```

**关键部件命名**：
| 部位 | 标准名称 | 错误名称 |
|------|---------|---------|
| 粉色圆环出风口 | "pink hollow ring" / "outlet" | "head", "top" |
| 深灰色手柄 | "handle" / "grip" | "body", "stick" |
| 银色按钮 | "two silver buttons" | "controls" |
| 进风口滤网 | "filter at bottom of handle" | "back" |

**朝向描述标准（必须这样写）**：
```
✅ "吹风面（风从这里吹出，有圆形空洞的一面）指向她的头部/头发"
✅ "手持面（光滑粉色面，握持时朝向人的一面）背对头发"

English:
✅ "The AIR-OUT side (showing the hollow opening where air blows out) faces her hair"
✅ "The HAND-HELD side (smooth pink surface) faces away from hair, toward her hand"
```

**❌ 绝对禁止的描述**：
- "外表面/内表面" - 容易混淆
- "出风口展示圆环中间的圆形空洞面对头发" - 逻辑混乱
- "45-degree angle" - 没说清楚是哪个轴的45度

---

### 3. 表情描述规范

**标准公式**：
```
[眉毛] + [眼睛] + [嘴巴] + [整体情绪] + [禁止表情]
```

**正确示例**：
```
✅ "Eyebrows raised and furrowed in surprise, eyes widened,
     mouth slightly open in 'wow' expression"

✅ "Biggest energetic smile - teeth clearly showing, eyes squinting with joy
     (crow's feet visible), entire face lit up with excitement"

✅ "Furrowed brows tightly knit, obvious pouting lips like sad emoji,
     visible disappointment - NOT angry, NOT crying"
```

**关键检查点**：
- [ ] 眉毛是否与情绪匹配？
- [ ] 眼睛是否参与表情（不只是嘴在笑）？
- [ ] 是否有"死鱼眼"或"塑料感"？
- [ ] 笑容自然有牙齿（不是假笑）

---

### 4. 手机/手持设备视角规范（critical）

**核心原则**：
> 当人物手持手机/设备查看时，镜头不应看到屏幕内容。

**标准公式**：
```
[手持方式] + [手机朝向] + [可见部分] + [禁止事项]
```

**正确示例**：
```
✅ "Right hand holding phone with BACK OF PHONE facing camera
    (screen facing her face, screen NOT visible to camera)"

✅ "PHONE POSITION CRITICAL: Phone back facing camera, screen facing her face.
    Camera sees phone back/edge only, ABSOLUTELY NO phone screen visible to camera"
```

**场景对照表**：
| 场景 | 镜头看到 | 角色看到 | 写法 |
|------|---------|---------|------|
| 人物看手机 | 手机背面/侧面 | 手机屏幕 | "phone back facing camera, screen facing her face" |
| 手机特写（纯产品） | 手机屏幕 | （无人物） | "close-up of iPhone screen showing time" |
| 人物自拍 | 手机屏幕+人脸 | 手机屏幕 | "holding phone at arm length, screen facing camera AND her face" |

---

### 5. 整体结构模板

```markdown
[比例和风格]
9:16 vertical TikTok style video frame, photorealistic live action.

[主体]
Subject: [人物描述，保持一致性]

[关键要素 - 按优先级排序，全部大写 CRITICAL 标记]
1. HAND POSITION CRITICAL: [详细手部描述]
2. Product direction CRITICAL: [详细朝向描述]
3. Expression CRITICAL: [详细表情描述]
4. Phone position CRITICAL: [如手持手机，必须写明朝向]

[动作]
Action: [正在做什么]

[产品细节]
Product: [颜色、材质、关键特征 - 每个提示词中重复完整定义]

[背景]
Background: [环境描述]

[光线]
Lighting: [光效描述]

[风格强调]
Style: photorealistic live action, shot on iPhone, natural lighting
```

---

### 6. 有效关键词库

**手部相关**：
- `anatomically correct hands`
- `proper finger count`
- `four fingers wrapped around lower handle`
- `thumb resting on side`
- `wrist straight, not bent`

**产品相关**：
- `lower handle below buttons`
- `hollow ring points toward`
- `tilted upward/downward at 45 degrees`
- `lying on its side`
- `parallel to body`

**表情相关**：
- `eyebrows raised/furrowed/knit`
- `eyes widened/squinting/crinkling`
- `mouth slightly open/pouting/smiling with teeth`
- `genuine smile (not fake)`

**平台风格**：
- `photorealistic live action`
- `TikTok UGC vlog aesthetic`
- `shot on iPhone`
- `authentic skin texture`

---

### 7. 生成前检查表

```
□ 手部描述用了"four fingers wrapped around"格式
□ 产品朝向用了"points toward/faces/aimed at"格式
□ 吹风机区分了"吹风面"和"手持面"
□ 角度描述明确了参照物（如"tilted upward at 45 degrees"）
□ 表情描述了眉毛+眼睛+嘴巴
□ 【人物看手机时】手机背面对镜头，屏幕不对镜头
□ 关键约束用了"CRITICAL"标记
□ 禁止事项用了"NOT"明确排除
```

---

### 8. 分镜转 Nano Banana 提示词工作流

**触发词**：
```
把分镜转为 Nano Banana 提示词：[粘贴分镜内容]
```

**执行步骤**：
1. **解析分镜**：提取每镜的景别、画面描述、情绪
2. **应用规范**：按上述 7 项检查表逐一核对
3. **生成提示词**：按"整体结构模板"格式输出
4. **自检**：对照"历史错误记录"排查常见问题

**输出格式示例**：
```python
FRAMES = [
    {
        "id": "01",
        "name": "scene01_alarm",
        "prompt": """9:16 vertical TikTok style...

Subject: 24-year-old East Asian female...

HAND POSITION CRITICAL: ...
Product direction CRITICAL: ...
Expression CRITICAL: ...

Action: ...

Product: Dark gray hair dryer with PINK HOLLOW RING...

Background: ...
Lighting: Bright warm natural window light
Style: photorealistic live action, shot on iPhone"""
    },
    # ...
]
```
