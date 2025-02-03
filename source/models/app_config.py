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
from dataclasses import dataclass, field
from typing import Dict

import darkdetect
from PySide6.QtCore import QCoreApplication, QSize, QStandardPaths
from utilities.helpers import load_json


@dataclass(frozen=True)
class AppConfig:
    _instance = None
    _lock = threading.Lock()
    _initialized = False
    _metadata_set = False

    _config_file: Dict = field(
        default_factory=lambda: load_json(
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "config.json",
            )
        )
    )

    APP_TITLE: str = field(init=False)
    APP_VERSION: str = field(init=False)
    DEVELOPER: str = field(init=False)
    GITHUB_URL: str = field(init=False)
    DEV_MODE: bool = field(init=False)
    PORTABLE: bool = field(init=False)
    BASE_FONT_SIZE: int = field(init=False)
    SPLASH_ENABLED: bool = field(init=False)
    STEAM_FRIENDS_ENABLED: bool = field(init=False)

    VERTICAL_CAPSULE_SIZE: QSize = field(init=False)
    HORIZONTAL_CAPSULE_SIZE: QSize = field(init=False)
    COLLECTION_STYLE: str = field(init=False)
    LIST_STYLE: str = field(init=False)
    GRID_STYLE: str = field(init=False)
    ALTERNATE_LIST_ROW_COLORS: bool = field(init=False)
    SORT_FAVOURITES_FIRST: bool = field(init=False)
    SORT_BY_RECENTLY_PLAYED: bool = field(init=False)

    PREFERS_DARK_MODE: bool = darkdetect.isDark()
    THEME: str = field(init=False)
    LAUNCH_PROCESS_DETACHED: bool = field(init=False)

    RESOURCE_PATH: str = field(init=False)
    USER_DATA_PATH: str = field(init=False)
    DEBUG_LEVELS: Dict[str, int] = field(init=False)

    APP_ICON_ON_DARK: str = field(init=False)
    APP_ICON_ON_LIGHT: str = field(init=False)
    APP_ICON: str = field(init=False)

    SPLASH_IMAGE_ON_DARK: str = field(init=False)
    SPLASH_IMAGE_ON_LIGHT: str = field(init=False)
    SPLASH_IMAGE: str = field(init=False)

    def __post_init__(self):
        if not AppConfig._initialized:
            if not AppConfig._metadata_set:
                QCoreApplication.setApplicationName(self._config_file.get("APP_TITLE"))
                QCoreApplication.setOrganizationName(self._config_file.get("DEVELOPER"))
                QCoreApplication.setApplicationVersion(
                    self._config_file.get("APP_VERSION")
                )
                QCoreApplication.setOrganizationDomain(
                    self._config_file.get("GITHUB_URL")
                )
                AppConfig._metadata_set = True

            AppConfig.APP_TITLE = str(self._config_file.get("APP_TITLE"))
            AppConfig.APP_VERSION = str(self._config_file.get("APP_VERSION"))
            AppConfig.DEVELOPER = str(self._config_file.get("DEVELOPER"))
            AppConfig.GITHUB_URL = str(self._config_file.get("GITHUB_URL"))
            AppConfig.DEV_MODE = bool(self._config_file.get("DEV_MODE"))
            AppConfig.PORTABLE = bool(self._config_file.get("PORTABLE"))
            AppConfig.BASE_FONT_SIZE = int(self._config_file.get("BASE_FONT_SIZE", 9))
            AppConfig.SPLASH_ENABLED = bool(self._config_file.get("SPLASH_ENABLED"))
            AppConfig.STEAM_FRIENDS_ENABLED = bool(
                self._config_file.get("STEAM_FRIENDS_ENABLED")
            )
            AppConfig.VERTICAL_CAPSULE_SIZE = QSize(
                *self._config_file.get("VERTICAL_CAPSULE_SIZE")
            )
            AppConfig.HORIZONTAL_CAPSULE_SIZE = QSize(
                *self._config_file.get("HORIZONTAL_CAPSULE_SIZE")
            )
            AppConfig.COLLECTION_STYLE = self._config_file.get(
                "COLLECTION_STYLE", "list"
            ).lower()
            if AppConfig.COLLECTION_STYLE not in {"list", "grid"}:
                raise ValueError

            AppConfig.LIST_STYLE = self._config_file.get("LIST_STYLE", "icon").lower()
            if AppConfig.LIST_STYLE not in {"icon", "logo"}:
                raise ValueError

            AppConfig.GRID_STYLE = self._config_file.get(
                "GRID_STYLE", "capsule_wide"
            ).lower()
            if AppConfig.GRID_STYLE not in {"capsule", "capsule_wide", "icon"}:
                raise ValueError

            AppConfig.ALTERNATE_LIST_ROW_COLORS = self._config_file.get(
                "ALTERNATE_LIST_ROW_COLORS", False
            )

            AppConfig.SORT_FAVOURITES_FIRST = self._config_file.get(
                "SORT_FAVOURITES_FIRST", False
            )
            AppConfig.SORT_BY_RECENTLY_PLAYED = self._config_file.get(
                "SORT_BY_RECENTLY_PLAYED", True
            )

            AppConfig.RESOURCE_PATH = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources"
            )
            AppConfig.USER_DATA_PATH = (
                QStandardPaths.writableLocation(QStandardPaths.AppLocalDataLocation)
                if not AppConfig.PORTABLE
                else os.path.join(AppConfig.RESOURCE_PATH, "userdata")
            )

            AppConfig.DEBUG_LEVELS = {
                "GameDatabaseManager": logging.INFO,
                "GameListManager": logging.INFO,
                "GameListWidget": logging.INFO,
            }

            AppConfig.THEME = self._config_file.get("THEME", "auto")
            AppConfig.LAUNCH_PROCESS_DETACHED = self._config_file.get(
                "LAUNCH_PROCESS_DETACHED", False
            )

            AppConfig.APP_ICON_ON_DARK = os.path.join(
                AppConfig.RESOURCE_PATH, "icons", "icon_on_dark.png"
            )
            AppConfig.APP_ICON_ON_LIGHT = os.path.join(
                AppConfig.RESOURCE_PATH, "icons", "icon_on_light.png"
            )
            AppConfig.APP_ICON = (
                AppConfig.APP_ICON_ON_DARK
                if AppConfig.PREFERS_DARK_MODE
                else AppConfig.APP_ICON_ON_LIGHT
            )

            AppConfig.SPLASH_IMAGE_ON_DARK = os.path.join(
                AppConfig.RESOURCE_PATH, "icons", "splash_image_on_dark.png"
            )
            AppConfig.SPLASH_IMAGE_ON_LIGHT = os.path.join(
                AppConfig.RESOURCE_PATH, "icons", "splash_image_on_light.png"
            )
            AppConfig.SPLASH_IMAGE = (
                AppConfig.SPLASH_IMAGE_ON_DARK
                if AppConfig.PREFERS_DARK_MODE
                else AppConfig.SPLASH_IMAGE_ON_LIGHT
            )

            AppConfig._initialized = True

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super(AppConfig, cls).__new__(cls, *args, **kwargs)
                print("AppConfig instance created")
        return cls._instance
