# coding:utf-8
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPixmap, QPainter, QColor, QBrush, QPainterPath
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout

from qfluentwidgets import ScrollArea, isDarkTheme, FluentIcon, SingleDirectionScrollArea
from ..common.config import cfg, HELP_URL, REPO_URL, EXAMPLE_URL, FEEDBACK_URL
from ..common.icon import Icon, FluentIconBase
from ..components.link_card import LinkCardView
from ..components.sample_card import SampleCardView
from ..common.style_sheet import StyleSheet
from ..components.battery_card import BatteryCard
from ..components.monitoring_status_card import MonitoringStatusCard
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
        # self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.view.setObjectName('view')
        StyleSheet.MONITORING_STATUS_CARD.apply(self)

    def updateMonitoringStatus(self, monitoring_status_dic):
        self.monitoring_status_card.updateMonitoringStatus(monitoring_status_dic)

    def addMonitoringStatusCard(self, monitoring_status_dic):
        self.monitoring_status_card = MonitoringStatusCard(monitoring_status_dic)
        self.vBoxLayout.addWidget(self.monitoring_status_card, 0, Qt.AlignTop)
        # self.view.setFixedHeight(480)
        self.setFixedHeight(self.monitoring_status_card.height() + 50)
        # print("bannerView", self.view.size())
        # print("monitoring_status_card", self.monitoring_status_card.size())

class BannerWidget(QWidget):
    """ Banner widget """

    def __init__(self, router, parent=None):
        super().__init__(parent=parent)
        self.router = router
        # self.setFixedHeight(336)
        # self.setFixedHeight(600)

        self.vBoxLayout = QVBoxLayout(self)
        # self.vBoxLayout.setObjectName("vBoxLayout")
        self.galleryLabel = QLabel('Monitoring Status', self)
        self.banner = QPixmap(':/gallery/images/header1.png')
        self.bannerCardView = BannerCardView(self)

        self.bannerCardView.setObjectName('bannerWidget')
        self.setStyleSheet("#bannerWidget{background-color: red;}")

        self.galleryLabel.setObjectName('galleryLabel')

        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(0, 20, 0, 0)
        self.vBoxLayout.addWidget(self.galleryLabel)
        self.vBoxLayout.addWidget(self.bannerCardView, 1, Qt.AlignTop)
        self.vBoxLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        self.bannerCardView.addMonitoringStatusCard(
            self.router.get_monitoring_status_dic()
        )
        self.bannerCardView.setObjectName("bannerCardView")

        # self.setStyleSheet("#vBoxLayout{background: transparent;} ")

    def update_monitoring_status(self):
        self.bannerCardView.updateMonitoringStatus(self.router.get_monitoring_status_dic())



class MonitoringStatusInterface(ScrollArea):
    """ Home interface """

    def __init__(self, router, parent=None):
        super().__init__(parent=parent)
        self.router = router
        self.banner = BannerWidget(router, self)
        self.view = Backdrop(self)
        self.vBoxLayout = QVBoxLayout(self.view)
        # self.setMinimumHeight(1000)

        # print("bannerWidget", self.size())

        self.__initWidget()
        # print("interface", self.size())

    def update_monitoring_status(self):
        self.banner.update_monitoring_status()

    def __initWidget(self):
        self.view.setObjectName('interface')
        self.setObjectName('monitoringStatusInterface')
        # self.banner.setObjectName("bannerWidget")
        # StyleSheet.HOME_INTERFACE.apply(self)
        StyleSheet.MONITORING_STATUS_CARD.apply(self)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidget(self.view)
        self.setWidgetResizable(True)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 36)
        self.vBoxLayout.setSpacing(40)
        self.vBoxLayout.addWidget(self.banner)
        self.vBoxLayout.setAlignment(Qt.AlignTop)

