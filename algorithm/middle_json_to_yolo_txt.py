"""
转换middle json为yolo txt格式
"""

import json
import os
from glob import glob
from decimal import Decimal


def middle_json_to_yolo_txt(dst_label_dir):
    """
    从middle json转换到目标文件夹

    :param dst_label_dir: 目标标注文件夹
    :return:
    """

    current_path = os.path.dirname(os.path.abspath(__file__))  # 当前路径
    middle_json_paths = glob(os.path.join(current_path, "middle_json", "*.json"))  # 中间标注文件路径
    for middle_json_path in middle_json_paths:
        with open(middle_json_path, "r", encoding="utf-8") as f:
            middle_json = json.load(f)

        """获得图片名"""
        img_path = middle_json["image"]["path"]
        base = os.path.basename(img_path)
        img_name = os.path.splitext(base)[0]
        width = middle_json["image"]["width"]
        height = middle_json["image"]["height"]

        """转换"""
        dst_label_path = os.path.join(dst_label_dir, img_name + ".txt")  # 目标标注文件路径
        labels = middle_json["label"]
        dst_label_str = ""  # 转换后的标注信息
        for i in labels:
            label_property = i["extra"]["property"]  # 标签属性
            if label_property == "bndbox":
                label = i["name"]
                xmin = i["xmin"]
                xmax = i["xmax"]
                ymin = i["ymin"]
                ymax = i["ymax"]

                cx = ((float(xmin) + float(xmax)) / 2) / width
                cy = ((float(ymin) + float(ymax)) / 2) / height
                w = (float(xmax) - float(xmin)) / width
                h = (float(ymax) - float(ymin)) / height

                # 不能没有标注范围
                if w < 0.000001 or h < 0.000001:
                    continue

                cx_str = str(Decimal(cx).quantize(Decimal("0.0001"),
                                                  rounding="ROUND_HALF_UP"))  # 四舍五入
                cy_str = str(Decimal(cy).quantize(Decimal("0.0001"), rounding="ROUND_HALF_UP"))
                w_str = str(Decimal(w).quantize(Decimal("0.0001"), rounding="ROUND_HALF_UP"))
                h_str = str(Decimal(h).quantize(Decimal("0.0001"), rounding="ROUND_HALF_UP"))

                object_str = "{} {} {} {} {}\n"
                dst_label_str += object_str.format(label, cx_str, cy_str, w_str, h_str)

        with open(dst_label_path, "w", encoding="utf-8") as f:
            f.write(dst_label_str)
