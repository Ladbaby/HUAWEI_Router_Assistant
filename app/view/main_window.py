# coding: utf-8
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtWidgets import QApplication

from qfluentwidgets import NavigationAvatarWidget, NavigationItemPosition, MessageBox, FluentWindow
from qfluentwidgets import FluentIcon as FIF

from .gallery_interface import GalleryInterface
from .home_interface import HomeInterface
from .monitoring_status_interface import MonitoringStatusInterface
from .basic_input_interface import BasicInputInterface
from .date_time_interface import DateTimeInterface
from .dialog_interface import DialogInterface
from .layout_interface import LayoutInterface
from .icon_interface import IconInterface
from .material_interface import MaterialInterface
from .menu_interface import MenuInterface
from .navigation_view_interface import NavigationViewInterface
from .scroll_interface import ScrollInterface
from .status_info_interface import StatusInfoInterface
from .setting_interface import SettingInterface
from .battery_history_interface import BatteryHistoryInterface
from .text_interface import TextInterface
from .view_interface import ViewInterface
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
        self.iconInterface = IconInterface(self)
        self.basicInputInterface = BasicInputInterface(self)
        self.dateTimeInterface = DateTimeInterface(self)
        self.dialogInterface = DialogInterface(self)
        self.layoutInterface = LayoutInterface(self)
        self.menuInterface = MenuInterface(self)
        self.materialInterface = MaterialInterface(self)
        self.navigationViewInterface = NavigationViewInterface(self)
        self.scrollInterface = ScrollInterface(self)
        self.statusInfoInterface = StatusInfoInterface(self)
        self.settingInterface = SettingInterface(self)
        # self.textInterface = TextInterface(self)
        # self.viewInterface = ViewInterface(self)

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
        self.addSubInterface(self.iconInterface, Icon.EMOJI_TAB_SYMBOLS, t.icons)
        self.navigationInterface.addSeparator()

        # pos = NavigationItemPosition.SCROLL
        # self.addSubInterface(self.basicInputInterface, FIF.CHECKBOX,t.basicInput, pos)
        # self.addSubInterface(self.dateTimeInterface, FIF.DATE_TIME, t.dateTime, pos)
        # self.addSubInterface(self.dialogInterface, FIF.MESSAGE, t.dialogs, pos)
        # self.addSubInterface(self.layoutInterface, FIF.LAYOUT, t.layout, pos)
        # self.addSubInterface(self.materialInterface, FIF.PALETTE, t.material, pos)
        # self.addSubInterface(self.menuInterface, Icon.MENU, t.menus, pos)
        # self.addSubInterface(self.navigationViewInterface, FIF.MENU, t.navigation, pos)
        # self.addSubInterface(self.scrollInterface, FIF.SCROLL, t.scroll, pos)
        # self.addSubInterface(self.statusInfoInterface, FIF.CHAT, t.statusInfo, pos)
        # self.addSubInterface(self.textInterface, Icon.TEXT, t.text, pos)
        # self.addSubInterface(self.viewInterface, Icon.GRID, t.view, pos)

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
