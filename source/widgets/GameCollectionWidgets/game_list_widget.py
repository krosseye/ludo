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

import logging
import os

from core.app_config import app_config
from core.config import user_config
from PySide6.QtCore import (
    QMutex,
    QMutexLocker,
    QObject,
    QRunnable,
    QSize,
    Qt,
    QThreadPool,
    QTimer,
    Signal,
    Slot,
)
from PySide6.QtGui import QIcon, QKeyEvent, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
)
from utilities.generators import IconPixmap

from .context_menu import GameEntryContextMenu
from .list_item_widget import ListItemWidget

CONFIG = app_config

PREFERS_DARK_MODE = CONFIG.PREFERS_DARK_MODE

GAMES_DIRECTORY = os.path.join(CONFIG.USER_DATA_PATH, "games")

ITEM_SIZE = QSize(48, 48)

SCROLL_DELAY = 200
SEARCH_DELAY = 300

logger = logging.getLogger(__name__)


class GameListWidget(QListWidget):
    """
    A custom list widget that manages and displays the list from the game list manager.
    """

    left_clicked = Signal(str)
    right_clicked = Signal(str)

    def __init__(self, game_list_manager, parent=None):
        super().__init__()

        self.ICON_STYLE = user_config["LIST_STYLE"]
        self.ICON_SIZE = QSize(32, 32) if self.ICON_STYLE == "icon" else QSize(48, 32)

        self._game_list_manager = game_list_manager
        self._current_games = None
        self._loaded_widgets = set()

        self.thread_pool = QThreadPool()
        self._loaded_widgets_mutex = QMutex()

        self._search_debounce_timer = QTimer(self)
        self._search_debounce_timer.setSingleShot(True)
        self._search_debounce_timer.setInterval(SEARCH_DELAY)

        self._scroll_debounce_timer = QTimer(self)
        self._scroll_debounce_timer.setSingleShot(True)
        self._scroll_debounce_timer.setInterval(SCROLL_DELAY)

        self._search_bar = parent.search_bar
        self._sort_by_recent_checkbox = parent.sort_by_recent_checkbox
        self._favourites_checkbox = parent.favourites_checkbox
        self._sort_order_combobox = parent.sort_order_combobox

        self._connect_signals()
        self._setup_layout()
        self._update_game_list()

    def _connect_signals(self):
        self._search_debounce_timer.timeout.connect(
            lambda: self._filter_games_list(self._search_bar.text())
        )

        self._scroll_debounce_timer.timeout.connect(self._load_visible_icons)

        self._search_bar.search_text_changed.connect(
            lambda: self._search_debounce_timer.start(SEARCH_DELAY)
        )
        self._search_bar.cleared.connect(self._filter_games_list)

        self._game_list_manager.dataChanged.connect(self._refresh)
        self._game_list_manager.layoutChanged.connect(self._refresh)
        self._game_list_manager.game_selected.connect(self._select_game)

        self.currentItemChanged.connect(self._on_item_changed)
        self._item_changed_connected = True
        self.verticalScrollBar().valueChanged.connect(self._on_view_changed)
        self.itemClicked.connect(
            lambda game: self.left_clicked.emit(game.data(Qt.UserRole).id)
        )

    def _setup_layout(self):
        palette = self.palette()
        highlight_color = palette.highlight().color()

        hover_color = highlight_color
        hover_color.setAlpha(64)

        r, g, b, a = (
            hover_color.red(),
            hover_color.green(),
            hover_color.blue(),
            hover_color.alpha(),
        )

        self.setIconSize(self.ICON_SIZE)
        self.setFrameShape(QFrame.NoFrame)
        self.setAlternatingRowColors(user_config["ALTERNATE_LIST_ROW_COLORS"])
        self.setStyleSheet(f"""
            GameListWidget {{
                background-color: transparent;
                outline: none;
                }}
            GameListWidget::item{{
                background-color: transparent;
                border-radius: 5px;
                border: none;
                padding-left:4px;
                }}
            GameListWidget::item:selected{{
                border: 2px solid {highlight_color.name()};
            
                }}
            GameListWidget::item:hover{{
                background-color: rgba{r, g, b, a};
                }}
        """)

        self.no_games_label = QLabel("<h2>No games found :(</h2>")
        self.no_games_label.setWordWrap(True)
        self.no_games_label.setAlignment(Qt.AlignCenter)
        self.no_games_label.setVisible(False)

        self.setLayout(QVBoxLayout())
        self.layout().addStretch(1)
        self.layout().addWidget(self.no_games_label)
        self.layout().addStretch(2)

    def _filter_games_list(self, search_text=None):
        if not search_text:
            self._update_game_list()
            self._sort_by_recent_checkbox.setEnabled(True)
            self._favourites_checkbox.setEnabled(True)
            self._sort_order_combobox.setEnabled(True)
            self.no_games_label.setVisible(False)

        else:
            # Filter the games based on the search text
            self._sort_by_recent_checkbox.setEnabled(False)
            self._favourites_checkbox.setEnabled(False)
            self._sort_order_combobox.setEnabled(False)
            search_text = search_text.strip().lower()

            filtered_games = sorted(
                [
                    game
                    for game in self._game_list_manager.all_games
                    if search_text in game.title.lower()
                ],
                key=lambda game: (
                    game.title.lower().find(search_text),
                    game.title.lower(),
                ),
            )

            if filtered_games == self._current_games:
                return

            if filtered_games:
                self._update_game_list(filtered_games)
                self.no_games_label.setVisible(False)
            else:
                self._update_game_list(filtered_games)
                self.no_games_label.setVisible(True)

    def _load_visible_icons(self):
        """
        Load widgets for the items currently visible in the viewport.
        """

        if len(self._loaded_widgets) == self._game_list_manager.rowCount():
            return

        viewport_rect = self.viewport().rect()
        visible_items = [
            self.item(i)
            for i in range(self.count())
            if viewport_rect.intersects(self.visualItemRect(self.item(i)))
        ]

        for item in visible_items:
            game = item.data(Qt.UserRole)
            item.setText("")
            if game and game.id not in self._loaded_widgets:
                worker = WidgetLoaderWorker(
                    game.id, self._game_list_manager, self.ICON_STYLE, self.ICON_SIZE
                )
                worker.widget_ready.connect(self._set_item_widget)
                self.thread_pool.start(worker)

    @Slot(str, QPixmap, str, bool)
    def _set_item_widget(self, game_id, icon, title, is_favourite):
        with QMutexLocker(self._loaded_widgets_mutex):
            if game_id not in self._loaded_widgets:
                for index in range(self.count()):
                    item = self.item(index)
                    game = item.data(Qt.UserRole)
                    if game and game.id == game_id:
                        logger.debug(f"Widget created for {game.title}")

                        widget = ListItemWidget(
                            icon=icon,
                            text=title,
                            is_favourite=is_favourite,
                        )
                        self.setItemWidget(item, widget)
                        self._loaded_widgets.add(game_id)
                        break

    def _refresh(self):
        """
        Refresh the list widget to show the latest data from the GameListManager.
        """
        self._update_game_list(None)

    def _update_game_list(self, filtered_games=None):
        """
        Refresh the list widget to show data from the GameListManager with an optional query.
        Handles additions, removals, reordering of items, and game name changes.
        """

        if filtered_games is None:
            games = self._game_list_manager.all_games
        else:
            games = filtered_games

        # Skip if no changes in content or order
        if self._current_games is games:
            return

        self.setUpdatesEnabled(False)
        if self._item_changed_connected:
            self.currentItemChanged.disconnect(self._on_item_changed)
            self._item_changed_connected = False

        try:
            id_to_item_map = {
                item.data(Qt.UserRole).id: item
                for item in (self.item(i) for i in range(self.count()))
            }

            # Update _loaded_widgets dynamically
            existing_ids = set(id_to_item_map.keys())
            self._loaded_widgets.intersection_update(existing_ids)

            # Remove games no longer in the list
            current_game_ids = {game.id for game in games}
            self._remove_deleted_games(existing_ids, current_game_ids)

            # Add or reorder games
            for new_index, game in enumerate(games):
                existing_item = id_to_item_map.get(game.id)

                if existing_item:
                    self._reorder_and_update_item(existing_item, game, new_index)
                else:
                    self._add_new_game_item(game, new_index)

            self._current_games = games
            self._load_visible_icons()

        finally:
            if filtered_games is None:
                self._select_game(self._game_list_manager.selected_game)
            else:
                self.setCurrentItem(None)
            self.setUpdatesEnabled(True)
            if not self._item_changed_connected:
                self.currentItemChanged.connect(self._on_item_changed)
                self._item_changed_connected = True

            if self._game_list_manager.rowCount() <= 0:
                self.no_games_label.setVisible(True)
            else:
                self.no_games_label.setVisible(False)

    def _remove_deleted_games(self, existing_ids, current_game_ids):
        """Remove items from the widget if their IDs are no longer in the game list."""
        for i in reversed(range(self.count())):
            item = self.item(i)
            game_id = item.data(Qt.UserRole).id
            if game_id not in current_game_ids:
                self.takeItem(i)
                self._loaded_widgets.discard(game_id)

    def _reorder_and_update_item(self, existing_item, game, new_index):
        """Reorder an existing item and update its properties if necessary."""
        current_index = self.row(existing_item)
        if current_index != new_index:
            self.takeItem(current_index)
            self.insertItem(new_index, existing_item)

        existing_game = existing_item.data(Qt.UserRole)
        existing_item.setText(game.title)
        existing_game.title = game.title
        self._loaded_widgets.discard(game.id)

    def _add_new_game_item(self, game, new_index):
        """Add a new game to the widget."""
        item = QListWidgetItem(game.title)
        item.setData(Qt.UserRole, game)
        item.setSizeHint(ITEM_SIZE)
        self.insertItem(new_index, item)

    def _on_item_changed(self, current, previous):
        if current:
            game = current.data(Qt.UserRole)
            if game:
                self._game_list_manager.selected_game = game.id
                logger.debug(
                    "Selected game changed to: %s (ID: %s)", game.title, game.id
                )

    def _select_game(self, game_id):
        """
        Programmatically select a game by its ID.

        Args:
            game_id (str): The ID of the game to select.
        """
        for index in range(self.count()):
            item = self.item(index)
            game = item.data(Qt.UserRole)
            if game and game.id == game_id:
                self.setCurrentItem(item)
                self.scrollToItem(item)
                logger.debug("Game selected: %s (ID: %s)", game.title, game.id)
                break

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Left:
            self._game_list_manager.select_previous()
        elif event.key() == Qt.Key_Right:
            self._game_list_manager.select_next()
        else:
            super().keyPressEvent(event)

    def contextMenuEvent(self, event):
        item = self.itemAt(event.pos())
        if item:
            game = item.data(Qt.UserRole)
            self.right_clicked.emit(game.id)
            if game:
                logger.debug(
                    "Opening context menu for game: %s (ID: %s)", game.title, game.id
                )
                GameEntryContextMenu(self._game_list_manager, game.id)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._on_view_changed()

    def _on_view_changed(self):
        self._scroll_debounce_timer.start(SCROLL_DELAY)
        logger.debug("Scroll event processed, debounce timer started.")


class WidgetLoaderWorker(QRunnable, QObject):
    """
    A worker class to load game widgets asynchronously.
    """

    widget_ready = Signal(str, QPixmap, str, bool)

    def __init__(self, game_id, game_list_manager, icon_style, icon_size):
        super().__init__()
        QObject.__init__(self)
        self.game_id = game_id
        self.game_list_manager = game_list_manager

        self.icon_style = icon_style
        self.icon_size = icon_size

    def run(self):
        game = self.game_list_manager.find_game_by_id(self.game_id)
        icon = self.create_icon(game).pixmap(self.icon_size)
        self.widget_ready.emit(game.id, icon, game.title, game.favourite)

    def create_icon(self, game):
        """
        Create or load an icon for a given game.

        Args:
            game: The game object for which to create/load an icon.

        Returns:
            QIcon: The icon representing the game.
        """
        try:
            icon_base_path = os.path.join(GAMES_DIRECTORY, game.id)
            icon_path = None

            for ext in ["png", "jpg", "jpeg", "ico"]:
                potential_icon_path = f"{icon_base_path}/{self.icon_style}.{ext}"
                if os.path.exists(potential_icon_path):
                    icon_path = potential_icon_path
                    break

            if not icon_path:
                icon_path = IconPixmap(
                    title=game.title,
                    width=self.icon_size.width(),
                    height=self.icon_size.height(),
                )

            icon = QIcon(icon_path)
            logger.debug("Created icon for game: %s (ID: %s)", game.title, game.id)
            return icon

        except Exception as e:
            logger.error(f"Error creating icon for {game.title}: {e}")
            return QIcon()
