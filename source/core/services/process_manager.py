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

from typing import Dict

from core.api.runner import GameRunner
from PySide6.QtCore import QObject


class ProcessManager(QObject):
    def __init__(self) -> None:
        super().__init__()
        self._processes: Dict[str, GameRunner] = {}

    def add_process(self, runner: GameRunner):
        """Only track runners that can be stopped."""
        if not runner.can_stop():
            return  # Ignore detached/unstoppable runners

        game_id = runner.game_data.id
        if game_id in self._processes:
            return  # Already tracked

        self._processes[game_id] = runner
        runner.game_stopped.connect(lambda _: self.remove_process(game_id))
        runner.error_occurred.connect(lambda _: self.remove_process(game_id))

    def remove_process(self, game_id: str):
        if game_id in self._processes:
            del self._processes[game_id]

    def get_runner(self, game_id: str) -> GameRunner | None:
        """Returns a runner only if it's trackable (can_stop() == True)."""
        return self._processes.get(game_id)

    def is_running(self, game_id: str) -> bool:
        """Returns True only if the runner is tracked AND running."""
        runner = self.get_runner(game_id)
        return runner.is_running() if runner else False  # runner.can_stop() is implied

    def stop_game(self, game_id: str):
        """Only attempts to stop if the runner is trackable."""
        runner = self.get_runner(game_id)
        if runner:
            runner.stop_game()  # can_stop() is implied
