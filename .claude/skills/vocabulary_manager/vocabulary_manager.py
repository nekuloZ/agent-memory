"""
vocabulary_manager - Jarvis 语言学习词汇管理器

支持单词、短语、句子的记录与查询
数据存储：jarvis-memory/L3_Semantic/language/vocabulary/
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)

# 项目根目录（Jarvis 根目录）
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
VOCABULARY_BASE = PROJECT_ROOT / "jarvis-memory" / "L3_Semantic" / "language" / "vocabulary"


class VocabularyManager:
    """词汇管理器 - 核心类"""

    SUPPORTED_LANGUAGES = {
        'en': '英语',
        'ja': '日语',
        'zh': '中文'
    }

    def __init__(self, language: str = 'en'):
        """
        初始化管理器

        Args:
            language: 语言代码，默认 'en' (英语)
        """
        if language not in self.SUPPORTED_LANGUAGES:
            raise ValueError(f"不支持的语言: {language}。支持: {list(self.SUPPORTED_LANGUAGES.keys())}")

        self.language = language
        self.language_name = self.SUPPORTED_LANGUAGES[language]

        # 目录结构
        self.vocabulary_dir = VOCABULARY_BASE / language
        self.words_dir = self.vocabulary_dir / "words"
        self.phrases_dir = self.vocabulary_dir / "phrases"
        self.sentences_dir = self.vocabulary_dir / "sentences"

        # 确保目录存在
        self._init_directories()

    def _init_directories(self):
        """初始化所有必要的目录"""
        for directory in [self.words_dir, self.phrases_dir, self.sentences_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    # ==================== 词汇记录功能 ====================

    def add_word(self, word: str, definition: str = "", phonetic: str = "",
                 part_of_speech: str = "", example: str = "",
                 tags: List[str] = None, notes: str = "",
                 synonyms: List[str] = None, antonyms: List[str] = None,
                 collocations: List[str] = None, syllables: str = "",
                 source: str = "", source_type: str = "", context: str = "") -> Optional[str]:
        """
        添加生词记录

        Returns:
            str: 保存的文件路径，如果已存在且来源相同则返回 None
        """
        word = word.lower().strip()
        filepath = self.words_dir / f"{word}.json"

        # 去重检查并处理多来源
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)

            existing_source = existing_data.get('source', '')
            if source and source != existing_source:
                # 新来源不同，更新来源信息
                if 'sources' not in existing_data:
                    existing_data['sources'] = []
                    if existing_source:
                        existing_data['sources'].append({
                            'source': existing_source,
                            'source_type': existing_data.get('source_type', ''),
                            'context': existing_data.get('context', ''),
                            'added_at': existing_data.get('created_at', '')
                        })

                existing_data['sources'].append({
                    'source': source,
                    'source_type': source_type,
                    'context': context,
                    'added_at': datetime.now().isoformat()
                })

                existing_data['source'] = source
                existing_data['source_type'] = source_type

                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(existing_data, f, ensure_ascii=False, indent=2)

                return str(filepath)
            else:
                return None  # 已存在且来源相同

        timestamp = datetime.now().isoformat()

        entry = {
            "word": word,
            "phonetic": phonetic,
            "syllables": syllables,
            "part_of_speech": part_of_speech,
            "definition": definition,
            "example": example,
            "tags": tags or [],
            "notes": notes,
            "synonyms": synonyms or [],
            "antonyms": antonyms or [],
            "collocations": collocations or [],
            "source": source,
            "source_type": source_type,
            "context": context,
            "created_at": timestamp,
            "language": self.language
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(entry, f, ensure_ascii=False, indent=2)

        return str(filepath)

    def add_phrase(self, phrase: str, meaning: str = "", usage: str = "",
                   examples: List[str] = None, tags: List[str] = None,
                   notes: str = "", register: str = "",
                   source: str = "", source_type: str = "", context: str = "") -> Optional[str]:
        """添加短语记录"""
        # 简单去重
        for existing_file in self.phrases_dir.glob("*.json"):
            try:
                with open(existing_file, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
                    if existing.get('phrase') == phrase:
                        existing_source = existing.get('source', '')
                        if source and source != existing_source:
                            if 'sources' not in existing:
                                existing['sources'] = []
                                if existing_source:
                                    existing['sources'].append({
                                        'source': existing_source,
                                        'source_type': existing.get('source_type', ''),
                                        'added_at': existing.get('created_at', '')
                                    })

                            existing['sources'].append({
                                'source': source,
                                'source_type': source_type,
                                'added_at': datetime.now().isoformat()
                            })

                            existing['source'] = source
                            existing['source_type'] = source_type

                            with open(existing_file, 'w', encoding='utf-8') as f:
                                json.dump(existing, f, ensure_ascii=False, indent=2)

                            return str(existing_file)
                        else:
                            return None
            except:
                continue

        timestamp = datetime.now().isoformat()

        entry = {
            "phrase": phrase,
            "meaning": meaning,
            "usage": usage,
            "examples": examples or [],
            "tags": tags or [],
            "notes": notes,
            "register": register,
            "source": source,
            "source_type": source_type,
            "context": context,
            "created_at": timestamp,
            "language": self.language
        }

        filename = f"{phrase[:20]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.phrases_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(entry, f, ensure_ascii=False, indent=2)

        return str(filepath)

    def add_sentence(self, sentence: str, translation: str = "",
                     analysis: str = "", key_words: List[str] = None,
                     grammar_points: List[str] = None, tags: List[str] = None,
                     notes: str = "",
                     source: str = "", source_type: str = "",
                     context: str = "", sentences_group: List[Dict] = None) -> Optional[str]:
        """添加句子记录"""
        # 去重检查
        for existing_file in self.sentences_dir.glob("*.json"):
            try:
                with open(existing_file, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
                    if existing.get('sentence') == sentence:
                        existing_source = existing.get('source', '')
                        if source and source != existing_source:
                            if 'sources' not in existing:
                                existing['sources'] = []
                                if existing_source:
                                    existing['sources'].append({
                                        'source': existing_source,
                                        'source_type': existing.get('source_type', ''),
                                        'context': existing.get('context', ''),
                                        'added_at': existing.get('created_at', '')
                                    })

                            existing['sources'].append({
                                'source': source,
                                'source_type': source_type,
                                'context': context,
                                'added_at': datetime.now().isoformat()
                            })

                            existing['source'] = source
                            existing['source_type'] = source_type
                            existing['context'] = context

                            # 更新 sentences_group（如果有）
                            if sentences_group:
                                existing['sentences_group'] = sentences_group

                            with open(existing_file, 'w', encoding='utf-8') as f:
                                json.dump(existing, f, ensure_ascii=False, indent=2)

                            return str(existing_file)
                        else:
                            return None
            except:
                continue

        timestamp = datetime.now().isoformat()

        entry = {
            "sentence": sentence,
            "translation": translation,
            "analysis": analysis,
            "key_words": key_words or [],
            "grammar_points": grammar_points or [],
            "tags": tags or [],
            "notes": notes,
            "source": source,
            "source_type": source_type,
            "context": context,
            "created_at": timestamp,
            "language": self.language
        }

        if sentences_group:
            entry["sentences_group"] = sentences_group

        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.sentences_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(entry, f, ensure_ascii=False, indent=2)

        return str(filepath)

    # ==================== 查询功能 ====================

    def get_word(self, word: str) -> Optional[Dict]:
        """获取单词详情"""
        filepath = self.words_dir / f"{word.lower().strip()}.json"
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def list_words(self, tag: str = None) -> List[Dict]:
        """列出所有单词"""
        words = []
        for filepath in self.words_dir.glob("*.json"):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if tag is None or tag in data.get('tags', []):
                    words.append(data)
        return words

    def list_phrases(self, tag: str = None) -> List[Dict]:
        """列出所有短语"""
        phrases = []
        for filepath in self.phrases_dir.glob("*.json"):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if tag is None or tag in data.get('tags', []):
                    phrases.append(data)
        return phrases

    def list_sentences(self, tag: str = None) -> List[Dict]:
        """列出所有句子"""
        sentences = []
        for filepath in self.sentences_dir.glob("*.json"):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if tag is None or tag in data.get('tags', []):
                    sentences.append(data)
        return sentences

    def get_statistics(self) -> Dict:
        """获取学习统计信息"""
        return {
            "language": self.language,
            "language_name": self.language_name,
            "word_count": len(list(self.words_dir.glob("*.json"))),
            "phrase_count": len(list(self.phrases_dir.glob("*.json"))),
            "sentence_count": len(list(self.sentences_dir.glob("*.json"))),
            "generated_at": datetime.now().isoformat()
        }


# ==================== 全局实例 ====================

_managers = {}


def get_manager(language: str = 'en') -> VocabularyManager:
    """获取指定语言的管理器实例（单例模式）"""
    if language not in _managers:
        _managers[language] = VocabularyManager(language)
    return _managers[language]


# 英语管理器快捷方式
english_manager = get_manager('en')


if __name__ == '__main__':
    # 测试代码
    manager = get_manager('en')

    # 测试添加单词
    result = manager.add_word(
        word="test",
        definition="a procedure intended to establish the quality, performance, or reliability of something",
        phonetic="/test/",
        part_of_speech="noun",
        example="This is a test.",
        tags=["test"],
        source="Test Source"
    )
    print(f"Added word: {result}")

    # 测试查询
    word_info = manager.get_word("test")
    print(f"Word info: {word_info}")

    # 测试统计
    stats = manager.get_statistics()
    print(f"Statistics: {stats}")
