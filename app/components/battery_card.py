# coding:utf-8
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QFrame, QLabel, QVBoxLayout, QHBoxLayout

from qfluentwidgets import IconWidget, TextWrap, FlowLayout, ProgressRing
from ..common.style_sheet import StyleSheet


class BatteryCard(QFrame):
    """ Sample card """

    def __init__(self, ring_value, title, content, parent=None):
        super().__init__(parent=parent)

        self.progressRing = ProgressRing(self)
        self.titleLabel = QLabel(title, self)
        self.contentLabel = QLabel(TextWrap.wrap(content, 45, False)[0], self)

        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()

        self.setFixedSize(360, 120)

        self.hBoxLayout.setSpacing(28)
        self.hBoxLayout.setContentsMargins(20, 0, 0, 0)
        self.vBoxLayout.setSpacing(2)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setAlignment(Qt.AlignVCenter)

        self.hBoxLayout.setAlignment(Qt.AlignVCenter)
        self.hBoxLayout.addWidget(self.progressRing)
        self.hBoxLayout.addLayout(self.vBoxLayout)
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.addWidget(self.titleLabel)
        self.vBoxLayout.addWidget(self.contentLabel)
        self.vBoxLayout.addStretch(1)

        self.progressRing.setValue(ring_value)
        self.progressRing.setTextVisible(True)
        self.titleLabel.setObjectName('contentLabel')
        self.contentLabel.setObjectName('titleLabel')

    def update_ring_value(self, ring_value, battery_status_str):
        self.progressRing.setValue(ring_value)
        self.contentLabel.setText(battery_status_str)


