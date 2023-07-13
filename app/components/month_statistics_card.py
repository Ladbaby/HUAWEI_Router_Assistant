# coding:utf-8
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QFrame, QLabel, QVBoxLayout, QHBoxLayout

from qfluentwidgets import IconWidget, TextWrap, FlowLayout, ProgressBar, ProgressRing
from ..common.style_sheet import StyleSheet


class MonthStatisticsCard(QFrame):

    def __init__(self, month_statistics_dic, parent=None):
        super().__init__(parent=parent)

        self.progressBar = ProgressBar(self)
        self.titleLabel = QLabel("Month Statistics", self)
        self.contentLabel = QLabel(TextWrap.wrap(str(100 - month_statistics_dic["Month Percentage"]) + "%\n" + month_statistics_dic["Current Upload Download"] + " / " + month_statistics_dic['Traffic Max Limit'], 45, False)[0], self)

        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()

        self.progressBar.setFixedWidth(100)
        self.setFixedSize(360, 120)

        self.hBoxLayout.setSpacing(28)
        self.hBoxLayout.setContentsMargins(20, 0, 0, 0)
        self.vBoxLayout.setSpacing(2)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setAlignment(Qt.AlignVCenter)

        self.hBoxLayout.setAlignment(Qt.AlignVCenter)
        self.hBoxLayout.addWidget(self.progressBar)
        self.hBoxLayout.addLayout(self.vBoxLayout)
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.addWidget(self.titleLabel)
        self.vBoxLayout.addWidget(self.contentLabel)
        self.vBoxLayout.addStretch(1)

        self.progressBar.setValue(int(100 - month_statistics_dic["Month Percentage"]))
        self.progressBar.setTextVisible(True)
        self.titleLabel.setObjectName('contentLabel')
        self.contentLabel.setObjectName('titleLabel')

    def update_month_statistics(self, month_statistics_dic):
        self.progressBar.setValue(int(100 - month_statistics_dic["Month Percentage"]))
        self.contentLabel.setText(str(100 - month_statistics_dic["Month Percentage"]) + "%\n" + month_statistics_dic["Current Upload Download"] + " / " + month_statistics_dic['Traffic Max Limit'])


