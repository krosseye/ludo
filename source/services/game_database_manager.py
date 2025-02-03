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
from datetime import datetime

from models import AppConfig
from models.game import Game
from PySide6.QtCore import QObject, Signal
from PySide6.QtSql import QSqlDatabase, QSqlQuery

CONFIG = AppConfig()
DB_PATH = os.path.join(CONFIG.USER_DATA_PATH, "games.db")
DEBUG_LEVEL = CONFIG.DEBUG_LEVELS["GameDatabaseManager"]

logging.basicConfig(level=DEBUG_LEVEL)
logger = logging.getLogger("GameDatabaseManager")


class GameDatabaseManager(QObject):
    game_added = Signal(Game)
    game_updated = Signal(str, Game)
    game_deleted = Signal(str)
    game_favourited = Signal(str, bool)
    game_last_played_updated = Signal(str, str)

    CREATE_TABLE_QUERY = """
          CREATE TABLE IF NOT EXISTS games (
              id TEXT PRIMARY KEY,
              title TEXT,
              sortTitle TEXT,
              favourite INTEGER DEFAULT 0,
              starRating REAL,
              developer TEXT,
              publisher TEXT,
              year INTEGER,
              description TEXT,
              executablePath TEXT,
              workingDirectory TEXT,
              launchOptions TEXT,
              browseDirectory TEXT,
              lastPlayed TEXT,
              sessionsPlayed INTEGER DEFAULT 0,
              playtime REAL DEFAULT 0.0
          )
      """

    SELECT_ALL_GAMES_QUERY = "SELECT * FROM games"

    SELECT_GAME_BY_ID_QUERY = "SELECT * FROM games WHERE id = ?"

    INSERT_GAME_QUERY = """
        INSERT INTO games (
            id, 
            title, 
            sortTitle, 
            favourite, 
            starRating, 
            developer, 
            publisher, 
            year, 
            description, 
            executablePath, 
            workingDirectory, 
            launchOptions, 
            browseDirectory, 
            lastPlayed, 
            sessionsPlayed, 
            playtime
            )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    UPDATE_GAME_QUERY = """
        UPDATE games SET 
            title = ?, 
            sortTitle = ?, 
            favourite = ?, 
            starRating = ?, 
            developer = ?, 
            publisher = ?, 
            year = ?, 
            description = ?, 
            executablePath = ?, 
            workingDirectory = ?, 
            launchOptions = ?, 
            browseDirectory = ?, 
            lastPlayed = ?, 
            sessionsPlayed = ?, 
            playtime = ?
        WHERE id = ?
    """

    DELETE_GAME_QUERY = "DELETE FROM games WHERE id = ?"

    COUNT_GAME_BY_ID_QUERY = "SELECT COUNT(1) FROM games WHERE id = ?"

    UPDATE_FAVOURITE_QUERY = "UPDATE games SET favourite = ? WHERE id = ?"

    UPDATE_LAST_PLAYED_QUERY = "UPDATE games SET lastPlayed = ? WHERE id = ?"

    def __init__(self, db_path=DB_PATH):
        super().__init__()
        self.db_path = os.path.abspath(db_path)

        # Ensure the directory exists
        db_dir = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir):
            try:
                os.makedirs(db_dir, exist_ok=True)
                logger.info(f"Created missing directory: {db_dir}")
            except OSError as e:
                error_msg = f"Failed to create directory {db_dir}: {e}"
                logger.error(error_msg)
                raise

        self.db = self._setup_qsql_database()
        self._create_table()

    def __enter__(self):
        if not self.db.isOpen():
            if not self.db.open():
                error_msg = (
                    "Failed to open database connection during context management."
                )
                logger.error(error_msg)
                raise RuntimeError(error_msg)
            logger.debug("Database connection opened.")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.db.isOpen():
            self.db.close()
            logger.debug("Database connection closed.")

    def _setup_qsql_database(self):
        try:
            db = QSqlDatabase.addDatabase("QSQLITE")
            db.setDatabaseName(self.db_path)
            if not db.open():
                error_msg = f"Failed to open database at {self.db_path}: {db.lastError().text()}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
            logger.info(f"Successfully connected to database at {self.db_path}")
            return db
        except Exception as e:
            logger.exception("Error setting up database connection.")
            raise

    def _create_table(self):
        try:
            with self:
                self._execute_query(self.CREATE_TABLE_QUERY)
                logger.info("Games table created or already exists.")
        except Exception as e:
            logger.exception("Failed to create the games table.")
            raise

    def _execute_query(self, query_text, values=None):
        query = QSqlQuery(self.db)
        try:
            query.prepare(query_text)
            if values:
                for value in values:
                    query.addBindValue(value)
            if not query.exec():
                error_msg = f"Database query failed: {query.lastError().text()}"
                logger.error(f"Query failed: {query_text}, Values: {values}")
                raise RuntimeError(error_msg)
            logger.debug(f"Query executed successfully: {query_text}, Values: {values}")
            return query
        except Exception as e:
            logger.exception(f"Error executing query: {query_text}, Values: {values}")
            raise

    def _map_query_to_game(self, query):
        try:
            return Game(
                id=query.value("id"),
                title=query.value("title"),
                sortTitle=query.value("sortTitle"),
                favourite=bool(query.value("favourite")),
                starRating=float(query.value("starRating")),
                developer=query.value("developer"),
                publisher=query.value("publisher"),
                year=query.value("year"),
                description=query.value("description"),
                executablePath=query.value("executablePath"),
                workingDirectory=query.value("workingDirectory"),
                launchOptions=query.value("launchOptions"),
                browseDirectory=query.value("browseDirectory"),
                lastPlayed=query.value("lastPlayed"),
                sessionsPlayed=int(query.value("sessionsPlayed")),
                playtime=float(query.value("playtime")),
            )
        except Exception as e:
            logger.exception("Failed to map query result to Game object.")
            raise

    def get_game_by_id(self, game_id: str) -> Game | None:
        try:
            with self:
                query = self._execute_query(self.SELECT_GAME_BY_ID_QUERY, [game_id])
                if query.next():
                    logger.info(f"Game found with ID: {game_id}")
                    return self._map_query_to_game(query)
            logger.warning(f"No game found with ID: {game_id}")
            return None
        except Exception as e:
            logger.exception(f"Error retrieving game by ID: {game_id}")
            raise

    def all_games(self) -> list[Game]:
        try:
            with self:
                query = self._execute_query(self.SELECT_ALL_GAMES_QUERY)
                self.games = []
                while query.next():
                    self.games.append(self._map_query_to_game(query))
                logger.info(f"Loaded {len(self.games)} games from the database.")
        except Exception as e:
            logger.exception("Error retrieving games from the database.")
            raise

        return self.games

    def add_game(self, game: Game):
        try:
            with self:
                values = [
                    game.id,
                    game.title,
                    game.sortTitle,
                    int(game.favourite),
                    float(game.starRating),
                    game.developer,
                    game.publisher,
                    game.year,
                    game.description,
                    game.executablePath,
                    game.workingDirectory,
                    game.launchOptions,
                    game.browseDirectory,
                    game.lastPlayed,
                    int(game.sessionsPlayed),
                    float(game.playtime),
                ]
                self._execute_query(self.INSERT_GAME_QUERY, values)
                self.game_added.emit(game)
                logger.info(
                    f"Game added to database (id={game.id}, title={game.title})"
                )
        except Exception as e:
            logger.exception(
                f"Failed to add game to database (id={game.id}, title={game.title})."
            )
            raise

    def update_game(self, game_id: str, updated_game: Game):
        try:
            with self:
                values = [
                    updated_game.title,
                    updated_game.sortTitle,
                    int(updated_game.favourite),
                    float(updated_game.starRating),
                    updated_game.developer,
                    updated_game.publisher,
                    updated_game.year,
                    updated_game.description,
                    updated_game.executablePath,
                    updated_game.workingDirectory,
                    updated_game.launchOptions,
                    updated_game.browseDirectory,
                    updated_game.lastPlayed,
                    int(updated_game.sessionsPlayed),
                    float(updated_game.playtime),
                    game_id,
                ]
                self._execute_query(self.UPDATE_GAME_QUERY, values)
                self.game_updated.emit(game_id, updated_game)
                logger.info(
                    f"Game updated in database (id={updated_game.id}, title={updated_game.title})"
                )
        except Exception as e:
            logger.exception(f"Failed to update game in database (id={game_id}).")
            raise

    def game_exists(self, game_id: str) -> bool:
        try:
            with self:
                query = self._execute_query(self.COUNT_GAME_BY_ID_QUERY, [game_id])
                if query.next():
                    exists = query.value(0) > 0
                    logger.info(f"Game exists check for ID {game_id}: {exists}")
                    return exists
                else:
                    logger.warning(
                        f"Game exists check failed to return a result for ID {game_id}."
                    )
                    return False
        except Exception as e:
            logger.exception(f"Error checking if game exists (id={game_id}).")
            raise

    def delete_game(self, game_id: str):
        try:
            with self:
                query = self._execute_query(self.DELETE_GAME_QUERY, [game_id])
                if query.numRowsAffected() == 0:
                    error_msg = f"Game with ID {game_id} not found."
                    logger.error(error_msg)
                    raise ValueError(error_msg)
                self.game_deleted.emit(game_id)
                logger.info(f"Signal Fired: Game deleted from database (id={game_id})")
        except Exception as e:
            logger.exception(f"Failed to delete game from database (id={game_id}).")
            raise

    def mark_as_favourite(self, game_id: str, is_favourite: bool):
        try:
            with self:
                self._execute_query(
                    self.UPDATE_FAVOURITE_QUERY, [int(is_favourite), game_id]
                )
                self.game_favourited.emit(game_id, is_favourite)
                logger.info(
                    f"Signal Fired: Game favourited (id={game_id}, favourite={is_favourite})"
                )
        except Exception as e:
            logger.exception(
                f"Failed to update favourite status (id={game_id}, favourite={is_favourite})."
            )
            raise

    def update_last_played(self, game_id: str, last_played):
        try:
            if not isinstance(last_played, datetime):
                error_msg = f"Invalid datetime object provided: {last_played}"
                logger.error(error_msg)
                raise ValueError(error_msg)

            last_played_str = last_played.strftime("%Y/%m/%d %H:%M:%S")

            with self:
                self._execute_query(
                    self.UPDATE_LAST_PLAYED_QUERY, [last_played_str, game_id]
                )
                self.game_last_played_updated.emit(game_id, last_played_str)
                logger.info(
                    f"Updated lastPlayed for game (id={game_id}) to {last_played_str}"
                )
        except Exception as e:
            logger.exception(f"Failed to update lastPlayed for game (id={game_id}).")
            raise
