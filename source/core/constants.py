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

import os

from PySide6.QtWidgets import QStyleFactory

DEVELOPER = "Killian W (krosseye)"  # Do not change this line

APP_TITLE = "Ludo"
APP_VERSION = "0.1.0-Alpha.1"
MAINTAINER = DEVELOPER  # Set to the active maintainer
GITHUB_URL = "https://github.com/krosseye/ludo"

RESOURCE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources"
)

COLLECTION_STYLE_OPTIONS = ["list", "grid"]
LIST_STYLE_OPTIONS = ["icon", "logo"]
GRID_STYLE_OPTIONS = ["capsule", "capsule_wide", "icon"]
THEME_OPTIONS = ["auto"] + list(QStyleFactory.keys())

DEFAULT_USER_CONFIG = {
    "THEME": "auto",
    "BASE_FONT_SIZE": 9,
    "COLLECTION_STYLE": "list",
    "LIST_STYLE": "icon",
    "GRID_STYLE": "capsule_wide",
    "STEAM_FRIENDS_ENABLED": True,
    "ALTERNATE_LIST_ROW_COLORS": False,
    "SORT_BY_RECENTLY_PLAYED": True,
    "SORT_FAVOURITES_FIRST": False,
    "KICKBACK_MODE": False,
}
