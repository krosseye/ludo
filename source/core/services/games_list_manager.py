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
from dataclasses import replace
from typing import Optional

from core.app_config import app_config
from core.config import user_config
from core.models import Game
from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt, Signal
from PySide6.QtGui import QIcon

from .game_manager import GameManager

CONFIG = app_config
GAMES_DIRECTORY = os.path.join(CONFIG.USER_DATA_PATH, "games")

logger = logging.getLogger("GameListManager")


class GameListManager(QAbstractListModel):
    game_selected = Signal(str)

    def __init__(self, game_db_manager) -> None:
        super().__init__()
        self._game_db_manager = game_db_manager
        self.game_manager = GameManager(self._game_db_manager)
        self._games: list[Game] = []
        self._current_sort_order = Qt.AscendingOrder
        self._selected_game_id: Optional[str] = None
        self._group_favourites: bool = user_config["SORT_FAVOURITES_FIRST"]
        self._sort_by_recent: bool = user_config["SORT_BY_RECENTLY_PLAYED"]

        self._load_games()
        self.selected_game = self._games[0].id if self._games else None

        self._game_db_manager.game_added.connect(self._on_game_added)
        self._game_db_manager.game_updated.connect(self._on_game_updated)
        self._game_db_manager.game_last_played_updated.connect(
            self._on_last_played_updated
        )
        self._game_db_manager.game_deleted.connect(self._on_game_deleted)
        self._game_db_manager.game_favourited.connect(self._on_favourite_changed)
        self.dataChanged.connect(lambda: logger.debug("List data changed."))
        self.layoutChanged.connect(lambda: logger.debug("List layout changed."))

    @property
    def all_games(self) -> list[Game]:
        """
        Retrieve all games currently loaded in the model.

        Returns:
            list[Game]: A list of all games in the model.
        """

        return list(self._games)

    @property
    def selected_game(self) -> Optional[str]:
        """
        Retrieve the currently selected game's ID.

        Returns:
            str or None: The ID of the selected game, or None if no game is selected.
        """

        return self._selected_game_id

    @selected_game.setter
    def selected_game(self, game_id: str) -> None:
        """
        Set the selected game by its ID.

        Args:
            game_id (str): The ID of the game to select.

        Emits:
            game_selected: After successfully selecting a game.
        """

        try:
            game = self.find_game_by_id(game_id)
            if game:
                if self._selected_game_id != game_id:
                    self._selected_game_id = game.id
                    self.game_selected.emit(game.id)
                    logger.debug(f"Game selected: {game.id} ({game.title})")
        except Exception as e:
            logger.error(f"Error setting selected game ID {game_id}: {str(e)}")

    @property
    def sort_order(self) -> Qt.SortOrder:
        """
        Get the current sort order of the games list.

        Returns:
            Qt.SortOrder: The current sort order.
        """
        return self._current_sort_order

    @sort_order.setter
    def sort_order(self, sort_order: Qt.SortOrder) -> None:
        """
        Set a new sort order for the games list and reload the games.

        Args:
            sort_order (Qt.SortOrder): The new sort order.
        """

        try:
            if self._current_sort_order != sort_order:
                self._current_sort_order = sort_order
                self._load_games()
                logger.debug(f"Sort order changed (now: {self._current_sort_order})")
        except Exception as e:
            logger.error(f"Error setting sort order: {str(e)}")

    @property
    def group_favourites(self) -> bool:
        return self._group_favourites

    @group_favourites.setter
    def group_favourites(self, value: bool) -> None:
        try:
            self._group_favourites = value
            self._load_games()
            logger.debug(f"Group favourites toggled (now: {self._group_favourites})")
        except Exception as e:
            logger.error(f"Error toggling favourites group: {str(e)}")

    @property
    def sort_by_recent(self) -> bool:
        return self._sort_by_recent

    @sort_by_recent.setter
    def sort_by_recent(self, value: bool) -> None:
        try:
            self._sort_by_recent = value
            self._load_games()
            logger.debug(f"Sort by recent changed: {bool(value)}")
        except Exception as e:
            logger.error(f"Error sorting by recent: {str(e)}")

    def _on_game_added(self, game_data: Game) -> None:
        """
        Handle the addition of a new game to the model.

        Args:
            game_data (Game): The game object that was added.
        """

        try:
            self.beginInsertRows(QModelIndex(), len(self._games), len(self._games))
            self._games.append(game_data)
            self.endInsertRows()
            self.layoutChanged.emit()
            self._apply_sorting(self._games)
            self.selected_game = game_data.id
        except Exception as e:
            logger.error(f"Error adding game: {str(e)}")

    def _on_game_updated(self, game_id: str, updated_data: Game) -> None:
        """
        Handle updates to an existing game in the model.

        Args:
            game_id (str): The ID of the game being updated.
            updated_data (Game): The updated game data.
        """

        try:
            game = next((g for g in self._games if g.id == game_id), None)
            if game:
                if game != updated_data:
                    updated_game = replace(game, **updated_data.__dict__)
                    index = self._games.index(game)
                    self._games[index] = updated_game
                    self.dataChanged.emit(self.index(index), self.index(index))
                self._apply_sorting(self._games)
            else:
                logger.warning(f"Game not found for update: {game_id}")
        except Exception as e:
            logger.error(f"Error updating game ID {game_id}: {str(e)}")

    def _on_game_deleted(self, game_id: str) -> None:
        """
        Handle the deletion of a game from the model.

        Args:
            game_id (str): The ID of the game being deleted.
        """

        try:
            for row, game in enumerate(self._games):
                if game.id == game_id:
                    self.beginRemoveRows(QModelIndex(), row, row)
                    self._games.pop(row)
                    self.endRemoveRows()

                    # Determine the next game to select
                    if row < len(self._games):  # If there is a next game
                        next_game_id = self._games[row].id
                    elif row > 0:  # If there is a previous game
                        next_game_id = self._games[row - 1].id
                    else:  # No games left
                        next_game_id = None

                    self.selected_game = next_game_id
                    self.layoutChanged.emit()
                    break
            self._apply_sorting(self._games)
        except Exception as e:
            logger.error(f"Error deleting game ID {game_id}: {str(e)}")

    def _on_favourite_changed(self, game_id: str, is_favourite: bool) -> None:
        """
        Handle changes to a game's favourite status.

        Args:
            game_id (str): The ID of the game whose favourite status changed.
            is_favourite (bool): The new favourite status.
        """

        try:
            for row, game in enumerate(self._games):
                if game.id == game_id:
                    game.favourite = is_favourite
                    self.dataChanged.emit(self.index(row), self.index(row))
                    self._apply_sorting(self._games)
                    logger.debug(
                        f"Game favourited (id={game_id}, favourite={is_favourite})"
                    )
                    break
        except Exception as e:
            logger.error(
                f"Error changing favourite status for game ID {game_id}: {str(e)}"
            )

    def _on_last_played_updated(self, game_id: str, last_played_str: str) -> None:
        """
        Handle updates to a game's last played timestamp.

        Args:
            game_id (str): The ID of the game being updated.
            last_played_str (str): The new last played timestamp as a string.
        """
        try:
            for row, game in enumerate(self._games):
                if game.id == game_id:
                    game.lastPlayed = last_played_str
                    self.dataChanged.emit(self.index(row), self.index(row))
                    self._apply_sorting(self._games)
                    logger.debug(
                        f"Game last played updated (id={game_id}, lastPlayed={last_played_str})"
                    )
                    break
        except Exception as e:
            logger.error(f"Error updating last played for game ID {game_id}: {str(e)}")

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._games) if not parent.isValid() else 0

    def data(self, index, role):
        if not index.isValid() or index.row() >= len(self._games):
            return None

        game = self._games[index.row()]

        try:
            if role == Qt.DisplayRole:
                return game.title
            elif role == Qt.DecorationRole:
                return self._fetch_game_icon(game)
            elif role == Qt.UserRole:
                return game
            else:
                logger.warning(f"Unsupported role: {role} for game ID {game.id}")
                return None
        except Exception as e:
            logger.error(
                f"Error retrieving data for game ID {game.id}, role {role}: {str(e)}"
            )
            return None

    def _load_games(self) -> None:
        """
        Populate the model with games retrieved from the database manager.

        This method fetches all games from the database, sorts them, and updates the model.
        """

        try:
            games = self._game_db_manager.all_games()
            self._apply_sorting(games)
            logger.info(f"Populated games list with {len(games)} games.")
        except Exception as e:
            logger.error(f"Error populating games list: {str(e)}")

    def _apply_sorting(self, games: list[Game]) -> None:
        """
        Sort the list of games based on the current sort order, sorting preference,
        and grouping preference.

        Args:
            games (list[Game]): The list of games to sort. If None, fetches games from the database.
        """
        try:
            if games is None:
                games = self._game_db_manager.all_games()

            def sort_key(game: Game):
                last_played = (
                    game.lastPlayed if game.lastPlayed is not None else float("-inf")
                )
                return last_played if self._sort_by_recent else game.sortTitle.lower()

            if self._group_favourites:
                favorites = [game for game in games if game.favourite]
                non_favorites = [game for game in games if not game.favourite]

                favorites.sort(
                    key=sort_key,
                    reverse=(
                        self._current_sort_order == Qt.AscendingOrder
                        if self._sort_by_recent
                        else self._current_sort_order == Qt.DescendingOrder
                    ),
                )
                non_favorites.sort(
                    key=sort_key,
                    reverse=(
                        self._current_sort_order == Qt.AscendingOrder
                        if self._sort_by_recent
                        else self._current_sort_order == Qt.DescendingOrder
                    ),
                )

                self._games = favorites + non_favorites
            else:
                self._games = sorted(
                    games,
                    key=sort_key,
                    reverse=(
                        self._current_sort_order == Qt.AscendingOrder
                        if self._sort_by_recent
                        else self._current_sort_order == Qt.DescendingOrder
                    ),
                )
            self.layoutChanged.emit()
            logger.debug("Games sorted successfully.")
        except Exception as e:
            logger.error(f"Error sorting games: {str(e)}")

    def _fetch_game_icon(self, game: Game) -> QIcon:
        """
        Retrieve the icon associated with a game.

        Args:
            game (Game): The game object for which the icon is being retrieved.

        Returns:
            QIcon: The game's icon if found; otherwise, a default icon.
        """

        try:
            icon_path = os.path.join(GAMES_DIRECTORY, game.id, "icon")
            return QIcon(icon_path)
        except Exception as e:
            logger.error(f"Error retrieving icon for game ID {game.id}: {str(e)}")
            return QIcon()

    def find_game_by_id(self, game_id: str) -> Game | None:
        """
        Retrieve a game by its ID.

        Args:
            game_id (str): The ID of the game to retrieve.

        Returns:
            Game or None: The game object if found; otherwise, None.
        """

        try:
            game = next((game for game in self._games if game.id == game_id), None)
            if game is None:
                logger.warning(f"Game not found for ID {game_id}")
            return game
        except Exception as e:
            logger.error(f"Error retrieving game by ID {game_id}: {str(e)}")
            return None

    def has_game(self, game_id: str) -> bool:
        return self._game_db_manager.game_exists(game_id)

    def select_next(self) -> None:
        """
        Select the next game in the list.

        If the current selection is the last game, wrap around to the first game.
        If no game is selected, select the first game.
        """
        try:
            if not self._games:
                logger.warning("Cannot select next: No games in the list.")
                return

            if self._selected_game_id is None:
                self.selected_game = self._games[0].id
            else:
                current_index = next(
                    (
                        i
                        for i, g in enumerate(self._games)
                        if g.id == self._selected_game_id
                    ),
                    -1,
                )

                if current_index == -1:
                    logger.warning(
                        "Current selected game not found in list. Selecting the first game."
                    )
                    self.selected_game = self._games[0].id
                else:
                    next_index = (current_index + 1) % len(self._games)
                    self.selected_game = self._games[next_index].id
        except Exception as e:
            logger.error(f"Error selecting next game: {str(e)}")

    def select_previous(self) -> None:
        """
        Select the previous game in the list.

        If the current selection is the first game, wrap around to the last game.
        If no game is selected, select the first game.
        """
        try:
            if not self._games:
                logger.warning("Cannot select previous: No games in the list.")
                return

            if self._selected_game_id is None:
                self.selected_game = self._games[0].id
            else:
                current_index = next(
                    (
                        i
                        for i, g in enumerate(self._games)
                        if g.id == self._selected_game_id
                    ),
                    -1,
                )

                if current_index == -1:
                    logger.warning(
                        "Current selected game not found in list. Selecting the first game."
                    )
                    self.selected_game = self._games[0].id
                else:
                    previous_index = (current_index - 1 + len(self._games)) % len(
                        self._games
                    )
                    self.selected_game = self._games[previous_index].id
        except Exception as e:
            logger.error(f"Error selecting previous game: {str(e)}")
