"""
标注格式转换pyqt主界面
"""
import os
import PyQt5.QtCore as qc
import PyQt5.QtWidgets as qw
import sys
from enum import Enum
from algorithm.rolabelimg_xml_to_middle_json import rolabelimg_xml_to_middle_json
from algorithm.yolo_txt_to_middle_json import yolo_txt_to_middle_json
from algorithm.rolabelimg_rotated_xml_to_middle_json import rolabelimg_rotated_xml_to_middle_json
from algorithm.coco_json_to_middle_json import coco_json_to_middle_json
from algorithm.labelimg_xml_to_middle_json import labelimg_xml_to_middle_json

from algorithm.middle_json_to_yolo_txt import middle_json_to_yolo_txt
from algorithm.middle_json_to_rolabelimg_xml import middle_json_to_rolabelimg_xml
from algorithm.middle_json_to_rolabelimg_rotated_xml import middle_json_to_rolabelimg_rotated_xml
from algorithm.middle_json_to_coco_json import middle_json_to_coco_json
from algorithm.middle_json_to_labelimg_xml import middle_json_to_labelimg_xml

from settings import Settings


class LabelFormat(Enum):
    """
    标注格式

    注：所有角度为0的robndbox都会被当成bndbox，存在中间标注格式中
    """
    YOLO_TXT = "YOLO TXT"
    LABELIMG_XML = "LABELIMG XML"
    ROLABELIMG_XML = "ROLABELIMG XML"  # 既有robndbox又有bndbox
    ROLABELIMG_XML_ONLY_ROTATED = "ROLABELIMG XML (ONLY ROTATED)"  # 只有robndbox
    COCO_JSON = "COCO JSON"


class MethodPrefix(Enum):
    """转换函数前缀"""
    YOLO_TXT = "yolo_txt"
    LABELIMG_XML = "labelimg_xml"
    ROLABELIMG_XML = "rolabelimg_xml"
    ROLABELIMG_XML_ONLY_ROTATED = "rolabelimg_rotated_xml"
    COCO_JSON = "coco_json"


class MainWindow(qw.QDialog):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setWindowTitle("标注文件格式转换")
        # self.setFixedHeight(218)  # 设置固定高度
        self.setMinimumWidth(900)  # 最小宽度

        main_v_layout = qw.QVBoxLayout(self)

        """选择标注格式"""
        annotation_select_h_layout = qw.QHBoxLayout()  # 选择标注格式
        self.label_formats = [
            LabelFormat.YOLO_TXT.value,
            LabelFormat.LABELIMG_XML.value,
            LabelFormat.ROLABELIMG_XML.value,
            LabelFormat.ROLABELIMG_XML_ONLY_ROTATED.value,
            LabelFormat.COCO_JSON.value
        ]  # 标注格式
        self.method_prefix = [
            MethodPrefix.YOLO_TXT.value,
            MethodPrefix.LABELIMG_XML.value,
            MethodPrefix.ROLABELIMG_XML.value,
            MethodPrefix.ROLABELIMG_XML_ONLY_ROTATED.value,
            MethodPrefix.COCO_JSON.value
        ]  # 转换函数前缀
        self.left_cbox = qw.QComboBox()
        self.left_cbox.addItems(self.label_formats)
        label1 = qw.QLabel("转")
        label1.setAlignment(qc.Qt.AlignmentFlag.AlignCenter)
        self.right_cbox = qw.QComboBox()
        self.right_cbox.addItems(self.label_formats)
        annotation_select_h_layout.addWidget(self.left_cbox)
        annotation_select_h_layout.addWidget(label1)
        annotation_select_h_layout.addWidget(self.right_cbox)
        annotation_select_h_layout.setStretch(0, 1)
        annotation_select_h_layout.setStretch(1, 0)
        annotation_select_h_layout.setStretch(2, 1)

        """选择图像文件夹"""
        src_img_h_layout = qw.QHBoxLayout()
        label2 = qw.QLabel("图像文件夹：")
        label2.setAlignment(qc.Qt.AlignmentFlag.AlignRight | qc.Qt.AlignmentFlag.AlignVCenter)
        self.src_img_line_edit = qw.QLineEdit()
        self.src_img_dir_btn = qw.QPushButton("浏览")
        src_img_h_layout.addWidget(label2)
        src_img_h_layout.addWidget(self.src_img_line_edit)
        src_img_h_layout.addWidget(self.src_img_dir_btn)

        """选择源标注文件夹"""
        src_label_h_layout = qw.QHBoxLayout()
        label3 = qw.QLabel("源标注文件夹：")
        label3.setAlignment(qc.Qt.AlignmentFlag.AlignRight | qc.Qt.AlignmentFlag.AlignVCenter)
        self.src_label_line_edit = qw.QLineEdit()
        self.src_label_dir_btn = qw.QPushButton("浏览")
        src_label_h_layout.addWidget(label3)
        src_label_h_layout.addWidget(self.src_label_line_edit)
        src_label_h_layout.addWidget(self.src_label_dir_btn)

        """选择目标标注文件夹"""
        dst_label_h_layout = qw.QHBoxLayout()
        label3 = qw.QLabel("目标标注文件夹：")
        label3.setAlignment(qc.Qt.AlignmentFlag.AlignRight | qc.Qt.AlignmentFlag.AlignVCenter)
        self.dst_label_line_edit = qw.QLineEdit()
        self.dst_label_dir_btn = qw.QPushButton("浏览")
        dst_label_h_layout.addWidget(label3)
        dst_label_h_layout.addWidget(self.dst_label_line_edit)
        dst_label_h_layout.addWidget(self.dst_label_dir_btn)

        """筛除类别"""
        deleted_label_h_layout = qw.QHBoxLayout()
        self.deleted_cbox = qw.QCheckBox("筛除类别（正则表达式）：")
        self.deleted_cbox.setChecked(True)
        self.deleted_label_line_edit = qw.QLineEdit()
        deleted_label_h_layout.addWidget(self.deleted_cbox)
        deleted_label_h_layout.addWidget(self.deleted_label_line_edit)

        """筛选类别"""
        selected_label_h_layout = qw.QHBoxLayout()
        self.selected_cbox = qw.QCheckBox("筛选类别（正则表达式）：")
        self.selected_cbox.setChecked(False)
        self.selected_label_line_edit = qw.QLineEdit()
        self.selected_label_line_edit.setEnabled(False)  # 禁用
        selected_label_h_layout.addWidget(self.selected_cbox)
        selected_label_h_layout.addWidget(self.selected_label_line_edit)

        """重命名类别"""
        rename_label_h_layout = qw.QHBoxLayout()
        self.table_widget = qw.QTableWidget()
        self.table_widget.setColumnCount(2)
        self.table_widget.setRowCount(500)  # 生成足够的行数
        # 对所有表格初始化
        row_item = ["", ""]
        for i in range(1000):
            for j in range(len(row_item)):
                item = qw.QTableWidgetItem(row_item[j])
                self.table_widget.setItem(i, j, item)
        self.table_widget.setHorizontalHeaderLabels(["类别（正则表达式）", "重命名"])
        self.table_widget.horizontalHeader().setSectionResizeMode(qw.QHeaderView.Stretch)
        self.table_widget.setSelectionBehavior(qw.QAbstractItemView.SelectRows)  # 选中整行
        self.table_widget.verticalHeader().setVisible(False)  # 隐藏行标题
        font = self.table_widget.horizontalHeader().font()  # 表格字体加粗
        font.setBold(True)
        self.table_widget.horizontalHeader().setFont(font)
        rename_label_h_layout.addWidget(self.table_widget)

        """按钮布局"""
        btn_layout = qw.QHBoxLayout()
        h_spacer = qw.QSpacerItem(0, 0, qw.QSizePolicy.Expanding, qw.QSizePolicy.Fixed)
        self.option_btn = qw.QPushButton("高级选项")
        self.ok_btn = qw.QPushButton("确定")
        btn_layout.addItem(h_spacer)
        # btn_layout.addWidget(self.option_btn)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addItem(h_spacer)

        main_v_layout.addLayout(annotation_select_h_layout)
        main_v_layout.addLayout(src_img_h_layout)
        main_v_layout.addLayout(src_label_h_layout)
        main_v_layout.addLayout(dst_label_h_layout)
        main_v_layout.addLayout(deleted_label_h_layout)
        main_v_layout.addLayout(selected_label_h_layout)
        main_v_layout.addLayout(rename_label_h_layout)
        main_v_layout.addLayout(btn_layout)
        main_v_layout.setAlignment(qc.Qt.AlignmentFlag.AlignVCenter)
        self.setLayout(main_v_layout)

        """取消焦点"""
        self.src_img_dir_btn.setFocusPolicy(qc.Qt.NoFocus)
        self.src_label_dir_btn.setFocusPolicy(qc.Qt.NoFocus)
        self.dst_label_dir_btn.setFocusPolicy(qc.Qt.NoFocus)
        self.ok_btn.setFocusPolicy(qc.Qt.NoFocus)
        self.option_btn.setFocusPolicy(qc.Qt.NoFocus)

        # 绑定事件
        self.src_img_dir_btn.clicked.connect(self.set_src_img_dir)
        self.src_label_dir_btn.clicked.connect(self.set_src_label_dir)
        self.dst_label_dir_btn.clicked.connect(self.set_dst_label_dir)
        self.ok_btn.clicked.connect(self.on_ok)
        self.deleted_cbox.clicked.connect(self.set_deleted_cbox_checked)
        self.selected_cbox.clicked.connect(self.set_selected_cbox_checked)

        """配置"""
        self.settings = Settings()

    def set_deleted_cbox_checked(self):
        """
        设置筛除combox选择
        :return:
        """

        if self.deleted_cbox.isChecked():
            self.selected_cbox.setChecked(False)
            self.selected_label_line_edit.setEnabled(False)
            self.deleted_label_line_edit.setEnabled(True)
        elif not self.deleted_cbox.isChecked():
            self.selected_cbox.setChecked(True)
            self.selected_label_line_edit.setEnabled(True)
            self.deleted_label_line_edit.setEnabled(False)

    def set_selected_cbox_checked(self):
        """
        设置筛选combox选择
        :return:
        """

        if self.selected_cbox.isChecked():
            self.deleted_cbox.setChecked(False)
            self.deleted_label_line_edit.setEnabled(False)
            self.selected_label_line_edit.setEnabled(True)
        elif not self.selected_cbox.isChecked():
            self.deleted_cbox.setChecked(True)
            self.deleted_label_line_edit.setEnabled(True)
            self.selected_label_line_edit.setEnabled(False)

    def set_src_img_dir(self):
        """
        设置图片文件夹路径
        :return:
        """

        """导入配置"""
        src_img_dir_path = self.settings["src_img"]  # 图片文件夹
        if src_img_dir_path is None:
            src_img_dir_path = "./"

        """选取文件夹"""
        dir_path = qw.QFileDialog.getExistingDirectory(self, "选取文件夹", src_img_dir_path)
        self.src_img_line_edit.setText(dir_path)
        self.settings["src_img"] = dir_path

    def set_src_label_dir(self):
        """
        设置源标注文件夹路径
        :return:
        """

        """导入配置"""
        src_label_dir_path = self.settings["src_label"]  # 图片文件夹
        if src_label_dir_path is None:
            src_label_dir_path = "./"

        """选取文件夹"""
        dir_path = qw.QFileDialog.getExistingDirectory(self, "选取文件夹", src_label_dir_path)
        self.src_label_line_edit.setText(dir_path)
        self.settings["src_label"] = dir_path

    def set_dst_label_dir(self):
        """
        设置目标标注文件夹路径
        :return:
        """

        """导入配置"""
        dst_label_dir_path = self.settings["dst_label"]  # 图片文件夹
        if dst_label_dir_path is None:
            dst_label_dir_path = "./"

        """选取文件夹"""
        dir_path = qw.QFileDialog.getExistingDirectory(self, "选取文件夹", dst_label_dir_path)
        self.dst_label_line_edit.setText(dir_path)
        self.settings["dst_label"] = dir_path

    def on_ok(self):
        """
        转换标注文件格式
        :return:
        """

        src_img_dir = self.src_img_line_edit.text()  # 图片文件夹
        src_label_dir = self.src_label_line_edit.text()  # 源标注文件夹
        dst_label_dir = self.dst_label_line_edit.text()  # 目标标注文件夹
        deleted_regex = self.deleted_label_line_edit.text()  # 筛除类别
        selected_regex = self.selected_label_line_edit.text()  # 筛选类别
        deleted_state = self.deleted_cbox.isChecked()  # 筛除combox是否选中
        selected_state = self.selected_cbox.isChecked()  # 筛选combox是否选中

        dir_exists1 = self.check_path("图像文件夹", src_img_dir)
        dir_exists2 = self.check_path("源标注文件夹", src_label_dir)
        dir_exists3 = self.check_path("目标标注文件夹", dst_label_dir)

        # 如果文件夹路径都正确，则转换格式
        if dir_exists1 and dir_exists2 and dir_exists3:
            left_selected_index = self.left_cbox.currentIndex()  # 左边选择
            right_selected_index = self.right_cbox.currentIndex()  # 右边选择

            rename_label_regexes = self.get_table_content()  # 获得table内容（重命名正则）

            """函数前缀"""
            left_method_prefix = self.method_prefix[left_selected_index]
            right_method_prefix = self.method_prefix[right_selected_index]
            left_method = left_method_prefix + "_to_middle_json"
            right_method = "middle_json_to_" + right_method_prefix
            eval(left_method)(src_img_dir, src_label_dir, (deleted_regex, deleted_state),
                              (selected_regex, selected_state), rename_label_regexes)
            eval(right_method)(dst_label_dir)
            self.show_message("标注文件转换成功！", icon=qw.QMessageBox.Icon.NoIcon)

    def get_table_content(self):
        data = []
        for i in range(500):
            col1 = self.table_widget.item(i, 0).text()
            col2 = self.table_widget.item(i, 1).text()
            row_data = [col1, col2]
            if row_data != ["", ""]:
                data.append(row_data)
        return data

    def show_message(self, text, title="提示", icon=qw.QMessageBox.Icon.Critical, flag=qw.QMessageBox.Ok):
        """
        显示提示
        :param text: 提示的信息
        :return:
        """
        msg = qw.QMessageBox()
        msg.setWindowTitle(title)
        msg.setIcon(icon)
        msg.setInformativeText(text)
        msg.setStandardButtons(flag)
        result = msg.exec()  # 显示窗口（运行结果）
        return result

    def check_path(self, propery, path):
        """
        检查路径是否正确
        :param propery:哪种路径
        :param path:路径
        :return:
        """

        if not os.path.exists(path):
            self.show_message(propery + "路径不存在！")
            return False
        return True


# if __name__ == '__main__':
app = qw.QApplication(sys.argv)
w = MainWindow()
w.show()
sys.exit(app.exec_())
