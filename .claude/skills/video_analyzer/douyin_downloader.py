#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抖音视频下载器 - Playwright版
绕过反爬机制，直接控制浏览器下载视频
"""

import sys
import os

# 设置UTF-8编码
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)

import asyncio
import json
import re
import time
import urllib.request
import ssl
from pathlib import Path
from urllib.parse import urlparse, parse_qs, unquote
from playwright.async_api import async_playwright, Page, BrowserContext


class DouyinDownloader:
    def __init__(self):
        self.cookie_file = Path("douyin_cookies.json")
        self.output_dir = Path("video_analysis")
        self.output_dir.mkdir(exist_ok=True)

    def log(self, msg: str):
        timestamp = time.strftime('%H:%M:%S')
        print(f"[{timestamp}] {msg}")

    def load_cookies(self) -> list:
        """加载cookie"""
        if self.cookie_file.exists():
            try:
                data = json.loads(self.cookie_file.read_text(encoding='utf-8'))
                cookies = data.get('cookies', [])
                self.log(f"已加载 {len(cookies)} 个cookie")
                return cookies
            except Exception as e:
                self.log(f"加载cookie失败: {e}")
        return []

    def extract_video_id(self, url: str) -> str:
        """提取视频ID"""
        # 处理短链接 https://v.douyin.com/xxxxx/
        if 'v.douyin.com' in url:
            return url.split('/')[-1].split('?')[0]
        # 处理长链接 https://www.douyin.com/video/123456
        match = re.search(r'/video/(\d+)', url)
        if match:
            return match.group(1)
        return url.split('/')[-1].split('?')[0]

    async def get_video_info(self, page: Page, url: str) -> dict:
        """获取视频信息"""
        self.log("获取视频信息...")

        try:
            # 访问视频页面 - 增加超时时间，使用domcontentloaded而非networkidle
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(5)  # 等待页面完全加载

            # 提取标题
            title_selectors = [
                '[data-e2e="video-desc"]',
                '.video-info-title',
                'h1',
                '[class*="title"]',
            ]
            title = "未知标题"
            for selector in title_selectors:
                try:
                    elem = await page.query_selector(selector)
                    if elem:
                        title = await elem.text_content()
                        if title and title.strip():
                            title = title.strip()[:100]
                            break
                except:
                    continue

            # 提取作者
            author_selectors = [
                '[data-e2e="video-author-nickname"]',
                '.video-info-author',
                '[class*="author"]',
                '[class*="nickname"]',
            ]
            author = "未知作者"
            for selector in author_selectors:
                try:
                    elem = await page.query_selector(selector)
                    if elem:
                        author = await elem.text_content()
                        if author and author.strip():
                            author = author.strip()[:50]
                            break
                except:
                    continue

            # 提取播放量/点赞
            stats = {}
            try:
                # 尝试提取各种统计数据
                stat_selectors = [
                    '[data-e2e="video-play-count"]',
                    '[data-e2e="video-like-count"]',
                    '[class*="play-count"]',
                    '[class*="like-count"]',
                ]
                for selector in stat_selectors:
                    elem = await page.query_selector(selector)
                    if elem:
                        text = await elem.text_content()
                        if text:
                            stats[selector] = text.strip()
            except:
                pass

            return {
                'title': title,
                'author': author,
                'stats': stats,
                'url': page.url,
            }

        except Exception as e:
            self.log(f"获取信息失败: {e}")
            return {'title': '未知', 'author': '未知', 'url': url}

    async def download_video(self, page: Page, video_id: str, folder_path: Path, context: BrowserContext) -> Path:
        """下载视频"""
        self.log("准备下载视频...")

        video_file = folder_path / f"{video_id}.mp4"

        # 尝试多种方式获取视频
        try:
            # 方法1: 通过video标签直接获取src
            video_url = await page.evaluate("""() => {
                const video = document.querySelector('video');
                if (video) {
                    return video.src || video.currentSrc;
                }
                return null;
            }""")

            if video_url:
                self.log(f"找到视频URL: {video_url[:60]}...")
                # 使用浏览器下载
                await self._download_with_browser(page, video_url, video_file)
                return video_file

            # 方法2: 从页面源码中提取
            content = await page.content()
            # 查找视频URL模式
            patterns = [
                r'(https://[^\'"\s]+\.mp4[^\'"\s]*)',
                r'"playAddr":\s*"([^"]+)"',
                r'"downloadAddr":\s*"([^"]+)"',
            ]
            for pattern in patterns:
                matches = re.findall(pattern, content)
                if matches:
                    video_url = unquote(matches[0])
                    self.log(f"从源码提取视频URL: {video_url[:60]}...")
                    await self._download_with_browser(page, video_url, video_file)
                    return video_file

            # 方法3: 监听网络请求
            self.log("尝试拦截网络请求...")
            video_url = await self._intercept_video_request(page)
            if video_url:
                await self._download_with_browser(page, video_url, video_file)
                return video_file

        except Exception as e:
            self.log(f"下载失败: {e}")

        return None

    async def _download_with_browser(self, page: Page, video_url: str, output_file: Path):
        """使用浏览器下载视频"""
        self.log("开始下载...")

        try:
            # 使用CDP命令下载
            import urllib.request
            import ssl

            # 创建SSL上下文
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            # 获取cookie
            cookies = await page.context.cookies()
            cookie_str = '; '.join([f"{c['name']}={c['value']}" for c in cookies])

            # 创建请求
            headers = {
                'User-Agent': await page.evaluate('() => navigator.userAgent'),
                'Referer': page.url,
                'Cookie': cookie_str,
            }

            req = urllib.request.Request(video_url, headers=headers)

            # 下载
            with urllib.request.urlopen(req, context=ssl_context, timeout=60) as response:
                with open(output_file, 'wb') as f:
                    total_size = int(response.headers.get('Content-Length', 0))
                    downloaded = 0
                    chunk_size = 8192

                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)

                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            if downloaded % (chunk_size * 10) == 0:
                                self.log(f"下载进度: {percent:.1f}%")

            self.log(f"下载完成: {output_file.stat().st_size} bytes")

        except Exception as e:
            self.log(f"下载失败: {e}")
            raise

    async def _intercept_video_request(self, page: Page) -> str:
        """监听网络响应，捕获真实 CDN 视频 URL"""
        video_url = None

        # 监听 response 事件，拿到真实 CDN 地址（而非 blob URL）
        def on_response(response):
            nonlocal video_url
            url = response.url
            # 匹配抖音常见 CDN 域名下的 mp4 请求
            is_cdn = any(domain in url for domain in [
                'douyinvod.com', 'douyin.com/video', 'tiktokcdn.com',
                'bytecdn.cn', 'bytedance.com',
            ])
            if is_cdn and '.mp4' in url and not video_url:
                video_url = url
                self.log(f"捕获到 CDN 视频响应: {url[:80]}...")

        page.on("response", on_response)

        # 刷新页面触发真实网络请求
        try:
            await page.reload(wait_until="domcontentloaded", timeout=30000)
        except Exception:
            pass
        await asyncio.sleep(5)

        page.remove_listener("response", on_response)
        return video_url

    async def extract_caption(self, page: Page) -> str:
        """提取视频文案/字幕"""
        self.log("提取视频文案...")

        try:
            # 尝试获取视频描述
            desc_selectors = [
                '[data-e2e="video-desc"]',
                '.video-info-description',
                '[class*="desc"]',
            ]
            caption = ""
            for selector in desc_selectors:
                try:
                    elem = await page.query_selector(selector)
                    if elem:
                        text = await elem.text_content()
                        if text:
                            caption = text.strip()
                            break
                except:
                    continue

            return caption
        except Exception as e:
            self.log(f"提取文案失败: {e}")
            return ""

    async def process_video(self, url: str, index: int) -> dict:
        """处理单个视频"""
        video_id = self.extract_video_id(url)
        folder_name = f"{index:02d}_douyin_{video_id}"
        folder_path = self.output_dir / folder_name
        folder_path.mkdir(parents=True, exist_ok=True)

        self.log(f"=" * 60)
        self.log(f"处理抖音视频: {video_id}")
        self.log(f"文件夹: {folder_name}")
        self.log(f"=" * 60)

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled']
            )

            context = await browser.new_context(
                viewport={'width': 1280, 'height': 800},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )

            # 加载cookie
            cookies = self.load_cookies()
            if cookies:
                await context.add_cookies(cookies)
                self.log("已加载cookie")

            page = await context.new_page()

            try:
                # 获取视频信息
                info = await self.get_video_info(page, url)

                # 保存元数据
                metadata = {
                    'title': info['title'],
                    'uploader': info['author'],
                    'webpage_url': info['url'],
                    'platform': 'douyin',
                    'video_id': video_id,
                    'stats': info.get('stats', {}),
                }

                import json
                (folder_path / 'metadata.json').write_text(
                    json.dumps(metadata, ensure_ascii=False, indent=2),
                    encoding='utf-8'
                )

                # 保存info.md
                md_content = f"# {info['title']}\n\n"
                md_content += f"**平台**: DOUYIN\n\n"
                md_content += f"**作者**: {info['author']}\n\n"
                md_content += f"**链接**: {info['url']}\n\n"
                (folder_path / 'info.md').write_text(md_content, encoding='utf-8')

                # 提取文案
                caption = await self.extract_caption(page)
                if caption:
                    (folder_path / 'transcript.txt').write_text(caption, encoding='utf-8')
                    self.log("文案已保存")

                # 下载视频
                video_file = await self.download_video(page, video_id, folder_path, context)

                # 修正文件名（如果video_id为空）
                if video_file and video_file.exists() and video_file.name == '.mp4':
                    actual_id = page.url.split('/')[-1].split('?')[0][:20] or 'video'
                    new_file = folder_path / f"{actual_id}.mp4"
                    video_file.rename(new_file)
                    video_file = new_file

                if video_file and video_file.exists():
                    self.log(f"[OK] 视频下载完成: {video_file}")
                else:
                    self.log("[WARN] 视频下载失败，但元数据已保存")

                await browser.close()

                return {
                    'folder': folder_path,
                    'metadata': metadata,
                    'video_file': video_file,
                }

            except Exception as e:
                self.log(f"[ERROR] 处理失败: {e}")
                await browser.close()
                return None

    async def run(self, urls: list):
        """批量处理"""
        results = []
        for i, url in enumerate(urls, 1):
            result = await self.process_video(url, i)
            if result:
                results.append(result)
            await asyncio.sleep(3)

        self.log(f"\n全部完成! 成功处理 {len(results)}/{len(urls)} 个视频")
        return results


def main():
    """主函数"""
    print("=" * 60)
    print("抖音视频下载器 - Playwright版")
    print("=" * 60)

    urls_file = Path('video_urls.txt')
    if not urls_file.exists():
        print("\n[错误] 未找到 video_urls.txt")
        return

    with open(urls_file, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    # 过滤出抖音链接（支持短链接和长链接）
    douyin_urls = [u for u in urls if 'douyin.com' in u or 'v.douyin.com' in u]

    if not douyin_urls:
        print("\n没有找到抖音链接")
        return

    print(f"\n共 {len(douyin_urls)} 个抖音视频")

    downloader = DouyinDownloader()
    asyncio.run(downloader.run(douyin_urls))


if __name__ == '__main__':
    main()
