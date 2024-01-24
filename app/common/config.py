# coding:utf-8
from enum import Enum

from PyQt5.QtCore import QLocale
from qfluentwidgets import (qconfig, QConfig, ConfigItem, OptionsConfigItem, BoolValidator,
                            OptionsValidator, RangeConfigItem, RangeValidator,
                            FolderListValidator, EnumSerializer, FolderValidator, ConfigSerializer, __version__)


class Language(Enum):
    """ Language enumeration """

    CHINESE_SIMPLIFIED = QLocale(QLocale.Chinese, QLocale.China)
    CHINESE_TRADITIONAL = QLocale(QLocale.Chinese, QLocale.HongKong)
    ENGLISH = QLocale(QLocale.English)
    AUTO = QLocale()

class DeviceName(Enum):
    WIFI = "HUAWEI Mobile WiFi"
    ROUTER = "HUAWEI Mobile Router"


class LanguageSerializer(ConfigSerializer):
    """ Language serializer """

    def serialize(self, language):
        return language.value.name() if language != Language.AUTO else "Auto"

    def deserialize(self, value: str):
        return Language(QLocale(value)) if value != "Auto" else Language.AUTO


class Config(QConfig):
    """ Config of application """

    # folders
    # musicFolders = ConfigItem(
    #     "Folders", "LocalMusic", [], FolderListValidator())
    # downloadFolder = ConfigItem(
    #     "Folders", "Download", "app/download", FolderValidator())

    # main window
    dpiScale = OptionsConfigItem(
        "MainWindow", "DpiScale", "Auto", OptionsValidator([1, 1.25, 1.5, 1.75, 2, "Auto"]), restart=True)
    language = OptionsConfigItem(
        "MainWindow", "Language", Language.AUTO, OptionsValidator(Language), LanguageSerializer(), restart=True)

    # Material
    blurRadius  = RangeConfigItem("Material", "AcrylicBlurRadius", 15, RangeValidator(0, 40))

    # software update
    checkUpdateAtStartUp = ConfigItem("Update", "CheckUpdateAtStartUp", True, BoolValidator())

    batteryUpperBoundNotification = ConfigItem("Battery", "batteryUpperBoundNotification", True, BoolValidator())

    batteryUpperBoundThreshold = RangeConfigItem("Battery", "batteryUpperBoundThreshold", 80, RangeValidator(0, 100))

    batteryLowerBoundNotification = ConfigItem("Battery", "batteryLowerBoundNotification", True, BoolValidator())

    batteryLowerBoundThreshold = RangeConfigItem("Battery", "batteryLowerBoundThreshold", 30, RangeValidator(0, 100))

    deviceName = OptionsConfigItem("Device", "deviceName", DeviceName.WIFI, OptionsValidator(DeviceName), EnumSerializer(DeviceName))
    # themeMode = OptionsConfigItem(
    #     "QFluentWidgets", "ThemeMode", Theme.AUTO, OptionsValidator(Theme), EnumSerializer(Theme))

    enableLogging = ConfigItem("Developer", "enableLogging", False, BoolValidator())

YEAR = 2023
AUTHOR = "ladbaby"
VERSION = __version__
HELP_URL = "https://pyqt-fluent-widgets.readthedocs.io/zh_CN/latest"
REPO_URL = "https://github.com/zhiyiYo/PyQt-Fluent-Widgets"
EXAMPLE_URL = "https://github.com/zhiyiYo/PyQt-Fluent-Widgets/tree/master/examples"
FEEDBACK_URL = "https://github.com/zhiyiYo/PyQt-Fluent-Widgets/issues"
RELEASE_URL = "https://github.com/zhiyiYo/PyQt-Fluent-Widgets/releases/latest"
SUPPORT_URL = "https://afdian.net/a/zhiyiYo"


cfg = Config()
qconfig.load('app/config/config.json', cfg)