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

from models import AppConfig
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
)

CONFIG = AppConfig()


class AboutDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setFixedSize(550, 500)

        icon_path = CONFIG.APP_ICON
        self.app_title = CONFIG.APP_TITLE
        self.domain = CONFIG.GITHUB_URL
        self.version = CONFIG.APP_VERSION
        self.developer = CONFIG.DEVELOPER

        icon_label = QLabel()
        icon_label.setPixmap(
            QPixmap(icon_path).scaled(
                128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        )
        icon_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        header_label = QLabel(f"<h1>About {self.app_title}</h1>")
        header_label.setTextFormat(Qt.RichText)
        header_label.setAlignment(Qt.AlignLeft)
        header_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        html_content = self._generate_about_text()

        description_label = QLabel(html_content)
        description_label.setWordWrap(True)
        description_label.setAlignment(Qt.AlignTop)
        description_label.setOpenExternalLinks(True)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.StyledPanel)
        description_label.setContentsMargins(10, 10, 10, 10)
        scroll_area.setWidget(description_label)

        okay_button = QPushButton("OK")
        okay_button.clicked.connect(self.accept)
        okay_button.setDefault(True)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(okay_button)

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(header_label)
        vertical_layout.addWidget(scroll_area)

        horizontal_layout = QHBoxLayout()
        horizontal_layout.addWidget(icon_label, alignment=Qt.AlignTop)
        horizontal_layout.addLayout(vertical_layout)

        main_layout = QVBoxLayout()
        main_layout.addLayout(horizontal_layout)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
        self.setWindowTitle(f"About {self.app_title}")

    def _generate_about_text(self):
        html_content = f"""
            <p><strong>{self.app_title}</strong> is a universal game launcher designed to unify all your gaming platforms into a single, seamless experience.</p>
            <p>Built with <strong>PySide6/Qt</strong>, {self.app_title} offers a fast, native desktop experience with a customizable interface.</p>
            <p>You are currently using version <strong>{self.version}</strong>.</p>
    
            <h2>Important Notice</h2>
            <p><em>{self.app_title} is under active development. All features, design, and functionality are subject to change as the project evolves.</em></p>
            <p>For more information and to access the source code, visit the project's <a href="{self.domain}">GitHub repository</a>.</p>
    
            <h2>License</h2>
            <p>This project is distributed under the 
            <a href="https://www.mozilla.org/en-US/MPL/2.0/">Mozilla Public License (MPL v2.0)</a>.</p>
            <footer>Copyright © 2025, {self.developer}.</footer>
        """

        return html_content
