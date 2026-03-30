#!/usr/bin/env python3
"""
抖音视频真实URL抓取器
通过监听网络响应获取真实CDN链接
"""
import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright

TARGET_URL = "https://v.douyin.com/zphPK4AAz-I/"
OUTPUT_DIR = Path("video_analysis/01_douyin_pump")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

async def grab_video_url():
    video_urls = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()

        # 加载 cookie
        cookie_file = Path("douyin_cookies.json")
        if cookie_file.exists():
            import json
            raw = json.loads(cookie_file.read_text(encoding="utf-8"))
            # 支持 list 格式或 {cookies: [...]} 格式
            cookies = raw if isinstance(raw, list) else raw.get("cookies", [])
            # 过滤掉无效 cookie
            valid = []
            for c in cookies:
                if c.get("name") and c.get("value"):
                    valid.append({
                        "name": c["name"],
                        "value": c["value"],
                        "domain": c.get("domain", ".douyin.com"),
                        "path": c.get("path", "/"),
                    })
            if valid:
                await context.add_cookies(valid)
                print(f"[OK] 加载了 {len(valid)} 个 cookie")

        page = await context.new_page()

        # 监听网络响应，捕获视频 CDN URL
        async def on_response(response):
            url = response.url
            content_type = response.headers.get("content-type", "")
            if (
                "video" in content_type
                or url.endswith(".mp4")
                or ("v26-web" in url and "mp4" in url)
                or ("aweme" in url and "mp4" in url)
                or ("douyinvod" in url)
                or ("bytecdn" in url and "video" in url)
            ):
                if url not in video_urls:
                    video_urls.append(url)
                    print(f"[捕获] {url[:100]}...")

        page.on("response", on_response)

        print(f"[INFO] 打开视频页面...")
        await page.goto(TARGET_URL, wait_until="domcontentloaded")
        await page.wait_for_timeout(8000)  # 等待视频加载

        # 尝试点击播放
        try:
            await page.click("video", timeout=3000)
        except:
            pass

        await page.wait_for_timeout(5000)

        await browser.close()

    if video_urls:
        print(f"\n[OK] 找到 {len(video_urls)} 个视频URL:")
        for i, url in enumerate(video_urls, 1):
            print(f"  {i}. {url}")

        # 保存到文件
        url_file = OUTPUT_DIR / "video_cdn_urls.txt"
        url_file.write_text("\n".join(video_urls), encoding="utf-8")
        print(f"\n[OK] URL已保存到: {url_file}")

        # 用最长的URL下载（通常是完整视频）
        best_url = max(video_urls, key=len)
        print(f"\n[INFO] 开始下载最佳URL...")
        import urllib.request
        import ssl
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE

        out_file = OUTPUT_DIR / "video.mp4"
        req = urllib.request.Request(best_url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://www.douyin.com/",
        })
        with urllib.request.urlopen(req, context=ssl_ctx, timeout=60) as resp:
            total = int(resp.headers.get("Content-Length", 0))
            data = resp.read()
            out_file.write_bytes(data)
            print(f"[OK] 下载完成: {out_file} ({len(data)//1024}KB)")
    else:
        print("[WARN] 未捕获到视频URL，请检查页面是否正常加载")

asyncio.run(grab_video_url())
