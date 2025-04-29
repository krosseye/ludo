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
from typing import Optional

from core.services import GameListManager
from dialogs.GameEntryDialog import GameEntryDialog
from PySide6.QtGui import QCursor, QGuiApplication, QIcon
from PySide6.QtWidgets import QMenu, QWidgetAction
from widgets.components.play_button import PlayButton


class GameEntryContextMenu(QMenu):
    def __init__(self, game_list: GameListManager, game_id) -> None:
        super().__init__()
        self.game_list = game_list

        self.setContentsMargins(5, 5, 5, 5)

        game_info = self.game_list.find_game_by_id(game_id)
        browse_path = getattr(game_info, "browseDirectory", "")
        is_favourite = bool(getattr(game_info, "favourite", False))

        self._create_play_button_action(game_info)
        self.addSeparator()

        self._configure_favourite_action(game_id, is_favourite)
        self._configure_browse_action(browse_path)

        self._create_properties_action(game_id)
        self.exec_(QCursor.pos())

    def _create_play_button_action(self, game_info):
        """Create and add the Play button action."""
        play_button = PlayButton(game_info)
        play_button.clicked.connect(self.close)

        button_action = QWidgetAction(self)
        button_action.setDefaultWidget(play_button)
        self.addAction(button_action)

    def _configure_favourite_action(self, game_id: str, is_favourite: bool):
        """Configure the 'Add to Favourites' action based on the favourite status."""
        favourite_action = self.addAction("Add to &Favourites")
        favourite_action.setIcon(QIcon.fromTheme("emblem-favorite"))
        favourite_action.triggered.connect(
            lambda: self.game_list.game_manager.mark_as_favourite(
                game_id, not is_favourite
            )
        )

        favourite_action.setText(
            "Remove from &Favourites" if is_favourite else "Add to &Favourites"
        )

    def _configure_browse_action(self, browse_path: Optional[str]):
        """Configure the 'Browse Local Files' action."""
        browse_action = self.addAction(QIcon.fromTheme("folder"), "&Browse Local Files")

        if browse_path:
            browse_action.setEnabled(True)
            browse_action.triggered.connect(
                lambda: self._browse_local_files(browse_path)
            )
        else:
            browse_action.setEnabled(False)

    def _create_properties_action(self, game_id: str):
        """Create and add the 'Properties' action."""
        edit_action = self.addAction(
            QIcon.fromTheme("applications-games"), "&Properties..."
        )
        edit_action.triggered.connect(lambda: self._open_modify_dialog(game_id))

    def _browse_local_files(self, path: str):
        """Open the folder containing the game or its directory."""
        if os.path.isfile(path):
            path = os.path.dirname(path)

        try:
            self._open_path_in_system_explorer(path)
        except Exception as e:
            print(f"Failed to open path: {path}. Error: {e}")

    def _open_path_in_system_explorer(self, path: str):
        """Open the given path in the system's file explorer."""
        if os.name == "nt":  # Windows
            os.startfile(path)
        elif os.name == "posix":  # macOS and Linux
            self._open_path_on_unix_system(path)

    def _open_path_on_unix_system(self, path: str):
        """Open the given path in a macOS or Linux file explorer."""
        if os.uname().sysname == "Darwin":  # macOS
            os.system(f'open "{path}"')
        else:  # Linux
            os.system(f'xdg-open "{path}"')

    def _open_modify_dialog(self, game_id: str) -> None:
        """Open the GameEntryDialog to modify the selected game's details."""
        game_info = self.game_list.find_game_by_id(game_id)
        if game_info:
            modify_dialog = GameEntryDialog(self.game_list, game_id=game_id)

            screen_geometry = QGuiApplication.primaryScreen().availableGeometry()
            dialog_geometry = modify_dialog.geometry()
            dialog_x = (screen_geometry.width() - dialog_geometry.width()) // 2
            dialog_y = (screen_geometry.height() - dialog_geometry.height()) // 2

            modify_dialog.move(dialog_x, dialog_y)
            modify_dialog.exec()
