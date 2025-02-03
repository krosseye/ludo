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

import hashlib

from PySide6.QtCore import QPointF, QRect, Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontMetrics,
    QLinearGradient,
    QPainter,
    QPalette,
    QPixmap,
)


class IconPixmap(QPixmap):
    def __init__(self, title: str = "?", width=128, height=128):
        super().__init__(width, height)
        self.title = title
        self._generate_icon()

    def _generate_icon(self):
        """
        Generate a QPixmap with the first two letters of the title as the icon.
        """
        self.fill(Qt.transparent)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        font = QFont()
        font.setPointSize(int(self.width() * 0.50))
        font.setBold(True)
        painter.setFont(font)

        first_two_letters = self.title[:2]

        painter.setPen(QPalette().text().color())
        painter.drawText(self.rect(), Qt.AlignCenter, first_two_letters)

        painter.end()


class HeroPixmap(QPixmap):
    def __init__(self, width=1920, height=620, seed=None):
        super().__init__(width, height)

        self.palette = QPalette()
        self.gradient = self._create_gradient(seed)
        self._fill_pixmap()

    def _create_gradient(self, seed):
        """
        Create a linear gradient based on the seed or palette highlight color.
        """
        gradient = QLinearGradient(QPointF(0, 0), QPointF(self.width(), self.height()))
        if not seed:
            default_color = self.palette.highlight().color()
            gradient.setColorAt(0.0, default_color.lighter())
            gradient.setColorAt(1.0, default_color)
        else:
            color = self._string_to_color(seed)
            gradient.setColorAt(0.0, color)
            gradient.setColorAt(1.0, color.darker())
        return gradient

    def _string_to_color(self, seed: str):
        """
        Convert a string seed into a QColor.
        """
        hash_object = hashlib.sha256(seed.encode())
        r, g, b = [int(hash_object.hexdigest()[i : i + 2], 16) for i in range(0, 6, 2)]
        return QColor.fromRgb(r, g, b).lighter(150)

    def _fill_pixmap(self):
        """
        Fill the pixmap with the gradient.
        """
        painter = QPainter(self)
        painter.setBrush(self.gradient)
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())
        painter.end()


class CoverPixmap(QPixmap):
    def __init__(self, width=600, height=900, seed=None):
        super().__init__(width, height)

        self.title = seed

        self.palette = QPalette()
        self.gradient = self._create_gradient(seed)
        self._fill_pixmap()

    def _create_gradient(self, seed):
        """
        Create a linear gradient based on the seed or palette highlight color.
        """
        gradient = QLinearGradient(QPointF(0, 0), QPointF(self.width(), self.height()))
        if not seed:
            default_color = self.palette.highlight().color()
            gradient.setColorAt(0.0, default_color.lighter())
            gradient.setColorAt(1.0, default_color)
        else:
            color = self._string_to_color(seed)
            gradient.setColorAt(0.0, color)
            gradient.setColorAt(1.0, color.darker())
        return gradient

    def _string_to_color(self, seed: str):
        """
        Convert a string seed into a QColor.
        """
        hash_object = hashlib.sha256(seed.encode())
        r, g, b = [int(hash_object.hexdigest()[i : i + 2], 16) for i in range(0, 6, 2)]
        return QColor.fromRgb(r, g, b).lighter(150)

    def _fill_pixmap(self):
        """
        Fill the pixmap with the gradient and draw the title with adaptive font size.
        """
        painter = QPainter(self)
        painter.setBrush(self.gradient)
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())

        font = QFont()
        font.setBold(True)
        font.setPointSize(32)

        font_metrics = QFontMetrics(font)
        max_width, max_height = (
            self.width() * 0.75,
            self.height() * 0.75,
        )
        text_rect = QRect(0, 0, max_width, max_height)

        while True:
            wrapped_text_rect = font_metrics.boundingRect(
                text_rect, Qt.AlignCenter | Qt.TextWordWrap, self.title
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

        painter.setFont(font)
        painter.setPen(QColor("white"))
        painter.drawText(text_rect, Qt.AlignCenter | Qt.TextWordWrap, self.title)

        painter.end()
