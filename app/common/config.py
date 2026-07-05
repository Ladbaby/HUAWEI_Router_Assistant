# coding:utf-8
from enum import Enum

import datetime
import pathlib
import tomllib

from PyQt5.QtCore import QLocale
from qfluentwidgets import (qconfig, QConfig, ConfigItem, OptionsConfigItem, BoolValidator,
                            OptionsValidator, RangeConfigItem, RangeValidator,
                            EnumSerializer, ConfigSerializer)


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

    # main window
    dpiScale = OptionsConfigItem(
        "MainWindow", "DpiScale", "Auto", OptionsValidator([1, 1.25, 1.5, 1.75, 2, "Auto"]), restart=True)
    language = OptionsConfigItem(
        "MainWindow", "Language", Language.AUTO, OptionsValidator(Language), LanguageSerializer(), restart=True)

    # Material
    blurRadius  = RangeConfigItem("Material", "AcrylicBlurRadius", 15, RangeValidator(0, 40))

    batteryUpperBoundNotification = ConfigItem("Battery", "batteryUpperBoundNotification", True, BoolValidator())

    batteryUpperBoundThreshold = RangeConfigItem("Battery", "batteryUpperBoundThreshold", 80, RangeValidator(0, 100))

    batteryLowerBoundNotification = ConfigItem("Battery", "batteryLowerBoundNotification", True, BoolValidator())

    batteryLowerBoundThreshold = RangeConfigItem("Battery", "batteryLowerBoundThreshold", 30, RangeValidator(0, 100))

    deviceName = OptionsConfigItem("Device", "deviceName", DeviceName.WIFI, OptionsValidator(DeviceName), EnumSerializer(DeviceName))
    # themeMode = OptionsConfigItem(
    #     "QFluentWidgets", "ThemeMode", Theme.AUTO, OptionsValidator(Theme), EnumSerializer(Theme))

    enableLogging = ConfigItem("Developer", "enableLogging", False, BoolValidator())

YEAR = datetime.date.today().year
AUTHOR = "ladbaby"

def _read_version() -> str:
    """Read the application version from pyproject.toml."""
    pyproject = pathlib.Path(__file__).parent.parent.parent / "pyproject.toml"
    with open(pyproject, "rb") as f:
        data = tomllib.load(f)
    return data["project"]["version"]

VERSION = _read_version()
REPO_URL = "https://github.com/Ladbaby/HUAWEI_Router_Assistant"
FEEDBACK_URL = "https://github.com/Ladbaby/HUAWEI_Router_Assistant/issues"
RELEASE_URL = "https://github.com/Ladbaby/HUAWEI_Router_Assistant/releases/latest"


cfg = Config()
qconfig.load('app/config/config.json', cfg)