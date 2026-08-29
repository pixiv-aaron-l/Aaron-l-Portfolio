from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox
)


from tools.json_manager import load_json, save_json


class Page(QWidget):

    def __init__(self):

        super().__init__()

        self.data = load_json(
            "site_config.json"
        )

        layout = QVBoxLayout()

        self.setLayout(
            layout
        )

        title = QLabel(
            "Website Settings"
        )

        title.setStyleSheet("""
            QLabel {
                font-size:32px;
                font-weight:bold;
            }
        """)

        layout.addWidget(
            title
        )

        self.site_name_input = QLineEdit()

        self.site_name_input.setPlaceholderText(
            "Corner branding text (e.g. Aaron-l Gallery)"
        )

        self.site_name_input.setText(
            self.data.get(
                "site_name",
                ""
            )
        )

        layout.addWidget(
            self.site_name_input
        )

        self.since_year_input = QLineEdit()

        self.since_year_input.setPlaceholderText(
            "Since year (e.g. 2025) — leave empty to hide"
        )

        self.since_year_input.setText(
            self.data.get(
                "since_year",
                ""
            )
        )

        layout.addWidget(
            self.since_year_input
        )

        layout.addStretch()

        save_button = QPushButton(
            "Save Settings"
        )

        save_button.clicked.connect(
            self.save
        )

        layout.addWidget(
            save_button
        )

    def save(self):

        data = {

            "site_name":
                self.site_name_input.text().strip(),

            "since_year":
                self.since_year_input.text().strip()

        }

        save_json(
            "site_config.json",
            data
        )

        self.data = load_json(
            "site_config.json"
        )

        QMessageBox.information(

            self,

            "Saved",

            "Website settings saved."

        )
