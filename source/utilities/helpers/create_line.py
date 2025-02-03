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

from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QWidget


def create_vertical_line(height=None, stretch=False) -> QWidget:
    """Create a vertical line separator."""
    line = QFrame()
    line.setFrameShape(QFrame.VLine)
    line.setFrameShadow(QFrame.Sunken)
    if height is not None:
        line.setFixedHeight(height)
    if not stretch:
        return line
    else:
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)
        layout.addStretch()
        layout.addWidget(line)
        layout.addStretch()

        return widget


def create_horizontal_line(width=None, stretch=False) -> QWidget:
    """Create a horizontal line separator."""
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setFrameShadow(QFrame.Sunken)
    if width is not None:
        line.setFixedWidth(width)
    if not stretch:
        return line
    else:
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)
        layout.addStretch()
        layout.addWidget(line)
        layout.addStretch()

        return widget
