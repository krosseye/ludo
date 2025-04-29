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

from dataclasses import dataclass


@dataclass
class Game:
    # Basic info
    id: str = ""  # Unique identifier for the game
    title: str = ""  # Display name of the game
    sortTitle: str = ""  # Alternate title used for sorting

    # User preferences
    favourite: bool = False  # Whether the game is marked as a favorite
    starRating: float = 0.0  # User's star rating for the game

    # Metadata
    developer: str = ""  # Game developer's name
    publisher: str = ""  # Game publisher's name
    year: int = 0  # Year the game was released
    description: str = ""  # Short description or summary of the game

    # Paths and launch configuration
    executablePath: str = ""  # Path to the game's executable file
    workingDirectory: str = ""  # Working directory when launching
    launchOptions: str = ""  # Custom launch options or arguments
    browseDirectory: str = ""  # Path for browsing related files or assets

    # Gameplay stats
    lastPlayed: str = ""  # ISO 8601 datetime format
    sessionsPlayed: int = 0  # Total number of sessions played
    playtime: float = 0.0  # Total playtime in minutes
