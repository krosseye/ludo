#############################################################################
##
## Copyright (C) 2025 Killian-W.
## All rights reserved.
##
## This file is part of the Ludo project.
##
## Licensed under the MIT License.
## You may obtain a copy of the License at:
##     https://opensource.org/licenses/MIT
##
## This software is provided "as is," without warranty of any kind.
##
#############################################################################

import webbrowser

from core.api.runner import GameRunner
from core.models import Game
from PySide6.QtGui import QIcon


class WebLinkRunner(GameRunner):
    def __init__(self, game_data: Game):
        super().__init__(game_data)

    def get_runner_name(self) -> str:
        return "Web Link Runner"

    def run_game(self):
        target = self.game_data.executablePath.strip()
        if not self._validate_url():
            error_msg = f"Invalid URL: {target}"
            self.error_occurred.emit(error_msg)
            return

        try:
            webbrowser.open(target)
            self.game_started.emit()
        except Exception as e:
            self.error_occurred.emit(str(e))

    def _validate_url(self) -> bool:
        target = self.game_data.executablePath.strip().lower()
        return target.startswith("http://") or target.startswith("https://")

    def get_runner_icon(self) -> QIcon:
        return QIcon.fromTheme("applications-internet")

    def get_runner_version(self) -> str:
        return "1.0.0"
