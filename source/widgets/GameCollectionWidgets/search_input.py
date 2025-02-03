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

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
)


class SearchBarWidget(QFrame):
    """A custom widget that combines a search input field and a clear button."""

    search_text_changed = Signal(str)
    return_key_pressed = Signal(str)
    cleared = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 5, 0)
        self.setFrameShape(QFrame.StyledPanel)

        search_icon = QIcon.fromTheme("edit-find")
        icon_label = QLabel(self)
        icon_label.setPixmap(search_icon.pixmap(16, 16))
        icon_label.setFixedSize(16, 16)

        self.search_bar = QLineEdit(self)
        self.search_bar.setStyleSheet("background-color: transparent; border: none;")
        self.search_bar.setPlaceholderText("Search by Name...")
        self.search_bar.setFixedHeight(32)

        self.clear_button = QPushButton(self, icon=QIcon.fromTheme("window-close"))
        self.clear_button.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
                font-size: 14px;
            }
        """)
        self.clear_button.setIconSize(QSize(8, 8))
        self.clear_button.setFixedSize(24, 24)
        self.clear_button.setCursor(Qt.PointingHandCursor)

        self.clear_button.hide()

        self.search_bar.textChanged.connect(self.text_changed)
        self.search_bar.returnPressed.connect(self.return_pressed)
        self.clear_button.clicked.connect(self.clear)

        layout.addWidget(icon_label)
        layout.addWidget(self.search_bar)
        layout.addWidget(self.clear_button)

        self.setLayout(layout)

    def text(self):
        return str(self.search_bar.text())

    def clear(self):
        """Clear the text in the search bar."""
        self.search_bar.clear()
        self.search_bar.setFocus()
        self.cleared.emit()

    def text_changed(self, text):
        """Emit the signal when the search text changes and toggle clear button visibility."""
        self.search_text_changed.emit(text)
        self.clear_button.setVisible(bool(text))

    def return_pressed(self):
        """Emit the signal when the return key is pressed."""
        self.return_key_pressed.emit(self.search_bar.text().strip())
