"""
转换middle json为rolabelimg xml格式
"""

import json
import os
from glob import glob
from lxml import etree


def middle_json_to_rolabelimg_xml(dst_label_dir):
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
        labels = middle_json["label"]
        dst_label_str = ""  # 转换后的标注信息
        for i in labels:
            label_property = i["extra"]["property"]
            if label_property == "robndbox":
                label = i["name"]
                cx = i["cx"]
                cy = i["cy"]
                w = i["w"]
                h = i["h"]
                angle = i["angle"]

                object_str = "<object><type>robndbox</type><name>{}</name><pose>Unspecified</pose><truncated>0</truncated><difficult>0</difficult><robndbox><cx>{}</cx><cy>{}</cy><w>{}</w><h>{}</h><angle>{}</angle></robndbox></object>"
                dst_label_str += object_str.format(label, cx, cy, w, h, angle)
            if label_property == "bndbox":
                label = i["name"]
                xmin = i["xmin"]
                xmax = i["xmax"]
                ymin = i["ymin"]
                ymax = i["ymax"]

                object_str = "<object><type>bndbox</type><name>{}</name><pose>Unspecified</pose><truncated>0</truncated><difficult>0</difficult><bndbox><xmin>{}</xmin><ymin>{}</ymin><xmax>{}</xmax><ymax>{}</ymax></bndbox></object>"
                dst_label_str += object_str.format(label, xmin, ymin, xmax, ymax)

        """图片文件夹名"""
        img_folder = os.path.basename(os.path.dirname(img_path))
        folder_str = "<folder>{}</folder>".format(img_folder)

        """图片名"""
        filename_str = "<filename>{}</filename>".format(img_name)

        """图片路径"""
        path_str = "<path>{}</path>".format(img_path)

        """数据库名"""
        source_str = "<source><database>Unknown</database></source>"

        """图片大小"""
        size_str = "<size><width>{}</width><height>{}</height><depth>3</depth></size>".format(width, height)

        """是否分割"""
        segmented_str = "<segmented>0</segmented>"

        """拼接xml"""
        xml_out = '<annotation verified="no">' + folder_str + filename_str + path_str + source_str + size_str + \
                  segmented_str + dst_label_str + "</annotation>"

        """标准化输出xml"""
        xml_out = etree.fromstring(xml_out)
        xml_out = etree.tostring(xml_out, pretty_print=True).decode()

        """写入obb xml文件"""
        dst_label_path = os.path.join(dst_label_dir, img_name + ".xml")  # 目标标注文件路径
        with open(dst_label_path, "w") as f:
            f.write(xml_out)
