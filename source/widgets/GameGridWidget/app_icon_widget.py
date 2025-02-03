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
from typing import Any

from models import AppConfig
from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QRect, Qt, Signal
from PySide6.QtGui import QIcon, QPainter, QPalette, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QLabel,
    QVBoxLayout,
    QWidget,
)
from utilities.generators.generate_graphic import IconPixmap

CONFIG = AppConfig()

ITEM_WIDTH = 48
ITEM_HEIGHT = 48
ANIMATION_DURATION = 75


class AppLauncherIcon(QFrame):
    """Represents an icon button for launching a game."""

    clicked: Signal = Signal()
    right_click: Signal = Signal()

    def __init__(
        self,
        title: str,
        icon_path: str,
        game_id: str,
        is_favourite: bool = False,
        parent=None,
        selected: bool = False,
    ) -> None:
        super().__init__(parent)
        self._selected = selected
        self.game_id: str = game_id
        self.is_favourite: bool = is_favourite

        self._init_ui(title, icon_path)
        self._setup_blur_animation()
        self.selected = self._selected

        self.setFocusPolicy(Qt.ClickFocus)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def _init_ui(self, title: str, icon_path: str) -> None:
        """Initialize UI components of the button."""
        self.setLayout(QVBoxLayout())

        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        widget.setLayout(layout)

        # Truncate the title if it's longer than 24 characters
        self.truncated_title: str = title if len(title) <= 24 else title[:24] + "..."

        self.icon_label: QLabel = QLabel()
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setFixedHeight(ITEM_HEIGHT)
        self.icon_label.setPixmap(self._load_icon(icon_path))

        self.title_label: QLabel = QLabel(self.truncated_title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setWordWrap(True)
        self.setToolTip(title)

        layout.addStretch()
        layout.addWidget(self.icon_label)
        layout.addStretch()
        layout.addWidget(self.title_label)
        layout.addStretch()

        self.layout().addWidget(widget)
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.setFixedSize(96, 112)

        self.setFrameShape(QFrame.StyledPanel)

        self.heart_spritesheet = QPixmap(
            os.path.join(CONFIG.RESOURCE_PATH, "icons", "heart_spritesheet.png")
        )

    def _setup_blur_animation(self) -> None:
        """Set up the drop shadow effect and blur radius animation."""
        self.shadow_effect = QGraphicsDropShadowEffect(self)
        self.shadow_effect.setOffset(0, 0)
        self.shadow_effect.setBlurRadius(0)
        self.shadow_effect.setColor(QPalette().highlight().color())
        self.setGraphicsEffect(self.shadow_effect)

        self.blur_animation = QPropertyAnimation(self.shadow_effect, b"blurRadius")
        self.blur_animation.setDuration(ANIMATION_DURATION)
        self.blur_animation.setEasingCurve(QEasingCurve.OutQuad)

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, selected: bool = False):
        if selected:
            self.highlight()
            self._start_animation(True)
        else:
            self.reset_highlight()
            if self._selected == selected:
                return
            self._start_animation(False)

        self._selected = selected

    def _start_animation(self, expand: bool) -> None:
        """Start the blur radius animation."""
        self.blur_animation.stop()
        if expand:
            self.blur_animation.setStartValue(0)
            self.blur_animation.setEndValue(10)  # Maximum blur radius for selection
        else:
            self.blur_animation.setStartValue(10)
            self.blur_animation.setEndValue(0)  # No shadow for unselected state
        self.blur_animation.start()

    def _load_icon(self, icon_path: str) -> QPixmap:
        """Load the icon using QIcon for consistent handling of all file types."""
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
            pixmap = icon.pixmap(ITEM_WIDTH, ITEM_HEIGHT)
            return pixmap
        else:
            return IconPixmap(
                title=self.truncated_title, width=ITEM_WIDTH, height=ITEM_HEIGHT
            )

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)

    def paintEvent(self, event) -> None:
        """Custom paint event to draw the heart graphic."""
        super().paintEvent(event)

        if self.is_favourite and not self.heart_spritesheet.isNull():
            painter = QPainter(self)
            padding = 5

            # Define the rectangle for the third heart in the spritesheet
            heart_width = 192
            heart_height = 192
            heart_rect = QRect(heart_width * 2, 0, heart_width, heart_height)

            scale = 24

            painter.drawPixmap(
                self.width() - scale - padding,
                padding,
                scale,
                scale,
                self.heart_spritesheet,
                heart_rect.x(),
                heart_rect.y(),
                heart_rect.width(),
                heart_rect.height(),
            )
            painter.end()

    def _show_context_menu(self, pos: Any) -> None:
        """Emit the right-click signal to show the context menu."""
        self.right_click.emit()

    def highlight(self) -> None:
        """Highlight the button with a different background color and an outline."""
        self.setStyleSheet(f"""
            AppLauncherIcon{{
                background-color: {QPalette().toolTipBase().color().lighter().name()};
                border: 2px solid {QPalette().highlight().color().name()}; border-radius:5px;
                padding:-1px;
            }}                   
            """)

    def reset_highlight(self) -> None:
        """Reset the button's background color and remove the outline."""
        self.setStyleSheet(
            f"""AppLauncherIcon{{
                background-color: {QPalette().button().color().name()};
                border: 1px solid {QPalette().button().color().lighter().name()};border-radius:5px;
                }}
                """
        )
