from core.config import user_config
from core.constants import (
    APP_TITLE,
    COLLECTION_STYLE_OPTIONS,
    DEFAULT_USER_CONFIG,
    GRID_STYLE_OPTIONS,
    LIST_STYLE_OPTIONS,
    LOGO_POSITION_IN_HERO_OPTIONS,
    THEME_OPTIONS,
)
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{APP_TITLE} Settings")
        self.setMinimumWidth(400)

        self.controls = {}
        self.initial_values = user_config.copy()

        self.layout = QVBoxLayout(self)
        self.form_layout = QFormLayout()
        self.changed = False

        self.build_ui()
        self.update_save_button_state()

    def build_ui(self):
        # Comboboxes
        self._add_combobox("THEME", THEME_OPTIONS)
        self._add_spinbox("BASE_FONT_SIZE", min_=6, max_=24)
        self._add_combobox("LOGO_POSITION_IN_HERO", LOGO_POSITION_IN_HERO_OPTIONS)
        self._add_combobox("COLLECTION_STYLE", COLLECTION_STYLE_OPTIONS)
        self._add_combobox("LIST_STYLE", LIST_STYLE_OPTIONS)
        self._add_combobox("GRID_STYLE", GRID_STYLE_OPTIONS)

        # Checkboxes
        for key in [
            "STEAM_FRIENDS_ENABLED",
            "ALTERNATE_LIST_ROW_COLORS",
            "SORT_BY_RECENTLY_PLAYED",
            "SORT_FAVOURITES_FIRST",
        ]:
            self._add_checkbox(key)

        # Save / Cancel buttons
        self.save_btn = QPushButton("Apply")
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self.save_settings)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)

        form_widget = QWidget()
        form_widget.setLayout(self.form_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(form_widget)

        self.layout.addWidget(scroll_area)
        self.layout.addLayout(btn_layout)

    def _add_combobox(self, key, options):
        combo = QComboBox()
        combo.addItems(options)
        current_value = user_config.get(key)
        if current_value in options:
            combo.setCurrentText(current_value)
        combo.currentTextChanged.connect(self._on_change)
        self.controls[key] = combo
        self._add_row_with_reset(self._labelize(key), combo, key)

    def _add_spinbox(self, key, min_, max_):
        spin = QSpinBox()
        spin.setMinimum(min_)
        spin.setMaximum(max_)
        spin.setValue(user_config.get(key))
        spin.valueChanged.connect(self._on_change)
        self.controls[key] = spin
        self._add_row_with_reset(self._labelize(key), spin, key)

    def _add_checkbox(self, key):
        checkbox = QCheckBox()
        checkbox.setChecked(user_config.get(key))
        checkbox.stateChanged.connect(self._on_change)
        self.controls[key] = checkbox
        self._add_row_with_reset(self._labelize(key), checkbox, key)

    def _add_row_with_reset(self, label_text, widget, key):
        layout = QHBoxLayout()
        layout.addWidget(widget)

        reset_btn = QPushButton("↺")
        reset_btn.setToolTip("Reset to default")
        reset_btn.setFixedWidth(24)
        reset_btn.clicked.connect(lambda: self._reset_field(key))
        layout.addWidget(reset_btn)

        container = QLabel()
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.form_layout.addRow(QLabel(label_text), layout)

    def _reset_field(self, key):
        default_value = DEFAULT_USER_CONFIG.get(key)
        widget = self.controls[key]

        if isinstance(widget, QComboBox):
            widget.setCurrentText(default_value)
        elif isinstance(widget, QSpinBox):
            widget.setValue(default_value)
        elif isinstance(widget, QCheckBox):
            widget.setChecked(default_value)

        self._on_change()

    def _labelize(self, key):
        return " ".join(word.capitalize() for word in key.split("_"))

    def _on_change(self):
        self.update_save_button_state()

    def update_save_button_state(self):
        self.changed = any(
            self._value_from_widget(key, widget) != self.initial_values.get(key)
            for key, widget in self.controls.items()
        )
        self.save_btn.setEnabled(self.changed)

    def _value_from_widget(self, key, widget):
        if isinstance(widget, QComboBox):
            return widget.currentText()
        elif isinstance(widget, QSpinBox):
            return widget.value()
        elif isinstance(widget, QCheckBox):
            return widget.isChecked()

    def save_settings(self):
        updated = False

        for key, widget in self.controls.items():
            new_val = self._value_from_widget(key, widget)
            if user_config.get(key) != new_val:
                user_config[key] = new_val
                updated = True

        if updated:
            user_config.save()
            self._prompt_restart()

        self.accept()

    def _prompt_restart(self):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Restart Required")
        msg.setText("Settings have been updated.")
        msg.setInformativeText(
            "The application must be restarted to apply the changes."
        )
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.button(QMessageBox.Yes).setText("Restart Now")
        msg.button(QMessageBox.No).setText("Later")

        if msg.exec() == QMessageBox.Yes:
            self._restart_app()

    @staticmethod
    def _restart_app():
        import sys

        from PySide6.QtCore import QProcess

        QProcess.startDetached(sys.executable, sys.argv)
        import PySide6.QtWidgets as QtWidgets

        QtWidgets.QApplication.quit()
