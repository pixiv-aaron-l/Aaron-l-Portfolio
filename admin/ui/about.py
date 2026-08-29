from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QFrame,
    QScrollArea
)


from tools.json_manager import load_json, save_json
from tools.update_manager import update_last_modified


# ============================================================
# Shared header style for section labels inside the editor
# (Introduction / Links), so both look consistent.
# ============================================================

SECTION_LABEL_STYLE = """
    QLabel {
        font-size:18px;
        font-weight:bold;
        margin-top:12px;
    }
"""


def normalize_links(links):

    """
    Always returns a plain list of {"text", "url"} dicts,
    regardless of which older about.json shape is on disk:

    - current format: a plain list
        [{"text": "...", "url": "..."}, ...]

    - previous format: predefined + custom
        {"predefined": {...}, "custom": [...]}

    - original format: flat predefined links only
        {"pixiv": "...", "reddit": "...", "discord": "..."}

    Links are fully manual, so any old "predefined"
    Pixiv/Reddit/Discord entries are intentionally NOT carried
    over automatically. Only entries that were already manually
    created (the old "custom" list, or the current plain list)
    are preserved.
    """

    if isinstance(
        links,
        list
    ):

        result = []

        for entry in links:

            if not isinstance(
                entry,
                dict
            ):

                continue

            result.append({

                "text": entry.get(
                    "text",
                    ""
                ),

                "url": entry.get(
                    "url",
                    ""
                )

            })

        return result

    if isinstance(
        links,
        dict
    ):

        custom = links.get(
            "custom",
            []
        )

        result = []

        if isinstance(
            custom,
            list
        ):

            for entry in custom:

                if not isinstance(
                    entry,
                    dict
                ):

                    continue

                result.append({

                    "text": entry.get(
                        "text",
                        ""
                    ),

                    "url": entry.get(
                        "url",
                        ""
                    )

                })

        return result

    return []


class LinkRow(QFrame):

    """
    One editable row for an About Me link:
    clickable text + URL + a remove button. Lives inside the
    scrollable links box.
    """

    def __init__(self, text="", url="", on_remove=None):

        super().__init__()

        self.on_remove = on_remove

        layout = QHBoxLayout()

        self.setLayout(
            layout
        )

        layout.setContentsMargins(
            0, 0, 0, 0
        )

        self.text_input = QLineEdit()

        self.text_input.setPlaceholderText(
            "Link text (e.g. Pixiv, My Twitter)"
        )

        self.text_input.setText(
            text
        )

        self.url_input = QLineEdit()

        self.url_input.setPlaceholderText(
            "https://..."
        )

        self.url_input.setText(
            url
        )

        self.remove_button = QPushButton(
            "Remove"
        )

        self.remove_button.clicked.connect(
            self.handle_remove
        )

        layout.addWidget(
            self.text_input,
            1
        )

        layout.addWidget(
            self.url_input,
            2
        )

        layout.addWidget(
            self.remove_button
        )

    def handle_remove(self):

        if self.on_remove:

            self.on_remove(
                self
            )

    def to_dict(self):

        return {

            "text": self.text_input.text().strip(),

            "url": self.url_input.text().strip()

        }


class Page(QWidget):

    def __init__(self):

        super().__init__()

        self.data = load_json(
            "about.json"
        )

        self.link_rows = []

        outer_layout = QVBoxLayout()

        self.setLayout(
            outer_layout
        )

        # --------------------------------------------------------
        # Introduction — sits at the very top of the page and
        # keeps a stable amount of space no matter how many
        # links are added below it.
        # --------------------------------------------------------

        intro_label = QLabel(
            "Introduction"
        )

        intro_label.setStyleSheet(
            SECTION_LABEL_STYLE
        )

        outer_layout.addWidget(
            intro_label
        )

        self.introduction = QTextEdit()

        self.introduction.setText(
            self.data.get(
                "introduction",
                ""
            )
        )

        outer_layout.addWidget(
            self.introduction,
            2
        )

        # --------------------------------------------------------
        # Links — fully manual, added one by one from the admin.
        # The rows live inside their own scrollable box (same
        # idea as the Introduction text box scrolling on its
        # own), so adding many links never squeezes the
        # Introduction box.
        # --------------------------------------------------------

        links_label = QLabel(
            "Links"
        )

        links_label.setStyleSheet(
            SECTION_LABEL_STYLE
        )

        outer_layout.addWidget(
            links_label
        )

        self.links_scroll = QScrollArea()

        self.links_scroll.setWidgetResizable(
            True
        )

        outer_layout.addWidget(
            self.links_scroll,
            3
        )

        links_content = QWidget()

        self.links_scroll.setWidget(
            links_content
        )

        self.links_container = QVBoxLayout()

        links_content.setLayout(
            self.links_container
        )

        self.links_container.setAlignment(
            Qt.AlignTop
        )

        links = normalize_links(
            self.data.get(
                "links",
                []
            )
        )

        for entry in links:

            self.add_link_row(
                entry.get("text", ""),
                entry.get("url", "")
            )

        # --------------------------------------------------------
        # Add Link + Save, both at the very bottom of the page.
        # --------------------------------------------------------

        add_link_button = QPushButton(
            "Add Link"
        )

        add_link_button.clicked.connect(
            lambda: self.add_link_row()
        )

        outer_layout.addWidget(
            add_link_button
        )

        save_button = QPushButton(
            "Save About"
        )

        save_button.clicked.connect(
            self.save
        )

        outer_layout.addWidget(
            save_button
        )

    def add_link_row(self, text="", url=""):

        row = LinkRow(

            text,

            url,

            on_remove=self.remove_link_row

        )

        self.link_rows.append(
            row
        )

        self.links_container.addWidget(
            row
        )

    def remove_link_row(self, row):

        if row in self.link_rows:

            self.link_rows.remove(
                row
            )

        self.links_container.removeWidget(
            row
        )

        row.deleteLater()

    def save(self):

        links = []

        for row in self.link_rows:

            entry = row.to_dict()

            if entry["text"] and entry["url"]:

                links.append(
                    entry
                )

        data = {

            "introduction":
                self.introduction.toPlainText(),


            "links": links,


            "last_updated":
                self.data.get(
                    "last_updated",
                    ""
                )

        }

        save_json(
            "about.json",
            data
        )

        update_last_modified()

        self.data = load_json(
            "about.json"
        )

        QMessageBox.information(

            self,

            "Saved",

            "About information saved."

        )
