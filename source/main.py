#############################################################################
##
## Copyright (C) 2025 Killian-W.
## All rights reserved.
##
## This file is part of the Ludo project.
##
## Licensed under the MIT License.
## You may obtain a copy of the License at:
##     https://opensource.org/licenses/MIT
##
## This software is provided "as is," without warranty of any kind.
##
#############################################################################

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

import core.constants as constants  # type: ignore
from core.app_config import app_config
from core.config import user_config
from PySide6.QtCore import QCoreApplication, Qt
from PySide6.QtGui import QFont, QIcon, QPixmap
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtWidgets import QApplication, QMessageBox, QSplashScreen
from widgets.main_window import MainWindow

_instance_server = None


def setup_application(_app_config, _user_config) -> QApplication:
    """Set up and return the QApplication instance."""
    app = QApplication(sys.argv)
    if not _user_config["THEME"].lower() == "auto":
        app.setStyle(_user_config["THEME"])
    font = QFont()
    font.setPointSize(_user_config["BASE_FONT_SIZE"])
    app.setFont(font)
    app.setWindowIcon(QIcon(_app_config.APP_ICON))
    return app


def check_single_instance(app_name):
    global _instance_server

    socket = QLocalSocket()
    socket.connectToServer(app_name)
    if socket.waitForConnected(500):
        socket.close()
        return False  # Another instance is running

    # No instance running - create server
    _instance_server = QLocalServer()
    _instance_server.removeServer(app_name)
    if not _instance_server.listen(app_name):
        logging.error(
            f"Could not create local server: {_instance_server.errorString()}"
        )
        return False  # Failed to create server

    return True


def configure_logging(config):
    logging.basicConfig(
        level=config.LOG_LEVEL,
        format="%(asctime)s | %(levelname)s | %(name)s - %(message)s",
        datefmt="%Y/%m/%d %H:%M:%S",
        handlers=[
            RotatingFileHandler(
                str(
                    Path(
                        os.path.join(
                            config.USER_DATA_PATH,
                            "app.log",
                        )
                    ).resolve()
                ),
                maxBytes=5 * 1024 * 1024,
                backupCount=3,
            ),
            logging.StreamHandler(),
        ],
    )


def configure_window(window: MainWindow) -> None:
    """Configure the window size, position, and title."""
    screen_geometry = window.screen().geometry()
    width = int(screen_geometry.width() // 1.75)
    height = int(screen_geometry.height() // 1.45)
    window.resize(width, height)
    window.move(
        (screen_geometry.width() - width) // 2,
        (screen_geometry.height() - height) // 2,
    )


def show_splash_screen(config) -> QSplashScreen:
    pixmap = QPixmap(config.SPLASH_IMAGE)
    scaled_pixmap = pixmap.scaled(512, 512, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    splash = QSplashScreen(scaled_pixmap)
    splash.show()
    return splash


def main():
    if sys.platform == "win32":
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            f"{constants.APP_TITLE}.App.{constants.APP_VERSION}"
        )

    QCoreApplication.setApplicationName(constants.APP_TITLE)
    QCoreApplication.setOrganizationName(constants.DEVELOPER)
    QCoreApplication.setApplicationVersion(constants.APP_VERSION)
    QCoreApplication.setOrganizationDomain(constants.GITHUB_URL)

    if not check_single_instance("LudoAppUniqueInstance"):
        temp_app = QApplication(sys.argv)

        msg_box = QMessageBox()
        msg_box.setWindowTitle(f"{constants.APP_TITLE} - Instance Already Running")
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setText(
            f"Another instance of {constants.APP_TITLE} is already running."
        )
        msg_box.setInformativeText(
            "Only one instance can run at a time. This application will now close."
        )
        msg_box.setStandardButtons(QMessageBox.Ok)

        try:
            msg_box.setWindowIcon(QIcon(app_config.APP_ICON))
        except Exception:
            pass

        msg_box.exec()
        temp_app.quit()
        sys.exit(1)

    config = app_config
    _user_config = user_config
    _user_config.set_config_file(
        Path(
            os.path.join(
                config.USER_DATA_PATH,
                "config.json",
            )
        ).resolve()
    )

    app = setup_application(config, _user_config)

    splash_enabled = config.SPLASH_ENABLED
    if splash_enabled:
        splash = show_splash_screen(config)

    configure_logging(config)
    window = MainWindow()
    configure_window(window)

    if splash_enabled:
        splash.close()

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
