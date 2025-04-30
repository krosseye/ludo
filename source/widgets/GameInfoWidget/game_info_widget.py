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

from core.app_config import app_config
from core.services import GameListManager
from PySide6.QtCore import QPoint, QRect, Qt, Signal
from PySide6.QtGui import QColor, QKeyEvent, QPainter
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)
from utilities.generators import HeroPixmap

from .description_widget import GameDescriptionWidget
from .details_frame_widget import DetailsFrame
from .hero_image_frame import HeroImageFrame
from .stat_bar_widget import StatBar
from .title_bar_widget import TitleBar

CONFIG = app_config
USER_DATA_PATH = os.path.join(CONFIG.USER_DATA_PATH, "games")


class AlignmentButton(QPushButton):
    def __init__(self, alignment: str, parent=None):
        super().__init__(parent)
        self.alignment = alignment
        self.setFixedSize(40, 40)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(f"Align {alignment.capitalize()}")

        self._setup_style()

    def _setup_style(self):
        pal = self.palette()
        base_color = pal.base().color()
        alt_color = pal.mid().color()
        highlight_color = pal.highlight().color()

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {base_color.name()};
                border: 1px solid {alt_color.name()};
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {alt_color.name()};
                border: 1px solid {pal.midlight().color().name()};
            }}
            QPushButton:pressed {{
                background-color: {highlight_color.name()};
            }}
        """)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        color = self.palette().highlight().color()
        if self.isDown():
            color = QColor("white")

        rect = self.rect().adjusted(10, 10, -10, -10)

        if self.alignment == "north":
            painter.fillRect(QRect(rect.left(), rect.top(), rect.width(), 6), color)
        elif self.alignment == "south":
            painter.fillRect(
                QRect(rect.left(), rect.bottom() - 6, rect.width(), 6), color
            )
        elif self.alignment == "west":
            painter.fillRect(QRect(rect.left(), rect.top(), 6, rect.height()), color)
        elif self.alignment == "east":
            painter.fillRect(
                QRect(rect.right() - 6, rect.top(), 6, rect.height()), color
            )
        elif self.alignment == "center":
            center = rect.center()
            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(center, 6, 6)


class PositionSelectorWidget(QWidget):
    position_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._create_ui()

    def _create_ui(self):
        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        self.setLayout(layout)

        for row, col in [(0, 0), (0, 2), (2, 0), (2, 2)]:
            spacer = QWidget()
            spacer.setFixedSize(10, 10)
            spacer.setAttribute(Qt.WA_TransparentForMouseEvents)
            layout.addWidget(spacer, row, col)

        positions = {
            "north": (0, 1),
            "south": (2, 1),
            "west": (1, 0),
            "east": (1, 2),
            "center": (1, 1),
        }

        for pos, (row, col) in positions.items():
            btn = AlignmentButton(pos)
            btn.clicked.connect(lambda _, p=pos: self._select_position(p))
            layout.addWidget(btn, row, col)

    def _select_position(self, position):
        self.position_selected.emit(position)
        self.hide()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setCompositionMode(QPainter.CompositionMode_Clear)
        painter.fillRect(self.rect(), Qt.transparent)


class GameInfoWidget(QFrame):
    """Displays detailed information about a selected game."""

    def __init__(self, game_list: GameListManager, parent=None):
        super().__init__(parent)

        self.game_list = game_list
        self._initialize_ui()
        self._connect_signals()
        self.update_displayed_game()

    def _initialize_ui(self):
        """Sets up the user interface layout and components."""
        self._setup_main_layout()
        self._setup_title_bar()
        self._setup_scroll_area()
        self._setup_scrollable_content()

    def _setup_main_layout(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

    def _setup_title_bar(self):
        self.title_bar = TitleBar(self)
        self.main_layout.addWidget(self.title_bar, 0)

    def _setup_scroll_area(self):
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setWidgetResizable(True)
        self.main_layout.addWidget(self.scroll_area, 1)

    def _setup_scrollable_content(self):
        self.scrollable_content = QWidget()
        self.scrollable_layout = QVBoxLayout(self.scrollable_content)
        self.scrollable_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_area.setWidget(self.scrollable_content)

        self._setup_hero_image_frame()
        self._setup_stat_bar()
        self._setup_info_content_layout()

    def _setup_hero_image_frame(self):
        self.hero_image_frame = HeroImageFrame()
        self.hero_image_frame.setMinimumHeight(150)
        self.scrollable_layout.addWidget(self.hero_image_frame, 3)

        self.hero_image_frame.setContextMenuPolicy(Qt.CustomContextMenu)
        self.hero_image_frame.customContextMenuRequested.connect(
            self._show_logo_position_menu
        )

    def _show_logo_position_menu(self, position):
        dialog = PositionSelectorWidget(self)
        dialog.position_selected.connect(self._set_logo_position)

        global_pos = self.hero_image_frame.mapToGlobal(position)
        dialog.move(
            global_pos
            - QPoint(dialog.sizeHint().width() // 2, dialog.sizeHint().height() // 2)
        )
        dialog.show()

    def _set_logo_position(self, position):
        game_id = self.game_list.selected_game
        if game_id:
            self.game_list.game_manager.set_logo_position(game_id, position)

    def _setup_stat_bar(self):
        self.stat_bar = StatBar()
        self.scrollable_layout.addWidget(self.stat_bar, 0)

    def _setup_info_content_layout(self):
        self.info_content_layout = QHBoxLayout()
        self.scrollable_layout.addLayout(self.info_content_layout, 3)

        self._setup_description_frame()
        self._setup_details_frame()

    def _setup_description_frame(self):
        self.description_frame = GameDescriptionWidget()
        self.info_content_layout.addWidget(self.description_frame, 2)

    def _setup_details_frame(self):
        self.details_frame = DetailsFrame(self)
        self.details_frame.setMinimumHeight(200)
        self.info_content_layout.addWidget(self.details_frame, 1)

    def _connect_signals(self):
        """Connect signals from the GameListManager to appropriate handlers."""
        self.game_list.game_selected.connect(self.update_displayed_game)
        self.game_list.dataChanged.connect(self.update_displayed_game)

    def mousePressEvent(self, event):
        self.setFocus()

    def keyPressEvent(self, event: QKeyEvent):
        """Handles key press events for navigating between games."""
        if event.key() == Qt.Key_Left:
            self.game_list.select_previous()
        elif event.key() == Qt.Key_Right:
            self.game_list.select_next()
        else:
            super().keyPressEvent(event)

    def update_displayed_game(self):
        """Updates the displayed game information."""
        selected_game = self.game_list.find_game_by_id(self.game_list.selected_game)
        if selected_game:
            self._populate_game_details(selected_game)

    def _populate_game_details(self, game_info):
        """Populates the UI with details from the given game info."""
        user_data_path = os.path.join(USER_DATA_PATH, game_info.id)

        self._update_hero_image(game_info.title, user_data_path)
        self._update_logo_image(game_info.title, user_data_path, game_info.logoPosition)
        self._update_title_bar(game_info, user_data_path)
        self._update_stat_bar(game_info)
        self._update_description(game_info.description or "No description available")
        self._update_details_frame(game_info)
        self._reset_scroll_bars()
        self._update_cover_image(user_data_path, game_info.title)

    def _update_hero_image(self, title, path):
        hero_image_path = (
            self._find_image_path(path, "hero") or HeroPixmap(seed=title).toImage()
        )
        self.hero_image_frame.set_hero_image(hero_image_path)

    def _update_logo_image(self, title, path, position):
        logo_image_path = self._find_image_path(path, "logo")

        if logo_image_path:
            self.hero_image_frame.set_logo_image(logo_image_path, position)
        else:
            self.hero_image_frame.set_logo_text(title)

    def _update_title_bar(self, game_info, path):
        icon_image_path = self._find_image_path(path, "icon") or None
        self.title_bar.set_icon_image(icon_image_path)
        self.title_bar.set_title(game_info.title)
        self.title_bar.play_button.update_game_info(game_info)

    def _update_stat_bar(self, game_info):
        self.stat_bar.update_stats(
            game_info.lastPlayed or None,
            game_info.sessionsPlayed or "0",
            game_info.playtime or 0,
        )

    def _update_description(self, description):
        self.description_frame.update_description(description)

    def _update_details_frame(self, game_info):
        self.details_frame.set_star_rating(float(game_info.starRating or 0.0))
        self.details_frame.set_publisher(game_info.publisher or "Unknown")
        self.details_frame.set_developer(game_info.developer or "Unknown")
        self.details_frame.set_release_year(game_info.year or "Unknown")

    def _reset_scroll_bars(self):
        """Resets all scroll bars to the top."""
        self.details_frame.verticalScrollBar().setValue(0)
        self.description_frame.verticalScrollBar().setValue(0)
        self.scroll_area.verticalScrollBar().setValue(0)

    def _update_cover_image(self, path, title):
        cover_image_path = self._find_image_path(path, "capsule") or None
        self.description_frame.update_cover_image(cover_image_path, title)

    @staticmethod
    def _find_image_path(base_path, file_name):
        """Finds the first matching image file with supported extensions."""
        extensions = ["jpg", "jpeg", "png", "ico"]

        for ext in extensions:
            file_path = os.path.join(base_path, f"{file_name}.{ext}")
            if os.path.exists(file_path):
                return file_path
        return None
