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

from core.app_config import app_config
from core.config import user_config
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)
from utilities.helpers import create_horizontal_line, create_vertical_line
from widgets.components.spritesheet_checkbox import LabeledSpritesheetCheckBox
from widgets.GameGridWidget import GameGridWidget

from .game_list_widget import GameListWidget
from .search_input import SearchBarWidget

CONFIG = app_config

GAMES_DIRECTORY = os.path.join(
    CONFIG.USER_DATA_PATH,
    "games",
)


class GameCollectionWidget(QFrame):
    def __init__(self, game_list_manager):
        super().__init__()
        self.game_list_manager = game_list_manager

        self.setFrameStyle(QFrame.StyledPanel)
        self.search_bar = SearchBarWidget()

        filter_layout = QVBoxLayout()
        filter_layout.setContentsMargins(0, 0, 0, 0)
        filter_widget = QWidget()
        filter_widget.setLayout(filter_layout)

        self.sort_order_combobox = self._create_sorting_combobox()

        filter_layout.addWidget(self.sort_order_combobox)
        filter_layout.addWidget(self._create_sorting_checkboxes())

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.search_bar)
        self.layout.addWidget(filter_widget)
        self.layout.addWidget(create_horizontal_line())

        self.game_list_widget = (
            GameListWidget(self.game_list_manager, self)
            if user_config["COLLECTION_STYLE"] == "list"
            else GameGridWidget(self.game_list_manager, self)
        )

        self.layout.addWidget(self.game_list_widget)

    def _create_sorting_checkboxes(self):
        def _sort_by_recent(state):
            self.game_list_manager.sort_by_recent = state

        def _toggle_favourites_first(state):
            self.game_list_manager.group_favourites = state

        self.sort_by_recent_checkbox = LabeledSpritesheetCheckBox(
            "Recently Played",
            os.path.join(
                CONFIG.RESOURCE_PATH, "icons", "spritesheet", "history_spritesheet.png"
            ),
        )
        self.sort_by_recent_checkbox.setToolTip("Sort by recently played.")
        self.sort_by_recent_checkbox.setChecked(self.game_list_manager.sort_by_recent)
        self.sort_by_recent_checkbox.stateChanged.connect(
            lambda state: _sort_by_recent(state)
        )

        self.favourites_checkbox = LabeledSpritesheetCheckBox(text="Group Favourites")
        self.favourites_checkbox.setToolTip("Group favourites before other games.")
        self.favourites_checkbox.setChecked(self.game_list_manager.group_favourites)
        self.favourites_checkbox.stateChanged.connect(
            lambda state: _toggle_favourites_first(state)
        )

        sort_checkbox_widget = QFrame()
        sort_checkbox_layout = QHBoxLayout()
        sort_checkbox_layout.setContentsMargins(0, 0, 0, 0)
        sort_checkbox_widget.setLayout(sort_checkbox_layout)

        sort_checkbox_layout.addWidget(self.favourites_checkbox)
        sort_checkbox_layout.addWidget(create_vertical_line())
        sort_checkbox_layout.addWidget(self.sort_by_recent_checkbox)
        sort_checkbox_layout.addStretch()

        return sort_checkbox_widget

    def _create_sorting_combobox(self):
        sort_order_combobox = QComboBox()
        sort_order_combobox.setFixedHeight(32)
        sort_order_combobox.addItem("Ascending")
        sort_order_combobox.addItem("Descending")

        sort_order_combobox.setCurrentIndex(
            0 if self.game_list_manager.sort_order == Qt.AscendingOrder else 1
        )

        sort_order_combobox.currentIndexChanged.connect(
            lambda index: self._on_sort_order_changed(index)
        )

        return sort_order_combobox

    def _on_sort_order_changed(self, index):
        self.game_list_manager.sort_order = (
            Qt.AscendingOrder if index == 0 else Qt.DescendingOrder
        )
