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
from datetime import datetime, timedelta

from core.app_config import app_config
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout
from utilities.helpers import create_vertical_line

CONFIG = app_config
ICON_BASE_PATH = os.path.join(CONFIG.RESOURCE_PATH, "icons")


class StatBar(QFrame):
    """A stat bar widget that displays game statistics (last played, sessions played, average session, playtime)."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self._main_layout = QHBoxLayout(self)
        self.setLayout(self._main_layout)
        self.setFrameShape(QFrame.StyledPanel)

        self._last_played_widget = self._create_stat_widget(
            "Last Played", "<h2>Unknown</h2>", "last_played_value", "calendar.png"
        )
        self._sessions_played_widget = self._create_stat_widget(
            "Sessions Played",
            "<h2>0</h2>",
            "sessions_played_value",
            "sessions_played.png",
        )
        self._average_session_widget = self._create_stat_widget(
            "Avg. Session",
            "<h2>0 minutes</h2>",
            "average_session_value",
            "average_session.png",
        )
        self._playtime_widget = self._create_stat_widget(
            "Play Time", "<h2>0 hours</h2>", "playtime_value", "playtime.png"
        )
        self.first_divider = create_vertical_line(stretch=True)
        self.second_divider = create_vertical_line(stretch=True)
        self.third_divider = create_vertical_line(stretch=True)

        self._main_layout.addStretch()
        self._main_layout.addWidget(self._last_played_widget)
        self._main_layout.addWidget(self.first_divider)
        self._main_layout.addWidget(self._sessions_played_widget)
        self._main_layout.addWidget(self.second_divider)
        self._main_layout.addWidget(self._average_session_widget)
        self._main_layout.addWidget(self.third_divider)
        self._main_layout.addWidget(self._playtime_widget)
        self._main_layout.addStretch()

        self._main_layout.setAlignment(Qt.AlignCenter)

    def _create_stat_widget(
        self, title: str, value: str, value_object_name: str, icon_path: str
    ) -> QFrame:
        widget = QFrame()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 0, 5, 0)

        icon_label = QLabel()
        icon_label.setObjectName(f"icon_{title.lower().replace(' ', '_')}")
        icon_label.setPixmap(
            QPixmap(
                os.path.join(
                    ICON_BASE_PATH,
                    "dark" if CONFIG.PREFERS_DARK_MODE else "light",
                    icon_path,
                )
            ).scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

        title_label = QLabel(f"<strong>{title}</strong>")
        value_label = QLabel(value)
        value_label.setObjectName(value_object_name)

        text_layout = QVBoxLayout()
        text_layout.addWidget(title_label)
        text_layout.addWidget(value_label)
        text_layout.setSpacing(2)

        layout.addWidget(icon_label)
        layout.addLayout(text_layout)
        layout.setAlignment(Qt.AlignLeft)

        return widget

    def update_stats(self, last_played, sessions_played, playtime):
        """Update the displayed stats with new values."""
        formatted_playtime = self._format_playtime(playtime)
        average_session = self._calculate_average_session(sessions_played, playtime)

        self.findChild(QLabel, "last_played_value").setText(
            f"<h2>{self._format_date(last_played)}</h2>"
        )
        self.findChild(QLabel, "sessions_played_value").setText(
            f"<h2>{sessions_played}</h2>"
        )
        self.findChild(QLabel, "average_session_value").setText(
            f"<h2>{average_session}</h2>"
        )
        self.findChild(QLabel, "playtime_value").setText(
            f"<h2>{formatted_playtime}</h2>"
        )

    def resizeEvent(self, event):
        """Handle widget resize events to show/hide icons and specific widgets based on width."""
        super().resizeEvent(event)

        widget_width = self.width()
        _compact = widget_width < 160 * 4
        _micro = widget_width < 125 * 4

        if _compact:
            for widget in self.findChildren(QLabel):
                if widget.objectName().startswith("icon_"):
                    widget.setVisible(False)
        else:
            for widget in self.findChildren(QLabel):
                if widget.objectName().startswith("icon_"):
                    widget.setVisible(True)

        if _micro:
            self._sessions_played_widget.setVisible(False)
            self._average_session_widget.setVisible(False)
            self.second_divider.setVisible(False)
            self.third_divider.setVisible(False)
        else:
            self._sessions_played_widget.setVisible(True)
            self._average_session_widget.setVisible(True)
            self.second_divider.setVisible(True)
            self.third_divider.setVisible(True)

    from datetime import datetime, timedelta

    @staticmethod
    def _format_date(input_date: str) -> str:
        if not input_date:
            return "Never"

        try:
            input_date_obj = datetime.strptime(input_date, "%Y/%m/%d %H:%M:%S")
        except ValueError:
            return "Invalid Date"

        today = datetime.today().date()
        input_date_only = input_date_obj.date()

        if input_date_only == today:
            return "Today"
        if input_date_only == today - timedelta(days=1):
            return "Yesterday"
        start_of_week = today - timedelta(days=today.weekday())
        if start_of_week <= input_date_only <= today:
            return "This Week"
        last_week_start = start_of_week - timedelta(days=7)
        last_week_end = start_of_week - timedelta(days=1)
        if last_week_start <= input_date_only <= last_week_end:
            return "Last Week"
        if input_date_obj.month == today.month and input_date_obj.year == today.year:
            return "This Month"

        date_format = "%b %d" if input_date_obj.year == today.year else "%b %d, %Y"
        return input_date_only.strftime(date_format)

    @staticmethod
    def _format_playtime(playtime):
        """Formats playtime to display in hours or minutes."""
        if playtime > 90:
            return f"{round(playtime / 60, 1):g} hours"
        else:
            return f"{round(playtime):g} minutes"

    @staticmethod
    def _calculate_average_session(sessions_played, playtime):
        """Calculates and formats the average session time."""
        if sessions_played == 0 or playtime == 0:
            return "0 minutes"

        average_session = round(float(playtime) / int(sessions_played))

        if average_session > 90:
            return f"{round(average_session / 60, 1):g} hours"
        else:
            return f"{average_session:g} minutes"
