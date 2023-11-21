# coding:utf-8
from datetime import datetime
from turtle import color

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QFrame, QLabel, QVBoxLayout, QHBoxLayout

from qfluentwidgets import IconWidget, TextWrap, FlowLayout, ProgressRing

from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg


import matplotlib
matplotlib.use('Qt5Agg')
# import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from ..common.config import cfg

class BatteryHistoryCard(QFrame):

    def __init__(self, battery_history_dic, parent=None):
        super().__init__(parent=parent)

        # test
        battery_history_dic = {
            "time": [1696838547, 1696838650, 1696838780],
            "battery": [20, 50, 80]
        }

        system_theme = str(cfg.get(cfg.themeMode))
        # TODO: system setting case
        background_color_dic = {
            "Theme.DARK": "black",
            "Theme.LIGHT": "white",
            "Use system setting": "black"
        }
        background_color = background_color_dic[system_theme]

        front_color_dic = {
            "Theme.DARK": "white",
            "Theme.LIGHT": "black",
            "Use system setting": "white"
        }
        front_color = front_color_dic[system_theme]

        battery_history_time_list = [self.convert_time(x) for x in battery_history_dic["time"]]
        x_ticks = [int(x / 60) for x in battery_history_dic["time"]]
        # battery_history_time_list_enum = [list(enumerate(battery_history_time_list)), []]
        # battery_history_time_dic = dict(enumerate(battery_history_time_list))

        # self.graphWidget = pg.PlotWidget()
        # self.graphWidget.setLabel('left', 'Battery Percentage', units='%')
        # self.graphWidget.plot(battery_history_dic["time"], battery_history_dic["battery"])
        # self.graphWidget.setYRange(0, 100)
        # stringaxis = pg.AxisItem(orientation='bottom')
        # stringaxis.setTicks(battery_history_time_list_enum)
        # self.graphWidget.setAxisItems(axisItems = {'bottom': stringaxis})
        # self.graphWidget.setLabel('bottom', 'Time', units='s')

        # self.graphWidget = pg.GraphicsLayoutWidget()
        # # self.graphWidget.setYRange(self.y(0, 100))
        # stringaxis = pg.AxisItem(orientation='bottom')
        # stringaxis.setTicks([battery_history_time_dic.items()])
        # plot = self.graphWidget.addPlot(axisItems={'bottom': stringaxis})
        # curve = plot.plot(list(battery_history_time_dic.keys()), battery_history_dic["battery"])

        self.graphWidget = MplCanvas(self, width=5, height=4, dpi=100)
        self.graphWidget.axes.set_facecolor(background_color)
        self.graphWidget.figure.patch.set_facecolor(background_color)
        # plt.figure(facecolor=background_color)
        self.graphWidget.axes.plot(x_ticks, battery_history_dic["battery"], color=front_color)

        self.graphWidget.axes.set_xticks(x_ticks)
        self.graphWidget.axes.set_xticklabels(battery_history_time_list, rotation=45, ha='right', color=front_color)

        self.graphWidget.axes.set_ylim(0, 100)

        # Customize y-axis tick labels.
        self.graphWidget.axes.set_yticks(range(0, 101, 10))
        self.graphWidget.axes.tick_params(axis='both', color=front_color)

        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()

        self.setFixedSize(360, 600)

        self.hBoxLayout.setSpacing(28)
        self.hBoxLayout.setContentsMargins(20, 0, 0, 0)
        self.vBoxLayout.setSpacing(2)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setAlignment(Qt.AlignVCenter)

        self.hBoxLayout.setAlignment(Qt.AlignVCenter)
        self.hBoxLayout.addLayout(self.vBoxLayout, 2)
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.addWidget(self.graphWidget)
        self.vBoxLayout.addStretch(1)

        self.setObjectName('batteryHistoryCard')

    def convert_time(self, unix_timestamp):
        return datetime.utcfromtimestamp(unix_timestamp + 8 * 60 * 60).strftime('%H:%M') # convert to UTC+8 time zone

class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)