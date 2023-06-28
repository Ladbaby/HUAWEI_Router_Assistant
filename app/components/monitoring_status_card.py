# coding:utf-8
from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtWidgets import QWidget, QFrame, QLabel, QVBoxLayout, QHBoxLayout, QTableWidgetItem, QStyleOptionViewItem, QHeaderView
from PyQt5.QtGui import QPalette

from qfluentwidgets import IconWidget, TextWrap, FlowLayout, ProgressRing, TableWidget, TableItemDelegate, isDarkTheme
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

class MonitoringStatusCard(QWidget):

    def __init__(self, monitoring_status_dic):
        super().__init__()

        self.hBoxLayout = QHBoxLayout(self)
        self.tableView = TableWidget(self)

        # NOTE: use custom item delegate
        # self.tableView.setItemDelegate(CustomTableItemDelegate(self.tableView))

        self.tableView.setWordWrap(False)
        self.tableView.setRowCount(len(monitoring_status_dic.keys()))
        self.tableView.setColumnCount(2)
        
        i = 0
        for key, value in monitoring_status_dic.items():
            if type(value) == int:
                value = str(value)
            for j in range(2):
                if j == 0:
                    self.tableView.setItem(i, j, QTableWidgetItem(key))
                elif j == 1:
                    self.tableView.setItem(i, j, QTableWidgetItem(value))
            i += 1

        self.tableView.verticalHeader().hide()
        self.tableView.setHorizontalHeaderLabels(['Name', 'Value'])
        # self.tableView.resizeColumnsToContents()
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.tableView.setSortingEnabled(True)

        self.setStyleSheet("Demo{background: rgb(249, 249, 249)} ")
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.addWidget(self.tableView)
        # self.resize(635, 700)
        self.resize(800, 1000)
        StyleSheet.BATTERY_CARD.apply(self)

    def update_ring_value(self, ring_value):
        self.progressRing.setValue(ring_value)


