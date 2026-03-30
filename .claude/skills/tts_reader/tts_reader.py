#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TTS Reader - 基于 MiniMax Speech-2.8 的文字朗读工具
支持英语/中文朗读、复读、调速
"""

import asyncio
import argparse
import os
import subprocess
import time
import requests
from pathlib import Path

# MiniMax API 配置
# MiniMax Speech API Key（Token Plan 包含 TTS 能力）
# 支持环境变量 MINIMAX_API_KEY 或 MINIMAX_SPEECH_API_KEY
MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY") or os.environ.get("MINIMAX_SPEECH_API_KEY", "")
MINIMAX_API_URL = "https://api.minimaxi.com/v1/t2a_v2"
MINIMAX_ASYNC_API_URL = "https://api.minimaxi.com/v1/t2a_async_v2"
MINIMAX_ASYNC_QUERY_URL = "https://api.minimaxi.com/v1/query/t2a_async_query_v2"
MINIMAX_FILE_RETRIEVE_URL = "https://api.minimaxi.com/v1/files/retrieve"

# 语音配置
# MiniMax Speech-2.8 支持的音色 (voice_id)
VOICES = {
    # 中文
    "zh-lyrical": "Chinese (Mandarin)_Lyrical_Voice",
    "zh-assistant": "Chinese (Mandarin)_Female_Assistant",
    "zh-educational": "Chinese (Mandarin)_Female_Educational",
    "zh-young": "Chinese (Mandarin)_Male_Young",
    "zh-mature": "Chinese (Mandarin)_Male_Mature",
    "zh-standard": "Chinese (Mandarin)_Female_Standard",
    # 英语（通用）
    "en-graceful": "English_Graceful_Lady",
    "en-expressive": "English_Expressive_Lady",
    "en-trustworthy": "English_Trustworthy_Man",
    "en-diligent": "English_Diligent_Man",
    "en-gentle": "English_Gentle-voiced_man",
    "en-whisper": "English_Whispering_girl",
    "en-aussie": "English_Aussie_Bloke",
    # 日语
    "jp-whisper": "Japanese_Whisper_Belle",
    "jp-intellectual": "Japanese_IntellectualSenior",
    "jp-princess": "Japanese_DecisivePrincess",
    "jp-knight": "Japanese_LoyalKnight",
    "jp-calm": "Japanese_CalmLady",
    "jp-kind": "Japanese_KindLady",
    "jp-youth": "Japanese_OptimisticYouth",
    "jp-boy": "Japanese_InnocentBoy",
    # 越南语
    "vi-kind": "Vietnamese_kindhearted_girl",
}

# 语速映射 (edge-tts 风格 -> MiniMax 风格)
# edge-tts: -30%, 0%, +30% -> MiniMax: 0.7, 1.0, 1.3
RATE_MAP = {
    "slow": 0.75,
    "normal": 1.0,
    "fast": 1.25,
}


def detect_language(text: str) -> str:
    """简单检测语言（中文/日文/英文，越南语无法自动识别需手动指定）"""
    has_cjk = False
    for char in text:
        if '\u4e00' <= char <= '\u9fff':
            return "zh"
        if '\u3040' <= char <= '\u309f' or '\u30a0' <= char <= '\u30ff':
            return "jp"  # 平假名或片假名
        if '\u4e00' <= char <= '\u9fff':
            has_cjk = True
    return "zh" if has_cjk else "en"


def speak_text(
    text: str,
    voice: str = None,
    rate: str = "normal",
    output_file: str = None,
    play: bool = True,
    emotion: str = None,
    sync: bool = False
) -> str:
    """
    文字转语音并播放（MiniMax Speech-2.8）

    Args:
        text: 要朗读的文字
        voice: 语音名称（如 en-jenny, zh-xiaoxiao）
        rate: 语速（slow/normal/fast）
        output_file: 输出文件路径（可选）
        play: 是否立即播放
        emotion: 情绪（happy, sad, angry, anxious 等）
        sync: True=同步模式（实时，消耗更多配额），False=异步turbo（省25%配额，默认）

    Returns:
        输出文件路径
    """
    # 自动检测语言
    lang = detect_language(text)

    # 自动选择语音（越南语无法自动识别，需手动指定 --voice vi-kind）
    if voice is None:
        if lang == "zh":
            voice = "zh-lyrical"
        elif lang == "jp":
            voice = "jp-kind"
        else:
            voice = "en-graceful"

    voice_id = VOICES.get(voice, voice)
    speed = RATE_MAP.get(rate, 1.0)

    # 生成临时文件名
    if output_file is None:
        output_file = f"tts_temp_{abs(hash(text)) % 100000}.mp3"

    if sync:
        # 同步模式：speech-2.8-hd，600 请求/次
        audio_hex = call_minimax_tts(
            text=text,
            voice_id=voice_id,
            speed=speed,
            emotion=emotion,
            output_file=output_file
        )
        if audio_hex is None:
            raise Exception("MiniMax TTS API 调用失败")
    else:
        # 异步模式（默认）：speech-2.8-turbo，225 请求/次，省 62%
        ok = call_minimax_tts_async(
            text=text,
            voice_id=voice_id,
            speed=speed,
            emotion=emotion,
            output_file=output_file
        )
        if not ok:
            raise Exception("MiniMax 异步 TTS API 调用失败")

    # 播放
    if play:
        play_audio(output_file)

    return output_file


def call_minimax_tts(
    text: str,
    voice_id: str,
    speed: float = 1.0,
    emotion: str = None,
    output_file: str = None
) -> str:
    """
    调用 MiniMax Speech-2.8 API

    Returns:
        十六进制编码的音频数据（同时写入文件）
    """
    headers = {
        "Authorization": f"Bearer {MINIMAX_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "speech-2.8-hd",
        "text": text,
        "stream": False,
        "voice_setting": {
            "voice_id": voice_id,
            "speed": speed,
            "vol": 1.0,
            "pitch": 0
        },
        "audio_setting": {
            "sample_rate": 32000,
            "bitrate": 128000,
            "format": "mp3"
        }
    }

    # 添加情绪控制（仅 speech-2.8 支持）
    if emotion:
        payload["voice_setting"]["emotion"] = emotion

    response = requests.post(
        MINIMAX_API_URL,
        headers=headers,
        json=payload,
        timeout=30
    )

    if response.status_code != 200:
        error_msg = f"HTTP {response.status_code}: {response.text}"
        print(f"API 错误: {error_msg}")
        # 检查是否是 key 错误
        if "login fail" in response.text or "auth" in response.text.lower():
            print("\n⚠️ API 认证失败！")
            print("请确认你使用的是 MiniMax Speech API Key，而非 Anthropic API Key")
            print("获取地址: https://platform.minimaxi.com/user-center/basic-information/interface-key")
        return None

    result = response.json()

    if result.get("base_resp", {}).get("status_code") != 0:
        status_msg = result.get("base_resp", {}).get("status_msg", "unknown")
        print(f"API 错误: {status_msg}")
        if "voice" in status_msg.lower():
            print("请检查 voice_id 是否正确")
        return None

    # 解码音频并保存
    audio_hex = result["data"]["audio"]
    audio_bytes = bytes.fromhex(audio_hex)

    with open(output_file, "wb") as f:
        f.write(audio_bytes)

    audio_length = result.get("extra_info", {}).get("audio_length", 0)
    print(f"生成音频: {output_file} ({audio_length}ms)")

    return audio_hex


def call_minimax_tts_async(
    text: str,
    voice_id: str,
    speed: float = 1.0,
    emotion: str = None,
    output_file: str = None,
    poll_interval: float = 2.0,
    max_polls: int = 60
) -> bool:
    """
    调用 MiniMax Speech-2.8 异步 API（turbo 模型，225 请求/次）

    Returns:
        True if successful, False otherwise
    """
    headers = {
        "Authorization": f"Bearer {MINIMAX_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "speech-2.8-turbo",
        "text": text,
        "voice_setting": {
            "voice_id": voice_id,
            "speed": speed,
            "vol": 1.0,
            "pitch": 0
        },
        "audio_setting": {
            "audio_sample_rate": 32000,
            "bitrate": 128000,
            "format": "mp3"
        }
    }

    if emotion:
        payload["voice_setting"]["emotion"] = emotion

    # Step 1: 提交异步任务
    response = requests.post(
        MINIMAX_ASYNC_API_URL,
        headers=headers,
        json=payload,
        timeout=30
    )

    if response.status_code != 200:
        print(f"提交异步任务失败: HTTP {response.status_code}: {response.text}")
        if "login fail" in response.text or "auth" in response.text.lower():
            print("\n⚠️ API 认证失败！请检查 MINIMAX_API_KEY 环境变量")
        return False

    result = response.json()
    if result.get("base_resp", {}).get("status_code") != 0:
        print(f"API 错误: {result.get('base_resp', {}).get('status_msg', 'unknown')}")
        return False

    task_id = result.get("task_id")
    if not task_id:
        print("未获取到 task_id")
        return False

    print(f"异步任务已提交 (task_id: {task_id}), 等待生成...")

    # Step 2: 轮询状态
    query_headers = {"Authorization": f"Bearer {MINIMAX_API_KEY}"}
    for i in range(max_polls):
        time.sleep(poll_interval)

        query_response = requests.get(
            MINIMAX_ASYNC_QUERY_URL,
            headers=query_headers,
            params={"task_id": task_id},
            timeout=10
        )

        if query_response.status_code != 200:
            print(f"查询状态失败: HTTP {query_response.status_code}")
            continue

        query_result = query_response.json()
        status = query_result.get("status")

        if status == "Processing":
            print(f"  生成中... ({(i + 1) * poll_interval:.0f}s)")
            continue
        elif status in ("Failed", "Expired"):
            msg = query_result.get("base_resp", {}).get("status_msg", "")
            print(f"任务{status}: {msg}")
            return False
        elif status == "Success":
            # Step 3: 获取下载链接并保存
            download_url = query_result.get("download_url") or query_result.get("audio_url")
            file_id = query_result.get("file_id")

            if not download_url and file_id:
                # 通过 file_id 获取下载链接
                file_resp = requests.get(
                    MINIMAX_FILE_RETRIEVE_URL,
                    headers=query_headers,
                    params={"file_id": file_id},
                    timeout=10
                )
                if file_resp.status_code == 200:
                    download_url = file_resp.json().get("file", {}).get("download_url")

            if not download_url:
                print("无法获取音频下载链接")
                return False

            audio_resp = requests.get(download_url, timeout=60)
            if audio_resp.status_code != 200:
                print(f"下载音频失败: HTTP {audio_resp.status_code}")
                return False

            with open(output_file, "wb") as f:
                f.write(audio_resp.content)

            print(f"生成音频: {output_file} (异步turbo)")
            return True

    print(f"轮询超时 ({max_polls * poll_interval:.0f}s)")
    return False


def play_audio(file_path: str, wait: bool = True):
    """播放音频文件"""
    cmd = ["ffplay", "-nodisp", "-autoexit", file_path]

    if wait:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


async def async_speak_text(
    text: str,
    voice: str = None,
    rate: str = "normal",
    output_file: str = None,
    play: bool = True,
    emotion: str = None,
    sync: bool = False
) -> str:
    """异步版本的 speak_text（保持兼容性）"""
    return speak_text(text, voice, rate, output_file, play, emotion, sync)


async def speak_repeatedly(
    text: str,
    repeat: int = 3,
    pause_between: float = 1.0,
    voice: str = None,
    rate: str = "normal",
    emotion: str = None
):
    """复读模式"""
    print(f"朗读 {repeat} 次: {text}")

    for i in range(repeat):
        print(f"  [{i+1}/{repeat}]")
        speak_text(text, voice=voice, rate=rate, emotion=emotion)
        if i < repeat - 1:
            await asyncio.sleep(pause_between)


async def interactive_mode():
    """交互模式"""
    print("=" * 50)
    print("TTS Reader - MiniMax Speech-2.8 交互模式")
    print("=" * 50)
    print("命令:")
    print("  直接输入文字 - 朗读")
    print("  /r 3 文字    - 复读3次")
    print("  /slow 文字   - 慢速朗读")
    print("  /fast 文字   - 快速朗读")
    print("  /happy 文字  - 开心情绪")
    print("  /sad 文字    - 悲伤情绪")
    print("  /list        - 列出所有语音")
    print("  /quit        - 退出")
    print("=" * 50)

    while True:
        try:
            user_input = input("\n> ").strip()

            if not user_input:
                continue

            if user_input == "/quit":
                break

            if user_input == "/list":
                print("\n可用语音:")
                print("\n中文:")
                for name in ["zh-xiaoxiao", "zh-xiaoyi", "zh-yunxi", "zh-yunyang", "zh-ning"]:
                    print(f"  {name}")
                print("\n英语:")
                for name in ["en-jenny", "en-guy", "en-aria", "en-ryan", "en-emma"]:
                    print(f"  {name}")
                continue

            # 复读模式
            if user_input.startswith("/r "):
                parts = user_input.split(" ", 2)
                if len(parts) >= 3:
                    repeat = int(parts[1])
                    text = parts[2]
                    await speak_repeatedly(text, repeat=repeat)
                continue

            # 慢速
            if user_input.startswith("/slow "):
                text = user_input[6:]
                speak_text(text, rate="slow")
                continue

            # 快速
            if user_input.startswith("/fast "):
                text = user_input[6:]
                speak_text(text, rate="fast")
                continue

            # 开心情绪
            if user_input.startswith("/happy "):
                text = user_input[8:]
                speak_text(text, emotion="happy")
                continue

            # 悲伤情绪
            if user_input.startswith("/sad "):
                text = user_input[5:]
                speak_text(text, emotion="sad")
                continue

            # 普通朗读
            speak_text(user_input)

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"错误: {e}")

    print("\n再见!")


def main():
    parser = argparse.ArgumentParser(description="TTS Reader - MiniMax Speech-2.8 文字朗读工具")
    parser.add_argument("text", nargs="?", help="要朗读的文字")
    parser.add_argument("-f", "--file", help="从文件读取文字")
    parser.add_argument("-v", "--voice", default=None, help="语音选择")
    parser.add_argument("-r", "--rate", default="normal", help="语速 (slow/normal/fast)")
    parser.add_argument("-o", "--output", help="输出文件（不播放）")
    parser.add_argument("--repeat", type=int, default=1, help="复读次数")
    parser.add_argument("-i", "--interactive", action="store_true", help="交互模式")
    parser.add_argument("--list-voices", action="store_true", help="列出所有语音")
    parser.add_argument("--emotion", default=None, help="情绪 (happy/sad/angry/anxious)")
    parser.add_argument("--sync", action="store_true", help="同步模式（实时，speech-2.8-hd，600请求/次；默认异步turbo，225请求/次）")

    args = parser.parse_args()

    if args.list_voices:
        print("可用语音:")
        groups = {
            "中文": ["zh-lyrical", "zh-assistant", "zh-educational", "zh-young", "zh-mature", "zh-standard"],
            "英语": ["en-graceful", "en-expressive", "en-trustworthy", "en-diligent", "en-gentle", "en-whisper", "en-aussie"],
            "日语": ["jp-whisper", "jp-intellectual", "jp-princess", "jp-knight", "jp-calm", "jp-kind", "jp-youth", "jp-boy"],
            "越南语": ["vi-kind"],
        }
        for lang, names in groups.items():
            print(f"\n{lang}:")
            for name in names:
                print(f"  {name}: {VOICES[name]}")
        return

    if args.interactive:
        asyncio.run(interactive_mode())
        return

    # 获取文字
    if args.file:
        text = Path(args.file).read_text(encoding="utf-8").strip()
    elif args.text:
        text = args.text
    else:
        print("请输入要朗读的文字，或使用 -i 进入交互模式")
        return

    # 朗读
    if args.repeat > 1:
        asyncio.run(speak_repeatedly(
            text, repeat=args.repeat, voice=args.voice, rate=args.rate, emotion=args.emotion
        ))
    else:
        output = speak_text(
            text, voice=args.voice, rate=args.rate,
            output_file=args.output, play=(not args.output),
            emotion=args.emotion, sync=args.sync
        )
        if args.output:
            print(f"已保存: {args.output}")


if __name__ == "__main__":
    main()
