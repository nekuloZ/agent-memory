#!/usr/bin/env python3
"""
汇总分析所有视频内容
生成完整的分析报告
"""

import os
import json
from pathlib import Path
from datetime import datetime

def load_video_data(video_folder):
    """加载单个视频的数据"""
    folder_path = Path(video_folder)
    if not folder_path.exists():
        return None

    # 加载元数据
    metadata_file = folder_path / 'metadata.json'
    info_file = folder_path / 'info.md'

    data = {}

    if metadata_file.exists():
        with open(metadata_file, 'r', encoding='utf-8') as f:
            data['metadata'] = json.load(f)

    # 加载转录文本
    txt_files = list(folder_path.glob('*.txt'))
    if txt_files:
        with open(txt_files[0], 'r', encoding='utf-8') as f:
            data['transcript'] = f.read()
    else:
        data['transcript'] = ''

    return data

def generate_summary():
    """生成汇总报告"""
    analysis_dir = Path('video_analysis')
    if not analysis_dir.exists():
        print("video_analysis/ directory not found!")
        return

    # 获取所有视频文件夹
    video_folders = sorted([d for d in analysis_dir.iterdir() if d.is_dir()])

    print(f"Found {len(video_folders)} video folders")

    # 生成汇总报告
    report_lines = []
    report_lines.append("# 灵剑2011 - 视频内容分析报告")
    report_lines.append(f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report_lines.append(f"分析视频数: {len(video_folders)}")
    report_lines.append("\n" + "=" * 80 + "\n")

    # 视频列表概览
    report_lines.append("## 视频列表概览\n")

    videos_data = []
    for i, folder in enumerate(video_folders, 1):
        data = load_video_data(folder)
        if data and 'metadata' in data:
            meta = data['metadata']
            videos_data.append({
                'index': i,
                'folder': folder.name,
                'title': meta.get('title', 'N/A'),
                'upload_date': meta.get('upload_date', 'N/A'),
                'duration': meta.get('duration', 0),
                'view_count': meta.get('view_count', 0),
                'like_count': meta.get('like_count', 0),
                'transcript': data.get('transcript', '')
            })

            duration_min = meta.get('duration', 0) // 60
            report_lines.append(f"{i}. **{meta.get('title', 'N/A')[:60]}...**")
            report_lines.append(f"   - 发布时间: {meta.get('upload_date', 'N/A')}")
            report_lines.append(f"   - 时长: {duration_min}分钟")
            report_lines.append(f"   - 播放量: {meta.get('view_count', 0):,}")
            report_lines.append(f"   - 点赞: {meta.get('like_count', 0):,}")
            report_lines.append("")

    # 统计信息
    report_lines.append("\n" + "=" * 80)
    report_lines.append("## 统计信息\n")

    total_duration = sum(v['duration'] for v in videos_data)
    total_views = sum(v['view_count'] for v in videos_data)
    total_likes = sum(v['like_count'] for v in videos_data)

    report_lines.append(f"- 总视频数: {len(videos_data)}")
    report_lines.append(f"- 总时长: {total_duration // 60}小时{total_duration % 60}分钟")
    report_lines.append(f"- 总播放量: {total_views:,}")
    report_lines.append(f"- 总点赞: {total_likes:,}")
    report_lines.append(f"- 平均视频时长: {total_duration // len(videos_data) // 60}分钟")

    # 详细内容
    report_lines.append("\n" + "=" * 80)
    report_lines.append("## 详细内容\n")

    for v in videos_data:
        report_lines.append(f"\n### {v['index']}. {v['title']}\n")
        report_lines.append(f"**发布时间**: {v['upload_date']}")
        report_lines.append(f"**播放量**: {v['view_count']:,} | **点赞**: {v['like_count']:,}\n")
        report_lines.append("**转录内容**:\n")
        transcript = v['transcript'].strip()
        if transcript:
            # 限制长度
            if len(transcript) > 2000:
                report_lines.append(transcript[:2000] + "...")
            else:
                report_lines.append(transcript)
        else:
            report_lines.append("(无转录内容)")
        report_lines.append("\n" + "-" * 40 + "\n")

    # 保存报告
    report_text = '\n'.join(report_lines)
    with open('video_analysis_report.md', 'w', encoding='utf-8') as f:
        f.write(report_text)

    print(f"\nReport saved: video_analysis_report.md")
    print(f"Total size: {len(report_text)} characters")

    # 同时生成纯视频列表
    with open('video_titles.txt', 'w', encoding='utf-8') as f:
        for v in videos_data:
            f.write(f"{v['index']}. {v['title']}\n")
            f.write(f"   Date: {v['upload_date']} | Views: {v['view_count']:,}\n\n")

    print(f"Titles saved: video_titles.txt")

if __name__ == '__main__':
    generate_summary()
