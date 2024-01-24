# coding:utf-8
from asyncio.log import logger
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPixmap, QPainter, QImage
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

from qfluentwidgets import ScrollArea, SingleDirectionScrollArea, FlowLayout, PixmapLabel
from ..common.config import cfg
from ..common.style_sheet import StyleSheet
from ..components.battery_card import BatteryCard
from ..components.traffic_statistics_card import TrafficStatisticsCard
from ..components.month_statistics_card import MonthStatisticsCard
from ..components.backdrop import Backdrop

class BannerCardView(SingleDirectionScrollArea):

    def __init__(self, parent=None):
        super().__init__(parent, Qt.Horizontal)
        self.view = QWidget(self)
        self.flowLayout = FlowLayout(self.view)

        self.flowLayout.setContentsMargins(36, 12, 0, 0)
        self.flowLayout.setHorizontalSpacing(12)
        self.flowLayout.setVerticalSpacing(12)

        self.setWidget(self.view)
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.view.setObjectName('view')
        StyleSheet.BATTERY_CARD.apply(self)

    def addBatteryCard(self, ring_value, title, content):
        """ add link card """
        self.battery_card = BatteryCard(ring_value, title, content, self.view)
        self.flowLayout.addWidget(self.battery_card)

    def updateBatteryCard(self, ring_value, battery_status_str):
        self.battery_card.update_ring_value(ring_value, battery_status_str)

    def addTrafficStatisticsCard(self, traffic_statistics_dic):
        self.traffic_statistics_card = TrafficStatisticsCard(traffic_statistics_dic)
        self.flowLayout.addWidget(self.traffic_statistics_card)

    def updateTrafficStatisticsCard(self, traffic_statistics_dic):
        self.traffic_statistics_card.update_traffic_statistics(traffic_statistics_dic)

    def addMonthStatisticsCard(self, month_statistics_dic):
        self.month_statistics_card = MonthStatisticsCard(month_statistics_dic)
        self.flowLayout.addWidget(self.month_statistics_card)

    def updateMonthStatisticsCard(self, month_statistics_dic):
        self.month_statistics_card.update_month_statistics(month_statistics_dic)

class BannerWidget(QWidget):
    """ Banner widget """

    def __init__(self, router, parent=None):
        super().__init__(parent=parent)
        self.router = router
        self.setFixedHeight(600)

        self.vBoxLayout = QVBoxLayout(self)
        deviceName = cfg.get(cfg.deviceName).value
        self.galleryLabel = QLabel(deviceName, self)
        self.bannerCardView = BannerCardView(self)

        dpi = 300  # Set your desired DPI value
        if deviceName == 'HUAWEI Mobile WiFi':
            self.model_image = QImage(':/gallery/images/mobile_wifi3_pro_cover.png')
        elif deviceName == "HUAWEI Mobile Router":
            self.model_image = QImage(':/gallery/images/mobile_router.png')
        else:
            logger.error(f"Unknown device name: {deviceName}")
            exit(1)
        # Scale the image
        scaled_image = self.model_image.scaled(
            120, 120, transformMode=Qt.SmoothTransformation, aspectRatioMode=Qt.KeepAspectRatioByExpanding
        )
        # Create a new QImage with higher DPI
        new_image = QImage(scaled_image.size(), QImage.Format_ARGB32)
        # new_image.setDevicePixelRatio(2.0)
        new_image.fill(Qt.transparent)
        new_image.setDotsPerMeterX(int(dpi / 0.0254))
        new_image.setDotsPerMeterY(int(dpi / 0.0254))

        # Draw the scaled image onto the new image
        painter = QPainter(new_image)
        # painter.setRenderHint(QPainter.Antialiasing, True)
        painter.drawImage(QRectF(0, 0, scaled_image.width(), scaled_image.height()), scaled_image)
        painter.end()

        # Use the new image
        self.model_image = new_image
        self.model_pixmap = QPixmap.fromImage(self.model_image)
        self.model_pixmap = self.model_pixmap.scaled(120, 120, transformMode=Qt.SmoothTransformation, aspectRatioMode=Qt.KeepAspectRatioByExpanding)

        self.model_label = PixmapLabel(self)
        self.model_label.setPixmap(self.model_pixmap)

        self.galleryLabel.setObjectName('galleryLabel')

        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.addWidget(self.galleryLabel)
        self.vBoxLayout.addSpacing(30)
        self.vBoxLayout.addWidget(self.model_label, 0, Qt.AlignCenter)
        self.vBoxLayout.addWidget(self.bannerCardView, 0, Qt.AlignTop)
        self.vBoxLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # No.0
        self.bannerCardView.addBatteryCard(
            self.router.get_battery_percent(),
            self.tr('Battery'),
            self.tr(self.router.get_battery_status()),
        )

        self.bannerCardView.addTrafficStatisticsCard(
            self.router.get_traffic_statistics_dic()
        )

        self.bannerCardView.addMonthStatisticsCard(
            self.router.get_month_statistics_dic()
        )


    def update_monitoring_status(self):
        self.bannerCardView.updateBatteryCard(self.router.get_battery_percent(), self.router.get_battery_status())

    def update_traffic_statistics(self):
        self.bannerCardView.updateTrafficStatisticsCard(self.router.get_traffic_statistics_dic())

    def update_month_statistics(self):
        self.bannerCardView.updateMonthStatisticsCard(self.router.get_month_statistics_dic())

class HomeInterface(ScrollArea):
    """ Home interface """

    def __init__(self, router, parent=None):
        super().__init__(parent=parent)
        self.router = router
        self.banner = BannerWidget(router, self)
        self.view = Backdrop(self)
        self.vBoxLayout = QVBoxLayout(self.view)

        self.__initWidget()

    def update_monitoring_status(self):
        self.banner.update_monitoring_status()

    def update_traffic_statistics(self):
        self.banner.update_traffic_statistics()
    
    def update_month_statistics(self):
        self.banner.update_month_statistics()

    def __initWidget(self):
        self.view.setObjectName('view')
        self.setObjectName('homeInterface')
        StyleSheet.HOME_INTERFACE.apply(self)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidget(self.view)
        self.setWidgetResizable(True)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.addWidget(self.banner)
        self.vBoxLayout.setAlignment(Qt.AlignTop)
