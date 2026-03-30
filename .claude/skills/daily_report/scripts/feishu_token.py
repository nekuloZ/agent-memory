"""
飞书 Token 管理工具
- 自动刷新过期 token
- 每日第一次运行自动获取新 token
- API 调用失败时自动重试
"""
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime

# 配置
APP_ID = 'cli_a817e1ff72b8101c'
APP_SECRET = 'LPS7tuyaT4GgyJyKbFhZsdiEfa1W4BYk'
CACHE_FILE = '.feishu_token_cache.json'
TOKEN_EXPIRE_SECONDS = 7200  # 2小时


def fetch_new_token():
    """从飞书API获取新的 token"""
    resp = subprocess.run([
        'curl', '-s', '-X', 'POST',
        'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
        '-H', 'Content-Type: application/json',
        '-d', f'{{"app_id": "{APP_ID}", "app_secret": "{APP_SECRET}"}}'
    ], capture_output=True, text=True)

    result = json.loads(resp.stdout)
    if result.get('code') != 0:
        raise Exception(f'获取token失败: {result}')
    return result['tenant_access_token']


def get_token(force_refresh=False):
    """
    获取有效 token

    Args:
        force_refresh: 是否强制刷新（忽略缓存）
    """
    cache = Path(CACHE_FILE)

    # 读取缓存
    cached_data = None
    if cache.exists():
        try:
            cached_data = json.loads(cache.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, KeyError):
            pass

    # 检查是否需要刷新
    need_refresh = force_refresh

    if cached_data and not need_refresh:
        # 检查日期：如果是新的一天，强制刷新
        cache_date = cached_data.get('date')
        today = datetime.now().strftime('%Y-%m-%d')
        if cache_date != today:
            print(f'[Token] 新的一天，刷新token（{cache_date} → {today}）')
            need_refresh = True
        else:
            # 检查时间是否过期
            timestamp = cached_data.get('timestamp', 0)
            if time.time() - timestamp >= TOKEN_EXPIRE_SECONDS:
                print(f'[Token] token已过期，刷新中...')
                need_refresh = True

    if need_refresh or not cached_data:
        token = fetch_new_token()
        cached_data = {
            'token': token,
            'timestamp': time.time(),
            'date': datetime.now().strftime('%Y-%m-%d')
        }
        cache.write_text(json.dumps(cached_data, ensure_ascii=False), encoding='utf-8')
        print(f'[Token] 新token已获取: {token[:20]}...')
    else:
        print(f'[Token] 使用缓存token: {cached_data["token"][:20]}...')

    return cached_data['token']


def call_feishu_api(url, method='GET', headers=None, data=None, max_retry=2):
    """
    调用飞书API，自动处理 token 失效并重试

    Args:
        url: API URL
        method: HTTP 方法 (GET/POST)
        headers: 额外的请求头
        data: 请求体（字典或JSON字符串）
        max_retry: 最大重试次数

    Returns:
        (success: bool, result: dict, new_token: str|None)
    """
    if headers is None:
        headers = {}

    for attempt in range(max_retry + 1):
        # 获取 token（第一次失败后强制刷新）
        token = get_token(force_refresh=(attempt > 0))

        # 构建请求头
        request_headers = {
            'Authorization': f'Bearer {token}',
            **headers
        }

        if method == 'GET':
            cmd = ['curl', '-s', url]
            for k, v in request_headers.items():
                cmd.extend(['-H', f'{k}: {v}'])
        else:  # POST
            if isinstance(data, dict):
                data = json.dumps(data, ensure_ascii=False)
            cmd = ['curl', '-s', '-X', 'POST', url]
            for k, v in request_headers.items():
                cmd.extend(['-H', f'{k}: {v}'])
            cmd.extend(['-d', data])

        resp = subprocess.run(cmd, capture_output=True, text=True)

        try:
            result = json.loads(resp.stdout)
        except json.JSONDecodeError:
            result = {'code': -1, 'msg': f'JSON解析失败: {resp.stdout[:200]}'}

        # 检查 token 是否失效
        if result.get('code') == 99991663:
            if attempt < max_retry:
                print(f'[API] token失效，刷新后重试 ({attempt+1}/{max_retry})...')
                # 清除缓存，下次会获取新 token
                Path(CACHE_FILE).unlink(missing_ok=True)
                continue
            else:
                print(f'[API] token刷新后仍然失败')
                return False, result, None

        # 成功或其他错误
        return True, result, token

    return False, {'code': -1, 'msg': '超过最大重试次数'}, None


def clear_cache():
    """清除缓存（用于测试或手动刷新）"""
    Path(CACHE_FILE).unlink(missing_ok=True)
    print('[Token] 缓存已清除')


if __name__ == '__main__':
    # 测试
    print('测试获取 token...')
    token = get_token()
    print(f'Token: {token[:20]}...')
    print(f'缓存文件: {CACHE_FILE}')
