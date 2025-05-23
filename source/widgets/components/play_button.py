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
from datetime import datetime

from core.app_config import app_config
from core.plugins.runners import DefaultRunner
from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QHBoxLayout, QLabel, QMessageBox, QPushButton

CONFIG = app_config
PREFERS_DARK_MODE = CONFIG.PREFERS_DARK_MODE


class PlayButton(QPushButton):
    clicked = Signal(str)

    def __init__(self, game_info=None, game_list_manager=None):
        super().__init__()

        self.setFixedHeight(40)
        self.setObjectName("PlayButton")
        self.setAccessibleName("Play Game")
        self.setAccessibleDescription("Start playing the game")
        self.setFocusPolicy(Qt.StrongFocus)
        self._game_list_manager = game_list_manager
        self._runner = None

        icon_theme = "dark" if PREFERS_DARK_MODE else "light"
        self._play_icon = QIcon(
            os.path.join(
                CONFIG.RESOURCE_PATH, "icons", icon_theme, "filled", "play.png"
            )
        ).pixmap(QSize(24, 24))

        self._dismiss_icon = QIcon(
            os.path.join(CONFIG.RESOURCE_PATH, "icons", icon_theme, "dismiss.png")
        ).pixmap(QSize(24, 24))

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(5)

        self.icon_label = QLabel()
        self.text_label = QLabel()
        self.text_label.setAlignment(Qt.AlignCenter)

        layout.addStretch()
        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_label)
        layout.addStretch()

        self.setLayout(layout)

        self.update_game_info(game_info)

    def _can_run(self, game_info):
        """Determine if the game can be launched."""
        if not game_info:
            return False
        return bool(game_info.executablePath or game_info.launchOptions)

    def _update_state(self, enabled, running):
        play_mode = enabled and not running
        stop_mode = enabled and running and self._runner and self._runner.can_stop()

        self.setEnabled(enabled)
        self.setCursor(Qt.PointingHandCursor if enabled else Qt.ForbiddenCursor)

        if stop_mode:
            self.icon_label.setPixmap(self._dismiss_icon)
            self.text_label.setText("Stop")
            self.setToolTip(f"Stop {self.title}.")
            self.setProperty("buttonType", "stop")
        elif play_mode:
            self.icon_label.setPixmap(self._play_icon)
            self.text_label.setText("Play")
            self.setToolTip(f"Play {self.title}.")
            self.setProperty("buttonType", "play")
        else:
            self.icon_label.setPixmap(QPixmap())
            self.text_label.setText("Play")
            self.setToolTip(f"{self.title} is not ready.")
            self.setProperty("buttonType", "disabled")

        self.setStyleSheet("""
            QPushButton[buttonType="stop"] QLabel,
            QPushButton[buttonType="play"] QLabel {
                font-weight: bold;
            }
            
            QPushButton[buttonType="stop"] {
                background-color: red;
                color: white;
            }
            
            QPushButton[buttonType="play"] {
                background-color: palette(highlight);
                color: white;
            }
            
            QPushButton[buttonType="disabled"] {
                background-color: palette(button);
                color: palette(text);
            }
        """)

    def update_game_info(self, game_info):
        if not game_info:
            return

        self.game_info = game_info
        self.game_id = getattr(game_info, "id", "")
        self.title = getattr(game_info, "title", "")

        self._process_manager = self._game_list_manager.game_manager.process_manager
        self._runner = self._process_manager.get_runner(self.game_id)

        if not self._runner:
            self._runner = DefaultRunner(game_info)
            if self._runner.can_stop():
                self._process_manager.add_process(self._runner)
                self._runner.game_started.connect(
                    lambda: self._update_state(True, True)
                )
                self._runner.game_stopped.connect(
                    lambda _: self._update_state(True, False)
                )
                self._runner.error_occurred.connect(self._handle_runner_error)

        # Update UI state
        running = (
            self._runner.is_running()
            if self._runner and self._runner.can_stop()
            else False
        )
        can_run = self._can_run(game_info)
        self._update_state(can_run, running)

    def _handle_runner_error(self, error_message):
        """Handle errors from the runner."""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Error")
        msg_box.setText("An error occurred while running the game")
        msg_box.setInformativeText(error_message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()

    def mousePressEvent(self, event):
        self.clicked.emit(self.game_id)
        super().mousePressEvent(event)

        if not self.game_info or not self._can_run(self.game_info):
            return

        if self._runner and self._runner.can_stop() and self._runner.is_running():
            self._runner.stop_game()
        else:
            try:
                # Update last played time and increment sessions played
                self._game_list_manager.game_manager.update_last_played(
                    self.game_id, datetime.now()
                )
                self._game_list_manager.game_manager.increment_sessions_played(
                    self.game_id
                )

                if not self._runner:
                    self._runner = DefaultRunner(self.game_info)
                    if self._runner.can_stop():
                        self._process_manager.add_process(self._runner)
                        self._runner.game_started.connect(
                            lambda: self._update_state(True, True)
                        )
                        self._runner.game_stopped.connect(
                            lambda _: self._update_state(True, False)
                        )
                        self._runner.error_occurred.connect(self._handle_runner_error)

                self._runner.run_game()
            except Exception as e:
                self._handle_runner_error(str(e))
