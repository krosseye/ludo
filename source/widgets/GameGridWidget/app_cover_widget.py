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

from models import AppConfig
from PySide6.QtCore import (
    QEasingCurve,
    QPoint,
    QPropertyAnimation,
    QSize,
    Qt,
    Signal,
)
from PySide6.QtGui import QColor, QPalette, QPixmap
from PySide6.QtWidgets import QFrame, QGraphicsDropShadowEffect, QLabel, QVBoxLayout
from utilities.generators.generate_graphic import CoverPixmap

CONFIG = AppConfig()
PREFERS_DARK_MODE = CONFIG.PREFERS_DARK_MODE
ANIMATION_DURATION: int = 75

MAX_TITLE_LENGTH: int = 38
WIDE_MAX_TITLE_LENGTH: int = 44

VERTICAL_CAPSULE_SIZE = CONFIG.VERTICAL_CAPSULE_SIZE
HORIZONTAL_CAPSULE_SIZE = CONFIG.HORIZONTAL_CAPSULE_SIZE

HEART_SPRITE_PATH = os.path.join(
    CONFIG.RESOURCE_PATH, "icons", "spritesheet", "heart_spritesheet.png"
)


class AppLauncherCover(QFrame):
    """Represents a cover art widget for launching a game."""

    clicked = Signal()
    right_click = Signal()

    def __init__(
        self,
        title: str,
        icon_path: str,
        game_id: str,
        is_favourite: bool = False,
        parent=None,
        selected: bool = False,
        size: QSize = VERTICAL_CAPSULE_SIZE,
    ) -> None:
        super().__init__(parent)

        self.title = title
        self.icon_path = icon_path
        self.game_id = game_id
        self.is_favourite = is_favourite
        self._selected = selected

        self.item_width = size.width()
        self.item_height = size.height()
        self.wide = bool(size.width() > size.height())

        self.heart_spritesheet = QPixmap(HEART_SPRITE_PATH)
        self.prefers_dark = PREFERS_DARK_MODE
        self.highlight_border_color = QPalette().highlight().color().name()
        self.button_color = QPalette().button().color()
        self.button_color.setAlpha(int(255 * 0.75))
        self.default_border_color = self._get_default_border_color()

        self._init_ui()
        self._setup_blur_animation()
        self.selected = selected
        self._configure_signals()

    def enterEvent(self, event):
        self._toggle_hover_effect(is_enter_event=True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._toggle_hover_effect(is_enter_event=False)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, selected: bool = False):
        self.highlight(selected)

        if self._selected == selected and selected is False:
            return

        self.animation.setDirection(
            QPropertyAnimation.Forward if selected else QPropertyAnimation.Backward
        )
        self.animation.start()

        self._selected = selected

    def highlight(self, selected: bool = False):
        if selected:
            self._apply_highlight_style(self.highlight_border_color, border_size=2)
            self._show_ui_elements()
        else:
            self.shadow_effect.setBlurRadius(0)
            self._hide_ui_elements()
            self._apply_highlight_style(self.default_border_color)

    def _init_ui(self):
        self.setFixedSize(self.item_width + 1, self.item_height + 1)
        self.setLayout(self._setup_layout())
        self._create_heart_overlay()
        self._hide_ui_elements()

    def _setup_blur_animation(self):
        self.shadow_effect = QGraphicsDropShadowEffect()
        self.shadow_effect.setOffset(0, 0)
        self.shadow_effect.setBlurRadius(0)
        self.shadow_effect.setColor(QColor(self.highlight_border_color))
        self.setGraphicsEffect(self.shadow_effect)

        self.animation = QPropertyAnimation(self.shadow_effect, b"blurRadius")
        self.animation.setDuration(ANIMATION_DURATION)
        self.animation.setEasingCurve(QEasingCurve.OutQuad)
        self.animation.setStartValue(0)
        self.animation.setEndValue(10)
        self.animation.stop()

    def _setup_layout(self) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.addStretch()
        layout.addWidget(
            self._create_cover_graphic(),
            alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
        )
        layout.addStretch()
        layout.addWidget(self._create_title_label())
        layout.addStretch()
        layout.setContentsMargins(0, 0, 0, 0)
        return layout

    def _configure_signals(self):
        self.setFocusPolicy(Qt.ClickFocus)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def _show_context_menu(self, pos: QPoint) -> None:
        """Emit the right-click signal to show the context menu."""
        self.right_click.emit()

    def _get_default_border_color(self) -> str:
        button_color = QPalette().button().color()
        return (
            button_color.lighter().name()
            if self.prefers_dark
            else button_color.darker().name()
        )

    def _create_cover_graphic(self) -> QLabel:
        label = QLabel(self)
        pixmap = self._load_icon()
        scaled_pixmap = pixmap.scaled(
            self.item_width,
            self.item_height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        label.setPixmap(scaled_pixmap)
        label.setFixedSize(self.item_width, self.item_height)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover_graphic = label
        return label

    def _create_title_label(self) -> QLabel:
        _max_title_length = WIDE_MAX_TITLE_LENGTH if self.wide else MAX_TITLE_LENGTH

        truncated_title = (
            self.title[:_max_title_length] + "..."
            if len(self.title) > _max_title_length
            else self.title
        )

        r, g, b, a = (
            self.button_color.red(),
            self.button_color.green(),
            self.button_color.blue(),
            self.button_color.alpha() / 255.0,
        )

        label = QLabel(truncated_title)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(f"""
            QLabel {{
                padding:5px;
                margin:10px;
                border-radius:5px;
                border: 1px solid {self.default_border_color};
                background-color: rgba({r}, {g}, {b}, {a});
            }}
        """)

        if len(self.title) > _max_title_length:
            label.setToolTip(self.title)
        self.title_label = label

        return label

    def _create_heart_overlay(self):
        size = 32
        r, g, b, a = (
            self.button_color.red(),
            self.button_color.green(),
            self.button_color.blue(),
            self.button_color.alpha() / 255.0,
        )
        self.circle_label = QLabel(self)
        self.circle_label.setFixedSize(size, size)
        self.circle_label.setStyleSheet(f"""
            background-color: rgba({r}, {g}, {b}, {a});
            border-radius: {size / 2}px;
            border: 1px solid {self.default_border_color};
        """)
        self.circle_label.move(self.width() - size - 8, 7)

        self.heart_label = QLabel(self)
        self.heart_label.setFixedSize(24, 24)
        self.heart_label.setPixmap(
            self.heart_spritesheet.copy(384, 0, 192, 192).scaled(
                24, 24, Qt.KeepAspectRatio
            )
        )

        self._center_heart()

    def _center_heart(self):
        circle_x, circle_y = self.circle_label.x(), self.circle_label.y()
        circle_width, circle_height = (
            self.circle_label.width(),
            self.circle_label.height(),
        )
        heart_width, heart_height = self.heart_label.width(), self.heart_label.height()

        self.heart_label.move(
            circle_x + (circle_width - heart_width) // 2,
            circle_y + (circle_height - heart_height) // 2,
        )

    def _load_icon(self) -> QPixmap:
        if os.path.exists(self.icon_path):
            return QPixmap(self.icon_path).scaled(
                self.item_width, self.item_height, Qt.KeepAspectRatio
            )
        return CoverPixmap(
            seed=self.title, width=self.item_width, height=self.item_height
        )

    def _apply_highlight_style(self, border_color: str, border_size: int = 1):
        self.cover_graphic.setStyleSheet(
            f"border: {border_size}px solid {border_color};background-color:{QPalette().button().color().name()};"
        )

    def _show_ui_elements(self):
        self.circle_label.setVisible(self.is_favourite)
        self.heart_label.setVisible(self.is_favourite)
        self.title_label.setVisible(True)

    def _hide_ui_elements(self):
        self.circle_label.setVisible(False)
        self.heart_label.setVisible(False)
        self.title_label.setVisible(False)

    def _toggle_hover_effect(self, is_enter_event: bool):
        if not self._selected:
            self._show_ui_elements() if is_enter_event else self._hide_ui_elements()
