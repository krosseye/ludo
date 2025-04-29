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

APP_TITLE = "Ludo"
APP_VERSION = "0.1.0"
DEVELOPER = "Killian W (krosseye)"
GITHUB_URL = "https://github.com/krosseye/ludo"
RESOURCE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources"
)
DEFAULT_USER_CONFIG = {
    "THEME": "auto",  # auto, fusion, etc
    "BASE_FONT_SIZE": 9,
    "LOGO_POSITION_IN_HERO": "center",  # north, south, east, west, center
    "COLLECTION_STYLE": "list",  # list or grid
    "LIST_STYLE": "icon",  # icon or logo
    "GRID_STYLE": "capsule_wide",  # capsule, capsule_wide, or icon
    "STEAM_FRIENDS_ENABLED": True,
    "ALTERNATE_LIST_ROW_COLORS": False,
    "SORT_BY_RECENTLY_PLAYED": True,
    "SORT_FAVOURITES_FIRST": False,
    "KICKBACK_MODE": False,
}
