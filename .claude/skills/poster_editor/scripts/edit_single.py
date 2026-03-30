#!/usr/bin/env python3
"""
单区域文字修改模板
使用方式：修改 CONFIG 配置后运行

示例：修改海报中某个区域的文字
"""

from PIL import Image, ImageDraw, ImageFont

def edit_poster():
    # ==================== 配置区域 ====================
    CONFIG = {
        # 输入输出
        "input": "input.png",      # 原图文件名
        "output": "output.png",    # 输出文件名

        # 涂色区域（覆盖原文字）
        "box": {
            "x1": 100, "y1": 200,  # 左上角坐标
            "x2": 500, "y2": 300   # 右下角坐标
        },
        "bg_color": (255, 254, 252),  # 背景色 #FFFEFC

        # 文字配置
        "text": "新文字内容",
        "font_name": "C:/Windows/Fonts/msyh.ttc",  # 字体路径
        "font_size": 34,                          # 字号
        "text_color": (68, 68, 68),               # 字色 #444444

        # 对齐方式
        "align": "center",   # left(左对齐) / center(居中) / right(右对齐)
        "center_x": 300,     # 水平中心点/对齐基准点
        "top_y": 210         # 顶部Y坐标
    }
    # =================================================

    # 打开原图
    img = Image.open(CONFIG["input"])
    draw = ImageDraw.Draw(img)

    # 步骤1：涂色覆盖原区域
    box = CONFIG["box"]
    draw.rectangle(
        [box["x1"], box["y1"], box["x2"], box["y2"]],
        fill=CONFIG["bg_color"]
    )

    # 步骤2：加载字体
    try:
        font = ImageFont.truetype(CONFIG["font_name"], CONFIG["font_size"])
    except Exception as e:
        print(f"字体加载失败: {e}，使用默认字体")
        font = ImageFont.load_default()

    # 步骤3：计算位置
    bbox = draw.textbbox((0, 0), CONFIG["text"], font=font)
    text_width = bbox[2] - bbox[0]

    if CONFIG["align"] == "center":
        x = CONFIG["center_x"] - text_width // 2
    elif CONFIG["align"] == "right":
        x = CONFIG["center_x"] - text_width
    else:  # left
        x = CONFIG["center_x"]

    y = CONFIG["top_y"]

    # 步骤4：写入文字
    draw.text((x, y), CONFIG["text"], font=font, fill=CONFIG["text_color"])

    # 保存
    img.save(CONFIG["output"], "PNG")
    print(f"✓ 已保存: {CONFIG['output']}")

if __name__ == "__main__":
    edit_poster()
