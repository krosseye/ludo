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
import subprocess
import webbrowser

from dialogs.about_dialog import AboutDialog
from dialogs.GameEntryDialog import GameEntryDialog
from dialogs.system_info_dialog import SystemInfoDialog
from models import AppConfig
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QSplitter,
    QVBoxLayout,
    QWidget,
)
from services import GameDatabaseManager, GameListManager
from widgets.GameCollectionWidgets import GameCollectionWidget
from widgets.GameInfoWidget import GameInfoWidget

CONFIG = AppConfig()
PREFERS_DARK = CONFIG.PREFERS_DARK_MODE
ICON_BASE_PATH = (
    os.path.join(CONFIG.RESOURCE_PATH, "icons", "dark")
    if PREFERS_DARK
    else os.path.join(CONFIG.RESOURCE_PATH, "icons", "light")
)


class MainWindow(QMainWindow):
    SPLITTER_SIZES = [300, 600]

    def __init__(self):
        super().__init__()

        self.database = GameDatabaseManager()
        self.game_list = GameListManager(self.database)
        self.app_title = CONFIG.APP_TITLE
        self._set_title(self.game_list.selected_game)

        self._setup_central_widget()
        self._create_menu()
        self._setup_layout()
        self.game_list.game_selected.connect(self._set_title)

    def _set_title(self, game_id=None):
        if game_id:
            game = self.game_list.find_game_by_id(game_id)
            self.setWindowTitle(str(game.title + " - " + self.app_title))
        else:
            self.setWindowTitle(self.app_title)

    def _setup_central_widget(self):
        """Set the central widget."""
        self._central_widget = QWidget(self)
        self.setCentralWidget(self._central_widget)

    def _create_menu(self):
        """Create the menu bar."""
        menubar = self.menuBar()

        self._create_library_menu(menubar)

        self._create_view_menu(menubar)

        if CONFIG.STEAM_FRIENDS_ENABLED:
            self._create_friends_actions(menubar)

        self._create_help_menu(menubar)

    def _create_friends_actions(self, menubar):
        self.open_friends_action = QAction("Friends", self)
        self.open_friends_action.triggered.connect(self._open_steam_friends)
        menubar.addAction(self.open_friends_action)

    def _open_steam_friends(self):
        # Try to open the Steam friends window via steam:// URL
        try:
            subprocess.run(["steam", "steam://open/friends/"], check=True)
        except FileNotFoundError:
            # Fallback: open via web browser if Steam is not installed or the command is not found
            webbrowser.open("steam://open/friends/")

    def _create_library_menu(self, menubar):
        """Create the Library menu in the menu bar."""
        file_menu = menubar.addMenu("Library")
        file_menu.addAction(
            self._create_action("Add &New Game...", self._open_game_dialog)
        )
        file_menu.addAction(
            self._create_action("Edit &Current Game...", self._edit_current_game)
        )
        file_menu.addSeparator()
        file_menu.addAction(self._create_action("&Exit", self.close))

    def _create_view_menu(self, menubar):
        """Create the View menu in the menu bar."""
        view_menu = menubar.addMenu("View")

        self._fullscreen_action = self._create_fullscreen_action()
        view_menu.addAction(self._fullscreen_action)
        view_menu.addSeparator()

        self._create_toggle_actions(view_menu)

    def _create_toggle_actions(self, view_menu):
        """Create actions to toggle visibility of the list and right widget."""
        self._toggle_list_view_action = self._create_toggle_action(
            "Show List", self._toggle_list_view, True
        )
        view_menu.addAction(self._toggle_list_view_action)

        self._toggle_right_widget_action = self._create_toggle_action(
            "Show Details", self._toggle_right_widget, True
        )
        view_menu.addAction(self._toggle_right_widget_action)

    def _create_help_menu(self, menubar):
        """Create the Help menu in the menu bar."""
        help_menu = menubar.addMenu("&Help")
        help_menu.addAction(
            self._create_action(
                "System &Information", self._show_system_info_dialog, icon="computer"
            )
        )
        help_menu.addSeparator()
        help_menu.addAction(
            self._create_action(
                f"&About {self.app_title}",
                self._show_about_dialog,
                icon="help-about",
            )
        )

        help_menu.addAction(
            self._create_action(
                "About &Qt",
                QApplication.aboutQt,
                icon=os.path.join(ICON_BASE_PATH, "qt.png"),
            )
        )
        help_menu.addSeparator()

        help_menu.addAction(
            self._create_action(
                "Open on &GitHub",
                lambda: webbrowser.open(CONFIG.GITHUB_URL),
                icon=os.path.join(ICON_BASE_PATH, "github.png"),
            )
        )

        # help_menu.addAction(
        #     self._create_action(
        #         "Support on &Ko-Fi",
        #         lambda: webbrowser.open("https://ko-fi.com/"),
        #         icon=os.path.join(CONFIG.RESOURCE_PATH, "icons", "ko-fi.png"),
        #     )
        # )

    def _create_action(self, text, slot, icon=None):
        """Utility to create an action."""
        action = QAction(text, self)

        if icon:
            # Check if the icon ends with a common image file extension
            if icon.lower().endswith((".png")):
                action.setIcon(QIcon(icon))  # Load icon from file path
            else:
                action.setIcon(QIcon.fromTheme(icon))  # Load icon from theme

        action.triggered.connect(slot)
        return action

    def _create_fullscreen_action(self):
        """Create the Fullscreen action."""
        action = QAction("Fullscreen", self)
        action.setCheckable(True)
        action.triggered.connect(self._toggle_fullscreen)
        return action

    def _create_toggle_action(self, text, slot, checked=False):
        """Create a toggleable action."""
        action = QAction(text, self)
        action.setCheckable(True)
        action.setChecked(checked)
        action.triggered.connect(slot)
        return action

    def _setup_layout(self):
        """Setup the layout for the main window."""
        self._splitter = QSplitter(Qt.Horizontal, self._central_widget)
        self._setup_list_view()
        self._setup_info_widget()
        self._splitter.setSizes(self.SPLITTER_SIZES)

        layout = QVBoxLayout(self._central_widget)
        layout.addWidget(self._splitter)
        layout.setStretch(1, 3)

    def _setup_list_view(self):
        """Setup GameCollectionWidget or GameGridWidget."""

        self._list_view_widget = GameCollectionWidget(self.game_list)
        self._splitter.addWidget(self._list_view_widget)
        self._splitter.setCollapsible(0, False)

    def _setup_info_widget(self):
        """Setup the right-side GameInfoWidget."""
        self._info_widget = GameInfoWidget(self.game_list)
        self._info_widget.setContentsMargins(0, 0, 0, 0)
        self._splitter.addWidget(self._info_widget)
        self._splitter.setCollapsible(1, False)

    def _open_game_dialog(self, game_id=None):
        """Open the Add Game Dialog."""
        dialog = GameEntryDialog(self.game_list, game_id=game_id, parent=self)
        dialog.exec()

    def _edit_current_game(self):
        """Edit the selected game."""
        self._open_game_dialog(self.game_list.selected_game)

    def _toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        if self.isFullScreen():
            self.showNormal()
            self._fullscreen_action.setChecked(False)
        else:
            self.showFullScreen()
            self._fullscreen_action.setChecked(True)

    def _toggle_list_view(self):
        """Toggle the visibility of the GameCollectionWidget."""
        self._toggle_visibility(self._list_view_widget, self._toggle_list_view_action)

    def _toggle_right_widget(self):
        """Toggle the visibility of the GameInfoWidget."""
        self._toggle_visibility(self._info_widget, self._toggle_right_widget_action)

    def _toggle_visibility(self, widget, action):
        """Toggle visibility of a widget and update the corresponding action."""
        widget.setVisible(not widget.isVisible())
        action.setChecked(widget.isVisible())
        self._update_list_view_width()

    def _update_list_view_width(self):
        """Update the ListView width based on the visibility of the right widget."""
        if self._info_widget.isVisible():
            self._list_view_widget.setMaximumWidth(self.width() // 2)
        else:
            self._list_view_widget.setMaximumWidth(self.width())

    def _show_system_info_dialog(self):
        """Show the system information dialog."""
        system_info_dialog = SystemInfoDialog()
        system_info_dialog.exec()

    def _show_about_dialog(self):
        """Show the About dialog."""
        about_dialog = AboutDialog()
        about_dialog.exec()

    def resizeEvent(self, event):
        """Handle resize event."""
        self._update_list_view_width()
        super().resizeEvent(event)
