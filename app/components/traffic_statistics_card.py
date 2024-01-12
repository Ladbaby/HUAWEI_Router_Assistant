# coding:utf-8
from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtWidgets import QWidget, QFrame, QLabel, QVBoxLayout, QHBoxLayout, QTableWidgetItem, QStyleOptionViewItem, QHeaderView
from PyQt5.QtGui import QPalette

from qfluentwidgets import IconWidget, TableItemDelegate, isDarkTheme
from ..common.style_sheet import StyleSheet

class CustomTableItemDelegate(TableItemDelegate):
    """ Custom table item delegate """

    def initStyleOption(self, option: QStyleOptionViewItem, index: QModelIndex):
        super().initStyleOption(option, index)
        if index.column() != 1:
            return

        if isDarkTheme():
            option.palette.setColor(QPalette.Text, Qt.white)
            option.palette.setColor(QPalette.HighlightedText, Qt.white)
        else:
            option.palette.setColor(QPalette.Text, Qt.red)
            option.palette.setColor(QPalette.HighlightedText, Qt.red)

class TrafficStatisticsCard(QFrame):

    def __init__(self, traffic_statistics_dic):
        super().__init__()

        self.iconWidget = IconWidget(self)
        self.iconWidget.setIcon(":/gallery/images/icons/signal_" + str(traffic_statistics_dic["Signal Strength"]) + ".png")
        self.title_label = QLabel(traffic_statistics_dic["Network Type"], self)
        self.upload_label = QLabel("↑: " + traffic_statistics_dic["Current Upload Rate"], self)
        self.download_label = QLabel("↓: " + traffic_statistics_dic["Current Download Rate"], self)

        self.title_label.setObjectName('contentLabel')
        self.upload_label.setObjectName('titleLabel')
        self.download_label.setObjectName('titleLabel')

        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()

        self.setFixedSize(360, 120)
        self.iconWidget.setFixedSize(48, 48)
        # self.iconWidget.setFixedSize(64, 64)

        self.hBoxLayout.setSpacing(28)
        self.hBoxLayout.setContentsMargins(20, 0, 0, 0)
        self.vBoxLayout.setSpacing(2)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setAlignment(Qt.AlignVCenter)

        self.hBoxLayout.setAlignment(Qt.AlignVCenter)
        self.hBoxLayout.addWidget(self.iconWidget, 1, Qt.AlignCenter)
        self.hBoxLayout.addLayout(self.vBoxLayout, 2)
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.addWidget(self.title_label)
        self.vBoxLayout.addWidget(self.upload_label)
        self.vBoxLayout.addWidget(self.download_label)
        self.vBoxLayout.addStretch(1)

        # StyleSheet.TRAFFIC_STATISTICS_CARD.apply(self)

    def update_traffic_statistics(self, traffic_statistics_dic):
        self.title_label.setText(traffic_statistics_dic["Network Type"])
        self.upload_label.setText("↑: " + traffic_statistics_dic["Current Upload Rate"])
        self.download_label.setText("↓: " + traffic_statistics_dic["Current Download Rate"])
        self.iconWidget.setIcon(":/gallery/images/icons/signal_" + str(traffic_statistics_dic["Signal Strength"]) + ".png")

    


