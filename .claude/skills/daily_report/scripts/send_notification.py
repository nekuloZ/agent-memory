"""
发送飞书消息通知
支持发送日报链接给指定用户
"""
import requests
import json
import glob
import re

# ============= 配置区 =============
# 用户 open_id
USERS = {
    '胡总': 'ou_59475f003ce0fe225a5be09615a72925',
    '小松': 'ou_560b1ed72f8280eced3527b689f44cd4'
}

# 默认消息模板
DEFAULT_MESSAGE = '主播业绩日报已生成：{url}'

# ============= 获取 token（使用缓存）============
def get_token():
    from feishu_token import get_token as _get_token
    return _get_token()

# ============= 获取最新日报链接 =============
def get_latest_report_url():
    """从上传脚本输出中获取最新的飞书文档链接"""
    pattern = '主播业绩日报_*.md'
    files = glob.glob(pattern)
    if not files:
        return None

    # 按文件名排序，取最新的
    files.sort(reverse=True)
    latest_file = files[0]

    # 尝试从控制台输出历史获取（这里简化处理）
    # 实际使用时可以维护一个简单的链接记录文件
    return None

# ============= 发送消息 =============
def send_message(token, receive_id, message):
    """发送文本消息给指定用户"""
    content = json.dumps({'text': message})

    resp = requests.post(
        'https://open.feishu.cn/open-apis/im/v1/messages',
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
        params={'receive_id_type': 'open_id'},
        json={
            'receive_id': receive_id,
            'msg_type': 'text',
            'content': content
        }
    )

    result = resp.json()
    if result.get('code') != 0:
        print(f'发送失败: {result}')
        return False

    print(f'发送成功 -> message_id: {result["data"]["message_id"]}')
    return True

# ============= 发送给多个用户 =============
def send_to_users(token, user_list, message_template, **kwargs):
    """发送消息给用户列表"""
    for user_name in user_list:
        if user_name not in USERS:
            print(f'用户不存在: {user_name}')
            continue

        receive_id = USERS[user_name]
        message = message_template.format(**kwargs)

        print(f'发送给 {user_name}...')
        send_message(token, receive_id, message)

# ============= 主函数 =============
def main():
    import sys

    # 获取 token
    print('[1/2] 获取 access_token（使用缓存）...')
    token = get_token()
    if not token:
        return

    # 解析参数
    if len(sys.argv) < 3:
        print('用法:')
        print('  python send_notification.py <用户> <消息/链接>')
        print('')
        print('示例:')
        print('  python send_notification.py 小松 https://xxx.feishu.cn/docx/xxx')
        print('  python send_notification.py "胡总,小松" "日报已生成：{url}"')
        print('')
        print('快捷方式:')
        print('  python send_notification.py @all    # 发送给所有用户')
        return

    users_input = sys.argv[1]
    url_or_message = sys.argv[2]

    # 解析用户列表
    if users_input == '@all':
        user_list = list(USERS.keys())
    else:
        user_list = [u.strip() for u in users_input.split(',')]

    # 判断是链接还是消息模板
    if url_or_message.startswith('http'):
        message = DEFAULT_MESSAGE.format(url=url_or_message)
    else:
        message = url_or_message

    # 发送
    print(f'[2/2] 发送消息给 {user_list}...')
    send_to_users(token, user_list, message)

if __name__ == '__main__':
    main()
