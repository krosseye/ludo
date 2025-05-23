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

import logging
import os
import threading
from typing import Dict

import core.constants as constants  # type: ignore
import darkdetect  # type: ignore
from PySide6.QtCore import QSize, QStandardPaths
from utilities.helpers import load_json


class AppConfig:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialize()
                print("AppConfig instance created")
        return cls._instance

    def _initialize(self) -> None:
        print("Initializing")
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "app_config.json",
        )
        self._config_file: Dict = load_json(config_path)

        self.APP_TITLE = str(constants.APP_TITLE)
        self.APP_VERSION = str(constants.APP_VERSION)
        self.DEVELOPER = str(constants.DEVELOPER)
        self.GITHUB_URL = str(constants.GITHUB_URL)

        self.DEV_MODE = bool(self._config_file.get("DEV_MODE"))
        self.PORTABLE = bool(self._config_file.get("PORTABLE"))
        self.SPLASH_ENABLED = bool(self._config_file.get("SPLASH_ENABLED"))

        _vertical_size = self._config_file.get("VERTICAL_CAPSULE_SIZE", [150, 225])
        _horizontal_size = self._config_file.get("HORIZONTAL_CAPSULE_SIZE", [276, 129])

        self.VERTICAL_CAPSULE_SIZE = QSize(*_vertical_size)
        self.HORIZONTAL_CAPSULE_SIZE = QSize(*_horizontal_size)

        self.RESOURCE_PATH = constants.RESOURCE_PATH
        self.USER_DATA_PATH = (
            QStandardPaths.writableLocation(QStandardPaths.AppLocalDataLocation)
            if not self.PORTABLE
            else os.path.join(self.RESOURCE_PATH, "userdata")
        )

        _log_level_str = self._validate_choice(
            self._config_file.get("LOG_LEVEL", "WARNING").upper(),
            {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"},
            "LOG_LEVEL",
        )
        self.LOG_LEVEL = getattr(logging, _log_level_str, logging.WARNING)

        self.PREFERS_DARK_MODE = darkdetect.isDark()

        self.APP_ICON_ON_DARK = os.path.join(
            self.RESOURCE_PATH, "icons", "icon_on_dark.png"
        )
        self.APP_ICON_ON_LIGHT = os.path.join(
            self.RESOURCE_PATH, "icons", "icon_on_light.png"
        )
        self.APP_ICON = (
            self.APP_ICON_ON_DARK if self.PREFERS_DARK_MODE else self.APP_ICON_ON_LIGHT
        )

        self.SPLASH_IMAGE_ON_DARK = os.path.join(
            self.RESOURCE_PATH, "icons", "splash_image_on_dark.png"
        )
        self.SPLASH_IMAGE_ON_LIGHT = os.path.join(
            self.RESOURCE_PATH, "icons", "splash_image_on_light.png"
        )
        self.SPLASH_IMAGE = (
            self.SPLASH_IMAGE_ON_DARK
            if self.PREFERS_DARK_MODE
            else self.SPLASH_IMAGE_ON_LIGHT
        )

    def _validate_choice(self, value: str, allowed: set, field: str) -> str:
        if value not in allowed:
            raise ValueError(f"{field} must be one of {allowed}, got '{value}'")
        return value


app_config = AppConfig()
