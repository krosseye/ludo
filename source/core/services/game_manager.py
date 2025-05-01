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

from core.models import Game
from PySide6.QtCore import QObject

from .game_database_manager import GameDatabaseManager
from .process_manager import ProcessManager


class GameManager(QObject):
    def __init__(self, db_manager: GameDatabaseManager):
        super().__init__()
        self._db_manager = db_manager
        self.process_manager = ProcessManager()

    def mark_as_favourite(self, game_id: str, is_favourite: bool):
        """
        Update a game's favourite status via the database manager.

        Args:
            game_id (str): The ID of the game whose status is being updated.
            is_favourite (bool): The new favourite status.
        """
        self._db_manager.mark_as_favourite(game_id, is_favourite)

    def update_last_played(self, game_id: str, last_played: str):
        self._db_manager.update_last_played(game_id, last_played)

    def set_logo_position(self, game_id: str, position: str = "center"):
        self._db_manager.set_logo_position(game_id, position)

    def delete_game(self, game_id: str):
        """
        Delete a game from the model and database by its ID.

        Args:
            game_id (str): The ID of the game to delete.
        """
        self._db_manager.delete_game(game_id)

    def update_game(self, game_id: str, updated_game: Game):
        """
        Update an existing game's information via the database manager.

        Args:
            game_id (str): The ID of the game to update.
            updated_game (Game): The updated game object.
        """
        self._db_manager.update_game(game_id, updated_game)

    def add_game(self, game: Game) -> None:
        """
        Add a new game to the model via the database manager.

        Args:
            game (Game): The game object to add.
        """

        self._db_manager.add_game(game)
