---
name: douyin-ad-prompt
description: |
  **必须**使用此 skill 当用户需要：
  - 生成抖音/ TikTok 竖屏短视频广告提示词
  - 为 Veo 3 / 可灵 / 即梦 / Sora 等 AI 视频工具写 9:16 广告视频 prompt
  - 将产品信息转化为 AI 视频生成可用的结构化提示词
  - 提到"抖音广告"、"竖屏视频"、"9:16 产品视频"、"短视频脚本转提示词"等场景

  此 skill 专门优化抖音竖屏广告场景，包含抓眼球开场、快节奏剪辑，产品卖点可视化等电商短视频要素。

  **触发关键词**：抖音广告、竖屏视频、9:16、产品视频、Veo 3 广告，短视频提示词、带货视频
version: v1.4
last_updated: 2026-03-26
mode: ops
---

# 抖音竖屏短视频广告提示词生成器

> 专为 AI 视频生成工具（Veo 3 / 可灵 / 即梦 / 海螺 / Sora）优化的 9:16 竖屏广告视频提示词生成
>
> **核心原则：一张分镜图 → 一个视频片段，分别生成，后期拼接**

---

## ⚠️ 重要：竖屏格式问题

### Veo 3 (aichiapi) 的限制
- 生成的是**横屏容器**（如 1280x720）
- 但画面内容可以是**竖屏**（中间，两边黑边）
- **关键**：需要在提示词中强制强调竖屏构图，避免画面中途旋转成横屏

### 保持竖屏的提示词技巧

**必须包含以下关键句：**
```
9:16 VERTICAL PORTRAIT VIDEO.
CRITICAL: ALWAYS maintain VERTICAL orientation, NEVER rotate.
Keep subject centered in frame.
No panning to landscape/horizontal.
```

**避免的动作描述：**
- ❌ "camera pans left/right"
- ❌ "side view", "profile shot"
- ❌ "orbiting", "rotating camera"

**推荐的动作描述：**
- ✅ "camera pushes in", "pulls back"
- ✅ "medium shot to close-up"
- ✅ "front facing", "toward camera"

---

## 重要说明：AI 视频生成的工作流

### ❌ 不要这样做
上传**分镜多宫格图片**给 Veo 3，期望它自动生成完整叙事视频。

**结果：** Veo 3 只会把多宫格当成一张图做 zoom/pan 动画，完全不理解分镜叙事。

### ✅ 正确工作流

```
分镜多宫格（你的规划参考）
    ↓
拆分成 N 张单独的分镜图（每镜一张）
    ↓
每镜单独上传 + 写专门提示词 → 生成 4-8 秒片段
    ↓
人工剪辑拼接成 15-30 秒完整视频
```

**关键理解：**
- Veo 3 一次只能理解**一张图**
- 生成**一个场景**的 4-8 秒视频
- 多个场景需要**分别生成**，后期拼接
- 人物/产品一致性靠**双图参考**控制（分镜图 + 产品图）

---

## 双图参考技巧

### 什么时候用双图参考？

| 场景 | 参考图数量 | 说明 |
|------|-----------|------|
| 纯场景（无产品） | 1张 | 只需分镜图 |
| 产品特写/展示 | 2张 | 分镜图 + 产品白底图 |
| 使用演示 | 2张 | 分镜图 + 产品白底图 |

### 双图参考格式

```json
{
  "contents": [{
    "parts": [
      {"text": "提示词"},
      {"inlineData": {"mimeType": "image/png", "data": "分镜图base64"}},
      {"inlineData": {"mimeType": "image/png", "data": "产品图base64"}}
    ]
  }],
  "generationConfig": {
    "aspectRatio": "9:16",
    "duration": "5s"
  }
}
```

### 提示词格式（双图参考）

```
Cinematic video based on two reference images.

IMAGE 1 (scene composition): Use this layout - [场景描述]

IMAGE 2 (product reference): Match this exact product - [产品外观描述]

ACTION: [核心动作描述]

CRITICAL: Maintain vertical orientation throughout. 9:16 format.
```

---

## 输出格式（每镜一个）

为**每一个分镜**单独输出以下格式：

```json
{
  "shot_info": {
    "shot_number": "第1镜/共6镜",
    "duration": "6秒",
    "aspect_ratio": "9:16"
  },
  "reference_images": {
    "scene": "分镜图路径",
    "product": "产品图路径（可选）"
  },

  "prompt": {
    "scene_description": "场景整体描述",
    "action": "人物/产品动作（必须有动作！）",
    "camera_movement": "运镜：推/拉（避免横移/旋转）",
    "lighting": "光线描述",
    "style": "风格"
  },

  "vertical_tips": "保持竖屏的特别提示",

  "continuity": {
    "previous_shot_end": "前一镜结尾状态",
    "current_shot_start": "本镜开场承接",
    "product_appearance": "产品外观（每镜保持一致）",
    "character_appearance": "人物外观（每镜保持一致）"
  }
}
```

---

## 分镜提示词模板

### 竖屏构图必须项（每镜都要加）

```
9:16 VERTICAL PORTRAIT VIDEO.

CRITICAL RULES:
- ALWAYS maintain VERTICAL orientation, NEVER rotate
- Keep subject centered in frame
- No panning to landscape/horizontal
- Natural documentary handheld feel
```

### 痛点开场（第1镜）

**公式：** `[Cinematography] + [Subject] + [Action] + [Context] + [Style & Ambiance]`

**提示词：**
```
9:16 VERTICAL PORTRAIT VIDEO.
CRITICAL: ALWAYS maintain VERTICAL orientation, NEVER rotate. Keep subject centered.

[SONOGRAPHY] Close-up, documentary handheld with subtle shake.

[SUBJECT] A 50-year-old Chinese villager in red-blue plaid shirt and dark work trousers.

[ACTION] Squats at concrete fishpond edge, both hands gripping a red plastic bucket, LIFTING it from murky green water. Forearm muscles visibly tensed. Water drips from bucket rim.

[CONTEXT] Rural China fishpond setting. Murky green water. Overcast sky. Empty buckets nearby.

[STYLE] Natural diffused daylight. Documentary realism. Authentic UGC quality.
```

### 产品登场（第3镜）

**公式：** `[Cinematography] + [Subject] + [Action] + [Context] + [Style & Ambiance]`

**提示词（双图参考）：**
```
9:16 VERTICAL PORTRAIT VIDEO.
CRITICAL: ALWAYS maintain VERTICAL orientation, NEVER rotate. Keep subject centered.

Two reference images:
- Image 1 (scene): Villager at fishpond holding product toward camera
- Image 2 (product): Match this EXACT red pump appearance

[CINEMATOGRAPHY] Medium close-up, camera FAST PUSHES IN to product.

[SUBJECT] Same villager in plaid shirt, front facing toward camera.

[ACTION] Right arm EXTENDS FORWARD holding red cylindrical pump, presenting toward camera.

[CONTEXT] Background fishpond blurs to creamy bokeh.

[STYLE] Warm natural daylight. Product photography meets documentary.
```

### 使用演示（第4镜）

**公式：** `[Cinematography] + [Subject] + [Action] + [Context] + [Style & Ambiance]`

**提示词（双图参考）：**
```
9:16 VERTICAL PORTRAIT VIDEO.
CRITICAL: ALWAYS maintain VERTICAL orientation, NEVER rotate. Keep subject centered.

Two reference images:
- Image 1 (scene): Villager bending over pond edge, lowering pump into water
- Image 2 (product): Match this EXACT red pump appearance

[CINEMATOGRAPHY] Two-shot sequence. Close-up on hands.

[SUBJECT] Same villager in plaid shirt, leaning forward over concrete edge.

[ACTION] LEFT hand lowers red pump into murky water creating ripples. RIGHT hand holds small black remote, thumb pressing circular ON button.

[CONTEXT] Blue hose drapes over concrete bank. Pond water below. Concrete edge visible.

[STYLE] Documentary action. Natural pond reflections. Tactile detail.
```

---

## 竖屏构图要点

### ✅ 推荐运镜（成功率最高）

| 运镜 | 提示词写法 | 效果 |
|------|-----------|------|
| **推近** | "camera pushes in", "FAST PUSH IN to close-up" | 产品特写、强调细节 |
| **拉远** | "camera pulls back", "slow pull back to reveal" | 展示全貌、场景介绍 |
| **固定机位** | "fixed camera", "static shot" | 最稳定，避免旋转 |

### ❌ 避免运镜（容易导致横屏）

| 运镜 | 原因 |
|------|------|
| **横移 pan** | 容易触发横屏构图 |
| **旋转 rotate** | 直接导致画面翻转 |
| **环绕 orbit** | 360度展示，不适合竖屏 |
| **倾斜 tilt** | 破坏竖屏稳定性 |

### 相机控制核心原则

```
1. 主体移动 > 相机移动（让产品/人移动，相机固定）
2. 推近/拉远 > 横移/旋转（竖屏最适合纵深运动）
3. 正面角度 > 侧面角度（竖屏横向空间有限）
4. 特写/近景 > 远景/全景（竖屏视野窄，不适合大场景）
```

### 景别推荐

| 景别 | 适用场景 | 提示词 |
|------|---------|--------|
| **特写** | 产品细节展示 | "extreme close-up", "product detail" |
| **近景** | 人物表情/动作 | "close-up shot", "medium close-up" |
| **中景** | 人物+产品互动 | "medium shot", "waist-up view" |

### API 参数配置（关键）

```python
payload = {
    "generationConfig": {
        "responseModalities": ["VIDEO"],
        "duration": "5s",
        "aspectRatio": "9:16"  # 必须设置！
    }
}
```

**提示词中必须包含：**
```
9:16 VERTICAL PORTRAIT VIDEO.
CRITICAL: ALWAYS maintain VERTICAL orientation, NEVER rotate.
Keep subject centered in frame.
```

---

## 产品类型模板

### 模板 A：美妆护肤
1. 痛点特写（干燥/暗沉）
2. 产品展示
3. 使用演示
4. 效果展示

### 模板 B：3C数码
1. 产品特写
2. 功能演示
3. 使用场景
4. 价格/购买引导

### 模板 C：食品饮料
1. 食欲感特写
2. 制作过程
3. 享用场景
4. 产品展示

### 模板 D：家居用品
1. 问题场景（人工浇水累/慢）
2. 产品登场（竖屏展示）
3. 使用演示（竖向动作）
4. 效果对比

---

## 完整工作流程

### Step 1：确定分镜数量
**建议 3-6 个分镜**，每个 4-8 秒，总共 15-30 秒。

### Step 2：为每个分镜准备
- **分镜图**（单张，不是多宫格）
- **产品白底图**（用于双图参考）
- **产品固定描述**（每镜保持一致）
- **人物固定描述**（每镜保持一致）

### Step 3：生成提示词
- 每镜单独生成
- 包含竖屏强制要求
- 使用双图参考（当有产品时）

### Step 4：分别生成视频
- 每镜单独上传到 Veo 3 / 可灵 / 即梦
- 生成 4-8 秒片段
- 注意：横屏容器 + 竖屏内容是正常的

### Step 5：后期处理
- 用剪映拼接
- 确认每段视频画面内容是竖屏（中间，两边可能黑边）
- 添加 BGM 和字幕

---

## 常见问题

### Q: Veo 3 生成的是横屏视频？
A: 是的，这是 aichiapi 的限制。视频容器是 1280x720，但**画面内容是竖屏**（中间，两边黑边）。这是正常的，后期裁剪即可。

### Q: 怎么确保画面全程竖屏？
A: 在提示词开头加：
```
9:16 VERTICAL PORTRAIT VIDEO.
CRITICAL: Always vertical, never rotate.
```

### Q: 为什么不要上传多宫格分镜图？
A: Veo 3 会把整张多宫格当成一张图，只做简单的 zoom/pan，完全不理解分镜叙事。

### Q: 人物在不同片段里长得不一样？
A:
- 方案1：只拍产品，不出现人物
- 方案2：用双图参考（分镜图 + 产品图）
- 方案3：避免人物特写，多用产品特写

---

## 使用示例

**用户：** "我有6个分镜图，是抽水泵广告。第1镜是农民弯腰提水桶很累，第2镜是拿出抽水泵..."

**处理步骤：**
1. 确认产品固定描述（红色潜水泵，黑色把手，银色过滤网，金色出水口）
2. 确认是单张分镜图
3. 为每一镜生成带竖屏要求的提示词
4. 提示用户用双图参考（分镜图 + 产品白底图）

---

## API 调用示例（Python）

```python
import requests
import base64

API_KEY = "your_api_key"
MODEL = "veo_3_1_i2v_s_fast_ultra_fl"
ENDPOINT = f"https://media.aichiapi.com/v1beta/models/{MODEL}:generateContent"

def generate_video(prompt, frame_b64, product_b64=None):
    """生成竖屏视频"""

    # 构建 parts
    parts = [
        {"text": prompt},
        {"inlineData": {"mimeType": "image/png", "data": frame_b64}}
    ]
    if product_b64:
        parts.append({"inlineData": {"mimeType": "image/png", "data": product_b64}})

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["VIDEO"],
            "duration": "5s",
            "aspectRatio": "9:16"
        }
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    resp = requests.post(ENDPOINT, headers=headers, json=payload, timeout=300)
    return resp.json()
```

---

## 检查清单

生成前确认提示词包含：
- [ ] `9:16 VERTICAL PORTRAIT VIDEO.`
- [ ] `CRITICAL: Always vertical, never rotate.`
- [ ] 避免横移/旋转动作描述
- [ ] 推荐推近/拉远运镜
