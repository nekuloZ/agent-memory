#!/usr/bin/env python3
"""
多区域批量修改模板
支持一次性修改多个区域

示例：同时修改海报中多个卡片的文字
"""

from PIL import Image, ImageDraw, ImageFont

def edit_poster():
    # 输入输出
    input_path = "input.png"
    output_path = "output.png"

    # ==================== 配置多个修改区域 ====================
    EDITS = [
        {
            "name": "区域1-标题",           # 标识名称（用于日志）
            "box": {"x1": 100, "y1": 200, "x2": 500, "y2": 300},
            "bg_color": (255, 254, 252),    # #FFFEFC
            "text": "新标题",
            "font": "msyhbd.ttc",           # 微软雅黑粗体
            "size": 54,
            "color": (0, 0, 0),             # #000000
            "center_x": 300,
            "top_y": 210
        },
        {
            "name": "区域2-内容",
            "box": {"x1": 100, "y1": 400, "x2": 600, "y2": 500},
            "bg_color": (255, 254, 252),
            "text": "新内容",
            "font": "msyh.ttc",             # 微软雅黑常规
            "size": 34,
            "color": (68, 68, 68),          # #444444
            "center_x": 350,
            "top_y": 415
        },
        # 添加更多区域...
    ]
    # =========================================================

    img = Image.open(input_path)
    draw = ImageDraw.Draw(img)

    for edit in EDITS:
        print(f"处理: {edit['name']}")

        # 步骤1：涂色覆盖
        b = edit["box"]
        draw.rectangle([b["x1"], b["y1"], b["x2"], b["y2"]], fill=edit["bg_color"])

        # 步骤2：加载字体
        try:
            font = ImageFont.truetype(f"C:/Windows/Fonts/{edit['font']}", edit["size"])
        except Exception as e:
            print(f"  字体加载失败: {e}，使用默认字体")
            font = ImageFont.load_default()

        # 步骤3：居中计算
        bbox = draw.textbbox((0, 0), edit["text"], font=font)
        text_width = bbox[2] - bbox[0]
        x = edit["center_x"] - text_width // 2
        y = edit["top_y"]

        # 步骤4：写入文字
        draw.text((x, y), edit["text"], font=font, fill=edit["color"])

    # 保存
    img.save(output_path, "PNG")
    print(f"\n✓ 已保存: {output_path}")

if __name__ == "__main__":
    edit_poster()
