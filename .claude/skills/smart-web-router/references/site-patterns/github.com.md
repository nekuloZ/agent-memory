# GitHub Site Pattern

> 最后更新：2026-03-26

## 验证过的策略

| 操作 | 推荐工具 | 说明 |
|------|---------|------|
| README获取 | Tavily Extract / defuddle | 最快最干净 |
| Issues列表 | Tavily Extract | 静态内容可直接获取 |
| PR列表 | Tavily Extract | 同上 |
| 代码搜索 | Tavily Search | 用搜索代替直接爬取 |
| 用户仓库列表 | CDP Browser | 需要滚动加载 |

## 已知坑

1. **动态加载** - 页面会无限滚动加载，需用CDP Browser处理
2. **登录弹窗** - 会弹出登录框但不影响内容获取，忽略即可
3. **反爬限制** - 频繁访问可能触发限流，添加延迟

## 代理需求

**无需代理** - 直连即可访问

## 交互技巧

```bash
# 用CDP Browser滚动加载仓库列表
curl -X POST -d '{"expression": "window.scrollTo(0, document.body.scrollHeight)"}' "http://127.0.0.1:3456/eval"

# 点击 "Load more" 按钮（如果存在）
curl -X POST -d '{"selector": "button.load-more"}' "http://127.0.0.1:3456/click"
```
