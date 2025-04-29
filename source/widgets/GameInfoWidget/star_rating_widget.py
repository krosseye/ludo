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

from core.app_config import app_config
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QGridLayout, QLabel, QWidget

SPRITESHEET_PATH = os.path.join(
    app_config.RESOURCE_PATH,
    "icons",
    "spritesheet",
    "star_rating_spritesheet.png",
)


class StarRatingWidget(QWidget):
    SPRITE_SIZE = 192
    TOTAL_FRAMES = 11

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.spritesheet_path = SPRITESHEET_PATH
        self.stars: list = []
        self._rating: float = 0
        self._scaled_pixmaps_cache: dict = {}

        self._setup_layout()
        self._initialize_stars()

    @property
    def rating(self):
        """
        Get the star rating (float between 0 and 5 in intervals of 0.1).
        """
        return self._rating

    @rating.setter
    def rating(self, rating):
        """
        Set the star rating.
        :param rating: float between 0 and 5 in intervals of 0.1
        """
        self._rating = self._clamp_rating(rating)
        full_sprites = int(self._rating)  # Number of full stars
        fractional_index = round((self._rating - full_sprites) * 10)
        fractional_index = max(0, min(self.TOTAL_FRAMES - 1, fractional_index))

        if not self.stars:
            return

        star_size = self._get_star_size()
        for i, label in enumerate(self.stars):
            if i < full_sprites:
                offset = self.SPRITE_SIZE * 10  # Full star
            elif i == full_sprites and fractional_index > 0:
                offset = self.SPRITE_SIZE * fractional_index  # Fractional star
            else:
                offset = 0  # Empty star

            star_pixmap = self._get_scaled_pixmap(
                offset, (star_size.width(), star_size.height())
            )
            label.setPixmap(star_pixmap)

    def _setup_layout(self):
        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.setAlignment(Qt.AlignLeft)

    def _initialize_stars(self):
        for i in range(5):
            label = QLabel(self)
            label.setScaledContents(False)
            self.layout.addWidget(label, 0, i, alignment=Qt.AlignLeft)
            self.stars.append(label)

    def _clamp_rating(self, rating):
        return max(0, min(5, rating))

    def _get_scaled_pixmap(self, offset, size):
        key = (offset, size)
        if key not in self._scaled_pixmaps_cache:
            pixmap = QPixmap(self.spritesheet_path)
            original_pixmap = pixmap.copy(0, offset, self.SPRITE_SIZE, self.SPRITE_SIZE)
            scaled_pixmap = original_pixmap.scaled(
                size[0], size[1], Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self._scaled_pixmaps_cache[key] = scaled_pixmap
        return self._scaled_pixmaps_cache[key]

    def _get_star_size(self):
        widget_height = self.height()
        star_height = widget_height
        star_width = int(star_height * (self.SPRITE_SIZE / self.SPRITE_SIZE))
        return QSize(star_width, star_height)

    def resizeEvent(self, event):
        self.rating = self._rating
        super().resizeEvent(event)
