#!/usr/bin/env python3
"""
视频深度分析工具 v3 - 统一版
支持：B站(bilibili.com) + 抖音(douyin.com)
提取：标题、简介、视频、字幕/转录、元数据、视频截图
"""

import os
import sys
import json
import subprocess
import time
import re
from pathlib import Path
from urllib.parse import urlparse

# 使用 Python 模块方式调用
YT_DLP = [sys.executable, '-m', 'yt_dlp']
WHISPER = [sys.executable, '-m', 'whisper']

# Cookie 配置
DOUYIN_COOKIE_FILE = Path("douyin_cookies.json")


def detect_platform(url: str) -> str:
    """检测视频平台"""
    domain = urlparse(url).netloc.lower()

    if 'bilibili.com' in domain or 'b23.tv' in domain:
        return 'bilibili'
    elif 'douyin.com' in domain:
        return 'douyin'
    else:
        return 'unknown'


def extract_video_id(url: str, platform: str) -> str:
    """提取视频ID"""
    if platform == 'bilibili':
        # 提取 BV号或 av号
        patterns = [
            r'/video/(BV[\w]+)',
            r'/video/(av\d+)',
            r'BV[\w]+',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        # 从最后一部分提取
        return url.split('/')[-1].split('?')[0][:12]

    elif platform == 'douyin':
        # 提取抖音视频ID
        # 支持格式：
        # https://www.douyin.com/video/1234567890
        # https://v.douyin.com/xxxxx/
        patterns = [
            r'/video/(\d+)',
            r'/share/video/(\d+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        # 短链接提取
        return url.split('/')[-1].split('?')[0][:20]

    return url.split('/')[-1].split('?')[0][:12]


def create_video_folder(video_url: str, index: int, platform: str):
    """为每个视频创建独立文件夹"""
    video_id = extract_video_id(video_url, platform)
    folder_name = f"{index:02d}_{platform}_{video_id}"
    folder_path = Path("video_analysis") / folder_name
    folder_path.mkdir(parents=True, exist_ok=True)
    return folder_path, video_id


def get_douyin_cookies() -> list:
    """加载抖音cookie"""
    if DOUYIN_COOKIE_FILE.exists():
        try:
            data = json.loads(DOUYIN_COOKIE_FILE.read_text(encoding='utf-8'))
            cookies = data.get('cookies', [])
            # 转换为yt-dlp可用的netscape格式
            return cookies
        except Exception as e:
            print(f"  [WARN] 加载抖音cookie失败: {e}")
    return []


def save_cookies_to_netscape(cookies: list, output_file: Path):
    """将Playwright cookie转换为Netscape格式供yt-dlp使用"""
    lines = ["# Netscape HTTP Cookie File", ""]

    for cookie in cookies:
        domain = cookie.get('domain', '')
        flag = "TRUE" if domain.startswith('.') else "FALSE"
        path = cookie.get('path', '/')
        secure = "TRUE" if cookie.get('secure') else "FALSE"
        expires = str(int(cookie.get('expires', 0)))
        name = cookie.get('name', '')
        value = cookie.get('value', '')

        # 处理session cookie (expires = -1)
        if expires == '-1' or expires == '0':
            expires = str(int(time.time()) + 86400 * 30)  # 默认30天

        lines.append(f"{domain}\t{flag}\t{path}\t{secure}\t{expires}\t{name}\t{value}")

    output_file.write_text('\n'.join(lines), encoding='utf-8')


def get_video_metadata(video_url: str, folder_path: Path, platform: str):
    """获取视频元数据"""
    print(f"  获取元数据...")

    cmd = YT_DLP + ['--dump-json', '--skip-download']

    # 平台特定配置
    if platform == 'douyin':
        cookies = get_douyin_cookies()
        if cookies:
            cookie_file = folder_path / '.cookies.txt'
            save_cookies_to_netscape(cookies, cookie_file)
            cmd.extend(['--cookies', str(cookie_file)])
    elif platform == 'bilibili':
        # 尝试使用Firefox cookie
        cmd.extend(['--cookies-from-browser', 'firefox'])

    cmd.append(video_url)

    result = subprocess.run(
        cmd,
        capture_output=True, text=True, encoding='utf-8', errors='ignore'
    )

    # 清理临时cookie文件
    temp_cookie = folder_path / '.cookies.txt'
    if temp_cookie.exists():
        temp_cookie.unlink()

    if result.returncode == 0 and result.stdout:
        try:
            # 解析最后一行 JSON
            lines = result.stdout.strip().split('\n')
            for line in reversed(lines):
                if line.strip():
                    try:
                        metadata = json.loads(line)
                        break
                    except:
                        continue

            # 平台特定的元数据提取
            meta_info = {
                'title': metadata.get('title', 'N/A'),
                'description': metadata.get('description', 'N/A'),
                'uploader': metadata.get('uploader', metadata.get('channel', 'N/A')),
                'upload_date': metadata.get('upload_date', 'N/A'),
                'duration': metadata.get('duration', 0),
                'view_count': metadata.get('view_count', 0),
                'like_count': metadata.get('like_count', 0),
                'webpage_url': metadata.get('webpage_url', video_url),
                'thumbnail': metadata.get('thumbnail', ''),
                'platform': platform,
                'video_id': extract_video_id(video_url, platform),
            }

            # 保存为 JSON
            with open(folder_path / 'metadata.json', 'w', encoding='utf-8') as f:
                json.dump(meta_info, f, ensure_ascii=False, indent=2)

            # 保存为易读的 Markdown
            with open(folder_path / 'info.md', 'w', encoding='utf-8') as f:
                f.write(f"# {meta_info['title']}\n\n")
                f.write(f"**平台**: {platform.upper()}\n\n")
                f.write(f"**UP主/作者**: {meta_info['uploader']}\n\n")
                f.write(f"**发布时间**: {meta_info['upload_date']}\n\n")
                f.write(f"**时长**: {meta_info['duration'] // 60}分{meta_info['duration'] % 60}秒\n\n")
                f.write(f"**播放量**: {meta_info['view_count']:,}\n\n")
                f.write(f"**点赞**: {meta_info['like_count']:,}\n\n")
                f.write(f"**链接**: {meta_info['webpage_url']}\n\n")
                f.write(f"## 简介\n\n{meta_info['description']}\n")

            print(f"  [OK] 元数据: {meta_info['title'][:40]}...")
            return meta_info

        except Exception as e:
            print(f"  [ERROR] 解析失败: {e}")
            return None
    else:
        print(f"  [ERROR] 获取元数据失败")
        if result.stderr:
            print(f"  错误: {result.stderr[:200]}")
        return None


def download_video(video_url: str, folder_path: Path, video_id: str, platform: str):
    """下载视频文件"""
    print(f"  下载视频...")

    video_file = folder_path / f"{video_id}.mp4"

    if video_file.exists():
        print(f"  [OK] 视频已存在，跳过")
        return video_file

    cmd = YT_DLP + [
        '-f', 'best[height<=720]/best',  # 限制720p以节省空间
        '--merge-output-format', 'mp4',
        '--no-playlist',
        '-o', str(folder_path / f"{video_id}.%(ext)s"),
    ]

    # 平台特定配置
    if platform == 'douyin':
        cookies = get_douyin_cookies()
        if cookies:
            cookie_file = folder_path / '.cookies.txt'
            save_cookies_to_netscape(cookies, cookie_file)
            cmd.extend(['--cookies', str(cookie_file)])
            print(f"  [INFO] 使用抖音cookie下载")
        else:
            print(f"  [WARN] 未找到抖音cookie，可能下载失败")
    elif platform == 'bilibili':
        cmd.extend(['--cookies-from-browser', 'firefox'])
        print(f"  [INFO] 使用Firefox cookie下载")

    cmd.append(video_url)

    result = subprocess.run(cmd, capture_output=True)

    # 清理临时cookie文件
    temp_cookie = folder_path / '.cookies.txt'
    if temp_cookie.exists():
        temp_cookie.unlink()

    if result.returncode == 0:
        print(f"  [OK] 视频下载完成")
        return video_file
    else:
        print(f"  [ERROR] 视频下载失败")
        if result.stderr:
            print(f"  详情: {result.stderr[:200]}")
        return None


def extract_subtitles_or_transcribe(video_url: str, folder_path: Path, video_id: str, platform: str):
    """提取字幕或转录音频"""
    print(f"  提取字幕/转录...")

    cmd = YT_DLP + [
        '--write-subs', '--write-auto-subs',
        '--sub-langs', 'zh-CN,zh,zh-Hans,zh-TW',
        '--skip-download',
        '-o', str(folder_path / 'subtitle'),
    ]

    # 平台特定配置
    if platform == 'douyin':
        cookies = get_douyin_cookies()
        if cookies:
            cookie_file = folder_path / '.cookies.txt'
            save_cookies_to_netscape(cookies, cookie_file)
            cmd.extend(['--cookies', str(cookie_file)])
    elif platform == 'bilibili':
        cmd.extend(['--cookies-from-browser', 'firefox'])

    cmd.append(video_url)

    result = subprocess.run(cmd, capture_output=True)

    # 清理临时cookie文件
    temp_cookie = folder_path / '.cookies.txt'
    if temp_cookie.exists():
        temp_cookie.unlink()

    # 检查字幕文件
    subtitle_files = list(folder_path.glob('subtitle*.srt')) + list(folder_path.glob('subtitle*.vtt'))

    if subtitle_files:
        print(f"  [OK] 字幕: {subtitle_files[0].name}")
        convert_subtitle_to_text(subtitle_files[0], folder_path / 'transcript.txt')
        return 'subtitle'
    else:
        print(f"  [INFO] 无字幕，转录音频...")

        # 下载音频
        cmd_audio = YT_DLP + [
            '-x', '--audio-format', 'mp3',
            '--audio-quality', '0',
            '-o', str(folder_path / f"{video_id}.%(ext)s"),
        ]

        # 平台特定配置
        if platform == 'douyin':
            cookies = get_douyin_cookies()
            if cookies:
                cookie_file = folder_path / '.cookies.txt'
                save_cookies_to_netscape(cookies, cookie_file)
                cmd_audio.extend(['--cookies', str(cookie_file)])
        elif platform == 'bilibili':
            cmd_audio.extend(['--cookies-from-browser', 'firefox'])

        cmd_audio.append(video_url)

        subprocess.run(cmd_audio, capture_output=True)

        # 清理临时cookie文件
        temp_cookie = folder_path / '.cookies.txt'
        if temp_cookie.exists():
            temp_cookie.unlink()

        audio_file = folder_path / f"{video_id}.mp3"
        if audio_file.exists():
            print(f"  [INFO] Whisper转录中...")
            subprocess.run(
                WHISPER + [
                    str(audio_file),
                    '--model', 'medium',
                    '--language', 'Chinese',
                    '--output_dir', str(folder_path),
                    '--output_format', 'txt'
                ],
                capture_output=True
            )

            # 删除音频节省空间
            audio_file.unlink()

            # 重命名输出文件
            whisper_txt = folder_path / f"{video_id}.txt"
            if whisper_txt.exists():
                whisper_txt.rename(folder_path / 'transcript.txt')

            print(f"  [OK] 转录完成")
            return 'whisper'

        return None


def convert_subtitle_to_text(subtitle_path: Path, output_path: Path):
    """将字幕文件转换为纯文本"""
    content = subtitle_path.read_text(encoding='utf-8', errors='ignore')

    lines = []
    for line in content.split('\n'):
        line = line.strip()
        # 跳过空行、数字行、时间行
        if not line or line.isdigit() or '-->' in line:
            continue
        lines.append(line)

    output_path.write_text('\n'.join(lines), encoding='utf-8')


def extract_keyframes(video_file: Path, folder_path: Path):
    """从视频中提取关键帧截图"""
    print(f"  提取视频截图...")

    if not video_file or not video_file.exists():
        print(f"  [SKIP] 无视频文件")
        return 0

    screenshots_dir = folder_path / 'screenshots'
    screenshots_dir.mkdir(exist_ok=True)

    # 获取视频时长
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
         '-of', 'default=noprint_wrappers=1:nokey=1', str(video_file)],
        capture_output=True, text=True
    )

    try:
        duration = float(result.stdout.strip())
    except:
        duration = 60  # 默认1分钟

    # 根据视频长度决定截图位置
    if duration < 60:
        timestamps = [duration * 0.3, duration * 0.7]
    elif duration < 300:
        timestamps = [duration * 0.1, duration * 0.5, duration * 0.9]
    else:
        timestamps = [duration * p for p in [0.05, 0.25, 0.5, 0.75, 0.95]]

    for i, ts in enumerate(timestamps, 1):
        ts_str = f"{int(ts // 3600):02d}:{int((ts % 3600) // 60):02d}:{int(ts % 60):02d}"
        output_file = screenshots_dir / f'shot_{i:02d}_{int(ts)}s.jpg'
        subprocess.run([
            'ffmpeg', '-ss', ts_str, '-i', str(video_file),
            '-vframes', '1', '-q:v', '2',
            str(output_file)
        ], capture_output=True)

    screenshot_count = len(list(screenshots_dir.glob('*.jpg')))
    print(f"  [OK] 截图: {screenshot_count}张")
    return screenshot_count


def process_douyin_video(video_url: str, index: int) -> dict:
    """使用Playwright下载器处理抖音视频"""
    print(f"  [INFO] 使用Playwright下载器处理抖音视频...")

    # 创建临时链接文件
    temp_url_file = Path(f".douyin_temp_{index}.txt")
    temp_url_file.write_text(video_url, encoding='utf-8')

    try:
        # 调用douyin_downloader
        result = subprocess.run(
            [sys.executable, 'douyin_downloader.py'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )

        # 解析输出找到下载的文件夹
        output_lines = result.stdout.split('\n')
        folder_path = None

        for line in output_lines:
            if '文件夹:' in line:
                folder_name = line.split('文件夹:')[1].strip()
                folder_path = Path("video_analysis") / folder_name
                break

        if folder_path and folder_path.exists():
            # 读取元数据
            metadata_file = folder_path / 'metadata.json'
            if metadata_file.exists():
                metadata = json.loads(metadata_file.read_text(encoding='utf-8'))
                return {
                    'folder': folder_path,
                    'platform': 'douyin',
                    'metadata': metadata,
                    'subtitle_source': 'caption',  # 抖音直接提取文案
                }

        print(f"  [WARN] 抖音下载可能失败，请检查输出")
        return None

    finally:
        # 清理临时文件
        if temp_url_file.exists():
            temp_url_file.unlink()


def process_video(video_url: str, index: int):
    """处理单个视频的完整流程"""
    platform = detect_platform(video_url)

    print(f"\n{'='*70}")
    print(f"处理第 {index} 个视频 | 平台: {platform.upper()}")
    print(f"{'='*70}")

    if platform == 'unknown':
        print(f"[WARN] 无法识别平台: {video_url}")
        print(f"支持的链接格式:")
        print(f"  - B站: https://www.bilibili.com/video/BVxxxx")
        print(f"  - 抖音: https://www.douyin.com/video/1234567890")
        return None

    # 抖音使用专门的下载器
    if platform == 'douyin':
        return process_douyin_video(video_url, index)

    # 1. 创建文件夹
    folder_path, video_id = create_video_folder(video_url, index, platform)
    print(f"文件夹: {folder_path.name}")

    # 2. 获取元数据
    metadata = get_video_metadata(video_url, folder_path, platform)
    if not metadata:
        print("跳过此视频")
        return None

    # 3. 下载视频
    video_file = download_video(video_url, folder_path, video_id, platform)

    # 4. 提取字幕/转录
    subtitle_source = extract_subtitles_or_transcribe(video_url, folder_path, video_id, platform)

    # 5. 视频截图
    if video_file and video_file.exists():
        extract_keyframes(video_file, folder_path)

    print(f"[DONE] {metadata['title'][:40]}...")

    return {
        'folder': folder_path,
        'platform': platform,
        'metadata': metadata,
        'subtitle_source': subtitle_source,
    }


def generate_summary(results: list):
    """生成汇总报告"""
    if not results:
        print("\n没有成功处理的视频")
        return

    report_path = Path("video_analysis") / 'video_analysis_report.md'

    lines = ["# 视频分析报告\n"]
    lines.append(f"**生成时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    lines.append(f"**视频总数**: {len(results)}\n\n")

    # 按平台分组
    bilibili_videos = [r for r in results if r['platform'] == 'bilibili']
    douyin_videos = [r for r in results if r['platform'] == 'douyin']

    lines.append("## 统计\n")
    lines.append(f"- B站视频: {len(bilibili_videos)}\n")
    lines.append(f"- 抖音视频: {len(douyin_videos)}\n\n")

    lines.append("---\n\n")

    # B站视频
    if bilibili_videos:
        lines.append("## B站视频\n")
        for i, result in enumerate(bilibili_videos, 1):
            meta = result['metadata']
            lines.append(f"### {i}. {meta['title']}\n")
            lines.append(f"- **UP主**: {meta['uploader']}\n")
            lines.append(f"- **时长**: {meta['duration'] // 60}分{meta['duration'] % 60}秒\n")
            lines.append(f"- **播放**: {meta['view_count']:,} | **点赞**: {meta['like_count']:,}\n")
            lines.append(f"- **链接**: {meta['webpage_url']}\n")
            lines.append(f"- **字幕来源**: {result.get('subtitle_source', 'N/A')}\n")
            lines.append(f"- **文件夹**: `{result['folder'].name}/`\n\n")

    # 抖音视频
    if douyin_videos:
        lines.append("## 抖音视频\n")
        for i, result in enumerate(douyin_videos, 1):
            meta = result['metadata']
            lines.append(f"### {i}. {meta['title']}\n")
            lines.append(f"- **作者**: {meta['uploader']}\n")
            lines.append(f"- **时长**: {meta['duration'] // 60}分{meta['duration'] % 60}秒\n")
            lines.append(f"- **点赞**: {meta['like_count']:,}\n")
            lines.append(f"- **链接**: {meta['webpage_url']}\n")
            lines.append(f"- **字幕来源**: {result.get('subtitle_source', 'N/A')}\n")
            lines.append(f"- **文件夹**: `{result['folder'].name}/`\n\n")

    report_path.write_text('\n'.join(lines), encoding='utf-8')
    print(f"\n[OK] 汇总报告已保存: {report_path}")


def main():
    """主流程"""
    print("="*70)
    print("视频分析工具 v3 - 统一版")
    print("支持: B站 + 抖音")
    print("="*70)

    # 检查依赖
    urls_file = Path('video_urls.txt')
    if not urls_file.exists():
        print("\n[错误] 未找到 video_urls.txt 文件")
        print("请创建该文件并写入视频链接，每行一个")
        print("\n支持的链接格式:")
        print("  B站: https://www.bilibili.com/video/BV1xx411c7mD")
        print("  抖音: https://www.douyin.com/video/1234567890123456789")
        return

    # 读取视频链接
    with open(urls_file, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    print(f"\n共 {len(urls)} 个视频")
    print(f"输出目录: video_analysis/\n")

    # 检查抖音cookie
    if DOUYIN_COOKIE_FILE.exists():
        print(f"[OK] 已加载抖音cookie")
    else:
        print(f"[WARN] 未找到抖音cookie ({DOUYIN_COOKIE_FILE})")
        print(f"提示: 如需下载抖音视频，请先运行扫码登录获取cookie")
        print(f"  python cookie_refresher/douyin_qrcode_login.py")

    # 检查B站cookie (Firefox)
    print(f"[INFO] B站将使用Firefox浏览器cookie")

    # 创建主目录
    Path("video_analysis").mkdir(exist_ok=True)

    # 处理每个视频
    processed = []
    for i, url in enumerate(urls, 1):
        try:
            result = process_video(url, i)
            if result:
                processed.append(result)
            time.sleep(2)  # 避免请求过快
        except Exception as e:
            print(f"[ERROR] 处理失败: {e}")
            continue

    # 生成汇总报告
    generate_summary(processed)

    print(f"\n{'='*70}")
    print(f"全部完成! 成功处理 {len(processed)}/{len(urls)} 个视频")
    print(f"输出: video_analysis/")
    print(f"{'='*70}")


if __name__ == '__main__':
    main()
