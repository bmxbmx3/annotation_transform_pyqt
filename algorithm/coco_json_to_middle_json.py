"""
转换coco json为中间标注格式
"""

import re
from glob import glob
import os
import json
from PIL import Image
import shutil


def coco_json_to_middle_json(img_dir, src_label_dir, deleted_label_tuple, selected_label_tuple, rename_label_regexes):
    """转换coco json为中间标注格式

    :param img_dir:图片文件夹
    :param src_label_dir:源标注文件夹
    :param deleted_label_tuple:筛除类名的正则表达式
    :param selected_label_tuple:筛选类名的正则表达式
    :param rename_label_regexes:重命名的正则表达式
    :return:
    """
    # 筛选/筛除类名
    deleted_label_regex, deleted_state = deleted_label_tuple
    selected_label_regex, selected_state = selected_label_tuple

    src_labels_path = glob(os.path.join(src_label_dir, "*.json"))[0]  # 源标注文件路径（只有一个coco json文件）
    img_paths = glob(os.path.join(img_dir, "*.jpg")) + glob(os.path.join(img_dir, "*.png"))  # 图片文件夹路径
    deleted_label_pat = re.compile(deleted_label_regex)  # 筛除类名
    selected_label_pat = re.compile(selected_label_regex)  # 筛选类名
    rename_label_pats = [[re.compile(i[0]), i[1]] for i in rename_label_regexes]  # 重命名类名

    current_path = os.path.dirname(os.path.abspath(__file__))  # 当前路径
    dst_label_dir = os.path.join(current_path, "middle_json")  # 中间标注文件夹

    """事先清空middle_json文件夹下的所有文件"""
    shutil.rmtree(dst_label_dir)
    os.makedirs(dst_label_dir)

    with open(src_labels_path, "r", encoding="utf-8") as f:
        coco_json = json.load(f)

    """整理coco json"""
    image_id_map = {}  # 图片id
    category_id_map = {}  # 类别id

    # 图片id映射
    image_name_map = {}
    for i in coco_json["images"]:
        # 图片名
        image_name = os.path.splitext(i["file_name"])[0]
        image_name_map[image_name] = i["id"]

        path = os.path.join(img_dir, i["file_name"])  # 图片路径
        image_id_map[i["id"]] = {
            "image": {
                "path": path,
                "width": i["width"],
                "height": i["height"],
                "extra": {}
            },
            "label": []
        }

    # 类别id映射
    for i in coco_json["categories"]:
        category_id_map[i["id"]] = i["name"]

    for i in coco_json["annotations"]:

        """筛选/筛除类名"""
        label = category_id_map[i["category_id"]]
        if deleted_state:
            deleted_label_find = deleted_label_pat.findall(label)  # 筛除后的类名
            # 如果是筛除的类名，则跳过
            if deleted_label_find != [] and deleted_label_find[0] == label:
                continue
        elif selected_state:
            selected_label_find = selected_label_pat.findall(label)  # 筛除后的类名
            # 如果是筛出的类名，则选择
            if not (selected_label_find != [] and selected_label_find[0] == label):
                continue

        """重命名类名"""
        for j in rename_label_pats:
            rename_label_find = j[0].findall(label)
            # 如果找到类名，则代替
            if rename_label_find != [] and rename_label_find[0] == label:
                label = j[1]
                break

        image_id = i["image_id"]
        xmin, ymin, w, h = i["bbox"]
        xmax = xmin + w
        ymax = ymin + h

        image_id_map[image_id]["label"].append(
            {
                "name": label,
                "xmin": int(xmin),
                "xmax": int(xmax),
                "ymin": int(ymin),
                "ymax": int(ymax),
                "extra": {
                    "source": "coco",
                    "property": "bndbox"
                }
            }
        )

    for img_path in img_paths:
        """获得图片名"""
        base = os.path.basename(img_path)
        img_name = os.path.splitext(base)[0]

        """获得图片长宽"""
        img = Image.open(img_path)
        width, height = img.size

        """转换"""
        dst_label_path = os.path.join(dst_label_dir, img_name + ".json")  # 中间标注文件路径
        middle_json = {
            "image": {
                "path": img_path,
                "width": width,
                "height": height,
                "extra": {}
            },
            "label": []
        }
        # 如果图片有对应的源标注文件
        if img_name in image_name_map.keys():
            image_id = image_name_map[img_name]
            middle_json = image_id_map[image_id]
        with open(dst_label_path, "w", encoding="utf-8") as f:
            json.dump(middle_json, f, ensure_ascii=False)
