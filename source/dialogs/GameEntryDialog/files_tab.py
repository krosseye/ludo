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

from PySide6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)


class FilesTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.browse_path = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()

        local_files_group = QGroupBox("Local Files", self)
        local_files_layout = QFormLayout()

        self.folder_path_input = self._create_file_input(
            "Select Directory", self._browse_for_folder
        )
        self.file_path_input = self._create_file_input(
            "Select File Path", self._browse_for_file
        )
        self.launch_options_input = self._create_line_edit("Enter Launch Options")

        self.target_parent_radio = QRadioButton("Target's Parent Directory", self)
        self.start_in_radio = QRadioButton("Start In Directory", self)
        self.other_radio = QRadioButton("Other", self)

        self.other_radio.setChecked(True)

        self.target_parent_radio.toggled.connect(self._update_path_input)
        self.start_in_radio.toggled.connect(self._update_path_input)
        self.other_radio.toggled.connect(self._update_path_input)

        self.browse_path_input = self._create_line_edit(
            "Directory for browsing local files"
        )
        self.browse_path_input.setReadOnly(False)

        self.browse_button_other = QPushButton("Browse...", self)
        self.browse_button_other.clicked.connect(self._browse_for_other_path)

        radio_layout = self._create_radio_button_layout()

        local_files_layout.addRow(QLabel("Target:"), self.file_path_input)
        local_files_layout.addRow(QLabel("Start In:"), self.folder_path_input)
        local_files_layout.addRow(QLabel("Launch Options:"), self.launch_options_input)
        local_files_layout.addRow(QLabel(""))
        local_files_layout.addRow(QLabel("Browse Directory:"), radio_layout)

        local_files_group.setLayout(local_files_layout)

        layout.addWidget(local_files_group)
        layout.addStretch()

        self.setLayout(layout)

        self._update_path_input()

    def _create_file_input(self, placeholder, browse_function):
        """Helper method to create file selection input field."""
        line_edit = QLineEdit(self)
        line_edit.setPlaceholderText(placeholder)
        button = QPushButton("Browse...", self)
        button.clicked.connect(browse_function)

        layout = QHBoxLayout()
        layout.addWidget(line_edit)
        layout.addWidget(button)
        return layout

    def _create_line_edit(self, placeholder):
        """Helper method to create a line edit input field."""
        line_edit = QLineEdit(self)
        line_edit.setPlaceholderText(placeholder)
        return line_edit

    def _create_radio_button_layout(self):
        """Creates and returns the layout containing the radio buttons and browse path field."""
        radio_layout = QVBoxLayout()
        radio_layout.addWidget(self.target_parent_radio)
        radio_layout.addWidget(self.start_in_radio)
        radio_layout.addWidget(self.other_radio)

        browse_path_widget = QWidget()
        browse_path_layout = QHBoxLayout()
        browse_path_layout.setContentsMargins(0, 0, 0, 0)
        browse_path_widget.setLayout(browse_path_layout)
        browse_path_layout.addWidget(self.browse_path_input)
        browse_path_layout.addWidget(self.browse_button_other)
        radio_layout.addWidget(browse_path_widget)

        return radio_layout

    def _browse_for_folder(self):
        """Handles folder selection browse action."""
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.folder_path_input.itemAt(0).widget().setText(folder_path)

    def _browse_for_file(self):
        """Handles file selection browse action."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", "Executable Files (*.exe);;All Files (*)"
        )
        if file_path:
            self.file_path_input.itemAt(0).widget().setText(file_path)

    def _browse_for_other_path(self):
        """Handles other path browse action."""
        browse_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if browse_path:
            self.browse_path_input.setText(browse_path)

    def _update_path_input(self):
        """Updates the path input field based on the selected radio button."""
        if self.target_parent_radio.isChecked():
            self._set_path_input_to_target_parent()
        elif self.start_in_radio.isChecked():
            self._set_path_input_to_start_in()
        elif self.other_radio.isChecked():
            self._allow_path_browsing()
            self.browse_path_input.setText(self.browse_path if self.browse_path else "")

    def _set_path_input_to_target_parent(self):
        """Sets the path to the parent directory of the target file and makes it read-only."""
        target_path = self.file_path_input.itemAt(0).widget().text()
        parent_path = self._get_parent_directory(target_path)
        self.browse_path_input.setText(parent_path)
        self.browse_path_input.setReadOnly(True)
        self.browse_button_other.setVisible(False)

    def _set_path_input_to_start_in(self):
        """Sets the path to the start-in folder and makes it read-only."""
        start_in_path = self.folder_path_input.itemAt(0).widget().text()
        self.browse_path_input.setText(start_in_path)
        self.browse_path_input.setReadOnly(True)
        self.browse_button_other.setVisible(False)

    def _allow_path_browsing(self):
        """Allows the user to browse for a path."""

        self.browse_path_input.setReadOnly(False)
        self.browse_button_other.setVisible(True)

    def _set_radio_button_for_browse_path(
        self, browse_path, target_path, start_in_path
    ):
        """Determines which radio button should be selected based on the browse path."""
        parent_path = self._get_parent_directory(target_path)
        if browse_path == parent_path and parent_path:
            self.target_parent_radio.setChecked(True)
        elif browse_path == start_in_path and start_in_path:
            self.start_in_radio.setChecked(True)
        else:
            self.other_radio.setChecked(True)

    def _get_parent_directory(self, file_path):
        """Returns the parent directory of the given file path."""
        return os.path.dirname(file_path) if file_path else ""

    def get_values(self):
        """Returns all the field values as a dictionary."""
        return {
            "file_path": self.file_path_input.itemAt(0).widget().text(),
            "start_in_path": self.folder_path_input.itemAt(0).widget().text(),
            "launch_options": self.launch_options_input.text(),
            "browse_path": self.browse_path_input.text(),
            "target_parent_radio": self.target_parent_radio.isChecked(),
            "start_in_radio": self.start_in_radio.isChecked(),
            "other_radio": self.other_radio.isChecked(),
        }

    def set_values(self, values):
        """Sets the field values from the provided dictionary."""
        self.file_path_input.itemAt(0).widget().setText(values.get("file_path", ""))
        self.folder_path_input.itemAt(0).widget().setText(
            values.get("start_in_path", "")
        )
        self.launch_options_input.setText(values.get("launch_options", ""))

        browse_path = values.get("browse_path", "")
        self.browse_path = browse_path
        target_path = values.get("file_path", "")
        start_in_path = values.get("start_in_path", "")

        self._set_radio_button_for_browse_path(browse_path, target_path, start_in_path)

        self.browse_path_input.setText(browse_path)
        self._update_path_input()
