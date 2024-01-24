# coding:utf-8
from qfluentwidgets import (SettingCardGroup, SwitchSettingCard,
                            OptionsSettingCard, PrimaryPushSettingCard, ScrollArea,
                            ComboBoxSettingCard, ExpandLayout, CustomColorSettingCard,
                            setTheme, setThemeColor, RangeSettingCard)
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtCore import Qt, pyqtSignal, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QWidget, QLabel

from ..common.config import cfg, FEEDBACK_URL, REPO_URL, AUTHOR, VERSION, YEAR
from ..common.style_sheet import StyleSheet


class SettingInterface(ScrollArea):
    """ Setting interface """

    acrylicEnableChanged = pyqtSignal(bool)
    minimizeToTrayChanged = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        # setting label
        self.settingLabel = QLabel(self.tr("Settings"), self)

        self.batteryGroup = SettingCardGroup(
            self.tr("Battery"), self.scrollWidget)
        self.batteryUpperBoundNotificationSwitchCard = SwitchSettingCard(
            FIF.INFO,
            self.tr('Battery notification when charging over threshold'),
            self.tr('Recommended for longer battery life'),
            configItem=cfg.batteryUpperBoundNotification,
            parent=self.batteryGroup
        )
        self.batteryUpperBoundThresholdCard = RangeSettingCard(
            cfg.batteryUpperBoundThreshold,
            FIF.CARE_UP_SOLID,
            self.tr("Battery level's upper bound"),
            self.tr("Battery level's upper bound"),
            self.batteryGroup
        )
        self.batteryLowerBoundNotificationSwitchCard = SwitchSettingCard(
            FIF.INFO,
            self.tr('Battery notification when below threshold'),
            self.tr('Prevent your device from shutting down unexpectedly'),
            configItem=cfg.batteryLowerBoundNotification,
            parent=self.batteryGroup
        )
        self.batteryLowerBoundThresholdCard = RangeSettingCard(
            cfg.batteryLowerBoundThreshold,
            FIF.CARE_DOWN_SOLID,
            self.tr("Battery level's lower bound"),
            self.tr("Battery level's lower bound"),
            self.batteryGroup
        )

        self.deviceGroup = SettingCardGroup(
            self.tr("Device"), self.scrollWidget)
        self.deviceNameCard = OptionsSettingCard(
            cfg.deviceName,
            FIF.EDIT,
            self.tr('Device Name'),
            self.tr("Restart to take effect"),
            texts=[
                self.tr('HUAWEI Mobile WiFi'), self.tr('HUAWEI Mobile Router')
            ],
            parent=self.deviceGroup
        )

        # personalization
        self.personalGroup = SettingCardGroup(
            self.tr('Personalization'), self.scrollWidget)
        self.themeCard = OptionsSettingCard(
            cfg.themeMode,
            FIF.BRUSH,
            self.tr('Application theme'),
            self.tr("Change the appearance of your application"),
            texts=[
                self.tr('Light'), self.tr('Dark'),
                self.tr('Use system setting')
            ],
            parent=self.personalGroup
        )
        self.themeColorCard = CustomColorSettingCard(
            cfg.themeColor,
            FIF.PALETTE,
            self.tr('Theme color'),
            self.tr('Change the theme color of you application'),
            self.personalGroup
        )
        self.zoomCard = OptionsSettingCard(
            cfg.dpiScale,
            FIF.ZOOM,
            self.tr("Interface zoom"),
            self.tr("Change the size of widgets and fonts"),
            texts=[
                "100%", "125%", "150%", "175%", "200%",
                self.tr("Use system setting")
            ],
            parent=self.personalGroup
        )
        self.languageCard = ComboBoxSettingCard(
            cfg.language,
            FIF.LANGUAGE,
            self.tr('Language'),
            self.tr('Set your preferred language for UI'),
            texts=['简体中文', '繁體中文', 'English', self.tr('Use system setting')],
            parent=self.personalGroup
        )

        # material
        self.materialGroup = SettingCardGroup(
            self.tr('Material'), self.scrollWidget)
        self.blurRadiusCard = RangeSettingCard(
            cfg.blurRadius,
            FIF.ALBUM,
            self.tr('Acrylic blur radius'),
            self.tr('The greater the radius, the more blurred the image'),
            self.materialGroup
        )

        # developer
        self.developerGroup = SettingCardGroup(self.tr('Developer'), self.scrollWidget)
        self.enableLoggingCard = SwitchSettingCard(
            FIF.CODE,
            self.tr('Enable logging'),
            self.tr('log debug information'),
            configItem=cfg.enableLogging,
            parent=self.developerGroup
        )

        # application
        self.aboutGroup = SettingCardGroup(self.tr('About'), self.scrollWidget)
        self.feedbackCard = PrimaryPushSettingCard(
            self.tr('Provide feedback'),
            FIF.FEEDBACK,
            self.tr('Provide feedback'),
            self.tr('Help us improve the program by providing feedback'),
            self.aboutGroup
        )
        self.aboutCard = PrimaryPushSettingCard(
            self.tr('Repository'),
            FIF.INFO,
            self.tr('About'),
            '© ' + self.tr('Copyright') + f" {YEAR}, {AUTHOR}. " +
            self.tr('Version') + " " + VERSION,
            self.aboutGroup
        )

        self.__initWidget()

    def __initWidget(self):
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 80, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setObjectName('settingInterface')

        # initialize style sheet
        self.scrollWidget.setObjectName('scrollWidget')
        self.settingLabel.setObjectName('settingLabel')
        StyleSheet.SETTING_INTERFACE.apply(self)

        # initialize layout
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        self.settingLabel.move(36, 30)

        self.batteryGroup.addSettingCard(self.batteryUpperBoundNotificationSwitchCard)
        self.batteryGroup.addSettingCard(self.batteryUpperBoundThresholdCard)
        self.batteryGroup.addSettingCard(self.batteryLowerBoundNotificationSwitchCard)
        self.batteryGroup.addSettingCard(self.batteryLowerBoundThresholdCard)

        self.deviceGroup.addSettingCard(self.deviceNameCard)

        self.personalGroup.addSettingCard(self.themeCard)
        self.personalGroup.addSettingCard(self.themeColorCard)
        self.personalGroup.addSettingCard(self.zoomCard)
        self.personalGroup.addSettingCard(self.languageCard)

        self.materialGroup.addSettingCard(self.blurRadiusCard)

        self.aboutGroup.addSettingCard(self.feedbackCard)
        self.aboutGroup.addSettingCard(self.aboutCard)

        self.developerGroup.addSettingCard(self.enableLoggingCard)

        # add setting card group to layout
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(36, 10, 36, 0)
        self.expandLayout.addWidget(self.batteryGroup)
        self.expandLayout.addWidget(self.deviceGroup)
        self.expandLayout.addWidget(self.personalGroup)
        self.expandLayout.addWidget(self.materialGroup)
        self.expandLayout.addWidget(self.developerGroup)
        self.expandLayout.addWidget(self.aboutGroup)

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        cfg.themeChanged.connect(setTheme)

        # personalization
        self.themeColorCard.colorChanged.connect(setThemeColor)

        # about
        self.aboutCard.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(REPO_URL)))
        self.feedbackCard.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(FEEDBACK_URL)))
