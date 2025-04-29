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
import time
from datetime import datetime

from core.app_config import app_config
from PySide6.QtCore import QProcess, QSize, Qt, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QMessageBox

CONFIG = app_config
PREFERS_DARK_MODE = CONFIG.PREFERS_DARK_MODE
DETACHED_MODE = CONFIG.LAUNCH_PROCESS_DETACHED

KILL_TIMEOUT = 5000


class PlayButton(QFrame):
    clicked = Signal(str)

    def __init__(self, game_info=None, game_list_manager=None):
        super().__init__()

        self.setFixedHeight(40)
        self.setObjectName("PlayButton")
        self.setAccessibleName("Play Game")
        self.setAccessibleDescription("Start playing the game")
        self.setFocusPolicy(Qt.StrongFocus)
        self._game_list_manager = game_list_manager

        self._processes = {}
        self._max_start_time = 5

        self._play_icon = QIcon(
            os.path.join(CONFIG.RESOURCE_PATH, "icons", "dark", "filled", "play.png")
        ).pixmap(QSize(24, 24))

        self._dismiss_icon = QIcon(
            os.path.join(CONFIG.RESOURCE_PATH, "icons", "dark", "dismiss.png")
        ).pixmap(QSize(24, 24))

        # Layout
        layout = QHBoxLayout()
        self.icon_label = QLabel()
        self.label = QLabel()

        layout.addStretch()
        layout.addWidget(self.icon_label)
        layout.addWidget(self.label)
        layout.addStretch()

        self.setLayout(layout)

        prefers_dark = PREFERS_DARK_MODE
        palette = self.palette()
        self._border_color = (
            palette.midlight().color().name()
            if prefers_dark
            else palette.mid().color().name()
        )
        self.button_color = palette.button().color().name()
        self.highlighted_button_color = palette.highlight().color().name()

        self.update_game_info(game_info)

    def _can_run(self, game_id, target_path, launch_options):
        """Determine if the game can be launched."""
        if DETACHED_MODE:
            return bool(target_path or launch_options)
        process = self._processes.get(game_id)
        if process:
            if process["process"].state() == QProcess.Running:
                return False  # Already running
        return bool(target_path or launch_options)

    def _create_command(self, target_path, launch_options):
        """Create the command to run the game."""
        if not target_path and not launch_options:
            raise ValueError("No target path or launch options provided.")

        command = []

        if target_path:
            command.append(target_path)

        if launch_options:
            command.extend(launch_options.split())

        return command

    def _run_process(self, game_id, command, working_directory):
        """Launch the game using QProcess."""
        print(f"Running command: {command}")
        try:
            process = QProcess(self)
            target = command[0]
            args = command[1:]

            process.setWorkingDirectory(working_directory)

            if DETACHED_MODE:
                retval, pid = process.startDetached(target, args, working_directory)
                if not retval:
                    raise Exception("Failed to start the process in detached mode.")
                print(f"Process started in detached mode with PID: {pid}")
            else:
                process.start(target, args)
                if not process.waitForStarted():
                    raise Exception("Failed to start the process.")

                # Store the process in _processes if not in detached mode
                self._processes[game_id] = {
                    "process": process,
                    "pid": process.processId(),
                    "start_time": time.time(),
                }

                process.finished.connect(lambda: self._on_process_finished(game_id))
                process.errorOccurred.connect(self._on_process_error)
                process.readyReadStandardOutput.connect(
                    self._on_process_standard_output
                )
                process.readyReadStandardError.connect(self._on_process_standard_error)

            # Update last played time
            try:
                last_played_time = datetime.now()
                self._game_list_manager.game_manager.update_last_played(
                    game_id, last_played_time
                )
            except Exception as e:
                print(f"Error updating lastPlayed: {e}")

        except Exception as e:
            print(f"Error starting process: {e}")

    def _stop_process(self, game_id):
        """Stop a running process."""
        if game_id in self._processes:
            process = self._processes[game_id]["process"]
            if process.state() == QProcess.Running:
                process.terminate()
                if not process.waitForFinished(KILL_TIMEOUT):
                    process.kill()
                    print(f"Force killed the process for {self.title}.")

    def _on_process_finished(self, game_id):
        """Handle when the process finishes."""
        if game_id not in self._processes:
            return

        start_time = self._processes[game_id]["start_time"]
        process_duration = time.time() - start_time
        process = self._processes[game_id]["process"]
        exit_status = process.exitStatus()
        exit_code = process.exitCode()

        if exit_status == QProcess.NormalExit and exit_code == 0:
            if not process_duration < self._max_start_time:
                print(
                    f"Process for {self.title} finished successfully. Duration: {process_duration:.2f}s"
                )
            else:
                print(
                    f"Process for {self.title} finished too quickly ({process_duration:.2f}s), assuming external launcher."
                )
        else:
            print(
                f"Process for {self.title} finished with errors. Exit Code:{exit_code}"
            )

        del self._processes[game_id]
        self.update_game_info(self.game_info)

    def _on_process_standard_output(self):
        process = self.sender()
        output = process.readAllStandardOutput().data().decode()
        print(f"Output: {output}")

    def _on_process_standard_error(self):
        process = self.sender()
        error = process.readAllStandardError().data().decode()
        print(f"Error: {error}")

    def _on_process_error(self, error_code):
        error_messages = {
            QProcess.FailedToStart: "The process failed to start.",
            QProcess.Crashed: "The process crashed.",
            QProcess.Timedout: "The process timed out.",
            QProcess.WriteError: "Write error occurred.",
            QProcess.ReadError: "Read error occurred.",
        }
        error_message = error_messages.get(error_code, "An unknown error occurred.")
        print(f"Process Error: {error_message}")

    def _update_state(self, enabled, running):
        """Update the button's appearance based on the state."""
        play_mode = enabled and not (DETACHED_MODE and enabled)
        stop_mode = not DETACHED_MODE and running

        if stop_mode:
            icon, text, tooltip, bg_color = (
                self._dismiss_icon,
                "Stop",
                f"Stop {self.title}.",
                "red",
            )
        elif play_mode:
            icon, text, tooltip, bg_color = (
                self._play_icon,
                "Play",
                f"Play {self.title}.",
                self.highlighted_button_color,
            )
        else:
            icon, text, tooltip, bg_color = (
                QPixmap(),
                "Play",
                f"{self.title} is not ready.",
                self.button_color,
            )

        self.icon_label.setPixmap(icon)
        self.icon_label.setVisible(bool(icon))
        self.label.setText(text)
        self.setCursor(
            Qt.PointingHandCursor if play_mode or stop_mode else Qt.ArrowCursor
        )
        self.setToolTip(tooltip)

        text_color = (
            "white" if play_mode or stop_mode else self.palette().text().color().name()
        )
        self.setStyleSheet(f"""
            QFrame#PlayButton {{
                background-color: {bg_color};
                border: 1px solid {self._border_color};
                border-radius: 5px;
            }}
            QFrame#PlayButton QLabel {{
                font-weight:bold;
                color: {text_color};
                background-color: transparent;
            }}
        """)

    def update_game_info(self, game_info):
        """Update game information and the button state."""
        self.game_id = getattr(game_info, "id", "")
        self.title = getattr(game_info, "title", "")
        self.file_path = getattr(game_info, "executablePath", "")
        self.folder_path = getattr(game_info, "workingDirectory", "")
        self.launch_options = getattr(game_info, "launchOptions", "")

        self.game_info = game_info

        running = self.game_id in self._processes and not DETACHED_MODE
        can_run = self._can_run(self.game_id, self.file_path, self.launch_options)

        self._update_state(can_run, running)

    def mousePressEvent(self, event):
        """Handle button clicks."""
        self.clicked.emit(self.game_id)
        if self.game_id in self._processes and not DETACHED_MODE:
            self._stop_process(self.game_id)
            self.update_game_info(
                type(
                    "GameInfo",
                    (),
                    {
                        "id": self.game_id,
                        "title": self.title,
                        "executablePath": self.file_path,
                        "workingDirectory": self.folder_path,
                        "launchOptions": self.launch_options,
                    },
                )()
            )
        else:
            if self._can_run(self.game_id, self.file_path, self.launch_options):
                try:
                    command = self._create_command(self.file_path, self.launch_options)
                    self._run_process(self.game_id, command, self.folder_path)
                    # Immediately update state to show stop button (only if not in detached mode)
                    self.update_game_info(
                        type(
                            "GameInfo",
                            (),
                            {
                                "id": self.game_id,
                                "title": self.title,
                                "executablePath": self.file_path,
                                "workingDirectory": self.folder_path,
                                "launchOptions": self.launch_options,
                            },
                        )()
                    )
                except Exception as e:
                    msg_box = QMessageBox()
                    msg_box.setIcon(QMessageBox.Critical)
                    msg_box.setWindowTitle("Error")
                    msg_box.setText("An unexpected error occurred!")
                    msg_box.setInformativeText(
                        f"Failed to start {self.title}: {str(e)}"
                    )
                    msg_box.setStandardButtons(QMessageBox.Ok)
                    msg_box.exec()
