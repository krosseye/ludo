#############################################################################
##
## Copyright (C) 2025 Killian-W.
## All rights reserved.
##
## This file is part of the Ludo project.
##
## Licensed under the Mozilla Public License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at:
##     https://www.mozilla.org/en-US/MPL/2.0/
##
## This software is provided "as is," without warranties or conditions
## of any kind, either express or implied. See the License for details.
##
#############################################################################

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
)
from widgets.components.play_button import PlayButton


class TitleBar(QFrame):
    """A custom title bar to display game title and controls."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setContentsMargins(0, 0, 0, 0)

        layout = QHBoxLayout()
        self.setLayout(layout)
        self._game_list_manager = parent.game_list

        self._icon_label = QLabel()
        self._icon_label.setFixedSize(36, 36)
        self._title_label = QLabel()
        self._title_label.setWordWrap(True)
        self._title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        self.play_button = PlayButton(game_list_manager=self._game_list_manager)

        self.play_button.setFixedWidth(96)

        layout.addWidget(self._icon_label, 0)
        layout.addWidget(self._title_label, 1)
        layout.addWidget(self.play_button, 0)

    def set_title(self, title: str):
        """Set the game title."""
        self._title_label.setText(f"<h1>{title}</h1>")

    def set_icon_image(self, icon_path: str):
        """Set the icon image from the given file path."""
        if icon_path:
            icon = QIcon(icon_path)
            pixmap = icon.pixmap(48, 48)

            self._icon_label.setVisible(True)
            self._icon_label.setPixmap(
                pixmap.scaled(36, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        else:
            self._icon_label.setPixmap(QPixmap())
            self._icon_label.setVisible(False)
