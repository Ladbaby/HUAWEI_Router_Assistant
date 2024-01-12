# coding: utf-8
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtWidgets import QApplication

from qfluentwidgets import NavigationAvatarWidget, NavigationItemPosition, MessageBox, FluentWindow
from qfluentwidgets import FluentIcon as FIF

from .gallery_interface import GalleryInterface
from .home_interface import HomeInterface
from .monitoring_status_interface import MonitoringStatusInterface
from .setting_interface import SettingInterface
from .battery_history_interface import BatteryHistoryInterface
from ..common.config import SUPPORT_URL
from ..common.icon import Icon
from ..common.signal_bus import signalBus
from ..common.translator import Translator
from ..common import resource


class MainWindow(FluentWindow):

    def __init__(self, router):
        super().__init__()

        self.router = router

        # create sub interface
        self.homeInterface = HomeInterface(router, self)
        self.monitoringStatusInterface = MonitoringStatusInterface(router, self)
        self.batteryHistoryInterface = BatteryHistoryInterface(router, self)
        self.settingInterface = SettingInterface(self)

        # initialize layout
        self.initLayout()

        # add items to navigation interface
        self.initNavigation()

        self.initWindow()
        self.homeInterface.banner.setFixedHeight(self.height())

    def update_monitoring_status(self):
        self.homeInterface.update_monitoring_status()
        self.monitoringStatusInterface.update_monitoring_status()
        self.batteryHistoryInterface.update_monitoring_status()

    def update_traffic_statistics(self):
        self.homeInterface.update_traffic_statistics()

    def update_month_statistics(self):
        self.homeInterface.update_month_statistics()

    def initLayout(self):
        signalBus.switchToSampleCard.connect(self.switchToSample)
        signalBus.supportSignal.connect(self.onSupport)

    def initNavigation(self):
        # add navigation items
        t = Translator()
        self.addSubInterface(self.homeInterface, FIF.HOME, self.tr('Home'))
        self.addSubInterface(self.monitoringStatusInterface, Icon.GRID, self.tr('Monitoring Status'))
        self.addSubInterface(self.batteryHistoryInterface, Icon.GRID, self.tr('Battery History'))
        self.navigationInterface.addSeparator()

        # add custom widget to bottom
        self.navigationInterface.addWidget(
            routeKey='avatar',
            widget=NavigationAvatarWidget('Ladbaby', ':/gallery/images/grey.jpg'),
            onClick=self.onSupport,
            position=NavigationItemPosition.BOTTOM
        )
        self.addSubInterface(
            self.settingInterface, FIF.SETTING, self.tr('Settings'), NavigationItemPosition.BOTTOM)

    def initWindow(self):
        self.resize(960, 780)
        self.setMinimumWidth(760)
        self.setWindowIcon(QIcon(':/gallery/images/logo.png'))
        self.setWindowTitle('HUAWEI Router Assistant')

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)

    def onSupport(self):
        w = MessageBox(
            '支持作者🥰',
            '个人开发不易，如果这个项目帮助到了您，可以考虑请作者喝一瓶快乐水🥤。您的支持就是作者开发和维护项目的动力🚀',
            self
        )
        w.yesButton.setText('来啦老弟')
        w.cancelButton.setText('下次一定')
        if w.exec():
            QDesktopServices.openUrl(QUrl(SUPPORT_URL))

    def switchToSample(self, routeKey, index):
        """ switch to sample """
        interfaces = self.findChildren(GalleryInterface)
        for w in interfaces:
            if w.objectName() == routeKey:
                self.stackedWidget.setCurrentWidget(w, False)
                w.scrollToCard(index)
