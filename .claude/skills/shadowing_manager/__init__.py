"""
shadowing_manager - Jarvis 影子跟读管理器

支持传统文本跟读和 Shadowing Studio Web 界面

使用示例:
    from shadowing_manager import get_manager

    # 获取管理器
    manager = get_manager()

    # ===== 传统文本跟读 =====
    manager.add_text(
        title="The Road Not Taken",
        content="Two roads diverged in a yellow wood...",
        source="Robert Frost",
        difficulty="medium"
    )

    # 生成填空练习
    exercise = manager.generate_fill_in_blank("The Road Not Taken", ratio=0.2)

    # ===== Shadowing Studio Web 界面支持 =====
    # 创建带时间轴的字幕 JSON
    manager.create_subtitle_json(
        title="The One with the Embryos",
        content_type="tv",
        subtitles=[
            {"start": 0, "end": 3.2, "text": "Alright, let's play one more game.",
             "translation": "好吧，我们再玩一局。", "emotions": ["excited"]},
            {"start": 3.2, "end": 6.5, "text": "Yeah, but this time, let's play for real.",
             "translation": "对，但这次我们认真玩。", "emotions": ["determined"]}
        ],
        duration="22:15",
        difficulty="B1",
        source="Friends S04E12"
    )

    # 扫描并处理临时目录中的文件
    result = manager.scan_and_process_files()

    # 验证字幕 JSON 格式
    validation = manager.validate_subtitle_json("path/to/file.json")

    # 列出所有字幕内容
    contents = manager.list_subtitle_contents()
"""

from .shadowing_manager import ShadowingManager, get_manager

__all__ = ['ShadowingManager', 'get_manager']
