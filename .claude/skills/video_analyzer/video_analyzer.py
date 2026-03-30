#!/usr/bin/env python3
"""
视频深度分析工具 - 灵剑2011视频分析
提取：标题、简介、视频、字幕、截图
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path

# 使用 Python 模块方式调用
YT_DLP = [sys.executable, '-m', 'yt_dlp']
WHISPER = [sys.executable, '-m', 'whisper']

def create_video_folder(video_url, index):
    """为每个视频创建独立文件夹并获取元数据"""
    bvid = video_url.split('/')[-1].split('?')[0]
    folder_name = f"video_{index:02d}_{bvid}"
    folder_path = Path("video_analysis") / folder_name
    folder_path.mkdir(parents=True, exist_ok=True)
    return folder_path, bvid

def get_video_metadata(video_url, folder_path):
    """获取视频元数据（标题、简介等）"""
    print(f"  获取元数据...")

    # 使用 yt-dlp 获取元数据
    result = subprocess.run(
        YT_DLP + ['--dump-json', '--skip-download', video_url],
        capture_output=True, text=True, encoding='utf-8', errors='ignore'
    )

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

            # 保存元数据
            meta_info = {
                'title': metadata.get('title', 'N/A'),
                'description': metadata.get('description', 'N/A'),
                'uploader': metadata.get('uploader', 'N/A'),
                'upload_date': metadata.get('upload_date', 'N/A'),
                'duration': metadata.get('duration', 0),
                'view_count': metadata.get('view_count', 0),
                'like_count': metadata.get('like_count', 0),
                'webpage_url': metadata.get('webpage_url', video_url),
                'thumbnail': metadata.get('thumbnail', ''),
            }

            # 保存为 JSON
            with open(folder_path / 'metadata.json', 'w', encoding='utf-8') as f:
                json.dump(meta_info, f, ensure_ascii=False, indent=2)

            # 保存为易读的 Markdown
            with open(folder_path / 'info.md', 'w', encoding='utf-8') as f:
                f.write(f"# {meta_info['title']}\n\n")
                f.write(f"**UP主**: {meta_info['uploader']}\n\n")
                f.write(f"**发布时间**: {meta_info['upload_date']}\n\n")
                f.write(f"**时长**: {meta_info['duration'] // 60}分{meta_info['duration'] % 60}秒\n\n")
                f.write(f"**播放量**: {meta_info['view_count']:,}\n\n")
                f.write(f"**点赞**: {meta_info['like_count']:,}\n\n")
                f.write(f"**链接**: {meta_info['webpage_url']}\n\n")
                f.write(f"## 简介\n\n{meta_info['description']}\n")

            print(f"  [OK] Metadata saved: {meta_info['title'][:40]}...")
            return meta_info

        except Exception as e:
            print(f"  [ERROR] Parse failed: {e}")
            return None
    else:
        print(f"  [ERROR] Get metadata failed")
        return None

def download_video(video_url, folder_path, bvid):
    """下载视频文件"""
    print(f"  下载视频...")

    video_file = folder_path / f"{bvid}.mp4"

    if video_file.exists():
        print(f"  [OK] Video exists, skip")
        return video_file

    result = subprocess.run(
        YT_DLP + [
            '-f', 'best[height<=720]/best',  # 限制720p以节省空间
            '--merge-output-format', 'mp4',
            '-o', str(folder_path / f"{bvid}.%(ext)s"),
            video_url
        ],
        capture_output=True
    )

    if result.returncode == 0:
        print(f"  [OK] Video downloaded")
        return video_file
    else:
        print(f"  [ERROR] Video download failed")
        return None

def extract_subtitles_or_transcribe(video_url, folder_path, bvid):
    """提取字幕或转录音频"""
    print(f"  提取字幕/转录...")

    # 先尝试下载字幕
    result = subprocess.run(
        YT_DLP + [
            '--write-subs', '--write-auto-subs',
            '--sub-langs', 'zh-CN,zh',
            '--skip-download',
            '-o', str(folder_path / 'subtitle'),
            video_url
        ],
        capture_output=True
    )

    # 检查字幕文件
    subtitle_files = list(folder_path.glob('subtitle*.srt')) + list(folder_path.glob('subtitle*.vtt'))

    if subtitle_files:
        print(f"  [OK] Subtitle: {subtitle_files[0].name}")
        # 转换为纯文本
        convert_subtitle_to_text(subtitle_files[0], folder_path / 'transcript.txt')
        return 'subtitle'
    else:
        print(f"  [INFO] No subtitle, transcribe audio...")
        # 下载音频
        audio_file = folder_path / f"{bvid}.mp3"
        subprocess.run(
            YT_DLP + [
                '-x', '--audio-format', 'mp3',
                '--audio-quality', '0',
                '-o', str(folder_path / f"{bvid}.%(ext)s"),
                video_url
            ],
            capture_output=True
        )

        if audio_file.exists():
            # 转录
            print(f"  → Whisper 转录中...")
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
            print(f"  [OK] Transcribe done")
            return 'whisper'

        return None

def convert_subtitle_to_text(subtitle_path, output_path):
    """将字幕文件转换为纯文本"""
    content = subtitle_path.read_text(encoding='utf-8', errors='ignore')

    # 简单清理：去掉时间码和序号
    lines = []
    for line in content.split('\n'):
        line = line.strip()
        # 跳过空行、数字行、时间行
        if not line or line.isdigit() or '-->' in line:
            continue
        lines.append(line)

    output_path.write_text('\n'.join(lines), encoding='utf-8')

def extract_keyframes(video_file, folder_path):
    """从视频中提取关键帧截图"""
    print(f"  提取视频截图...")

    screenshots_dir = folder_path / 'screenshots'
    screenshots_dir.mkdir(exist_ok=True)

    # 获取视频时长
    result = subprocess.run(
        ['ffmpeg', '-i', str(video_file), '-hide_banner'],
        capture_output=True, text=True, errors='ignore'
    )

    # 提取截图：开始、1/3、2/3、结束位置
    timestamps = ['00:00:05', '00:01:00', '00:02:00', '00:05:00']

    for i, ts in enumerate(timestamps, 1):
        output_file = screenshots_dir / f'shot_{i:02d}_{ts.replace(":", "")}.jpg'
        subprocess.run([
            'ffmpeg', '-ss', ts, '-i', str(video_file),
            '-vframes', '1', '-q:v', '2',
            str(output_file)
        ], capture_output=True)

    screenshot_count = len(list(screenshots_dir.glob('*.jpg')))
    print(f"  [OK] Screenshots: {screenshot_count}")
    return screenshot_count

def process_video(video_url, index):
    """处理单个视频的完整流程"""
    print(f"\n{'='*70}")
    print(f"处理第 {index}/18 个视频")
    print(f"{'='*70}")

    # 1. 创建文件夹
    folder_path, bvid = create_video_folder(video_url, index)
    print(f"文件夹: {folder_path.name}")

    # 2. 获取元数据
    metadata = get_video_metadata(video_url, folder_path)
    if not metadata:
        print("跳过此视频")
        return None

    # 3. 下载视频
    video_file = download_video(video_url, folder_path, bvid)

    # 4. 提取字幕/转录
    subtitle_source = extract_subtitles_or_transcribe(video_url, folder_path, bvid)

    # 5. 视频截图
    if video_file and video_file.exists():
        extract_keyframes(video_file, folder_path)

    print(f"[DONE] {metadata['title'][:40]}...")
    return folder_path

def main():
    """主流程"""
    # 读取视频链接
    with open('video_urls.txt', 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]

    print(f"共 {len(urls)} 个视频需要处理")
    print(f"输出目录: video_analysis/")

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
            print(f"[ERROR] Failed: {e}")
            continue

    print(f"\n{'='*70}")
    print(f"All done! Processed {len(processed)} videos")
    print(f"Output: video_analysis/")
    print(f"{'='*70}")

if __name__ == '__main__':
    main()
