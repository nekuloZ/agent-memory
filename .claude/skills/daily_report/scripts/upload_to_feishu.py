"""
上传日报到飞书文件夹（转为在线文档）
"""
import requests
import os
import glob
import time

# ============= 配置区 =============
FOLDER_TOKEN = 'A3tWfWzyxlESe5dOrSsczwHJnwf'

# 自动找最新的日报文件
def get_latest_report():
    # 从项目根目录找报告文件
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(base_dir, '..', '..', '..', '..'))
    reports_dir = os.path.join(project_root, 'jarvis-memory', 'L0_Working', 'reports')
    pattern = os.path.join(reports_dir, '主播业绩日报_*.md')
    files = glob.glob(pattern)
    if not files:
        return None
    files.sort(reverse=True)
    return files[0]

# ============= 获取 token（使用缓存）============
def get_token():
    from feishu_token import get_token as _get_token
    return _get_token()

# ============= 步骤1: 上传文件获取 file_token =============
def upload_file(token, file_path):
    file_size = os.path.getsize(file_path)
    file_name = os.path.basename(file_path)

    url = 'https://open.feishu.cn/open-apis/drive/v1/files/upload_all'

    with open(file_path, 'rb') as f:
        files = {'file': (file_name, f, 'text/markdown')}
        data = {
            'file_name': file_name,
            'parent_type': 'explorer',
            'parent_node': FOLDER_TOKEN,
            'size': str(file_size)
        }
        headers = {'Authorization': f'Bearer {token}'}
        resp = requests.post(url, headers=headers, files=files, data=data)

    result = resp.json()
    if result.get('code') != 0:
        print(f'上传文件失败: {result}')
        print(f'错误码: {result.get("code")}')
        print(f'错误信息: {result.get("msg")}')
        return None

    file_token = result['data']['file_token']
    print(f'  上传成功，file_token: {file_token}')
    return file_token

# ============= 步骤2: 创建导入任务 =============
def create_import_task(token, file_token, file_name):
    # 获取文件扩展名（去掉日期部分，用 .md）
    file_extension = 'md'
    # 文档名去掉 .md 后缀
    doc_name = file_name.replace('.md', '') if file_name.endswith('.md') else file_name

    url = 'https://open.feishu.cn/open-apis/drive/v1/import_tasks'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json; charset=utf-8'
    }
    body = {
        'file_extension': file_extension,
        'file_token': file_token,
        'type': 'docx',  # 新版文档
        'file_name': doc_name,
        'point': {
            'mount_type': 1,
            'mount_key': FOLDER_TOKEN
        }
    }

    resp = requests.post(url, headers=headers, json=body)
    result = resp.json()

    if result.get('code') != 0:
        print(f'创建导入任务失败: {result}')
        print(f'错误码: {result.get("code")}')
        print(f'错误信息: {result.get("msg")}')
        return None

    ticket = result['data']['ticket']
    print(f'  导入任务创建成功，ticket: {ticket}')
    return ticket

# ============= 步骤3: 查询导入任务结果 =============
def query_import_result(token, ticket, max_wait=120):
    url = f'https://open.feishu.cn/open-apis/drive/v1/import_tasks/{ticket}'
    headers = {'Authorization': f'Bearer {token}'}

    start_time = time.time()
    while time.time() - start_time < max_wait:
        resp = requests.get(url, headers=headers)
        result = resp.json()

        if result.get('code') != 0:
            print(f'查询任务失败: {result}')
            return None

        job_data = result.get('data', {}).get('result', {})
        job_status = job_data.get('job_status')

        # job_status: 0=成功, 1=初始化, 2=处理中, 3+=各种错误
        if job_status == 0:
            doc_token = job_data.get('token')
            doc_url = job_data.get('url', '')
            print(f'  导入成功！')
            print(f'  文档token: {doc_token}')
            return doc_token
        elif job_status >= 3:
            error_msg = job_data.get('job_error_msg', f'错误码 {job_status}')
            print(f'  导入失败: {error_msg}')
            return None

        print(f'  处理中... (job_status={job_status})')
        time.sleep(3)

    print('  导入超时')
    return None

# ============= 主函数 =============
def main():
    file_path = get_latest_report()
    if not file_path:
        print('未找到日报文件，请先运行 python 直播日报.py')
        return

    file_name = os.path.basename(file_path)
    print(f'[使用文件] {file_name}')
    print('[1/4] 获取 access_token（使用缓存）...')
    token = get_token()
    if not token:
        return

    print('[2/4] 上传文件...')
    file_token = upload_file(token, file_path)
    if not file_token:
        return

    print('[3/4] 创建导入任务...')
    ticket = create_import_task(token, file_token, file_name)
    if not ticket:
        return

    print('[4/4] 等待导入完成...')
    doc_token = query_import_result(token, ticket)
    if not doc_token:
        return

    doc_url = f'https://zcn8fd75l4aq.feishu.cn/docx/{doc_token}'

    print(f'\n完成！')
    print(f'文档链接: {doc_url}')
    print(f'文件夹: https://zcn8fd75l4aq.feishu.cn/drive/folder/{FOLDER_TOKEN}')

if __name__ == '__main__':
    main()
