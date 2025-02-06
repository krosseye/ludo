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
from typing import Optional

from models import AppConfig
from PySide6.QtCore import Qt
from PySide6.QtGui import QFontMetrics, QPixmap
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

CONFIG = AppConfig()
HEART_SPRITESHEET = os.path.join(
    CONFIG.RESOURCE_PATH, "icons", "spritesheet", "heart_spritesheet.png"
)


class ListItemWidget(QWidget):
    def __init__(
        self,
        icon: Optional[QPixmap] = None,
        text: str = "",
        is_favourite: bool = False,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.is_favourite = is_favourite
        self.favourite_icon_min_width = 200
        self.full_text = text

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(10)

        self.icon_label = QLabel(self)
        self.text_label = QLabel(self)
        self.favourite_label = QLabel(self)

        heart_spritesheet = QPixmap(HEART_SPRITESHEET)
        self.heart_icon = heart_spritesheet.copy(384, 0, 192, 192).scaled(
            24, 24, Qt.KeepAspectRatio
        )
        self.favourite_label.setPixmap(self.heart_icon)

        self.layout.addWidget(self.icon_label)
        self.layout.addWidget(self.text_label, 1)
        self.layout.addWidget(self.favourite_label)
        self.layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.setStyleSheet("QLabel {background-color: transparent;}")
        self.update_data(icon, text, is_favourite)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_favourite_icon_visibility()
        self._set_text_with_ellipsis()

    def _update_favourite_icon_visibility(self):
        self.favourite_label.setVisible(
            self.width() >= self.favourite_icon_min_width and self.is_favourite
        )

    def _set_text_with_ellipsis(self):
        elided_text = QFontMetrics(self.text_label.font()).elidedText(
            self.full_text, Qt.ElideRight, self.text_label.width()
        )
        self.text_label.setText(elided_text)

    def update_data(
        self, icon: Optional[QPixmap] = None, text: str = "", is_favourite: bool = False
    ):
        if icon:
            self.icon_label.setPixmap(icon)
        self.full_text = text
        self.is_favourite = is_favourite
        self._update_favourite_icon_visibility()
        self._set_text_with_ellipsis()
