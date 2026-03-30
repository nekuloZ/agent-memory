# Twitter/X Site Pattern

> 最后更新：2026-03-26

## 验证过的策略

| 操作 | 推荐工具 | 说明 |
|------|---------|------|
| 搜索推文 | opencli twitter | 最稳定 |
| 获取用户推文 | opencli twitter | 直接调用官方API |
| 提取推文内容 | CDP Browser | 需要渲染JS |

## 已知坑

1. **登录墙** - 推文内容需要登录才能完整查看
2. **速率限制** - API调用频繁会触发限流
3. **重定向** - twitter.com → x.com 需要处理

## 代理需求

**必须代理** - twitter.com 和 x.com 都需要代理访问

## 交互技巧

```bash
# 用opencli获取用户推文
opencli twitter "用户名 --count 10"

# 用CDP Browser截图
curl -X POST "http://127.0.0.1:3456/navigate?url=https://twitter.com/用户名"
curl "http://127.0.0.1:3456/screenshot" -o tweet.png
```

## 登录态处理

CDP Browser 可以连接用户已有的Chrome实例，继承登录状态。
如需登录，请在Chrome中手动授权。
