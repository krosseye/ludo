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

from core.app_config import app_config
from PySide6.QtCore import QRect, QSize, Qt, Signal
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QSizePolicy, QWidget

RESOURCES_PATH = os.path.join(app_config.RESOURCE_PATH, "icons", "spritesheet")


class LabeledSpritesheetCheckBox(QWidget):
    stateChanged = Signal(int)

    def __init__(self, text: Optional[str] = "", spritesheet_path: str = ""):
        super().__init__()
        self.enabled = True
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setCursor(Qt.PointingHandCursor)
        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

        self.checkBox = SpritesheetCheckBox(self, spritesheet_path)
        self.checkBox.setFixedSize(24, 24)
        self.checkBox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.checkBox.stateChanged.connect(lambda state: self.stateChanged.emit(state))

        self.label = QLabel(text)
        self.label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

        layout.addWidget(self.checkBox)
        layout.addWidget(self.label)

        if text is None:
            self.label.setVisible(False)

    def setText(self, text):
        if text is None:
            self.label.setVisible(False)
            self.label.clear()
        else:
            self.label.setVisible(True)
            self.label.setText(text)

    def enterEvent(self, event):
        self.checkBox.enterEvent(event)

    def leaveEvent(self, event):
        self.checkBox.leaveEvent(event)

    def mousePressEvent(self, event):
        self.checkBox.mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.checkBox.update()
        event.accept()

    def setChecked(self, checked):
        self.checkBox.setChecked(checked)

    def setEnabled(self, enabled: bool):
        self.enabled = enabled
        self.checkBox.setEnabled(enabled)
        self.label.setEnabled(enabled)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, not enabled)
        self.setCursor(Qt.ArrowCursor if not enabled else Qt.PointingHandCursor)


class SpritesheetCheckBox(QCheckBox):
    def __init__(self, parent=None, spritesheet_path: str = ""):
        super().__init__(parent)
        self.enabled = True
        if not spritesheet_path:
            self.spritesheet = QPixmap(
                os.path.join(RESOURCES_PATH, "heart_spritesheet.png")
            )
        else:
            self.spritesheet = QPixmap(spritesheet_path)
        self.sprite_size = QSize(192, 192)
        self.hovering = False

        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(self.sprite_size)
        self.setContentsMargins(0, 0, 0, 0)
        self.setMouseTracking(True)

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        # Determine which sprite to use (0: unchecked, 1: hover, 2: checked)
        if self.isChecked() and self.enabled:
            sprite_x = 2 * self.sprite_size.width()  # Checked (third sprite)
        elif self.hovering and self.enabled:
            sprite_x = self.sprite_size.width()  # Hover (second sprite)
        else:
            sprite_x = 0  # Unchecked (first sprite)

        source_rect = QRect(
            sprite_x, 0, self.sprite_size.width(), self.sprite_size.height()
        )

        painter.drawPixmap(self.rect(), self.spritesheet, source_rect)

    def enterEvent(self, event):
        self.hovering = True
        self.update()

    def leaveEvent(self, event):
        self.hovering = False
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setChecked(not self.isChecked())
            self.update()
        event.accept()

    def setChecked(self, checked):
        super().setChecked(checked)

    def hitButton(self, pos):
        return self.rect().contains(pos)

    def sizeHint(self):
        return self.sprite_size

    def setEnabled(self, enabled: bool):
        self.enabled = enabled
        self.update()
        self.setAttribute(Qt.WA_TransparentForMouseEvents, not enabled)
        self.setCursor(Qt.ArrowCursor if not enabled else Qt.PointingHandCursor)
