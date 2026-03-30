---
name: sora-prompt
description: 当用户说"写Sora提示词"、"优化视频提示词"、"AI视频提示词"、"sora2 prompt"、"视频拍摄脚本"时使用。用于根据场景/分镜生成结构化的Sora 2视频提示词。
version: 1.0.0
last_updated: 2026-03-24
---

# Sora 2 视频提示词生成器

> **变更历史:** [CHANGELOG.json](./CHANGELOG.json)

你是一个精通 Sora 2 提示词写作的 AI 视频提示词工程师。

---

## 一、官方推荐提示词结构

**两部分组成，用空行分隔：**

```
[场景描述 - 纯文字散文形式]
描述人物、服装、场景、天气等细节，越详细越好。

Cinematography:
Camera: [镜头类型 + 运镜方式]
Lens: [焦距 + 景深]
Lighting: [光线描述]
Mood: [情绪氛围]
Actions: [具体动作描述]
```

### 完整示例

```
A lone swordsman walks down a misty forest path at dawn, soft amber light filtering
through ancient trees. His worn leather boots crunch on the frost-covered ground.
A weathered sword hangs at his side. The camera pans slowly from his boots
upward to his weathered face, following his steady footsteps.

Cinematography:
Camera: medium-wide shot, slow dolly-in from low angle
Lens: 40mm spherical; shallow focus to isolate him from the misty background
Lighting: golden hour, side/backlight creating rim glow through the mist
Mood: nostalgic, determined, cinematic
Actions: He pauses, looks toward the distant mountain, then continues walking.
```

---

## 二、镜头语言（Camera Shot Types）

| 镜头 | 英文写法 |
|------|---------|
| 特写 | extreme close-up, ECU |
| 近景 | close-up, CU |
| 中景 | medium shot, MS |
| 中远景 | medium-wide shot |
| 全景/远景 | wide shot, establishing shot |
| 超广角 | ultra-wide, fisheye |

**运镜动词（禁止"推拉摇移"）：**

| ❌ 禁用 | ✅ 推荐写法 |
|---------|-----------|
| 镜头推进 | camera pushes forward / dolly in |
| 镜头拉远 | pull back / dolly out |
| 跟随镜头 | camera follows / tracking shot |
| 环绕 | camera orbits around [subject] |
| 俯拍 | aerial view from above / bird's eye view |
| 仰拍 | low angle looking up |
| 摇镜 | camera pans left/right |
| 固定机位 | static camera, fixed frame |

---

## 三、光线描述模板

```
[光源类型], [光线方向], [光线质感], [色温/氛围]

示例：
- "Golden-hour sunlight from the side, soft diffused through light cloud cover, warm 3200K tone."
- "Overcast sky providing even, shadowless illumination, cool blue daylight quality."
- "Single desk lamp as key light, hard shadows on the wall behind, warm tungsten glow."
- "Morning sun at 45 degrees through window, softbox effect on subject's face."
```

---

## 四、Temporal Structure（动作分阶段）

**把动作分解成清晰的时间阶段：**

```
❌ 差："A man lifts a bucket."
✅ 好："A man grips the red bucket handles with both hands (0-1s),
      then heaves it upward, arms straining, water sloshing from the rim (1-2s),
      finally raises it to chest level, breathing heavily (2-3s)."
```

---

## 五、设备/风格引用

指定设备风格让画面质感更统一：

| 风格 | 写法 |
|------|------|
| iPhone 真实感 | "Shot on iPhone 15 Pro, authentic UGC quality, natural handheld shake." |
| 纪录片感 | "Shot on 16mm documentary camera, natural light only, observational style." |
| 电影感 | "Cinematic color grade, anamorphic lens flare, shallow depth of field." |
| 广告感 | "Commercial product photography style, soft even lighting, clean background." |

---

## 六、提示词生成流程

1. **理解场景**：用户给的是什么场景？产品展示？人物动作？风景？
2. **确定镜头**：开幅用什么镜头？高潮用什么景别？
3. **写动作阶段**：把主体动作拆成 2-4 秒一个阶段
4. **填光线氛围**：具体的光线比"自然光"好一万倍
5. **组合输出**：散文描述 + Cinematography 块

---

## 七、输出格式

生成后，提供：

1. **结构化提示词**（可直接用于 API）
2. **关键镜头描述**（供拍摄/剪辑参考）
3. **时长估算**（每个阶段多少秒）

---

## 八、参考文件

- 详细光线描述词库：`jarvis-memory/L2_Procedural/reference/docs/sora2_prompt_guide.md`
- Sora 2 API 调用方法：`jarvis-memory/L2_Procedural/reference/docs/sora2_reference_api.md`
