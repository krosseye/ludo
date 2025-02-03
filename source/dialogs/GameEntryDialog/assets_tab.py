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

from models import AppConfig
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

USER_DATA_PATH = AppConfig().USER_DATA_PATH
ASSETS_BASE_PATH = os.path.join(USER_DATA_PATH, "games")

ICON_PREVIEW_WIDTH = 100
LOGO_PREVIEW_WIDTH = 200
HERO_PREVIEW_WIDTH = 325
COVER_PREVIEW_WIDTH = 150
WIDE_CAPSULE_PREVIEW_WIDTH = 276


class AssetsTab(QWidget):
    def __init__(self, game_id=None, parent=None):
        super().__init__(parent)
        self.game_id = game_id if game_id else None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()

        self.icon_path_input, self.icon_preview = self._create_file_input(
            "Select icon image", self.browse_icon, ICON_PREVIEW_WIDTH
        )
        self.logo_path_input, self.logo_preview = self._create_file_input(
            "Select logo image", self.browse_logo, LOGO_PREVIEW_WIDTH
        )
        self.hero_path_input, self.hero_preview = self._create_file_input(
            "Select hero image", self.browse_hero, HERO_PREVIEW_WIDTH
        )
        self.cover_path_input, self.cover_preview = self._create_file_input(
            "Select capsule image", self.browse_cover, COVER_PREVIEW_WIDTH
        )
        self.capsule_wide_path_input, self.capsule_wide_preview = (
            self._create_file_input(
                "Select wide capsule image",
                self.browse_capsule_wide,
                WIDE_CAPSULE_PREVIEW_WIDTH,
            )
        )

        icon_hero_layout = QHBoxLayout()
        icon_hero_layout.addWidget(
            self._create_labeled_frame("Icon", self.icon_path_input, self.icon_preview),
            1,
        )
        icon_hero_layout.addWidget(
            self._create_labeled_frame("Hero", self.hero_path_input, self.hero_preview),
            2,
        )

        logo_capsule_layout = QVBoxLayout()
        logo_capsule_layout.addWidget(
            self._create_labeled_frame("Logo", self.logo_path_input, self.logo_preview),
            2,
        )
        logo_capsule_layout.addWidget(
            self._create_labeled_frame(
                "Wide Capsule", self.capsule_wide_path_input, self.capsule_wide_preview
            ),
            3,
        )

        capsule_layout = QHBoxLayout()
        capsule_layout.addWidget(
            self._create_labeled_frame(
                "Capsule", self.cover_path_input, self.cover_preview
            ),
            2,
        )
        capsule_layout.addLayout(logo_capsule_layout, 3)

        layout.addLayout(icon_hero_layout)
        layout.addLayout(capsule_layout)

        # Add "Open Assets Folder" button if game_id is provided
        if self.game_id:
            open_folder_button = QPushButton(
                icon=QIcon.fromTheme("folder"), text="Open Assets Folder", parent=self
            )
            open_folder_button.clicked.connect(self.open_assets_folder)
            open_folder_button.setFixedHeight(50)
            layout.addWidget(open_folder_button)

        self.setLayout(layout)

    def _create_file_input(self, placeholder, browse_function, preview_width):
        line_edit = QLineEdit(self)
        line_edit.setPlaceholderText(placeholder)
        button = QPushButton("Browse...", self)
        button.clicked.connect(browse_function)

        layout = QHBoxLayout()
        layout.addWidget(line_edit)
        layout.addWidget(button)

        preview_label = QLabel("<strong>No Image Selected</strong>", self)
        preview_label.setWordWrap(True)
        preview_label.setAlignment(Qt.AlignCenter)
        preview_label.setFixedWidth(preview_width)
        preview_label.setFixedHeight(100)  # Default height; will be updated dynamically
        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        preview_label.setSizePolicy(size_policy)
        return layout, preview_label

    def browse_icon(self):
        self._browse_file(
            self.icon_path_input,
            self.icon_preview,
            is_icon=True,
            width=ICON_PREVIEW_WIDTH,
        )

    def browse_logo(self):
        self._browse_file(
            self.logo_path_input, self.logo_preview, width=LOGO_PREVIEW_WIDTH
        )

    def browse_hero(self):
        self._browse_file(
            self.hero_path_input, self.hero_preview, width=HERO_PREVIEW_WIDTH
        )

    def browse_cover(self):
        self._browse_file(
            self.cover_path_input, self.cover_preview, width=COVER_PREVIEW_WIDTH
        )

    def browse_capsule_wide(self):
        self._browse_file(
            self.capsule_wide_path_input,
            self.capsule_wide_preview,
            width=WIDE_CAPSULE_PREVIEW_WIDTH,
        )

    def _browse_file(self, path_input, preview_label, is_icon=False, width=100):
        if is_icon:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Select File", "", "Images (*.png *.jpg *.jpeg *.ico)"
            )
        else:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Select File", "", "Images (*.png *.jpg *.jpeg)"
            )
        if file_path:
            path_input.itemAt(0).widget().setText(file_path)
            self.update_preview(preview_label, file_path, width)

    def update_preview(self, label, image_path, width=100):
        """Update the QLabel with the image preview, always using QIcon, and calculate height to maintain aspect ratio."""
        if image_path:
            icon = QIcon(image_path)
            available_sizes = icon.availableSizes()

            if not available_sizes:
                label.setPixmap(QPixmap())
                label.setText("<strong>No Image Selected</strong>")
                return

            best_size = min(
                available_sizes,
                key=lambda available_size: abs(available_size.width() - width),
            )

            pixmap = icon.pixmap(best_size)

            aspect_ratio = pixmap.width() / pixmap.height()
            height = int(width / aspect_ratio)

            scaled_pixmap = pixmap.scaled(
                width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )

            label.setPixmap(scaled_pixmap)
            label.setFixedHeight(scaled_pixmap.height())
            label.setText("")
        else:
            label.setPixmap(QPixmap())
            label.setText("<strong>No Image Selected</strong>")

    def _create_labeled_frame(self, label_text, input_layout, preview_label):
        frame = QGroupBox(label_text, self)
        frame_layout = QVBoxLayout()
        frame_layout.addWidget(preview_label, alignment=Qt.AlignCenter)
        frame_layout.addLayout(input_layout)
        frame.setLayout(frame_layout)

        return frame

    def open_assets_folder(self):
        """Opens the assets folder for the specified game ID."""
        folder_path = os.path.join(ASSETS_BASE_PATH, self.game_id)

        if os.path.exists(folder_path):
            if os.name == "nt":
                os.startfile(folder_path)
            elif os.uname().sysname == "Darwin":
                os.system(f'open "{folder_path}"')
            else:
                os.system(f'xdg "{folder_path}"')

        else:
            print(f"Folder {folder_path} does not exist.")
