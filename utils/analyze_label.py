"""
分析各个类的占比
"""

from pathlib import Path
import json
from collections import defaultdict
from decimal import Decimal

current_path = Path.cwd()  # 当前路径
parent_path = current_path.parent.absolute()
middle_json_dir = parent_path / "algorithm" / "middle_json"
middle_json_paths = middle_json_dir.glob("*.json")

label_count = defaultdict(int)  # 默认dict，收集各个label的数量
label_sum = 0  # 标注总数
for middle_json_path in middle_json_paths:
    middle_json_path = str(middle_json_path)
    with open(middle_json_path, "r", encoding="utf-8") as f:
        middle_json = json.load(f)
    for i in middle_json["label"]:
        label = i["name"]
        label_count[label] += 1
        label_sum += 1

temp = sorted(label_count.items(), key=lambda d: d[1], reverse=True)  # 降序排序
label_count_sort = []
for i in temp:
    percent = str(Decimal(i[1] / label_sum * 100).quantize(Decimal("0.001"), rounding="ROUND_HALF_UP"))
    count = str(i[1])
    label_count_sort.append([i[0], count, percent])
print(label_sum)
print(label_count_sort)
