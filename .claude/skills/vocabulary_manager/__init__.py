"""
vocabulary_manager - Jarvis 语言学习词汇管理器

使用示例:
    from vocabulary_manager import get_manager, english_manager

    # 获取管理器
    manager = get_manager('en')

    # 添加单词
    manager.add_word(
        word="ephemeral",
        definition="lasting for a very short time",
        source="《Appointment with Death》"
    )

    # 查询单词
    word_info = manager.get_word("ephemeral")

    # 列出所有单词
    words = manager.list_words()
"""

from .vocabulary_manager import (
    VocabularyManager,
    get_manager,
    english_manager
)

__all__ = ['VocabularyManager', 'get_manager', 'english_manager']
