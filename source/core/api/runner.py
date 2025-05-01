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
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget


class GameRunner(QObject):
    """
    Base class for game runners.

    Subclasses must implement core functionality such as `get_runner_name()`, `run_game()`,
    and optionally implement stopping and configuration behavior depending on their capabilities.

    Signals:
        - game_started: Emitted when a game is successfully launched.
        - game_stopped (int): Emitted when the game process stops with an exit code.
        - error_occurred (str): Emitted when an error occurs during game launch or execution.
    """

    game_started = Signal()
    game_stopped = Signal(int)
    error_occurred = Signal(str)

    def __init__(self, game_data: Game):
        super().__init__()
        self.game_data = game_data
        self.process = None

    def get_runner_name(self) -> str:
        """
        [REQUIRED]

        Return the display name of the runner.
        """
        raise NotImplementedError

    def get_runner_icon(self) -> QIcon:
        """
        [OPTIONAL]

        Return QIcon for the runner.
        """
        return QIcon.fromTheme("application-x-executable")

    def get_runner_version(self) -> str:
        """
        [OPTIONAL]

        Return version string of the runner.
        """
        return "1.0.0"

    def run_game(self):
        """
        [REQUIRED]

        Launch the game process.
        """
        raise NotImplementedError

    def can_stop(self) -> bool:
        """
        [OPTIONAL]

        Return `True` if this runner supports stopping the game.
        """
        return False

    def stop_game(self) -> bool:
        """
        [REQUIRED IF `can_stop()` RETURNS TRUE]

        Attempt to stop the game process.

        Returns `True` if successful, `False` otherwise.
        """
        raise NotImplementedError

    def is_running(self) -> bool:
        """
        [REQUIRED IF `can_stop()` RETURNS TRUE]

        Return whether the game is currently running.

        Returns `True` if running, `False` otherwise.
        """
        raise NotImplementedError

    def has_config_widget(self) -> bool:
        """
        [OPTIONAL]

        Return `True` if a config widget is available.
        """
        return False

    def get_config_widget(self) -> QWidget:
        """
        [REQUIRED IF `has_config_widget()` RETURNS TRUE]

        Provide the config widget for the runner.
        """
        raise NotImplementedError

    def can_validate_game(self) -> bool:
        """
        [OPTIONAL]

        Return `True` if this runner supports game validation.
        """
        return False

    def validate_game(self) -> bool:
        """
        [REQUIRED IF `can_validate()` RETURNS TRUE]

        Return True if the game is valid/configured correctly.
        """
        raise NotImplementedError
