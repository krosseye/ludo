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
import shutil

from models import AppConfig, Game
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QSlider,
    QTabWidget,
    QVBoxLayout,
)
from utilities.generators import generate_id

from .assets_tab import AssetsTab
from .files_tab import FilesTab
from .metadata_tab import MetadataTab

CONFIG = AppConfig()


USER_DATA_PATH = os.path.join(CONFIG.USER_DATA_PATH, "games")


class GameEntryDialog(QDialog):
    def __init__(self, game_list_manager, game_id=None, parent=None):
        super().__init__(parent)
        self.game_list_manager = game_list_manager
        self.game_id = game_id
        self.is_favourite = 0
        self.last_played = None
        self.sessions_played = 0
        self.playtime = 0.0

        self._init_ui()

        if self.game_id:
            self._load_game_data()

    def _init_ui(self):
        self.setWindowTitle(
            "Add New Game"
            if not self.game_id
            else f"Edit {self.game_list_manager.find_game_by_id(self.game_id).title}"
        )
        self.setModal(True)
        self.setMinimumSize(500, 500)

        main_layout = QVBoxLayout()
        tabs = QTabWidget()

        self.metadata_tab = MetadataTab(self, game_id=self.game_id)
        self.assets_tab = AssetsTab(parent=self, game_id=self.game_id)
        self.files_tab = FilesTab(self)

        tabs.addTab(self.metadata_tab, "Metadata")
        tabs.addTab(self.assets_tab, "Assets")
        tabs.addTab(self.files_tab, "Files")

        main_layout.addWidget(tabs)
        main_layout.addLayout(self._create_button_layout())
        self.setLayout(main_layout)

    def _create_button_layout(self):
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save", self)
        self.save_button.clicked.connect(self._save_game)
        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.reject)

        if self.game_id:
            self.delete_button = QPushButton("Delete", self)
            self.delete_button.clicked.connect(self._confirm_delete)
            button_layout.addWidget(self.delete_button)

        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        return button_layout

    def _load_game_data(self):
        game_data = self.game_list_manager.find_game_by_id(self.game_id)
        if game_data:
            self.is_favourite = bool(getattr(game_data, "favourite", 0))

            last_played_value = getattr(game_data, "lastPlayed", None)
            self.last_played = (
                None
                if last_played_value in (None, "None", "")
                else str(last_played_value)
            )

            self.sessions_played = int(getattr(game_data, "sessionsPlayed", 0))
            self.playtime = float(getattr(game_data, "playtime", 0.0))

            self.metadata_tab.title_input.setText(getattr(game_data, "title", ""))
            self.metadata_tab.sort_name_input.setText(
                getattr(game_data, "sortTitle", "")
            )
            self.metadata_tab.developer_input.setText(
                getattr(game_data, "developer", "")
            )
            self.metadata_tab.publisher_input.setText(
                getattr(game_data, "publisher", "")
            )
            self.metadata_tab.description_input.setPlainText(
                getattr(game_data, "description", "")
            )
            self.metadata_tab.star_rating_input.findChild(QSlider).setValue(
                float(getattr(game_data, "starRating", 0)) * 10
            )

            year = str(getattr(game_data, "year", 0)).zfill(4)
            self.metadata_tab.century_combo.setCurrentText(year[:2])
            self.metadata_tab.year_combo.setCurrentText(year[2:])

            file_values = {
                "file_path": getattr(game_data, "executablePath", ""),
                "start_in_path": getattr(game_data, "workingDirectory", ""),
                "launch_options": getattr(game_data, "launchOptions", ""),
                "browse_path": getattr(game_data, "browseDirectory", ""),
            }
            self.files_tab.set_values(file_values)

            # Load images dynamically from USER_DATA_PATH/<game_id>
            game_folder = os.path.join(USER_DATA_PATH, str(self.game_id))
            icon_path = os.path.join(game_folder, "icon")
            logo_path = os.path.join(game_folder, "logo")
            hero_path = os.path.join(game_folder, "hero")
            cover_path = os.path.join(game_folder, "capsule")
            capsule_wide_path = os.path.join(game_folder, "capsule_wide")

            self.assets_tab.update_preview(self.assets_tab.icon_preview, icon_path, 100)
            self.assets_tab.update_preview(self.assets_tab.logo_preview, logo_path, 200)
            self.assets_tab.update_preview(self.assets_tab.hero_preview, hero_path, 325)
            self.assets_tab.update_preview(
                self.assets_tab.cover_preview, cover_path, 150
            )
            self.assets_tab.update_preview(
                self.assets_tab.capsule_wide_preview, capsule_wide_path, 276
            )

    def _save_game(self):
        # Retrieve values from MetadataTab
        title = self.metadata_tab.title_input.text().strip()
        sort_name = self.metadata_tab.sort_name_input.text().strip()
        developer = self.metadata_tab.developer_input.text().strip()
        publisher = self.metadata_tab.publisher_input.text().strip()
        description = self.metadata_tab.description_input.toPlainText().strip()
        star_rating = (
            self.metadata_tab.star_rating_input.findChild(QSlider).value() / 10
        )

        century = self.metadata_tab.century_combo.currentText()
        decade = self.metadata_tab.year_combo.currentText()
        year = int(century + decade)

        # Retrieve values from AssetsTab
        icon_path = self.assets_tab.icon_path_input.itemAt(0).widget().text().strip()
        logo_path = self.assets_tab.logo_path_input.itemAt(0).widget().text().strip()
        hero_path = self.assets_tab.hero_path_input.itemAt(0).widget().text().strip()
        cover_path = self.assets_tab.cover_path_input.itemAt(0).widget().text().strip()
        capsule_wide_path = (
            self.assets_tab.capsule_wide_path_input.itemAt(0).widget().text().strip()
        )

        # Retrieve values from FilesTab
        file_values = self.files_tab.get_values()
        file_path = file_values.get("file_path", "").strip()
        folder_path = file_values.get("start_in_path", "").strip()
        launch_options = file_values.get("launch_options", "").strip()
        browse_path = file_values.get("browse_path", "").strip()

        if not title:
            QMessageBox.warning(self, "Incomplete Data", "Entries require a title.")
            return

        if not sort_name:
            sort_name = title

        # If no game_id exists, generate it
        new_game = False
        if not self.game_id:
            while True:
                self.game_id = generate_id()
                if not self.game_list_manager.has_game(self.game_id):
                    break
            new_game = True

        game_folder = os.path.join(USER_DATA_PATH, str(self.game_id))
        if not os.path.exists(game_folder):
            os.makedirs(game_folder)

        def _copy_image(source_path, filename):
            if source_path:
                extension = os.path.splitext(source_path)[1]
                dest_path = os.path.join(game_folder, f"{filename}{extension}")
                shutil.copy(source_path, dest_path)
                return os.path.join(str(self.game_id), f"{filename}{extension}")
            return ""

        icon_path = _copy_image(icon_path, "icon")
        logo_path = _copy_image(logo_path, "logo")
        hero_path = _copy_image(hero_path, "hero")
        cover_path = _copy_image(cover_path, "capsule")
        capsule_wide_path = _copy_image(capsule_wide_path, "capsule_wide")

        self.last_played = (
            None if self.last_played in (None, "None", "") else self.last_played
        )

        game = Game(
            id=self.game_id,
            title=title,
            sortTitle=sort_name,
            favourite=self.is_favourite,
            starRating=f"{star_rating:.1f}",
            developer=developer,
            publisher=publisher,
            year=year,
            description=description,
            executablePath=file_path,
            workingDirectory=folder_path,
            launchOptions=launch_options,
            browseDirectory=browse_path,
            lastPlayed=self.last_played,
            sessionsPlayed=self.sessions_played,
            playtime=self.playtime,
        )

        # Update or add the game in the metadata manager
        if not new_game:
            self.game_list_manager.update_game(self.game_id, game)
            QMessageBox.information(self, "Success", "Game modified successfully!")
        else:
            self.game_list_manager.add_game(game)
            QMessageBox.information(self, "Success", "Game added successfully!")

        self.accept()

    def _confirm_delete(self):
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            "Are you sure you want to delete this game entry?\nThis action is permanent and cannot be undone!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self._delete_game()

    def _delete_game(self):
        self.game_list_manager.delete_game(self.game_id)
        folder_path = os.path.join(USER_DATA_PATH, self.game_id)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
        QMessageBox.information(self, "Deleted", "Game deleted successfully!")
        self.accept()
