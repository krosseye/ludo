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
from typing import Any, Optional, Union

from models import AppConfig, Game
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
from services import GameListManager
from widgets.GameCollectionWidgets.context_menu import GameEntryContextMenu
from widgets.GameCollectionWidgets.search_input import SearchBarWidget

from .app_cover_widget import AppLauncherCover
from .app_icon_widget import AppLauncherIcon

CONFIG = AppConfig()

VERTICAL_CAPSULE_SIZE = CONFIG.VERTICAL_CAPSULE_SIZE
HORIZONTAL_CAPSULE_SIZE = CONFIG.HORIZONTAL_CAPSULE_SIZE
ICON_SIZE = QSize(96, 112)

GAMES_DIRECTORY = os.path.join(
    CONFIG.USER_DATA_PATH,
    "games",
)


class GameGridWidget(QFrame):
    """Displays a grid of game launcher icons with filtering and sorting options."""

    def __init__(
        self, game_list: GameListManager, parent: Optional[QWidget] = None
    ) -> None:
        super().__init__(parent)

        self.game_list: GameListManager = game_list
        self.filtered_games: list[Game] = game_list.all_games

        self.item_style = None
        self.item_spacing = 20
        self.set_item_style()

        self.setMinimumWidth(int(self.item_width + (self.item_spacing * 2)))

        self.cols: int = 1
        self.widget_width: Optional[int] = None

        self.layout: QVBoxLayout = QVBoxLayout()
        self.setFrameShape(QFrame.NoFrame)

        self.search_bar: SearchBarWidget = parent.search_bar
        self.search_bar.search_text_changed.connect(self._filter_games)
        self.sort_by_recent_checkbox = parent.sort_by_recent_checkbox
        self.favourites_checkbox = parent.favourites_checkbox
        self.sort_order_combobox = parent.sort_order_combobox

        self.no_entries_label = self._create_no_entries_label()

        _list_scroll_area: QScrollArea = QScrollArea()
        _list_scroll_area.setWidgetResizable(True)
        _list_scroll_area.setFrameShape(QScrollArea.NoFrame)

        _container: QWidget = QWidget()
        self.vertical_layout: QVBoxLayout = QVBoxLayout(_container)
        self.vertical_layout.setContentsMargins(0, 5, 0, 0)

        self.selected_game_id: Optional[str] = self.game_list.selected_game
        self.last_known_cols: Optional[int] = None

        self._populate_grid()

        _container.setLayout(self.vertical_layout)
        _list_scroll_area.setWidget(_container)

        self.layout.addWidget(self.no_entries_label)
        self.layout.addWidget(_list_scroll_area)

        self.setLayout(self.layout)

        self._connect_game_list_signals()

        self.setFocus()

    def set_item_style(self, style=CONFIG.GRID_STYLE):
        """
        Sets the item style and updates the dimensions.

        Supported styles are:
            "capsule": Sets the dimensions to 150x225.

            "capsule_wide": Sets the dimensions to 276x129.

            Any other value will default to "icon", with dimensions 96x112.

        """
        self.item_style = style

        if self.item_style == "capsule":
            self.item_width = VERTICAL_CAPSULE_SIZE.width()
            self.item_height = VERTICAL_CAPSULE_SIZE.height()

        elif self.item_style == "capsule_wide":
            self.item_width = HORIZONTAL_CAPSULE_SIZE.width()
            self.item_height = HORIZONTAL_CAPSULE_SIZE.height()
        else:
            self.item_style = "icon"
            self.item_width = ICON_SIZE.width()
            self.item_height = ICON_SIZE.height()

    def _connect_game_list_signals(self) -> None:
        """Connect signals from the game list to refresh the grid."""
        self.game_list.game_selected.connect(self._on_game_selected)

        self.game_list.dataChanged.connect(self.refresh)
        self.game_list.layoutChanged.connect(self.refresh)

    def _on_game_selected(self, game_id: str) -> None:
        """Highlight the selected game icon and reset the previous one."""
        if self.selected_game_id:
            previous_icon = self._get_widget_by_id(self.selected_game_id)
            if previous_icon:
                previous_icon.selected = False

        current_icon = self._get_widget_by_id(game_id)
        if current_icon:
            current_icon.selected = True

        self.selected_game_id = game_id

    def _create_no_entries_label(self) -> QLabel:
        """Creates and configures the label for no entries found."""
        label = QLabel("<h2>No games found :(</h2>", self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        label.setVisible(False)  # Initially hidden
        return label

    def _populate_grid(self) -> None:
        """Populate the grid with app icons based on filtered games."""

        # Clear the current vertical layout properly
        for i in reversed(range(self.vertical_layout.count())):
            layout = self.vertical_layout.itemAt(i).layout()
            if layout is not None:
                # Delete each widget in the layout
                for j in reversed(range(layout.count())):
                    widget = layout.itemAt(j).widget()
                    if widget is not None:
                        widget.deleteLater()  # Free memory
                self.vertical_layout.removeItem(layout)  # Remove the layout itself

        # Clear old stretch factors
        while self.vertical_layout.count() > 0:
            item = self.vertical_layout.itemAt(self.vertical_layout.count() - 1)
            if item.layout() is None:  # This means it was a stretch item
                self.vertical_layout.removeItem(item)
            else:
                break  # Stop if we hit a layout item

        # Calculate the number of rows needed
        rows = (
            len(self.filtered_games) + self.cols - 1
        ) // self.cols  # Ceiling division

        for row in range(rows):
            row_layout = QHBoxLayout()  # Create a new horizontal layout for this row
            for col in range(self.cols):
                app_index = row * self.cols + col
                if app_index < len(self.filtered_games):
                    game = self.filtered_games[app_index]
                    app_name: str = game.title
                    game_id: str = game.id
                    icon_base_path = os.path.join(GAMES_DIRECTORY, game_id)

                    icon = self._get_game_icon_path(icon_base_path)

                    app_icon_widget: Union[AppLauncherCover, AppLauncherIcon]

                    if self.item_style in {"capsule", "capsule_wide"}:
                        app_icon_widget = AppLauncherCover(
                            app_name,
                            icon,
                            game_id,
                            game.favourite,
                            self,
                            game_id == self.selected_game_id,
                            size=QSize(self.item_width, self.item_height),
                        )
                    else:
                        app_icon_widget = AppLauncherIcon(
                            app_name,
                            icon,
                            game_id,
                            game.favourite,
                            self,
                            game_id == self.selected_game_id,
                        )

                    app_icon_widget.clicked.connect(
                        lambda game_id=game_id: self._select_game(game_id)
                    )
                    app_icon_widget.right_click.connect(
                        lambda game_id=game_id: self._select_game(game_id)
                    )
                    app_icon_widget.right_click.connect(
                        lambda game_id=app_icon_widget.game_id: GameEntryContextMenu(
                            self.game_list, game_id
                        )
                    )

                    row_layout.addWidget(app_icon_widget)

            self.vertical_layout.addLayout(row_layout)

        self.vertical_layout.addStretch(1)

        self.vertical_layout.update()

    def _select_game(self, game_id):
        self.game_list.selected_game = game_id

    def _get_game_icon_path(self, icon_base_path: str) -> str:
        """Helper function to get the icon path for a game."""
        for ext in ["png", "jpg", "jpeg", "ico"]:
            potential_icon_path = f"{icon_base_path}/{self.item_style}.{ext}"
            if os.path.exists(potential_icon_path):
                return potential_icon_path
        return ""

    def resizeEvent(self, event: Any) -> None:
        """Handle resize events to update the number of columns."""

        # If widget width has changed, update it and recompute grid layout
        new_width = self.width()
        if self.widget_width != new_width:
            self.widget_width = new_width

            button_width: int = self.item_width
            spacing: int = self.item_spacing  # Default spacing

            new_cols: int = max(1, new_width // (button_width + spacing))

            if new_cols != self.cols:  # Only repopulate if column count has changed
                self.cols = new_cols
                self._populate_grid()

        super().resizeEvent(event)

    def _filter_games(self, text: str) -> None:
        """Filter the games based on the search text."""
        text = text.strip().lower()
        if not text:  # If no search text, show all games
            self.sort_by_recent_checkbox.setEnabled(True)
            self.favourites_checkbox.setEnabled(True)
            self.sort_order_combobox.setEnabled(True)
            self.filtered_games = self.game_list.all_games
        else:
            # Filter games based on title containing the search text
            self.sort_by_recent_checkbox.setEnabled(False)
            self.favourites_checkbox.setEnabled(False)
            self.sort_order_combobox.setEnabled(False)
            all_games = self.game_list.all_games

            self.filtered_games = sorted(
                [game for game in all_games if text in game.title.lower()],
                key=lambda game: (game.title.lower().find(text), game.title.lower()),
            )

        # Show the "No games found" label if no games match, otherwise hide it
        self.no_entries_label.setVisible(len(self.filtered_games) == 0)

        self._populate_grid()

    def refresh(self) -> None:
        """Refresh the game grid display."""
        _current_list = self.game_list.all_games
        if self.filtered_games is _current_list:
            print("bye bye!")
            return
        self.filtered_games = _current_list
        self._populate_grid()

    def _get_widget_by_id(self, game_id: str):
        """Return the icon by game ID."""
        use_cover = True if self.item_style in {"capsule", "capsule_wide"} else False
        for i in range(self.vertical_layout.count()):
            layout = self.vertical_layout.itemAt(i).layout()
            if layout:
                for j in range(layout.count()):
                    widget = layout.itemAt(j).widget()
                    if (
                        isinstance(
                            widget,
                            AppLauncherIcon if not use_cover else AppLauncherCover,
                        )
                        and widget.game_id == game_id
                    ):
                        return widget
        return None

    def mousePressEvent(self, event):
        self.setFocus()

    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press events for navigating games."""
        if event.key() == Qt.Key_Left:
            self.game_list.select_previous()
        elif event.key() == Qt.Key_Right:
            self.game_list.select_next()
        else:
            super().keyPressEvent(event)
