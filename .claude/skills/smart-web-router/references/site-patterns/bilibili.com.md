# bilibili.com Site Pattern

> 最后更新：2026-03-26

## 验证过的策略

| 操作 | 推荐工具 | 说明 |
|------|---------|------|
| 搜索视频 | opencli bilibili | 官方支持 |
| 获取视频信息 | opencli bilibili | 元数据完整 |
| 视频字幕/转录 | video_analyzer skill | B站专用 |
| 弹幕分析 | CDP Browser | 需要渲染 |

## 已知坑

1. **视频下载** - 需要 video_analyzer skill
2. **字幕获取** - 部分视频无字幕或字幕需要登录
3. **动态加载** - 评论等需要滚动加载

## 代理需求

**无需代理** - 国内直连

## 交互技巧

```bash
# 用opencli搜索B站
opencli bilibili "关键词"

# 用video_analyzer获取视频详情
# 见 video_analyzer skill
```

## 登录态

CDP Browser 可连接Chrome继承登录态，获取会员内容（如有）
