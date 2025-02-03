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

import sys

from models import AppConfig
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon, QPixmap
from PySide6.QtWidgets import QApplication, QSplashScreen
from widgets.main_window import MainWindow


def setup_application(config) -> QApplication:
    """Set up and return the QApplication instance."""
    app = QApplication(sys.argv)

    if not config.THEME.lower() == "auto":
        app.setStyle(config.THEME)

    font = QFont()
    font.setPointSize(config.BASE_FONT_SIZE)
    app.setFont(font)
    app.setWindowIcon(QIcon(config.APP_ICON))

    return app


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
    config = AppConfig()
    app = setup_application(config)

    _splash_enabled = config.SPLASH_ENABLED
    if _splash_enabled:
        splash = show_splash_screen(config)

    window = MainWindow()
    configure_window(window)

    if _splash_enabled:
        splash.close()

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
