"""
shadowing_manager - Jarvis 影子跟读管理器

支持文本保存、分类管理、填空练习生成
数据存储：jarvis-memory/L3_Semantic/language/shadowing/
"""

import json
import re
import random
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
SHADOWING_BASE = PROJECT_ROOT / "jarvis-memory" / "L3_Semantic" / "language" / "shadowing"
EXERCISES_BASE = PROJECT_ROOT / "jarvis-memory" / "L3_Semantic" / "language" / "exercises"


class ShadowingManager:
    """影子跟读管理器"""

    DIFFICULTY_LEVELS = ['easy', 'medium', 'hard']
    CEFR_LEVELS = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']

    def __init__(self, language: str = 'en'):
        """
        初始化管理器

        Args:
            language: 语言代码，默认 'en'
        """
        self.language = language
        self.shadowing_dir = SHADOWING_BASE
        self.exercises_dir = EXERCISES_BASE

        # 确保目录存在
        self._init_directories()

    def _init_directories(self):
        """初始化目录"""
        self.shadowing_dir.mkdir(parents=True, exist_ok=True)
        self.exercises_dir.mkdir(parents=True, exist_ok=True)

    def add_text(self, title: str, content: str,
                 source: str = "", difficulty: str = "medium",
                 tags: List[str] = None, cefr_level: str = "") -> str:
        """
        添加影子跟读文本

        Args:
            title: 文本标题
            content: 文本内容
            source: 来源
            difficulty: 难度 (easy/medium/hard)
            tags: 标签列表
            cefr_level: CEFR 等级

        Returns:
            str: 保存的文件路径
        """
        if difficulty not in self.DIFFICULTY_LEVELS:
            difficulty = "medium"

        timestamp = datetime.now().isoformat()

        entry = {
            "title": title,
            "content": content,
            "source": source,
            "difficulty": difficulty,
            "cefr_level": cefr_level,
            "tags": tags or [],
            "word_count": len(content.split()),
            "created_at": timestamp,
            "language": self.language
        }

        filename = f"{title[:30]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.shadowing_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(entry, f, ensure_ascii=False, indent=2)

        return str(filepath)

    def get_text(self, title: str) -> Optional[Dict]:
        """根据标题获取文本"""
        for filepath in self.shadowing_dir.glob("*.json"):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data.get('title') == title:
                    return data
        return None

    def list_texts(self, difficulty: str = None, tags: List[str] = None) -> List[Dict]:
        """
        列出所有文本

        Args:
            difficulty: 按难度过滤
            tags: 按标签过滤

        Returns:
            文本列表
        """
        texts = []
        for filepath in self.shadowing_dir.glob("*.json"):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

                # 难度过滤
                if difficulty and data.get('difficulty') != difficulty:
                    continue

                # 标签过滤
                if tags:
                    text_tags = set(data.get('tags', []))
                    if not any(tag in text_tags for tag in tags):
                        continue

                texts.append(data)

        return texts

    def search_texts(self, keyword: str) -> List[Dict]:
        """搜索文本"""
        results = []
        keyword_lower = keyword.lower()

        for filepath in self.shadowing_dir.glob("*.json"):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if (keyword_lower in data.get('title', '').lower() or
                    keyword_lower in data.get('content', '').lower() or
                    keyword_lower in data.get('source', '').lower()):
                    results.append(data)

        return results

    # ==================== 填空练习功能 ====================

    def generate_fill_in_blank(self, text_or_title: str, ratio: float = 0.2,
                                strategy: str = "random") -> Optional[Dict]:
        """
        生成填空练习

        Args:
            text_or_title: 文本内容或标题
            ratio: 挖空比例 (0.1-0.5)
            strategy: 挖空策略 (random/keywords/logic)

        Returns:
            练习数据字典
        """
        # 如果是标题，查找文本
        text_data = self.get_text(text_or_title)
        if text_data:
            text = text_data['content']
            source_title = text_data['title']
        else:
            text = text_or_title
            source_title = "自定义文本"

        words = text.split()
        total_words = len(words)
        num_blanks = max(1, int(total_words * ratio))

        # 根据策略选择挖空位置
        if strategy == "random":
            blank_positions = random.sample(range(total_words), min(num_blanks, total_words))
        elif strategy == "keywords":
            # 优先挖空名词、动词（简化版：挖空较长的词）
            candidates = [(i, w) for i, w in enumerate(words) if len(w) > 4]
            candidates.sort(key=lambda x: len(x[1]), reverse=True)
            blank_positions = [c[0] for c in candidates[:num_blanks]]
        else:
            blank_positions = random.sample(range(total_words), min(num_blanks, total_words))

        blank_positions.sort()

        # 生成练习
        blanks = []
        modified_words = words.copy()

        for i, pos in enumerate(blank_positions):
            answer = words[pos]
            # 清理标点
            clean_answer = re.sub(r'[^\w]', '', answer)
            if clean_answer:
                blanks.append({
                    "position": pos,
                    "answer": clean_answer,
                    "hint": f"第 {pos + 1} 个词",
                    "type": self._guess_word_type(clean_answer)
                })
                modified_words[pos] = "______"

        exercise_text = " ".join(modified_words)

        exercise = {
            "title": f"{source_title} - 填空练习",
            "original_text": text,
            "exercise_text": exercise_text,
            "blanks": blanks,
            "hints": {
                "total_words": total_words,
                "blank_count": len(blanks),
                "difficulty": self._calculate_difficulty(len(blanks), total_words)
            },
            "created_at": datetime.now().isoformat(),
            "source_text": source_title
        }

        # 保存练习
        filename = f"fill_blank_{source_title[:20]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.exercises_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(exercise, f, ensure_ascii=False, indent=2)

        exercise['filepath'] = str(filepath)
        return exercise

    def create_custom_blank(self, title: str, text: str, blanks: List[Dict]) -> str:
        """
        创建自定义填空练习

        Args:
            title: 练习标题
            text: 原始文本
            blanks: 挖空位置列表

        Returns:
            保存的文件路径
        """
        words = text.split()
        modified_words = words.copy()

        for blank in blanks:
            pos = blank['position']
            if 0 <= pos < len(words):
                modified_words[pos] = "______"

        exercise = {
            "title": title,
            "original_text": text,
            "exercise_text": " ".join(modified_words),
            "blanks": blanks,
            "hints": {
                "total_words": len(words),
                "blank_count": len(blanks)
            },
            "created_at": datetime.now().isoformat()
        }

        filename = f"custom_{title[:20]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.exercises_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(exercise, f, ensure_ascii=False, indent=2)

        return str(filepath)

    def list_exercises(self) -> List[Dict]:
        """列出所有练习"""
        exercises = []
        for filepath in self.exercises_dir.glob("*.json"):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                data['filepath'] = str(filepath)
                exercises.append(data)
        return exercises

    # ==================== 辅助方法 ====================

    def _guess_word_type(self, word: str) -> str:
        """猜测词性（简化版）"""
        # 简单的后缀规则
        if word.endswith(('tion', 'sion', 'ness', 'ment', 'ity')):
            return "noun"
        elif word.endswith(('ly', 'wise')):
            return "adverb"
        elif word.endswith(('ful', 'ous', 'ive', 'able', 'ible')):
            return "adjective"
        elif word.endswith(('ing', 'ed')):
            return "verb"
        return "unknown"

    def _calculate_difficulty(self, blank_count: int, total_words: int) -> str:
        """计算难度"""
        ratio = blank_count / total_words if total_words > 0 else 0
        if ratio < 0.15:
            return "easy"
        elif ratio < 0.25:
            return "medium"
        return "hard"

    # ==================== Shadowing Studio Web 界面支持（新增）====================

    CONTENT_TYPES = {
        'tv': {'emoji': '📺', 'name': '电视剧'},
        'movie': {'emoji': '🎬', 'name': '电影'},
        'podcast': {'emoji': '🎙️', 'name': '播客'},
        'talk': {'emoji': '🎤', 'name': '脱口秀'},
        'music': {'emoji': '🎵', 'name': '音乐'},
        'news': {'emoji': '📰', 'name': '新闻'},
        'documentary': {'emoji': '📹', 'name': '纪录片'}
    }

    EMOTION_LABELS = {
        'sincere': '真诚', 'warm': '温暖', 'regretful': '遗憾',
        'determined': '坚定', 'tender': '温柔', 'committed': '承诺',
        'excited': '兴奋', 'curious': '好奇', 'surprised': '惊讶',
        'challenging': '挑衅', 'shocked': '震惊', 'confident': '自信',
        'competitive': '竞争', 'professional': '专业', 'intriguing': '引人入胜',
        'serious': '严肃', 'informative': '信息性'
    }

    def create_subtitle_json(self, title: str, content_type: str, subtitles: List[Dict],
                           duration: str = "", difficulty: str = "", description: str = "",
                           source: str = "", tags: List[str] = None) -> str:
        """
        创建 Shadowing Studio 标准字幕 JSON 文件

        Args:
            title: 内容标题
            content_type: 类型 (tv/movie/podcast/talk/music/news/documentary)
            subtitles: 字幕列表，每个字幕包含 start, end, text, translation, emotions
            duration: 总时长 (MM:SS 或 HH:MM:SS)
            difficulty: CEFR 等级 (A1-C2)
            description: 内容描述
            source: 来源
            tags: 标签列表

        Returns:
            str: 保存的文件路径
        """
        if content_type not in self.CONTENT_TYPES:
            raise ValueError(f"无效的类型: {content_type}，可选: {list(self.CONTENT_TYPES.keys())}")

        # 标准化字幕数据
        normalized_subtitles = []
        for i, sub in enumerate(subtitles):
            normalized = {
                "start": float(sub["start"]),
                "end": float(sub["end"]),
                "text": str(sub["text"]).strip(),
                "translation": str(sub.get("translation", "")).strip(),
                "emotions": sub.get("emotions", [])
            }
            if sub.get("notes"):
                normalized["notes"] = str(sub["notes"])
            normalized_subtitles.append(normalized)

        entry = {
            "title": title,
            "type": content_type,
            "duration": duration,
            "difficulty": difficulty,
            "description": description,
            "source": source,
            "tags": tags or [],
            "subtitles": normalized_subtitles,
            "created_at": datetime.now().isoformat()
        }

        # 生成标准化文件名
        filename = self._generate_filename(title, content_type)
        filepath = self.shadowing_dir / f"{filename}.json"

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(entry, f, ensure_ascii=False, indent=2)

        return str(filepath)

    def _generate_filename(self, title: str, content_type: str) -> str:
        """生成标准化文件名"""
        # 清理标题：保留字母、数字、中文，空格和下划线转为连字符
        clean_title = re.sub(r'[^\w\u4e00-\u9fa5]+', '_', title.strip())
        clean_title = clean_title.strip('_')

        # 限制长度
        if len(clean_title) > 50:
            clean_title = clean_title[:50]

        return f"{content_type}-{clean_title}"

    def validate_subtitle_json(self, filepath: str) -> Dict:
        """
        验证字幕 JSON 文件格式

        Args:
            filepath: JSON 文件路径

        Returns:
            Dict: 验证结果 {'valid': bool, 'errors': List[str], 'data': Dict}
        """
        result = {'valid': False, 'errors': [], 'data': None}

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            result['errors'].append(f"JSON 解析错误: {e}")
            return result
        except FileNotFoundError:
            result['errors'].append(f"文件不存在: {filepath}")
            return result

        # 必需字段验证
        required_fields = ['title', 'type', 'subtitles']
        for field in required_fields:
            if field not in data:
                result['errors'].append(f"缺少必需字段: {field}")

        # 类型验证
        if data.get('type') and data['type'] not in self.CONTENT_TYPES:
            result['errors'].append(f"无效的类型: {data['type']}")

        # 字幕数组验证
        if not isinstance(data.get('subtitles'), list):
            result['errors'].append("subtitles 必须是数组")
        elif len(data['subtitles']) == 0:
            result['errors'].append("subtitles 数组不能为空")
        else:
            # 逐个验证字幕
            for i, sub in enumerate(data['subtitles']):
                if 'start' not in sub:
                    result['errors'].append(f"字幕 {i}: 缺少 start")
                elif not isinstance(sub['start'], (int, float)):
                    result['errors'].append(f"字幕 {i}: start 必须是数字")

                if 'end' not in sub:
                    result['errors'].append(f"字幕 {i}: 缺少 end")
                elif not isinstance(sub['end'], (int, float)):
                    result['errors'].append(f"字幕 {i}: end 必须是数字")

                if 'start' in sub and 'end' in sub:
                    if sub['start'] >= sub['end']:
                        result['errors'].append(f"字幕 {i}: start ({sub['start']}) 必须小于 end ({sub['end']})")

                    # 检查与前一个字幕的时间重叠
                    if i > 0:
                        prev_end = data['subtitles'][i-1]['end']
                        if sub['start'] < prev_end:
                            result['errors'].append(f"字幕 {i}: 开始时间 ({sub['start']}) 与前一个字幕结束时间 ({prev_end}) 重叠")

                if 'text' not in sub or not sub['text']:
                    result['errors'].append(f"字幕 {i}: 缺少 text")

        result['valid'] = len(result['errors']) == 0
        result['data'] = data
        return result

    def scan_and_process_files(self, temp_dir: str = None) -> Dict:
        """
        扫描并处理临时目录中的文件

        Args:
            temp_dir: 临时目录路径，默认使用 shadowing/临时/

        Returns:
            Dict: 处理结果
        """
        if temp_dir is None:
            temp_dir = self.shadowing_dir / "临时"
        else:
            temp_dir = Path(temp_dir)

        result = {
            'processed': [],
            'errors': [],
            'media_files': [],
            'json_files': []
        }

        if not temp_dir.exists():
            return result

        # 收集所有文件
        json_files = list(temp_dir.glob("*.json"))
        media_files = list(temp_dir.glob("*.mp3")) + list(temp_dir.glob("*.mp4")) + \
                     list(temp_dir.glob("*.wav")) + list(temp_dir.glob("*.ogg"))

        result['media_files'] = [str(f) for f in media_files]
        result['json_files'] = [str(f) for f in json_files]

        # 处理 JSON 文件
        for json_file in json_files:
            validation = self.validate_subtitle_json(str(json_file))

            if validation['valid']:
                data = validation['data']
                # 生成标准化文件名
                new_filename = self._generate_filename(data['title'], data['type'])
                target_path = self.shadowing_dir / f"{new_filename}.json"

                # 移动文件
                import shutil
                shutil.move(str(json_file), str(target_path))
                result['processed'].append({
                    'type': 'json',
                    'original': str(json_file),
                    'target': str(target_path),
                    'title': data['title']
                })
            else:
                result['errors'].append({
                    'file': str(json_file),
                    'errors': validation['errors']
                })

        # 处理媒体文件（尝试匹配已存在的 JSON）
        for media_file in media_files:
            base_name = media_file.stem.lower()

            # 查找匹配的 JSON 文件（同名或包含关系）
            matched = False
            for json_file in self.shadowing_dir.glob("*.json"):
                json_name = json_file.stem.lower()
                if base_name in json_name or json_name in base_name:
                    # 移动到同一目录，使用相同前缀
                    new_name = f"{json_file.stem}{media_file.suffix}"
                    target_path = self.shadowing_dir / new_name

                    import shutil
                    shutil.move(str(media_file), str(target_path))
                    result['processed'].append({
                        'type': 'media',
                        'original': str(media_file),
                        'target': str(target_path),
                        'matched_with': str(json_file)
                    })
                    matched = True
                    break

            if not matched:
                # 未匹配，移动到主目录但保留原文件名
                target_path = self.shadowing_dir / media_file.name
                import shutil
                shutil.move(str(media_file), str(target_path))
                result['processed'].append({
                    'type': 'media',
                    'original': str(media_file),
                    'target': str(target_path),
                    'matched_with': None
                })

        # 更新索引
        self._update_index()

        return result

    def _update_index(self):
        """更新索引文件"""
        index_path = self.shadowing_dir / "shadowing_index.json"

        contents = []
        for json_file in self.shadowing_dir.glob("*.json"):
            if json_file.name == "shadowing_index.json":
                continue

            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # 检查是否有对应的媒体文件
                media_files = list(self.shadowing_dir.glob(f"{json_file.stem}.*"))
                has_media = any(m.suffix in ['.mp3', '.mp4', '.wav', '.ogg'] for m in media_files)

                contents.append({
                    "id": json_file.stem,
                    "title": data.get('title', ''),
                    "type": data.get('type', ''),
                    "hasMedia": has_media,
                    "difficulty": data.get('difficulty', ''),
                    "subtitleCount": len(data.get('subtitles', [])),
                    "addedAt": data.get('created_at', '')
                })
            except Exception as e:
                logger.warning(f"读取文件失败: {json_file}, {e}")

        index = {
            "lastUpdated": datetime.now().isoformat(),
            "contents": contents
        }

        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2)

    def list_subtitle_contents(self, content_type: str = None) -> List[Dict]:
        """
        列出所有字幕内容（Web 界面格式）

        Args:
            content_type: 按类型过滤

        Returns:
            内容列表
        """
        contents = []

        for json_file in self.shadowing_dir.glob("*.json"):
            if json_file.name == "shadowing_index.json":
                continue

            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                if content_type and data.get('type') != content_type:
                    continue

                # 检查媒体文件
                media_files = list(self.shadowing_dir.glob(f"{json_file.stem}.*"))
                media_type = None
                for m in media_files:
                    if m.suffix == '.mp4':
                        media_type = 'video'
                        break
                    elif m.suffix in ['.mp3', '.wav', '.ogg']:
                        media_type = 'audio'

                info = self.CONTENT_TYPES.get(data.get('type', ''), {})

                contents.append({
                    "id": json_file.stem,
                    "title": data.get('title', ''),
                    "type": data.get('type', ''),
                    "emoji": info.get('emoji', '📄'),
                    "duration": data.get('duration', ''),
                    "difficulty": data.get('difficulty', ''),
                    "description": data.get('description', ''),
                    "hasMedia": media_type is not None,
                    "mediaType": media_type,
                    "subtitleCount": len(data.get('subtitles', []))
                })
            except Exception as e:
                logger.warning(f"读取文件失败: {json_file}, {e}")

        return contents


# ==================== 全局实例 ====================

_shadowing_manager = None


def get_manager() -> ShadowingManager:
    """获取管理器实例（单例模式）"""
    global _shadowing_manager
    if _shadowing_manager is None:
        _shadowing_manager = ShadowingManager()
    return _shadowing_manager


if __name__ == '__main__':
    # 测试代码
    manager = get_manager()

    # 测试添加文本
    result = manager.add_text(
        title="Test Text",
        content="This is a test text for shadowing practice.",
        source="Test Source",
        difficulty="easy"
    )
    print(f"Added text: {result}")

    # 测试生成填空
    exercise = manager.generate_fill_in_blank("Test Text", ratio=0.3)
    if exercise:
        print(f"Exercise text: {exercise['exercise_text']}")
        print(f"Answers: {[b['answer'] for b in exercise['blanks']]}")
