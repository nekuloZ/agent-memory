#!/usr/bin/env python3
"""
底部色块 + 多行居中文字模板
适用于海报底部公司信息、合作方信息、落款等
"""

from PIL import Image, ImageDraw, ImageFont

def add_footer():
    # ==================== 配置区域 ====================
    # 输入输出
    input_path = "input.png"
    output_path = "output.png"

    # 色块配置
    BOX = {"x1": 937, "y1": 3038, "x2": 1517, "y2": 3288}
    BG_COLOR = (254, 221, 173)  # #feddad 米黄色

    # 多行文字配置
    LINES = [
        "中国联合网络通信集团有限公司",
        "x",                          # 分隔符，可换成 "×" 或其他
        "繁星智能回收管理系统"
    ]

    # 对齐基准点（矩形中心点）
    CENTER_X = 1228  # 水平中心线
    CENTER_Y = 3213  # 垂直中心点

    # 字体配置
    FONT_NAME = "AlibabaPuHuiTi-3-85-Bold"  # 主选字体
    FONT_FALLBACK = "C:/Windows/Fonts/msyhbd.ttc"  # 备选字体
    FONT_SIZE = 42
    TEXT_COLOR = (237, 29, 0)  # #ED1D00 红色
    LINE_HEIGHT = 48           # 行间距
    # =================================================

    # 打开原图
    img = Image.open(input_path)
    draw = ImageDraw.Draw(img)

    # 步骤1：涂色块
    draw.rectangle(
        [BOX["x1"], BOX["y1"], BOX["x2"], BOX["y2"]],
        fill=BG_COLOR
    )

    # 步骤2：加载字体
    try:
        font = ImageFont.truetype(FONT_NAME, FONT_SIZE)
    except Exception as e:
        print(f"主字体加载失败: {e}，使用备选字体")
        try:
            font = ImageFont.truetype(FONT_FALLBACK, FONT_SIZE)
        except:
            font = ImageFont.load_default()

    # 步骤3：计算起始位置（垂直居中）
    total_height = len(LINES) * LINE_HEIGHT
    current_y = CENTER_Y - total_height // 2 + 5

    # 步骤4：逐行写入（水平居中）
    for line in LINES:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = CENTER_X - text_width // 2
        draw.text((x, current_y), line, font=font, fill=TEXT_COLOR)
        current_y += LINE_HEIGHT

    # 保存
    img.save(output_path, "PNG")
    print(f"✓ 已保存: {output_path}")

if __name__ == "__main__":
    add_footer()
