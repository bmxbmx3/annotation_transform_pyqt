"""
转换middle json为coco json格式
"""

import json
import os
from glob import glob


def middle_json_to_coco_json(dst_label_dir):
    """
    从middle json转换到目标文件夹

    :param dst_label_dir: 目标标注文件夹
    :return:
    """

    current_path = os.path.dirname(os.path.abspath(__file__))  # 当前路径
    middle_json_paths = glob(os.path.join(current_path, "middle_json", "*.json"))  # 中间标注文件路径

    # 转换后的coco json
    dst_label_json = {
        'images': [
        ],
        'categories': [
        ],
        'annotations': [
        ]
    }

    image_id = 1  # 图片id
    category_id = 1
    category_id_map = {}  # 类别id
    annotation_id = 1  # 标注个数id
    for middle_json_path in middle_json_paths:
        with open(middle_json_path, "r", encoding="utf-8") as f:
            middle_json = json.load(f)

        """获得图片名"""
        img_path = middle_json["image"]["path"]
        img_name = os.path.basename(img_path)

        width = middle_json["image"]["width"]
        height = middle_json["image"]["height"]

        image_json = {
            "file_name": img_name,
            "id": image_id,
            "width": width,
            "height": height
        }

        dst_label_json["images"].append(image_json)

        """转换"""
        labels = middle_json["label"]
        for i in labels:
            label_property = i["extra"]["property"]  # 标签属性
            if label_property == "bndbox":
                label = i["name"]
                xmin = i["xmin"]
                xmax = i["xmax"]
                ymin = i["ymin"]
                ymax = i["ymax"]

                w = int(xmax - xmin)
                h = int(ymax - ymin)

                # 如果找到新的label，则记录其类别id
                if label not in category_id_map.keys():
                    category_id_map[label] = category_id
                    category_id += 1

                    category_json = {
                        "id": category_id_map[label],
                        "name": label,
                        "supercategory": label
                    }

                    dst_label_json["categories"].append(category_json)

                annotation_json = {
                    "area": float(w * h),
                    "category_id": category_id_map[label],
                    "segmentation": [[xmin, ymin, xmax, ymin, xmax, ymax, xmin, ymax]],
                    "iscrowd": 0,
                    "bbox": [xmin, ymin, w, h],
                    "image_id": image_id,
                    "id": annotation_id
                }

                annotation_id += 1

                dst_label_json["annotations"].append(annotation_json)

        image_id += 1

    """写入目标标注文件夹"""
    json_name = os.path.basename(dst_label_dir)
    dst_label_path = os.path.join(dst_label_dir, json_name + ".json")
    with open(dst_label_path, "w", encoding="utf-8") as f:
        json.dump(dst_label_json, f, ensure_ascii=False)  # ensure_ascii=False是为了能显示中文