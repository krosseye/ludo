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

from core.app_config import app_config
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
from utilities.generators import CoverPixmap

CONFIG = app_config


class GameDescriptionWidget(QScrollArea):
    """Widget to display game details including description and cover art."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        description_content = self._create_description_section()
        description_content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setFrameShape(QScrollArea.NoFrame)
        self.cover_image_label = QLabel()
        self._configure_cover_image_label()

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.cover_image_label, 0, Qt.AlignTop | Qt.AlignLeft)
        main_layout.addStretch(1)
        main_layout.addWidget(description_content, 10)
        main_layout.addStretch(1)
        main_layout.setContentsMargins(15, 15, 15, 15)

        content_widget = QWidget()
        content_widget.setLayout(main_layout)

        self.setWidgetResizable(True)
        self.setWidget(content_widget)

    def _create_description_section(self) -> QWidget:
        description_widget = QWidget()
        description_layout = QVBoxLayout()
        description_widget.setLayout(description_layout)
        description_layout.setContentsMargins(5, 0, 5, 0)

        title_label = QLabel("<h2>About The Game</h2><hr/>")
        title_label.setAlignment(Qt.AlignHCenter)

        self.description_label = QLabel()
        self._configure_description_label()

        description_layout.addWidget(title_label)
        description_layout.addWidget(self.description_label)
        description_layout.addStretch()

        return description_widget

    def _configure_cover_image_label(self):
        self.cover_image_label.setAlignment(Qt.AlignCenter)
        self.cover_image_label.setFixedSize(CONFIG.VERTICAL_CAPSULE_SIZE)
        if CONFIG.PREFERS_DARK_MODE:
            border_color = self.palette().midlight().color().name()
        else:
            border_color = self.palette().mid().color().name()
        self.cover_image_label.setStyleSheet(
            f"QLabel {{border: 1px solid {border_color};}}"
        )

    def _configure_description_label(self):
        self.description_label.setAlignment(Qt.AlignTop)
        self.description_label.setWordWrap(True)
        self.description_label.setOpenExternalLinks(True)

    def update_description(self, html_content: str):
        """Updates the description text with provided HTML content."""
        self.description_label.setText(html_content)

    def update_cover_image(self, image_path: str, fallback_title: str):
        """Updates the cover image with the provided path or generates a placeholder."""
        if image_path:
            cover_pixmap = QPixmap(image_path).scaled(
                CONFIG.VERTICAL_CAPSULE_SIZE,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
        else:
            width, height = (
                CONFIG.VERTICAL_CAPSULE_SIZE.width(),
                CONFIG.VERTICAL_CAPSULE_SIZE.height(),
            )
            cover_pixmap = CoverPixmap(width, height, fallback_title)

        self.cover_image_label.setPixmap(cover_pixmap)

    def resizeEvent(self, event):
        """Handle widget resize events to show/hide the cover graphic based on width."""
        super().resizeEvent(event)

        widget_width = self.width()

        if widget_width < 375:
            self.cover_image_label.setVisible(False)
        else:
            self.cover_image_label.setVisible(True)
