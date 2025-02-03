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

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QSlider,
    QWidget,
)


class MetadataTab(QWidget):
    def __init__(self, parent=None, game_id=None):
        super().__init__(parent)
        self.game_id = game_id
        self._init_ui()

    def _init_ui(self):
        layout = QFormLayout()

        self._create_widgets()

        if self.game_id:
            layout.addRow(QLabel("Database ID:"), self._create_id_widget())

        layout.addRow(QLabel("Title:"), self.title_input)
        layout.addRow(QLabel("Sort Name:"), self.sort_name_input)
        layout.addRow(QLabel("Developer:"), self.developer_input)
        layout.addRow(QLabel("Publisher:"), self.publisher_input)
        layout.addRow(QLabel("Year:"), self.year_input)
        layout.addRow(QLabel("Star Rating:"), self.star_rating_input)
        layout.addRow(QLabel("Description:"), self.description_input)

        self.setLayout(layout)

    def _create_widgets(self):
        self.title_input = self._create_line_edit(
            "Enter game title", "The title of the game. This is required."
        )
        self.sort_name_input = self._create_line_edit(
            "Enter sort name", "The name used for sorting. Usually omits 'The' or 'A'."
        )
        self.developer_input = self._create_line_edit(
            "Enter developer name",
            "The name of the game developer or development studio.",
        )
        self.publisher_input = self._create_line_edit(
            "Enter publisher name", "The name of the game's publisher."
        )
        self.year_input = self._create_year_input()
        self.star_rating_input = self._create_star_rating_input()
        self.description_input = self._create_description_input()

    def _create_id_widget(self):
        db_id_layout = QHBoxLayout(self)
        db_id_widget = QWidget(self)
        db_id_layout.setContentsMargins(0, 0, 0, 0)
        db_id_widget.setLayout(db_id_layout)

        db_id_input = QLineEdit(self, text=self.game_id)
        db_id_input.setReadOnly(True)
        db_id_input.setToolTip(
            "This is the unique database ID for the game. It cannot be edited."
        )

        db_id_button = QPushButton(self, text="Copy")
        db_id_button.setToolTip("Click to copy the database ID to the clipboard.")
        db_id_button.clicked.connect(
            lambda: QApplication.clipboard().setText(self.game_id)
        )

        db_id_layout.addWidget(db_id_input)
        db_id_layout.addWidget(db_id_button)

        return db_id_widget

    def _create_line_edit(self, placeholder, tooltip):
        line_edit = QLineEdit(self)
        line_edit.setPlaceholderText(placeholder)
        line_edit.setToolTip(tooltip)
        return line_edit

    def _create_year_input(self):
        century_combo = QComboBox(self)
        century_combo.addItems(["00", "19", "20"])  # For centuries: 1900, 2000
        century_combo.setToolTip("Select the century (e.g., '20' for 2000s).")

        year_combo = QComboBox(self)
        year_combo.addItems([f"{i:02d}" for i in range(100)])  # Years 00-99
        year_combo.setToolTip(
            "Select the year within the century (e.g., '23' for 2023)."
        )

        century_combo.setCurrentText("00")
        year_combo.setCurrentText("00")

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(century_combo)
        layout.addWidget(year_combo)

        self.century_combo = century_combo
        self.year_combo = year_combo

        container_widget = QWidget(self)
        container_widget.setLayout(layout)

        return container_widget

    def _create_star_rating_input(self):
        widget = QWidget(self)
        layout = QHBoxLayout(self)
        widget.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel("0.0")
        slider = QSlider(Qt.Horizontal, self)
        slider.setValue(0)
        slider.setMinimum(0)
        slider.setMaximum(50)  # 5 * 10
        slider.setSingleStep(1)  # 0.1 * 10

        layout.addWidget(label)
        layout.addWidget(slider)
        slider.setToolTip("Rate the game on a scale from 0 to 5 stars.")

        slider.valueChanged.connect(lambda value: label.setText(str(value / 10)))
        return widget

    def _create_description_input(self):
        description_input = QPlainTextEdit(self)
        description_input.setPlaceholderText("Enter game description (HTML supported)")
        description_input.setToolTip(
            "Provide a description of the game. HTML formatting is supported."
        )
        return description_input
