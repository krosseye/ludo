#############################################################################
##
## Copyright (C) 2025 Killian-W.
## All rights reserved.
##
## This file is part of the Ludo project.
##
## Licensed under the Mozilla Public License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at:
##     https://www.mozilla.org/en-US/MPL/2.0/
##
## This software is provided "as is," without warranties or conditions
## of any kind, either express or implied. See the License for details.
##
#############################################################################

from typing import Optional

from models import AppConfig
from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import (
    QFont,
    QFontMetrics,
    QImage,
    QPainter,
    QPainterPath,
    QPalette,
    QPen,
)
from PySide6.QtWidgets import QFrame, QWidget

CONFIG = AppConfig()
PREFERS_DARK = CONFIG.PREFERS_DARK_MODE


class HeroImageFrame(QFrame):
    """Frame to display a hero image and a logo or H1 text label centered within the frame."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._main_image: QImage = QImage()
        self._logo_image: QImage = QImage()
        self._logo_text: Optional[str] = None
        self.setFrameShape(QFrame.NoFrame)

    def set_hero_image(self, image_path: str) -> None:
        """Load and set the hero image from the given file path."""
        self._load_image(image_path, is_logo=False)

    def set_logo_image(self, logo_path: str) -> None:
        """Load and set the logo image from the given file path."""
        self._logo_text = None
        self._load_image(logo_path, is_logo=True)

    def set_logo_text(self, text: str) -> None:
        """Set an H1 text label as the logo."""
        self._logo_image = QImage()
        self._logo_text = text
        self.update()

    def _load_image(self, path: str, is_logo: bool) -> None:
        """Load an image and update the frame."""
        image = QImage(path)
        if image.isNull():
            self._handle_image_load_error(path, is_logo)
            return
        if is_logo:
            self._logo_image = image
        else:
            self._main_image = image
        self.update()

    def _handle_image_load_error(self, path: str, is_logo: bool) -> None:
        """Handle errors when loading an image."""
        image_type = "logo" if is_logo else "hero"
        print(f"Error: Could not load {image_type} image from {path}")

    def paintEvent(self, event) -> None:
        """Override to draw the hero image and logo or text in the frame."""
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        self._draw_frame_border(painter)

        if not self._main_image.isNull():
            self._draw_hero_image(painter)

        if not self._logo_image.isNull():
            self._draw_logo_image(painter)
        elif self._logo_text:
            self._draw_logo_text(painter)

    def _draw_frame_border(self, painter: QPainter) -> None:
        """Draw a border with rounded corners around the frame."""

        pen = (
            QPen(QPalette().midlight().color(), 1)
            if PREFERS_DARK
            else QPen(QPalette().mid().color(), 1)
        )
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)

        rect = self.rect()
        path = self._create_rounded_rect_path(rect)
        painter.drawPath(path)

    def _draw_hero_image(self, painter: QPainter) -> None:
        """Draw the hero image scaled to fit the frame with rounded corners."""
        rect = self.rect().adjusted(1, 1, -1, -1)
        path = self._create_rounded_rect_path(rect, 2.5)
        painter.setClipPath(path)
        self._draw_scaled_image(painter, self._main_image, rect)

    def _draw_logo_image(self, painter: QPainter) -> None:
        """Draw the logo image centered within the frame."""
        max_width, max_height = self.width() * 0.5, self.height() * 0.5
        scaled_size = self._get_scaled_size(self._logo_image, max_width, max_height)
        x = (self.width() - scaled_size[0]) // 2
        y = (self.height() - scaled_size[1]) // 2
        painter.drawImage(QRect(x, y, *scaled_size), self._logo_image)

    def _draw_logo_text(self, painter: QPainter) -> None:
        """Draw the text label centered within the frame."""
        max_width, max_height = self.width() * 0.5, self.height() * 0.5
        font = QFont()
        font.setPointSize(64)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen("#ffffff")

        font_metrics = QFontMetrics(font)
        text_rect = QRect(0, 0, int(max_width), int(max_height))

        while True:
            wrapped_text_rect = font_metrics.boundingRect(
                text_rect,
                Qt.AlignCenter | Qt.TextWordWrap,
                self._logo_text,
                0,
            )

            if (
                wrapped_text_rect.width() <= max_width
                and wrapped_text_rect.height() <= max_height
            ):
                break
            font.setPointSize(font.pointSize() - 1)
            painter.setFont(font)
            font_metrics = QFontMetrics(font)

        text_rect.moveCenter(self.rect().center())
        painter.drawText(text_rect, Qt.AlignCenter | Qt.TextWordWrap, self._logo_text)

    def _create_rounded_rect_path(self, rect: QRect, radius: float = 5) -> QPainterPath:
        """Create a rounded rectangle path for clipping."""
        path = QPainterPath()
        corner_radius = radius
        path.addRoundedRect(rect, corner_radius, corner_radius)
        return path

    def _draw_scaled_image(self, painter: QPainter, image: QImage, rect: QRect) -> None:
        """Draw the image scaled to fit within the rectangle with anti-aliasing and aspect ratio preservation."""
        image_ratio = image.width() / image.height()
        frame_ratio = rect.width() / rect.height()

        if image_ratio > frame_ratio:
            scaled_height = rect.height()
            scaled_width = int(scaled_height * image_ratio)
            x_offset = (rect.width() - scaled_width) // 2
            target_rect = QRect(
                rect.left() + x_offset, rect.top(), scaled_width, scaled_height
            )
        else:
            scaled_width = rect.width()
            scaled_height = int(scaled_width / image_ratio)
            y_offset = (rect.height() - scaled_height) // 2
            target_rect = QRect(
                rect.left(), rect.top() + y_offset, scaled_width, scaled_height
            )

        painter.drawImage(target_rect, image)

    def _get_scaled_size(
        self, image: QImage, max_width: float, max_height: float
    ) -> tuple[int, int]:
        """Calculate the scaled size for the image based on maximum width/height constraints."""
        scale_factor = min(max_width / image.width(), max_height / image.height(), 1)
        return int(image.width() * scale_factor), int(image.height() * scale_factor)
