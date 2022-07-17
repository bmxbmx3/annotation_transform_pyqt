"""
转换rolabelimg rotated xml为中间标注格式
"""

from lxml import etree
import re
from glob import glob
import os
import html
import json
from PIL import Image
import shutil


def rolabelimg_rotated_xml_to_middle_json(img_dir, src_label_dir, deleted_label_tuple, selected_label_tuple,
                                          rename_label_regexes):
    """转换rolabelimg rotated xml为中间标注格式

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

    src_labels_paths = glob(os.path.join(src_label_dir, "*.xml"))  # 源标注文件路径
    img_paths = glob(os.path.join(img_dir, "*.jpg")) + glob(os.path.join(img_dir, "*.png"))  # 图片文件夹路径
    deleted_label_pat = re.compile(deleted_label_regex)  # 筛除类名
    selected_label_pat = re.compile(selected_label_regex)  # 筛选类名
    rename_label_pats = [[re.compile(i[0]), i[1]] for i in rename_label_regexes]  # 重命名类名

    current_path = os.path.dirname(os.path.abspath(__file__))  # 当前路径
    dst_label_dir = os.path.join(current_path, "middle_json")  # 中间标注文件夹

    """事先清空middle_json文件夹下的所有文件"""
    shutil.rmtree(dst_label_dir)
    os.makedirs(dst_label_dir)

    for img_path in img_paths:
        """获得图片名"""
        base = os.path.basename(img_path)
        img_name = os.path.splitext(base)[0]

        """转换"""
        src_label_path = os.path.join(src_label_dir, img_name + ".xml")  # 源标注文件路径
        dst_label_path = os.path.join(dst_label_dir, img_name + ".json")  # 中间标注文件路径

        """获得图片长宽"""
        img = Image.open(img_path)
        width, height = img.size

        # 转换后的中间标注信息
        middle_json = {
            "image": {
                "path": img_path,
                "width": width,
                "height": height,
                "extra": {

                }
            },
            "label": []
        }

        # 如果图片有对应的源标注文件
        if src_label_path in src_labels_paths:
            with open(src_label_path, "rb") as f:
                xml_in = f.read()
                """去除空白行"""
                parser = etree.XMLParser(remove_blank_text=True)
                elem = etree.XML(xml_in, parser=parser)
                xml_in = etree.tostring(elem).decode()

            """转换rolabelimg rotated xml（区分角度为0和不为0的）为middle json格式"""
            robndbox_regex = "<object><type>robndbox<\/type><name>(.*?)<\/name><pose>(.*?)<\/pose><truncated>(.*?)<\/truncated><difficult>(.*?)<\/difficult><robndbox><cx>(.*?)<\/cx>" \
                             "<cy>(.*?)<\/cy><w>(.*?)<\/w><h>(.*?)<\/h><angle>(.*?)<\/angle><\/robndbox><\/object>"
            robndbox_pat = re.compile(robndbox_regex)
            objects = robndbox_pat.findall(xml_in)
            for i in objects:
                """筛选/筛除类名"""
                label = html.unescape(i[0])  # 类名
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

                cx = float(i[4])
                cy = float(i[5])
                w = float(i[6])
                h = float(i[7])
                angle = i[8]

                # 如果robndbox有角度为0的，认定为bndbox
                if angle == "0.0":
                    xmin = int(cx - w / 2)
                    xmax = int(cx + w / 2)
                    ymin = int(cy - h / 2)
                    ymax = int(cy + h / 2)
                    # 防止转换后的四个顶点超出边界
                    xmin = 0 if xmin < 0 else xmin
                    xmax = width if xmax > width else xmax
                    ymin = 0 if ymin < 0 else ymin
                    ymax = height if ymax > height else ymax

                    label_json = {
                        "name": label,
                        "xmin": xmin,
                        "xmax": xmax,
                        "ymin": ymin,
                        "ymax": ymax,
                        "extra": {
                            "source": "rolabelimg (only rotated)",
                            "property": "bndbox"
                        }
                    }

                    middle_json["label"].append(label_json)

                # 如果robndbox有角度不为0的，认定为robndbox
                if angle != "0.0":
                    label_json = {
                        "name": label,
                        "cx": cx,
                        "cy": cy,
                        "w": w,
                        "h": h,
                        "angle": angle,
                        "extra": {
                            "source": "rolabelimg (only rotated)",
                            "property": "robndbox"
                        }
                    }

                    middle_json["label"].append(label_json)

        with open(dst_label_path, "w", encoding="utf-8") as f:
            json.dump(middle_json, f, ensure_ascii=False)
