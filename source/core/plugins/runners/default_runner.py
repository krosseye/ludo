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

import os
import shlex
import time

from core.api.runner import GameRunner
from core.models import Game
from PySide6.QtCore import QProcess

DETACHED_MODE = False
KILL_TIMEOUT = 5000  # ms


class DefaultRunner(GameRunner):
    def __init__(self, game_data: Game):
        super().__init__(game_data)
        self._process = None
        self._start_time = None

    def get_runner_name(self) -> str:
        return "Default Runner"

    def is_running(self) -> bool:
        if DETACHED_MODE:
            return False
        return self._process is not None and self._process.state() == QProcess.Running

    def run_game(self):
        try:
            command = self._create_command(
                self.game_data.executablePath, self.game_data.launchOptions
            )

            if not command:
                raise ValueError("No valid command provided to run the game.")

            target = command[0]
            args = command[1:]

            # Determine working directory
            working_dir = self.game_data.workingDirectory
            if not working_dir:
                working_dir = os.path.dirname(target) if os.path.isfile(target) else ""

            if not working_dir:
                raise ValueError("No working directory could be determined.")

            self._process = QProcess(self)
            self._process.setWorkingDirectory(working_dir)

            if DETACHED_MODE:
                success, pid = self._process.startDetached(target, args, working_dir)
                if not success:
                    raise RuntimeError("Failed to start detached process.")
                print(f"Detached process started with PID {pid}")
            else:
                self._process.finished.connect(self._on_process_finished)
                self._process.errorOccurred.connect(self._on_process_error)
                self._process.readyReadStandardOutput.connect(self._on_stdout)
                self._process.readyReadStandardError.connect(self._on_stderr)

                self._process.start(target, args)
                if not self._process.waitForStarted():
                    raise RuntimeError("Failed to start the process.")

                self._start_time = time.time()

            self.game_started.emit()

        except Exception as e:
            self.error_occurred.emit(str(e))
            print(f"Error launching game: {e}")

    def stop_game(self) -> bool:
        if self._process and self._process.state() == QProcess.Running:
            self._process.terminate()
            if not self._process.waitForFinished(KILL_TIMEOUT):
                self._process.kill()
            return True
        return False

    def can_stop(self) -> bool:
        return not DETACHED_MODE

    def _create_command(self, target_path: str, launch_options: str) -> list[str]:
        if target_path:
            command = [target_path]
            if launch_options:
                command.extend(shlex.split(launch_options))
        elif launch_options:
            # If no target is given, treat launch options as a full command
            command = shlex.split(launch_options)
        else:
            command = []

        return command

    def _on_process_finished(self, exit_code, _exit_status):
        duration = time.time() - self._start_time if self._start_time else 0
        print(f"Game finished. Exit code: {exit_code}. Duration: {duration:.2f}s")
        self._process = None
        self.game_stopped.emit(exit_code)

    def _on_process_error(self, error_code):
        error_map = {
            QProcess.FailedToStart: "Failed to start.",
            QProcess.Crashed: "Crashed.",
            QProcess.Timedout: "Timed out.",
            QProcess.WriteError: "Write error.",
            QProcess.ReadError: "Read error.",
        }
        msg = error_map.get(error_code, "Unknown error.")
        self.error_occurred.emit(msg)
        print(f"Process error: {msg}")

    def _on_stdout(self):
        if self._process:
            output = self._process.readAllStandardOutput().data().decode()
            print(f"STDOUT: {output}")

    def _on_stderr(self):
        if self._process:
            error = self._process.readAllStandardError().data().decode()
            print(f"STDERR: {error}")
