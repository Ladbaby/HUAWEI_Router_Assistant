# coding:utf-8
from PyQt5.QtCore import Qt, QRectF, QSize
from PyQt5.QtGui import QPixmap, QPainter, QColor, QBrush, QPainterPath, QImage, QPalette
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QGraphicsBlurEffect

from qfluentwidgets import ScrollArea, isDarkTheme, FluentIcon, SingleDirectionScrollArea, FlowLayout, PixmapLabel
from ..common.config import cfg, HELP_URL, REPO_URL, EXAMPLE_URL, FEEDBACK_URL
from ..common.icon import Icon, FluentIconBase
from ..components.link_card import LinkCardView
from ..components.sample_card import SampleCardView
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

        # self.flowLayout.setContentsMargins(36, 0, 0, 0)
        # self.flowLayout.setSpacing(12)
        # self.flowLayout.setAlignment(Qt.AlignLeft)

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
        # self.setFixedHeight(336)
        self.setFixedHeight(600)

        self.vBoxLayout = QVBoxLayout(self)
        self.galleryLabel = QLabel('HUAWEI Mobile WiFi 3 Pro', self)
        self.bannerCardView = BannerCardView(self)

        dpi = 300  # Set your desired DPI value
        self.model_image = QImage(':/gallery/images/mobile_wifi3_pro_cover.png')
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


        # print(self.model_image.devicePixelRatio())
        # print(self.model_image.logicalDpiX())
        # print(self.model_image.physicalDpiX())

        self.model_pixmap = QPixmap.fromImage(self.model_image)
        self.model_pixmap = self.model_pixmap.scaled(120, 120, transformMode=Qt.SmoothTransformation, aspectRatioMode=Qt.KeepAspectRatioByExpanding)

        # print(self.model_pixmap.devicePixelRatio())
        # print(self.model_pixmap.logicalDpiX())
        # print(self.model_pixmap.physicalDpiX())
        self.model_label = PixmapLabel(self)
        self.model_label.setPixmap(self.model_pixmap)
        # print(self.model_label.devicePixelRatio())
        # print(self.model_label.logicalDpiX())
        # print(self.model_label.physicalDpiX())

        self.galleryLabel.setObjectName('galleryLabel')

        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        # self.vBoxLayout.addSpacing(30)
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
        # self.loadSamples()

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
        # self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        # self.vBoxLayout.setSpacing(40)
        self.vBoxLayout.addWidget(self.banner)
        self.vBoxLayout.setAlignment(Qt.AlignTop)

    def loadSamples(self):
        """ load samples """
        # basic input samples
        basicInputView = SampleCardView(
            self.tr("Basic input samples"), self.view)
        basicInputView.addSampleCard(
            icon=":/gallery/images/controls/Button.png",
            title="Button",
            content=self.tr(
                "A control that responds to user input and emit clicked signal."),
            routeKey="basicInputInterface",
            index=0
        )
        basicInputView.addSampleCard(
            icon=":/gallery/images/controls/Checkbox.png",
            title="CheckBox",
            content=self.tr("A control that a user can select or clear."),
            routeKey="basicInputInterface",
            index=7
        )
        basicInputView.addSampleCard(
            icon=":/gallery/images/controls/ComboBox.png",
            title="ComboBox",
            content=self.tr(
                "A drop-down list of items a user can select from."),
            routeKey="basicInputInterface",
            index=9
        )
        basicInputView.addSampleCard(
            icon=":/gallery/images/controls/DropDownButton.png",
            title="DropDownButton",
            content=self.tr(
                "A button that displays a flyout of choices when clicked."),
            routeKey="basicInputInterface",
            index=11
        )
        basicInputView.addSampleCard(
            icon=":/gallery/images/controls/HyperlinkButton.png",
            title="HyperlinkButton",
            content=self.tr(
                "A button that appears as hyperlink text, and can navigate to a URI or handle a Click event."),
            routeKey="basicInputInterface",
            index=16
        )
        basicInputView.addSampleCard(
            icon=":/gallery/images/controls/RadioButton.png",
            title="RadioButton",
            content=self.tr(
                "A control that allows a user to select a single option from a group of options."),
            routeKey="basicInputInterface",
            index=17
        )
        basicInputView.addSampleCard(
            icon=":/gallery/images/controls/Slider.png",
            title="Slider",
            content=self.tr(
                "A control that lets the user select from a range of values by moving a Thumb control along a track."),
            routeKey="basicInputInterface",
            index=18
        )
        basicInputView.addSampleCard(
            icon=":/gallery/images/controls/SplitButton.png",
            title="SplitButton",
            content=self.tr(
                "A two-part button that displays a flyout when its secondary part is clicked."),
            routeKey="basicInputInterface",
            index=19
        )
        basicInputView.addSampleCard(
            icon=":/gallery/images/controls/ToggleSwitch.png",
            title="SwitchButton",
            content=self.tr(
                "A switch that can be toggled between 2 states."),
            routeKey="basicInputInterface",
            index=23
        )
        basicInputView.addSampleCard(
            icon=":/gallery/images/controls/ToggleButton.png",
            title="ToggleButton",
            content=self.tr(
                "A button that can be switched between two states like a CheckBox."),
            routeKey="basicInputInterface",
            index=24
        )
        self.vBoxLayout.addWidget(basicInputView)

        # date time samples
        dateTimeView = SampleCardView(self.tr('Date & time samples'), self.view)
        dateTimeView.addSampleCard(
            icon=":/gallery/images/controls/CalendarDatePicker.png",
            title="CalendarPicker",
            content=self.tr("A control that lets a user pick a date value using a calendar."),
            routeKey="dateTimeInterface",
            index=0
        )
        dateTimeView.addSampleCard(
            icon=":/gallery/images/controls/DatePicker.png",
            title="DatePicker",
            content=self.tr("A control that lets a user pick a date value."),
            routeKey="dateTimeInterface",
            index=2
        )
        dateTimeView.addSampleCard(
            icon=":/gallery/images/controls/TimePicker.png",
            title="TimePicker",
            content=self.tr(
                "A configurable control that lets a user pick a time value."),
            routeKey="dateTimeInterface",
            index=4
        )
        self.vBoxLayout.addWidget(dateTimeView)

        # dialog samples
        dialogView = SampleCardView(self.tr('Dialog samples'), self.view)
        dialogView.addSampleCard(
            icon=":/gallery/images/controls/Flyout.png",
            title="Dialog",
            content=self.tr("A frameless message dialog."),
            routeKey="dialogInterface",
            index=0
        )
        dialogView.addSampleCard(
            icon=":/gallery/images/controls/ContentDialog.png",
            title="MessageBox",
            content=self.tr("A message dialog with mask."),
            routeKey="dialogInterface",
            index=1
        )
        dialogView.addSampleCard(
            icon=":/gallery/images/controls/ColorPicker.png",
            title="ColorDialog",
            content=self.tr("A dialog that allows user to select color."),
            routeKey="dialogInterface",
            index=2
        )
        dialogView.addSampleCard(
            icon=":/gallery/images/controls/ColorPicker.png",
            title="TeachingTip",
            content=self.tr("A content-rich flyout for guiding users and enabling teaching moments."),
            routeKey="dialogInterface",
            index=3
        )
        self.vBoxLayout.addWidget(dialogView)

        # layout samples
        layoutView = SampleCardView(self.tr('Layout samples'), self.view)
        layoutView.addSampleCard(
            icon=":/gallery/images/controls/Grid.png",
            title="FlowLayout",
            content=self.tr(
                "A layout arranges components in a left-to-right flow, wrapping to the next row when the current row is full."),
            routeKey="layoutInterface",
            index=0
        )
        self.vBoxLayout.addWidget(layoutView)

        # material samples
        materialView = SampleCardView(self.tr('Material samples'), self.view)
        materialView.addSampleCard(
            icon=":/gallery/images/controls/Acrylic.png",
            title="AcrylicLabel",
            content=self.tr(
                "A translucent material recommended for panel background."),
            routeKey="materialInterface",
            index=0
        )
        self.vBoxLayout.addWidget(materialView)

        # menu samples
        menuView = SampleCardView(self.tr('Menu samples'), self.view)
        menuView.addSampleCard(
            icon=":/gallery/images/controls/MenuFlyout.png",
            title="RoundMenu",
            content=self.tr(
                "Shows a contextual list of simple commands or options."),
            routeKey="menuInterface",
            index=0
        )
        self.vBoxLayout.addWidget(menuView)

        # navigation
        navigationView = SampleCardView(self.tr('Navigation'), self.view)
        navigationView.addSampleCard(
            icon=":/gallery/images/controls/Pivot.png",
            title="Pivot",
            content=self.tr(
                "Presents information from different sources in a tabbed view."),
            routeKey="navigationViewInterface",
            index=0
        )
        self.vBoxLayout.addWidget(navigationView)

        # scroll samples
        scrollView = SampleCardView(self.tr('Scrolling samples'), self.view)
        scrollView.addSampleCard(
            icon=":/gallery/images/controls/ScrollViewer.png",
            title="ScrollArea",
            content=self.tr(
                "A container control that lets the user pan and zoom its content smoothly."),
            routeKey="scrollInterface",
            index=0
        )
        self.vBoxLayout.addWidget(scrollView)

        # state info samples
        stateInfoView = SampleCardView(self.tr('Status & info samples'), self.view)
        stateInfoView.addSampleCard(
            icon=":/gallery/images/controls/ProgressRing.png",
            title="StateToolTip",
            content=self.tr(
                "Shows the apps progress on a task, or that the app is performing ongoing work that does block user interaction."),
            routeKey="statusInfoInterface",
            index=0
        )
        stateInfoView.addSampleCard(
            icon=":/gallery/images/controls/InfoBar.png",
            title="InfoBar",
            content=self.tr(
                "An inline message to display app-wide status change information."),
            routeKey="statusInfoInterface",
            index=3
        )
        stateInfoView.addSampleCard(
            icon=":/gallery/images/controls/ProgressBar.png",
            title="ProgressBar",
            content=self.tr(
                "Shows the apps progress on a task, or that the app is performing ongoing work that doesn't block user interaction."),
            routeKey="statusInfoInterface",
            index=7
        )
        stateInfoView.addSampleCard(
            icon=":/gallery/images/controls/ProgressRing.png",
            title="ProgressRing",
            content=self.tr(
                "Shows the apps progress on a task, or that the app is performing ongoing work that doesn't block user interaction."),
            routeKey="statusInfoInterface",
            index=9
        )
        stateInfoView.addSampleCard(
            icon=":/gallery/images/controls/ToolTip.png",
            title="ToolTip",
            content=self.tr(
                "Displays information for an element in a pop-up window."),
            routeKey="statusInfoInterface",
            index=1
        )
        self.vBoxLayout.addWidget(stateInfoView)

        # text samples
        textView = SampleCardView(self.tr('Text samples'), self.view)
        textView.addSampleCard(
            icon=":/gallery/images/controls/TextBox.png",
            title="LineEdit",
            content=self.tr("A single-line plain text field."),
            routeKey="textInterface",
            index=0
        )
        textView.addSampleCard(
            icon=":/gallery/images/controls/NumberBox.png",
            title="SpinBox",
            content=self.tr(
                "A text control used for numeric input and evaluation of algebraic equations."),
            routeKey="textInterface",
            index=1
        )
        textView.addSampleCard(
            icon=":/gallery/images/controls/RichEditBox.png",
            title="TextEdit",
            content=self.tr(
                "A rich text editing control that supports formatted text, hyperlinks, and other rich content."),
            routeKey="textInterface",
            index=6
        )
        self.vBoxLayout.addWidget(textView)

        # view samples
        collectionView = SampleCardView(self.tr('View samples'), self.view)
        collectionView.addSampleCard(
            icon=":/gallery/images/controls/ListView.png",
            title="ListView",
            content=self.tr(
                "A control that presents a collection of items in a vertical list."),
            routeKey="viewInterface",
            index=0
        )
        collectionView.addSampleCard(
            icon=":/gallery/images/controls/DataGrid.png",
            title="TableView",
            content=self.tr(
                "The DataGrid control provides a flexible way to display a collection of data in rows and columns."),
            routeKey="viewInterface",
            index=1
        )
        collectionView.addSampleCard(
            icon=":/gallery/images/controls/TreeView.png",
            title="TreeView",
            content=self.tr(
                "The TreeView control is a hierarchical list pattern with expanding and collapsing nodes that contain nested items."),
            routeKey="viewInterface",
            index=2
        )
        self.vBoxLayout.addWidget(collectionView)
