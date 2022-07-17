"""
配置
"""

import PyQt5.QtCore as qc


class Settings(object):
    """包装QSettings类"""

    def __init__(self):
        self.data = qc.QSettings("label_transform_config.ini", "qc.QSettings.IniFormat")

    def __setitem__(self, key, value):
        self.data.setValue(key, value)

    def __getitem__(self, key):
        return self.data.value(key)


if __name__ == "__main__":
    a = Settings()
    print(a["2"])
