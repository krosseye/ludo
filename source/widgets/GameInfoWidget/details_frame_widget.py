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

import os

from models import AppConfig
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)
from utilities.helpers import create_horizontal_line

from .star_rating_widget import StarRatingWidget

CONFIG = AppConfig()
RESOURCE_PATH = CONFIG.RESOURCE_PATH
ICONS_PATH = os.path.join(
    RESOURCE_PATH, "icons", "dark" if CONFIG.PREFERS_DARK_MODE else "light"
)


class DetailsFrame(QScrollArea):
    """Widget to display detailed game information with responsive layout."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QScrollArea.NoFrame)
        self.setMinimumWidth(130)

        self._details_widget = QWidget()
        self._details_layout = QVBoxLayout(self._details_widget)
        self.setWidget(self._details_widget)

        self._sections = []

        self._create_rating_section()
        self._create_release_year_section()
        self._create_developer_section()
        self._create_publisher_section()

        self._details_layout.addStretch()

    def resizeEvent(self, event):
        self._adjust_layout(self.width())
        super().resizeEvent(event)

    def _adjust_layout(self, width):
        compact_mode = width < 225
        micro_mode = width < 150
        for icon_label, title_label, value_widget in self._sections:
            icon_label.setVisible(not micro_mode)

            if value_widget is self.star_section_widget:
                if compact_mode:
                    self._star_rating_widget.hide()
                    self._star_rating_text_label.show()
                else:
                    self._star_rating_widget.show()
                    self._star_rating_text_label.hide()

    def _create_section(
        self, title: str, value_widget: QWidget, icon: QIcon
    ) -> QWidget:
        section_widget = QWidget()
        section_layout = QHBoxLayout(section_widget)
        section_layout.setContentsMargins(0, 0, 5, 0)

        icon_label = QLabel()
        icon_label.setPixmap(icon.pixmap(32, 32))
        section_layout.addWidget(icon_label)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel(f"<strong>{title}</strong>")
        content_layout.addWidget(title_label)
        content_layout.addWidget(value_widget)

        section_layout.addWidget(content_widget, stretch=1)
        self._details_layout.addWidget(section_widget)

        # Add separator line after section (except for Publisher)
        if title != "Publisher":
            self._details_layout.addWidget(create_horizontal_line())

        self._sections.append((icon_label, title_label, value_widget))

        return value_widget

    def _create_rating_section(self):
        """Create the rating section for the game details."""
        self.star_section_widget = QWidget()
        star_section_layout = QVBoxLayout(self.star_section_widget)
        star_section_layout.setContentsMargins(0, 0, 0, 0)

        self._star_rating_widget = StarRatingWidget(self._details_widget)
        self._star_rating_text_label = QLabel("<h2>0.0</h2>")
        self._star_rating_text_label.setVisible(False)

        star_section_layout.addWidget(self._star_rating_widget)
        star_section_layout.addWidget(self._star_rating_text_label)

        self._create_section(
            "Rating",
            self.star_section_widget,
            QIcon(os.path.join(ICONS_PATH, "star.png")),
        )
        self._star_rating_widget.setFixedHeight(32)

    def _create_release_year_section(self):
        """Create the release year section."""
        self._release_year_label = QLabel("<h2>Unkown</h2>")
        self._create_section(
            "Release",
            self._release_year_label,
            QIcon(os.path.join(ICONS_PATH, "calendar.png")),
        )

    def _create_developer_section(self):
        """Create the developer section."""
        self._developer_label = self._create_link_label("Unknown")
        self._create_section(
            "Developer",
            self._developer_label,
            QIcon(os.path.join(ICONS_PATH, "keyboard.png")),
        )

    def _create_publisher_section(self):
        """Create the publisher section."""
        self._publisher_label = self._create_link_label("Unknown")
        self._create_section(
            "Publisher",
            self._publisher_label,
            QIcon(os.path.join(ICONS_PATH, "globe.png")),
        )

    def _create_link_label(self, initial_text: str) -> QLabel:
        """Create a label that can contain external links."""
        label = QLabel(f"<h2>{initial_text}</h2>")
        label.setWordWrap(True)
        label.setOpenExternalLinks(True)
        return label

    def set_star_rating(self, rating: float):
        """Set the star rating."""
        self._star_rating_widget.rating = rating
        self._star_rating_text_label.setText(f"<h2>{rating} / 5</h2>")
        self._star_rating_widget.setToolTip(f"Rating: {rating}")

    def set_release_year(self, year: int):
        """Set the release year."""
        self._release_year_label.setText(f"<h2>{year}</h2>")

    def set_developer(self, developer: str):
        """Set the developer name."""
        self._set_entity_value(self._developer_label, developer)

    def set_publisher(self, publisher: str):
        """Set the publisher name."""
        self._set_entity_value(self._publisher_label, publisher)

    def _set_entity_value(self, label: QLabel, name: str):
        """Helper method to set a developer or publisher name with optional link."""
        if name.lower() != "unknown":
            label.setText(
                f'<h2><a style="color: {self.palette().text().color().name()};" '
                f'href="https://www.wikipedia.org/wiki/Special:Search?search={name}" '
                f'target="_blank">{name}</a></h2>'
            )
            label.setToolTip("Open on Wikipedia")
        else:
            label.setText(f"<h2>{name}</h2>")
            label.setToolTip("")
