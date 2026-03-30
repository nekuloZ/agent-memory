"""
直播业绩日报生成脚本
数据源：直播每日数据.xlsx（飞书导出）

更新日志：
- v2.0: 使用新的 feishu_token API，自动刷新 token
- v2.1: 内嵌点评建议生成，修复乱码问题
"""

import sys
import io

# 设置控制台输出为UTF-8（解决Windows乱码）
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import pandas as pd
from datetime import datetime, timedelta
import subprocess
import json
import os

# ============= 配置区 =============
# 基础路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..', '..', '..', '..'))

# 数据目录
DATA_DIR = os.path.join(PROJECT_ROOT, 'jarvis-memory', 'data')
REPORTS_DIR = os.path.join(PROJECT_ROOT, 'jarvis-memory', 'L0_Working', 'reports')
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

# 文件路径
EXCEL_FILE = os.path.join(DATA_DIR, '直播每日数据.xlsx')
SHEET_NAME = '直播每日数据'
REPORT_OUTPUT_DIR = REPORTS_DIR

# 飞书配置
APP_TOKEN = 'FOjMbU3oEaiH9DskfvEclydBnkf'
TABLE_ID = 'tblRBXvqOVu6wHEr'


# ============= 飞书API下载函数 =============
def download_from_feishu():
    """从飞书下载最新数据，使用新的 token API"""
    from feishu_token import get_token, call_feishu_api

    print('[1/4] 获取 access_token...')
    token = get_token()

    print('[2/4] 创建导出任务...')
    success, result, _ = call_feishu_api(
        'https://open.feishu.cn/open-apis/drive/v1/export_tasks/',
        method='POST',
        headers={'Content-Type': 'application/json'},
        data={
            "token": APP_TOKEN,
            "type": "bitable",
            "file_type": "xlsx",
            "file_extension": "xlsx",
            "table_id": TABLE_ID
        }
    )

    if not success or result.get('code') != 0:
        print(f'错误: {result}')
        return False

    ticket = result['data']['ticket']

    print('[3/4] 轮询任务状态...')
    max_retries = 30
    for attempt in range(max_retries):
        success, result, _ = call_feishu_api(
            f'https://open.feishu.cn/open-apis/drive/v1/export_tasks/{ticket}?token={APP_TOKEN}'
        )

        if not success:
            print(f'  API调用失败: {result}')
            return False

        job_status = result['data']['result']['job_status']

        if job_status == 0:  # 成功
            file_token = result['data']['result']['file_token']
            print(f'  导出完成 (第{attempt+1}次检查)')
            break
        elif job_status == 2:  # 失败
            print(f'  导出失败: {result}')
            return False
        else:  # job_status == 1, 进行中
            print(f'  导出中... ({attempt+1}/{max_retries})', end='\r')
            import time
            time.sleep(2)
    else:
        print(f'\n  导出超时，请稍后手动重试')
        return False

    print('[4/4] 下载文件...')
    # 先删除旧文件
    try:
        if os.path.exists(EXCEL_FILE):
            os.remove(EXCEL_FILE)
            print(f'  已删除旧文件')
    except Exception as e:
        print(f'  警告：无法删除旧文件 ({e})，请手动关闭Excel后重试')
        return False

    # 使用 PowerShell 下载
    subprocess.run([
        'powershell', '-Command',
        f'Invoke-WebRequest -Uri "https://open.feishu.cn/open-apis/drive/v1/export_tasks/file/{file_token}/download" -Headers @{{"Authorization" = "Bearer {token}"}} -OutFile "{EXCEL_FILE}"'
    ])

    print(f'  已下载: {EXCEL_FILE}')
    return True


# ============= 数据分析函数 =============
def generate_insights(today_data, yesterday_data, sorted_anchors, time_slot_data, today_profit, yesterday_profit):
    """生成 AI 点评建议"""
    insights = []

    # 计算环比
    def mom(today, yesterday):
        if yesterday == 0:
            return None
        return (today - yesterday) / yesterday * 100

    gmv_mom = mom(today_data['GMV'], yesterday_data['GMV'])
    profit_mom = mom(today_profit, yesterday_profit)

    # 判断整体趋势
    if gmv_mom and gmv_mom >= 10:
        insights.append(("📈 今日亮点", f"整体表现强劲：GMV环比+{gmv_mom:.1f}%，利润环比+{profit_mom:.1f}%"))
    elif gmv_mom and gmv_mom <= -10:
        insights.append(("📉 今日预警", f"整体大幅下滑：GMV环比{gmv_mom:+.1f}%，需要重点关注"))

    # 找出表现最好和最差的主播
    if sorted_anchors:
        best_anchor = sorted_anchors[0]
        worst_anchor = sorted_anchors[-1] if len(sorted_anchors) > 1 else None

        if best_anchor[1]['GMV'] > 50000:
            best_roi = best_anchor[1]['GMV'] / best_anchor[1]['Ad'] if best_anchor[1]['Ad'] > 0 else 0
            insights.append(("⭐ 明星主播", f"{best_anchor[0]}：GMV {best_anchor[1]['GMV']:,.0f}，ROI {best_roi:.2f}，表现稳定"))

        if worst_anchor and worst_anchor[1]['GMV'] < 10000:
            insights.append(("⚠️ 需要关注", f"{worst_anchor[0]}：GMV 仅{worst_anchor[1]['GMV']:,.0f}，建议分析原因"))

    # 时段分析
    if time_slot_data:
        best_slot = max(time_slot_data, key=lambda x: x['gmv'])
        worst_slot = min(time_slot_data, key=lambda x: x['gmv'])

        if best_slot['gmv'] > 30000:
            insights.append(("🕐 黄金时段", f"{best_slot['slot']}（{best_slot['name']}）：GMV {best_slot['gmv']:,.0f}，ROI {best_slot['roi']:.2f}"))

        # 检查晚间时段是否表现差
        evening_slots = [s for s in time_slot_data if '21:30' in s['slot'] or '19:00' in s['slot']]
        if evening_slots:
            evening_avg = sum(s['gmv'] for s in evening_slots) / len(evening_slots)
            if evening_avg < 20000:
                insights.append(("⚠️ 时段预警", "晚间时段表现不佳，建议检查主播状态、选品、流量情况"))

    # 生成建议
    suggestions = []
    if gmv_mom and gmv_mom < -10:
        suggestions.append("恢复核心时段投放，检查商品组合和话术")
    if gmv_mom and gmv_mom >= 10:
        suggestions.append("继续保持当前策略，复制成功时段到其他时间")

    return insights, suggestions


def generate_report():
    """生成日报"""
    print('\n[分析] 读取数据...')
    df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)

    print('[分析] 按日期汇总...')
    daily_summary = df.groupby(df.iloc[:, 0]).apply(lambda x: pd.Series({
        'GMV': x.iloc[:, 10].sum(),
        '千川': x.iloc[:, 13].sum(),
        '时长': x.iloc[:, 15].sum(),
        '订单': x.iloc[:, 8].sum(),
        '观看': x.iloc[:, 5].sum(),
        '退货': x.iloc[:, 9].sum(),
        '场数': len(x)
    }))

    # 获取最新两天
    latest_dates = sorted(daily_summary.index, reverse=True)[:2]
    today = latest_dates[0]
    yesterday = latest_dates[1]

    today_data = daily_summary.loc[today]
    yesterday_data = daily_summary.loc[yesterday]

    # 计算利润
    def calculate_profit(gmv, refund, ad):
        refund_rate = refund / gmv if gmv > 0 else 0
        return gmv * (1 - refund_rate) - gmv * (1 - refund_rate) * (43/66) - ad

    # 偏离度评级
    def get_deviation_rating(current, benchmark):
        if benchmark is None or benchmark == 0:
            return 'N/A'
        diff = (current - benchmark) / benchmark * 100
        if diff >= 10:
            return f'{diff:+.0f}%🟢'
        elif diff <= -20:
            return f'{diff:+.0f}%🔴'
        elif diff <= -10:
            return f'{diff:+.0f}%⚠️'
        else:
            return f'{diff:+.0f}%➡️'

    # 计算历史基准
    def calculate_benchmark(target_data, today, days):
        cutoff_date = today - pd.Timedelta(days=days)
        historical = target_data[target_data.iloc[:, 0] < today]
        historical = historical[historical.iloc[:, 0] >= cutoff_date]

        if len(historical) == 0:
            return None

        return {
            'GMV': historical.iloc[:, 10].sum(),
            '千川': historical.iloc[:, 13].sum(),
            '时长': historical.iloc[:, 15].sum(),
            '订单': historical.iloc[:, 8].sum(),
            '观看': historical.iloc[:, 5].sum(),
            '退货': historical.iloc[:, 9].sum(),
            '场数': len(historical.groupby(historical.iloc[:, 0]))
        }

    # 计算基准的派生指标
    def benchmark_metrics(bench, days):
        if bench is None:
            return {'GMV': None, 'ROI': None, '利润': None, '观看': None}
        profit = calculate_profit(bench['GMV'], bench['退货'], bench['千川'])
        roi = bench['GMV'] / bench['千川'] if bench['千川'] > 0 else 0
        return {
            'GMV': bench['GMV'] / days,
            'ROI': roi,
            '利润': profit / days,
            '观看': bench['观看'] / days
        }

    today_profit = calculate_profit(today_data['GMV'], today_data['退货'], today_data['千川'])
    yesterday_profit = calculate_profit(yesterday_data['GMV'], yesterday_data['退货'], yesterday_data['千川'])

    # 环比
    def mom(today, yesterday):
        if yesterday == 0:
            return 'N/A'
        return f'{(today - yesterday) / yesterday * 100:+.1f}%'

    print(f'[分析] 生成报告（{today.date()}）...')

    # 获取今日原始数据进行主播排名
    today_raw = df[df.iloc[:, 0] == today]

    # 按主播汇总
    anchor_stats = {}
    for i in range(len(today_raw)):
        name_val = today_raw.iloc[i, 3]
        gmv = today_raw.iloc[i, 10]
        ad = today_raw.iloc[i, 13]
        duration = today_raw.iloc[i, 15]
        orders = today_raw.iloc[i, 8]
        view = today_raw.iloc[i, 5]
        refund = today_raw.iloc[i, 9]

        if pd.notna(name_val):
            names = [n.strip() for n in str(name_val).split(',')]
        else:
            names = ['未知']

        for name in names:
            if name not in anchor_stats:
                anchor_stats[name] = {'GMV': 0, 'Ad': 0, 'Duration': 0, 'Orders': 0, 'View': 0, 'Refund': 0}
            anchor_stats[name]['GMV'] += gmv
            anchor_stats[name]['Ad'] += ad
            anchor_stats[name]['Duration'] += duration
            anchor_stats[name]['Orders'] += orders
            anchor_stats[name]['View'] += view
            anchor_stats[name]['Refund'] += refund

    sorted_anchors = sorted(anchor_stats.items(), key=lambda x: x[1]['GMV'], reverse=True)

    # 生成Markdown
    md_content = f'''# 主播业绩日报（{today.date()}）

> 数据时间：{pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')} | 数据源：飞书直播数据表

> **评级说明：** 🟢+10%以上 | ➡️±10%以内 | ⚠️-10%~-20% | 🔴-20%以下

## 一、整体汇总

| 指标 | 今日 | 昨日 | 环比 |
|------|------|------|------|
| 直播场数 | {today_data['场数']:.0f} | {yesterday_data['场数']:.0f} | {mom(today_data['场数'], yesterday_data['场数'])} |
| 总GMV | {today_data['GMV']:,.0f} | {yesterday_data['GMV']:,.0f} | {mom(today_data['GMV'], yesterday_data['GMV'])} |
| 千川消耗 | {today_data['千川']:,.0f} | {yesterday_data['千川']:,.0f} | {mom(today_data['千川'], yesterday_data['千川'])} |
| ROI | {today_data['GMV']/today_data['千川']:.2f} | {yesterday_data['GMV']/yesterday_data['千川']:.2f} | {mom(today_data['GMV']/today_data['千川'], yesterday_data['GMV']/yesterday_data['千川'])} |
| 利润 | {today_profit:,.0f} | {yesterday_profit:,.0f} | {mom(today_profit, yesterday_profit)} |
| 直播时长(h) | {today_data['时长']:.1f} | {yesterday_data['时长']:.1f} | {mom(today_data['时长'], yesterday_data['时长'])} |
| 成交订单数 | {today_data['订单']:,.0f} | {yesterday_data['订单']:,.0f} | {mom(today_data['订单'], yesterday_data['订单'])} |
| 观看人数 | {today_data['观看']:,.0f} | {yesterday_data['观看']:,.0f} | {mom(today_data['观看'], yesterday_data['观看'])} |
| 平均客单价 | {today_data['GMV']/today_data['订单']:.1f} | {yesterday_data['GMV']/yesterday_data['订单']:.1f} | {mom(today_data['GMV']/today_data['订单'], yesterday_data['GMV']/yesterday_data['订单'])} |
| 千次观看成交(GPM) | {(today_data['GMV']/today_data['观看']*1000):,.0f} | {(yesterday_data['GMV']/yesterday_data['观看']*1000):,.0f} | {mom(today_data['GMV']/today_data['观看']*1000, yesterday_data['GMV']/yesterday_data['观看']*1000)} |
| 退货金额 | {today_data['退货']:,.0f} | {yesterday_data['退货']:,.0f} | {mom(today_data['退货'], yesterday_data['退货'])} |
| 单位时长GMV | {today_data['GMV']/today_data['时长']:,.0f} | {yesterday_data['GMV']/yesterday_data['时长']:,.0f} | {mom(today_data['GMV']/today_data['时长'], yesterday_data['GMV']/yesterday_data['时长'])} |
| 单位时长订单 | {today_data['订单']/today_data['时长']:.1f} | {yesterday_data['订单']/yesterday_data['时长']:.1f} | {mom(today_data['订单']/today_data['时长'], yesterday_data['订单']/yesterday_data['时长'])} |
| 单位时长利润 | {today_profit/today_data['时长']:,.0f} | {yesterday_profit/yesterday_data['时长']:,.0f} | {mom(today_profit/today_data['时长'], yesterday_profit/yesterday_data['时长'])} |

---

## 二、主播排名

| 排名 | 主播 | GMV | 千川 | ROI | 利润 | 退货率 | 时长 | GMV/h | 订单/h | 利润/h | 观看 | 订单 | 客单价 | 转化率 |
|------|------|-----|------|-----|------|--------|------|-------|--------|--------|------|------|--------|--------|
'''

    for i, (name, stats) in enumerate(sorted_anchors, 1):
        roi = stats['GMV'] / stats['Ad'] if stats['Ad'] > 0 else 0
        aov = stats['GMV'] / stats['Orders'] if stats['Orders'] > 0 else 0
        conversion = stats['Orders'] / stats['View'] if stats['View'] > 0 else 0
        refund_rate = stats['Refund'] / stats['GMV'] if stats['GMV'] > 0 else 0
        profit = calculate_profit(stats['GMV'], stats['Refund'], stats['Ad'])
        duration = stats['Duration']
        gmv_per_h = stats['GMV'] / duration if duration > 0 else 0
        orders_per_h = stats['Orders'] / duration if duration > 0 else 0
        profit_per_h = profit / duration if duration > 0 else 0

        md_content += f'| {i} | {name} | {stats["GMV"]:,.0f} | {stats["Ad"]:,.0f} | {roi:.2f} | {profit:,.0f} | {refund_rate:.2%} | {duration:.1f} | {gmv_per_h:,.0f} | {orders_per_h:.1f} | {profit_per_h:,.0f} | {stats["View"]:,.0f} | {stats["Orders"]:,.0f} | {aov:.1f} | {conversion:.2%} |\n'

    # 时段分析
    md_content += '''
---

## 三、主播时段细分

| 时段 | 主播 | 大小号 | GMV | 千川 | ROI | 利润 | 时长 | 观看 | 订单 | 客单价 | 转化率 |
|------|------|--------|-----|------|-----|------|------|------|------|--------|--------|
'''
    time_slot_data = []
    for i in range(len(today_raw)):
        slot = str(today_raw.iloc[i, 2]).replace('：', ':')
        name = today_raw.iloc[i, 3]
        size_type = today_raw.iloc[i, 1]
        gmv = today_raw.iloc[i, 10]
        ad = today_raw.iloc[i, 13]
        duration = today_raw.iloc[i, 15]
        orders = today_raw.iloc[i, 8]
        view = today_raw.iloc[i, 5]
        refund = today_raw.iloc[i, 9]

        roi = gmv / ad if ad > 0 else 0
        profit = calculate_profit(gmv, refund, ad)
        aov = gmv / orders if orders > 0 else 0
        conversion = orders / view if view > 0 else 0

        time_slot_data.append({
            'slot': slot,
            'name': name,
            'size_type': size_type,
            'gmv': gmv,
            'ad': ad,
            'roi': roi,
            'profit': profit,
            'duration': duration,
            'view': view,
            'orders': orders,
            'aov': aov,
            'conversion': conversion
        })

    time_slot_data.sort(key=lambda x: x['slot'])

    for item in time_slot_data:
        md_content += f'| {item["slot"]} | {item["name"]} | {item["size_type"]} | {item["gmv"]:,.0f} | {item["ad"]:,.0f} | {item["roi"]:.2f} | {item["profit"]:,.0f} | {item["duration"]:.1f} | {item["view"]:,.0f} | {item["orders"]:,.0f} | {item["aov"]:.1f} | {item["conversion"]:.2%} |\n'

    # 最佳时段分析
    best_gmv = max(time_slot_data, key=lambda x: x['gmv'])
    best_roi = max(time_slot_data, key=lambda x: x['roi'])
    best_conversion = max(time_slot_data, key=lambda x: x['conversion'])

    md_content += f'''
---

## 四、最佳时段分析

| 指标 | 最佳时段 | 主播 | 数值 |
|------|----------|------|------|
| 最高GMV | {best_gmv['slot']} | {best_gmv['name']} | {best_gmv['gmv']:,.0f} |
| 最高ROI | {best_roi['slot']} | {best_roi['name']} | {best_roi['roi']:.2f} |
| 最高转化率 | {best_conversion['slot']} | {best_conversion['name']} | {best_conversion['conversion']:.2%} |
'''

    # ============= 基准对比 =============
    print('[分析] 计算基准值...')

    bench_7d = calculate_benchmark(df, today, 7)
    bench_30d = calculate_benchmark(df, today, 30)
    metrics_7d = benchmark_metrics(bench_7d, 7)
    metrics_30d = benchmark_metrics(bench_30d, 30)

    today_metrics = {
        'GMV': today_data['GMV'],
        'ROI': today_data['GMV'] / today_data['千川'],
        '利润': today_profit,
        '观看': today_data['观看']
    }

    md_content += '''
---

## 五、基准对比

### 整体基准（7日/30日）
| 指标 | 今日 | 7日均 | 30日均 | vs7日 | vs30日 |
|------|------|-------|--------|-------|--------|
'''
    gmv_7d = f'{metrics_7d["GMV"]:,.0f}' if metrics_7d['GMV'] else 'N/A'
    gmv_30d = f'{metrics_30d["GMV"]:,.0f}' if metrics_30d['GMV'] else 'N/A'
    roi_7d = f'{metrics_7d["ROI"]:.2f}' if metrics_7d['ROI'] else 'N/A'
    roi_30d = f'{metrics_30d["ROI"]:.2f}' if metrics_30d['ROI'] else 'N/A'
    profit_7d = f'{metrics_7d["利润"]:,.0f}' if metrics_7d['利润'] else 'N/A'
    profit_30d = f'{metrics_30d["利润"]:,.0f}' if metrics_30d['利润'] else 'N/A'
    view_7d = f'{metrics_7d["观看"]:,.0f}' if metrics_7d['观看'] else 'N/A'
    view_30d = f'{metrics_30d["观看"]:,.0f}' if metrics_30d['观看'] else 'N/A'

    md_content += f'| GMV | {today_metrics["GMV"]:,.0f} | {gmv_7d} | {gmv_30d} | {get_deviation_rating(today_metrics["GMV"], metrics_7d["GMV"])} | {get_deviation_rating(today_metrics["GMV"], metrics_30d["GMV"])} |\n'
    md_content += f'| ROI | {today_metrics["ROI"]:.2f} | {roi_7d} | {roi_30d} | {get_deviation_rating(today_metrics["ROI"], metrics_7d["ROI"])} | {get_deviation_rating(today_metrics["ROI"], metrics_30d["ROI"])} |\n'
    md_content += f'| 利润 | {today_metrics["利润"]:,.0f} | {profit_7d} | {profit_30d} | {get_deviation_rating(today_metrics["利润"], metrics_7d["利润"])} | {get_deviation_rating(today_metrics["利润"], metrics_30d["利润"])} |\n'
    md_content += f'| 观看人数 | {today_metrics["观看"]:,.0f} | {view_7d} | {view_30d} | {get_deviation_rating(today_metrics["观看"], metrics_7d["观看"])} | {get_deviation_rating(today_metrics["观看"], metrics_30d["观看"])} |\n'

    # 主播基准
    md_content += '''
### 主播基准（7日/30日）
| 主播 | 今日GMV | 7日均 | 30日均 | vs7日 | vs30日 | 今日ROI | 7日均 | 30日均 | vs7日 | vs30日 |
|------|---------|-------|--------|-------|--------|---------|-------|--------|-------|--------|
'''

    for name, stats in sorted_anchors:
        anchor_df = df[df.iloc[:, 3].str.contains(name, na=False)]
        bench_7d = calculate_benchmark(anchor_df, today, 7)
        bench_30d = calculate_benchmark(anchor_df, today, 30)
        metrics_7d = benchmark_metrics(bench_7d, 7)
        metrics_30d = benchmark_metrics(bench_30d, 30)

        today_gmv = stats['GMV']
        today_roi = stats['GMV'] / stats['Ad'] if stats['Ad'] > 0 else 0

        gmv_7d = f'{metrics_7d["GMV"]:,.0f}' if metrics_7d['GMV'] else 'N/A'
        gmv_30d = f'{metrics_30d["GMV"]:,.0f}' if metrics_30d['GMV'] else 'N/A'
        roi_7d = f'{metrics_7d["ROI"]:.2f}' if metrics_7d['ROI'] else 'N/A'
        roi_30d = f'{metrics_30d["ROI"]:.2f}' if metrics_30d['ROI'] else 'N/A'

        md_content += f'| {name} | {today_gmv:,.0f} | {gmv_7d} | {gmv_30d} | {get_deviation_rating(today_gmv, metrics_7d["GMV"])} | {get_deviation_rating(today_gmv, metrics_30d["GMV"])} | {today_roi:.2f} | {roi_7d} | {roi_30d} | {get_deviation_rating(today_roi, metrics_7d["ROI"])} | {get_deviation_rating(today_roi, metrics_30d["ROI"])} |\n'

    # 时段基准
    md_content += '''
### 时段基准（7日/30日）
| 时段 | 今日GMV | 7日均 | 30日均 | vs7日 | vs30日 | 今日ROI | 7日均 | 30日均 | vs7日 | vs30日 | 评价 |
|------|---------|-------|--------|-------|--------|---------|-------|--------|-------|--------|------|
'''

    for item in time_slot_data:
        slot = item['slot']
        slot_df = df[df.iloc[:, 2].astype(str).str.replace('：', ':') == slot]
        bench_7d = calculate_benchmark(slot_df, today, 7)
        bench_30d = calculate_benchmark(slot_df, today, 30)
        metrics_7d = benchmark_metrics(bench_7d, 7)
        metrics_30d = benchmark_metrics(bench_30d, 30)

        today_gmv = item['gmv']
        today_roi = item['roi']

        gmv_7d = f'{metrics_7d["GMV"]:,.0f}' if metrics_7d['GMV'] else 'N/A'
        gmv_30d = f'{metrics_30d["GMV"]:,.0f}' if metrics_30d['GMV'] else 'N/A'
        roi_7d = f'{metrics_7d["ROI"]:.2f}' if metrics_7d['ROI'] else 'N/A'
        roi_30d = f'{metrics_30d["ROI"]:.2f}' if metrics_30d['ROI'] else 'N/A'

        gmv_rating = get_deviation_rating(today_gmv, metrics_30d["GMV"])
        roi_rating = get_deviation_rating(today_roi, metrics_30d["ROI"])
        if '🟢' in gmv_rating and '🟢' in roi_rating:
            evaluation = '🟢🟢双超'
        elif '🔴' in gmv_rating and '🔴' in roi_rating:
            evaluation = '🔴🔴双低'
        elif '🟢' in gmv_rating:
            evaluation = '量高'
        elif '🔴' in gmv_rating:
            evaluation = '量低'
        else:
            evaluation = '正常'

        md_content += f'| {slot} | {today_gmv:,.0f} | {gmv_7d} | {gmv_30d} | {get_deviation_rating(today_gmv, metrics_7d["GMV"])} | {get_deviation_rating(today_gmv, metrics_30d["GMV"])} | {today_roi:.2f} | {roi_7d} | {roi_30d} | {get_deviation_rating(today_roi, metrics_7d["ROI"])} | {get_deviation_rating(today_roi, metrics_30d["ROI"])} | {evaluation} |\n'

    # ============= AI 点评建议 =============
    print('[分析] 生成AI点评建议...')
    insights, suggestions = generate_insights(today_data, yesterday_data, sorted_anchors, time_slot_data, today_profit, yesterday_profit)

    md_content += '''
---

## 六、AI点评建议
'''

    for title, content in insights:
        md_content += f'\n### {title}\n{content}\n'

    if suggestions:
        md_content += '\n### 💡 优化建议\n'
        for i, suggestion in enumerate(suggestions, 1):
            md_content += f'{i}. {suggestion}\n'

    md_content += f'\n---\n\n> 报告生成时间：{pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")} | 数据日期：{today.date()}\n'

    # 保存文件（确保 UTF-8 编码）
    report_filename = os.path.join(REPORT_OUTPUT_DIR, f'主播业绩日报_{today.date()}.md')
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(md_content)

    print(f'[完成] 报告已生成: {report_filename}')
    print(f'  日期: {today.date()}')
    print(f'  GMV: {today_data["GMV"]:,.0f}')
    print(f'  环比: {mom(today_data["GMV"], yesterday_data["GMV"])}')
    return True


# ============= 主函数 =============
def main():
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == '--download-only':
            download_from_feishu()
        elif sys.argv[1] == '--report-only':
            generate_report()
        else:
            print('用法:')
            print('  python generate_report.py              # 下载 + 生成报告')
            print('  python generate_report.py --download-only  # 只下载')
            print('  python generate_report.py --report-only   # 只生成报告')
    else:
        if download_from_feishu():
            generate_report()


if __name__ == '__main__':
    main()
