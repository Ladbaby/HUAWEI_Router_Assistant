# coding:utf-8
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPixmap, QPainter, QColor, QBrush, QPainterPath
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout

from qfluentwidgets import ScrollArea, isDarkTheme, FluentIcon, SingleDirectionScrollArea
from ..common.style_sheet import StyleSheet
from ..components.monitoring_status_card import MonitoringStatusCard
from ..components.battery_history_card import BatteryHistoryCard
from ..components.backdrop import Backdrop

class BannerCardView(SingleDirectionScrollArea):

    def __init__(self, parent=None):
        super().__init__(parent, Qt.Horizontal)
        self.view = QWidget(self)
        self.vBoxLayout = QVBoxLayout(self.view)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(12)
        self.vBoxLayout.setAlignment(Qt.AlignTop)

        self.setWidget(self.view)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.view.setObjectName('view')
        StyleSheet.BATTERY_HISTORY_CARD.apply(self)

    def updateMonitoringStatus(self, monitoring_status_dic):
        self.monitoring_status_card.updateMonitoringStatus(monitoring_status_dic)

    def addMonitoringStatusCard(self, monitoring_status_dic):
        self.monitoring_status_card = MonitoringStatusCard(monitoring_status_dic)
        self.vBoxLayout.addWidget(self.monitoring_status_card, 0, Qt.AlignTop)
        self.setFixedHeight(self.monitoring_status_card.height() + 50)

    def addBatteryHistoryCard(self, battery_history_dic):
        self.battery_history_card = BatteryHistoryCard(battery_history_dic)
        self.vBoxLayout.addWidget(self.battery_history_card, 0, Qt.AlignTop)
        self.setFixedHeight(self.battery_history_card.height() + 50)

class BannerWidget(QWidget):
    """ Banner widget """

    def __init__(self, router, parent=None):
        super().__init__(parent=parent)
        self.router = router

        self.vBoxLayout = QVBoxLayout(self)
        self.galleryLabel = QLabel('Battery History', self)
        self.banner = QPixmap(':/gallery/images/header1.png')
        self.bannerCardView = BannerCardView(self)

        self.bannerCardView.setObjectName('bannerWidget')

        self.galleryLabel.setObjectName('galleryLabel')

        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(0, 20, 0, 0)
        self.vBoxLayout.addWidget(self.galleryLabel)
        self.vBoxLayout.addWidget(self.bannerCardView, 1, Qt.AlignTop)
        self.vBoxLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        self.bannerCardView.addBatteryHistoryCard(
            self.router.get_battery_history_dic()
        )
        self.bannerCardView.setObjectName("bannerCardView")

    def update_monitoring_status(self):
        self.bannerCardView.updateMonitoringStatus(self.router.get_monitoring_status_dic())

class BatteryHistoryInterface(ScrollArea):

    def __init__(self, router, parent=None):
        super().__init__(parent=parent)
        self.router = router
        self.banner = BannerWidget(router, self)
        self.view = Backdrop(self)
        self.vBoxLayout = QVBoxLayout(self.view)

        self.__initWidget()

    def update_monitoring_status(self):
        self.banner.update_monitoring_status()

    def __initWidget(self):
        self.view.setObjectName('interface')
        self.setObjectName('batteryHistoryInterface')
        StyleSheet.BATTERY_HISTORY_CARD.apply(self)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidget(self.view)
        self.setWidgetResizable(True)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 36)
        self.vBoxLayout.setSpacing(40)
        self.vBoxLayout.addWidget(self.banner)
        self.vBoxLayout.setAlignment(Qt.AlignTop)

