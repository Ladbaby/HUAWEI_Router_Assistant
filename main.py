import os
import sys
import asyncio
from time import perf_counter

from PyQt5.QtCore import Qt, QTranslator, QTimer, QTime
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from qfluentwidgets import FluentTranslator, DWMMenu
from qasync import QEventLoop, QApplication

from app.common.config import cfg
from app.view.main_window import MainWindow
from app.common.global_logger import logger
from app.common.RouterInfo import Router_HW



if __name__ == "__main__":
    if cfg.get(cfg.enableLogging):
        logger.info("---HUAWEI Router Assistant started---")
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
            # t1_start = perf_counter() 
            w.show()
            w.update_monitoring_status()
            # w.update_month_statistics()
            # t1_stop = perf_counter() 
            # logger.info(f"Elapsed time during the whole program in seconds: {t1_stop-t1_start}")
        else:
            pass

    # Adding item on the menu bar
    tray = QSystemTrayIcon()
    tray.setIcon(icon)
    tray.setVisible(True)
    tray.activated.connect(lambda reason: show_window(reason))


    # Creating the options
    menu = DWMMenu()
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
            w.update_month_statistics()

    def update_traffic_statistics():
        if w.isVisible():
            router.update_traffic_statistics()
            w.update_traffic_statistics()

    def update_battery_history():
        w.update_battery_history()

    async def main():
        while True:
            update()
            await asyncio.sleep(15)  # Run update every 15 seconds

    async def traffic_statistics_main():
        while True:
            update_traffic_statistics()
            await asyncio.sleep(1)  # Run update_traffic_statistics every 1 second

    async def battery_history_main():
        while True:
            update_battery_history()
            await asyncio.sleep(15 * 60) # run every 15 mins

    # Start the main and traffic statistics tasks
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    loop.create_task(main())
    loop.create_task(traffic_statistics_main())
    loop.create_task(battery_history_main())

    # Start the application event loop
    with loop:
        # loop.run_until_complete(app_close_event.wait())
        loop.run_forever()
    
