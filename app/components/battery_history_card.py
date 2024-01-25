# coding:utf-8
from datetime import datetime
from time import perf_counter

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QFrame, QLabel, QVBoxLayout, QHBoxLayout

from app.common.global_logger import logger

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from ..common.config import cfg

class BatteryHistoryCard(QFrame):

    def __init__(self, battery_history_dic, parent=None):
        super().__init__(parent=parent)


        # TEST
        # battery_history_dic = {
        #     "time": [1696838547, 1696838650, 1696838780, 1696838910],
        #     "battery": [20, 50, 80, 70]
        # }

        # TODO: system setting case
        self.background_color_dic = {
            "Theme.DARK": (0.152941176, 0.152941176, 0.152941176, 1),
            "Theme.LIGHT": (0.847058824, 0.847058824, 0.847058824, 1),
            "Theme.AUTO": (0.152941176, 0.152941176, 0.152941176, 1)
        }

        self.front_color_dic = {
            "Theme.DARK": "white",
            "Theme.LIGHT": "black",
            "Theme.AUTO": "white"
        }

        self.graphWidget = MplCanvas(self, dpi=100)

        self.updateBatteryHistory(battery_history_dic)

        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()

        self.hBoxLayout.setSpacing(28)
        self.vBoxLayout.setSpacing(2)
        self.vBoxLayout.setAlignment(Qt.AlignVCenter)

        self.hBoxLayout.setAlignment(Qt.AlignVCenter)
        self.hBoxLayout.addLayout(self.vBoxLayout, 2)
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.addWidget(self.graphWidget)
        self.vBoxLayout.addStretch(1)

        self.setObjectName('batteryHistoryCard')

    def convert_time(self, unix_timestamp):
        return datetime.utcfromtimestamp(unix_timestamp + 8 * 60 * 60).strftime('%H:%M') # convert to UTC+8 time zone

    def calculate_x_ticks(self, unix_timestamp):
        dt_object = datetime.utcfromtimestamp(unix_timestamp + 8 * 60 * 60)
        hour = dt_object.hour
        minute = dt_object.minute

        # Calculate new timestamps for xx:00 and xx:30
        timestamp_xx00 = int(datetime(dt_object.year, dt_object.month, dt_object.day, hour, 0).timestamp())
        timestamp_xx30 = int(datetime(dt_object.year, dt_object.month, dt_object.day, hour, 30).timestamp())

        return timestamp_xx00, timestamp_xx30

    def updateBatteryHistory(self, battery_history_dic):
        self.battery_history_dic = battery_history_dic
        system_theme = str(cfg.get(cfg.themeMode))
        background_color = self.background_color_dic[system_theme]
        front_color = self.front_color_dic[system_theme]
        self.graphWidget.axes.set_facecolor(background_color)
        self.graphWidget.figure.patch.set_facecolor(background_color)

        x_list = [int(x) for x in battery_history_dic["time"]]
        y_labels_list = [10 * x for x in range(11)]
        battery_history_time_list = []
        x_ticks = []
        stride = 15
        previous_timestamp = 0
        i = 0
        linewidth = min(5, self.width() / (len(x_list)) * 3)
        for x, y, charging in zip(x_list, battery_history_dic["battery"], battery_history_dic["charging"]):
            # vertical lines with color indicating charging status
            # if consecutive records less than `stride`, then ignore
            if (x - previous_timestamp <= 20 and i % stride == 0) or x - previous_timestamp > 20:
                i += 1
                if charging:
                    # green
                    color = (0 / 255, 255 / 255, 54 / 255)
                else:
                    # blue
                    color = (53 / 255, 193 / 255, 241 / 255)
                self.graphWidget.axes.axvline(x=x, color=color, linestyle='-', linewidth=linewidth, ymin=0.05, ymax=y / 100, solid_capstyle='round')
            elif x - previous_timestamp <= 20 and i % stride != 0:
                i += 1

            previous_timestamp = x

            # calculate x ticks
            timestamp_xx00, timestamp_xx30 = self.calculate_x_ticks(x)
            if timestamp_xx00 not in x_ticks:
                battery_history_time_list.append(self.convert_time(timestamp_xx00))
                battery_history_time_list.append(self.convert_time(timestamp_xx30))
                x_ticks.append(int(timestamp_xx00))
                x_ticks.append(int(timestamp_xx30))
        
        self.graphWidget.axes.set_xticks(x_ticks)
        self.graphWidget.axes.set_xticklabels(battery_history_time_list, rotation=45, ha='right', color=front_color)

        self.graphWidget.axes.set_ylim(0, 100)
        padding = 1800
        self.graphWidget.axes.set_xlim(x_list[-1] - padding, x_list[0] + padding)

        # Customize y-axis tick labels.
        self.graphWidget.axes.set_yticks(range(0, 101, 10))
        self.graphWidget.axes.set_yticklabels(y_labels_list, rotation=45, ha='right', color=front_color)
        self.graphWidget.axes.tick_params(axis='both', color=front_color)

        for i, spine in enumerate(self.graphWidget.axes.spines.values()):
            # hide spine between top and right axis
            if i == 1 or i == 3:
                spine.set_visible(False)
            else:
                spine.set_edgecolor(front_color)
        
        self.graphWidget.draw()

    def resizeEvent(self, event):
        # Call your custom function when the window is resized
        self.updateBatteryHistory(self.battery_history_dic)
        event.accept()

class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(parent.width() / dpi, parent.height() / dpi), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)