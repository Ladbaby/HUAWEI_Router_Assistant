from app.common.RouterInfo import Router_HW
# from PyQt5.QtGui import * 
# from PyQt5.QtWidgets import * 

import os
import sys

from PyQt5.QtCore import Qt, QTranslator, QTimer, QTime
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from qfluentwidgets import FluentTranslator

from app.common.config import cfg
from app.view.main_window import MainWindow



if __name__ == "__main__":
    if cfg.get(cfg.dpiScale) == "Auto":
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    else:
        os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
        os.environ["QT_SCALE_FACTOR"] = str(cfg.get(cfg.dpiScale))

    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)
    app.setAttribute(Qt.AA_DisableWindowContextHelpButton, True)

    locale = cfg.get(cfg.language).value
    translator = FluentTranslator(locale)
    galleryTranslator = QTranslator()
    galleryTranslator.load(locale, "gallery", ".", ":/gallery/i18n")

    app.installTranslator(translator)
    app.installTranslator(galleryTranslator)

    router = Router_HW()
    router.update_monitoring_status()

    # Adding an icon
    icon = QIcon(router.get_battery_icon_path())
    
    w = MainWindow(router)

    def show_window(button):
        if button == QSystemTrayIcon.Trigger:
            w.show()
            update()
        else:
            pass

    # Adding item on the menu bar
    tray = QSystemTrayIcon()
    tray.setIcon(icon)
    tray.setVisible(True)
    tray.activated.connect(lambda reason: show_window(reason))


    # Creating the options
    menu = QMenu()
    open_action = QAction("Open")
    open_action.triggered.connect(lambda: show_window(QSystemTrayIcon.Trigger))
    menu.addAction(open_action)

    # To quit the app
    quit = QAction("Quit")
    quit.triggered.connect(app.quit)
    menu.addAction(quit)

    # Adding options to the System Tray
    tray.setContextMenu(menu)
    
    w.show()

    def update():
        router.update_monitoring_status()
        icon = QIcon(router.get_battery_icon_path())
        tray.setIcon(icon)
        if w.isVisible():
            w.update_monitoring_status()

    def update_traffic_statistics():
        if w.isVisible():
            router.update_traffic_statistics()
            w.update_traffic_statistics()

    timer = QTimer()
    timer.timeout.connect(update)
    timer.start(15000)

    timer_traffic = QTimer()
    timer_traffic.timeout.connect(update_traffic_statistics)
    timer_traffic.start(1000)
    
    app.exec_()

    
    
