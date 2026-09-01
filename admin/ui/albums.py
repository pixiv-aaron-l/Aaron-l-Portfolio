import re

from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QLineEdit,
    QTextEdit,
    QCheckBox,
    QInputDialog,
    QMessageBox
)


from tools.json_manager import load_json, save_json


# ============================================================
# AUTOMATIC ALBUM FOLDER SLUGS
#
# Mirrors the same automation used for artwork page slugs: the
# folder is derived from the album title and disambiguated
# automatically if it's already taken, rather than typed in by
# hand. It's set once at creation and left stable afterward, so
# renaming an album later never orphans its already-uploaded
# images.
# ============================================================

def slugify(text):

    text = text.lower().strip()

    text = re.sub(
        r"[^a-z0-9]+",
        "-",
        text
    )

    text = text.strip("-")

    if not text:

        text = "album"

    return text


def generate_unique_album_folder(title, albums_data):

    base_slug = slugify(
        title
    )

    existing_folders = set()

    for album in albums_data.get(
        "albums",
        []
    ):

        existing_folders.add(
            album.get(
                "folder",
                ""
            )
        )

    if base_slug not in existing_folders:

        return base_slug

    counter = 2

    while f"{base_slug}{counter}" in existing_folders:

        counter += 1

    return f"{base_slug}{counter}"


def format_album_title(album):

    """
    Shared so the album list always looks the same whether it
    was just built from scratch (refresh) or a single item was
    updated in place (save).
    """

    title = album.get(
        "title",
        "Unnamed"
    )

    if album.get(
        "featured",
        False
    ):

        title = "★ " + title

    return title




class Page(QWidget):

    def __init__(self):

        super().__init__()



        main_layout = QHBoxLayout()

        self.setLayout(
            main_layout
        )



        # LEFT

        left = QVBoxLayout()


        left.addWidget(
            QLabel("Albums")
        )


        self.album_list = QListWidget()

        self.album_list.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.album_list.setTextElideMode(
            Qt.ElideRight
        )


        left.addWidget(
            self.album_list
        )



        self.create_button = QPushButton(
            "Create Album"
        )


        self.delete_button = QPushButton(
            "Delete Album"
        )


        self.up_button = QPushButton(
            "↑ Move Up"
        )


        self.down_button = QPushButton(
            "↓ Move Down"
        )


        left.addWidget(
            self.create_button
        )


        left.addWidget(
            self.delete_button
        )


        left.addWidget(
            self.up_button
        )


        left.addWidget(
            self.down_button
        )



        main_layout.addLayout(
            left,
            1
        )




        # RIGHT

        right = QVBoxLayout()


        right.addWidget(
            QLabel("Album Editor")
        )



        self.title_input = QLineEdit()

        self.date_input = QLineEdit()

        self.cover_input = QLineEdit()

        self.description_input = QTextEdit()



        fields = [

            (
                self.title_input,
                "Album title"
            ),

            (
                self.date_input,
                "Date"
            ),

            (
                self.cover_input,
                "Cover filename"
            ),

            (
                self.description_input,
                "Description"
            )

        ]



        for widget, placeholder in fields:

            widget.setPlaceholderText(
                placeholder
            )

            right.addWidget(
                widget
            )


        # --------------------------------------------------------
        # FEATURED ALBUM CHECKBOX
        #
        # Featured albums are the pool used by the random artwork
        # section on the About Me page.
        # --------------------------------------------------------

        self.featured_checkbox = QCheckBox(
            "Featured album (used for random artwork selection)"
        )

        right.addWidget(
            self.featured_checkbox
        )



        self.save_button = QPushButton(
            "Save Album"
        )


        right.addWidget(
            self.save_button
        )



        main_layout.addLayout(
            right,
            2
        )



        self.current_album = -1



        self.refresh()



        self.album_list.currentRowChanged.connect(
            self.load_album
        )


        self.create_button.clicked.connect(
            self.create_album
        )


        self.delete_button.clicked.connect(
            self.delete_album
        )


        self.save_button.clicked.connect(
            self.save_album
        )


        self.up_button.clicked.connect(
            self.move_up
        )


        self.down_button.clicked.connect(
            self.move_down
        )



    def showEvent(self, event):

        """
        Called by Qt every time this page actually becomes
        visible (e.g. switching back to the Albums tab).
        Re-reads albums.json and rebuilds the list while keeping
        the same album selected, so edits made anywhere else in
        the admin always show up here without restarting the
        app.
        """

        super().showEvent(event)

        selected = self.album_list.currentRow()

        self.refresh()

        if 0 <= selected < self.album_list.count():

            self.album_list.setCurrentRow(
                selected
            )



    def refresh(self):

        # Signals are blocked for the whole clear+repopulate
        # step. Without this, clear() fires currentRowChanged(-1)
        # mid-rebuild, which clobbers self.current_album before
        # any caller gets a chance to restore the real selection
        # afterward -- that was the root cause of saving
        # sometimes leaving nothing selected.

        self.album_list.blockSignals(
            True
        )

        self.album_list.clear()


        data = load_json(
            "albums.json"
        )


        for album in data.get(
            "albums",
            []
        ):

            self.album_list.addItem(
                format_album_title(
                    album
                )
            )


        self.album_list.blockSignals(
            False
        )




    def create_album(self):

        title, ok = QInputDialog.getText(

            self,

            "Create Album",

            "Album title:"

        )


        if not ok or not title:

            return



        data = load_json(
            "albums.json"
        )


        if "albums" not in data:

            data["albums"] = []



        folder = generate_unique_album_folder(
            title,
            data
        )



        data["albums"].append({

            "title": title,

            "folder": folder,

            "date": "",

            "description": "",

            "cover": "",

            "featured": False,

            "artworks": []

        })


        new_index = len(data["albums"]) - 1


        save_json(
            "albums.json",
            data
        )


        self.refresh()

        self.album_list.setCurrentRow(
            new_index
        )




    def load_album(self,index):

        self.current_album = index


        if index < 0:

            return



        data = load_json(
            "albums.json"
        )


        album = data["albums"][index]



        self.title_input.setText(
            album.get(
                "title",
                ""
            )
        )


        self.date_input.setText(
            album.get(
                "date",
                ""
            )
        )


        self.cover_input.setText(
            album.get(
                "cover",
                ""
            )
        )


        self.description_input.setPlainText(
            album.get(
                "description",
                ""
            )
        )


        self.featured_checkbox.setChecked(
            album.get(
                "featured",
                False
            )
        )




    def save_album(self):

        if self.current_album < 0:

            return



        data = load_json(
            "albums.json"
        )


        album = data["albums"][self.current_album]



        album["title"] = self.title_input.text()

        album["date"] = self.date_input.text()

        album["cover"] = self.cover_input.text()

        album["description"] = self.description_input.toPlainText()

        album["featured"] = self.featured_checkbox.isChecked()

        # Note: the folder ("folder") is intentionally never
        # changed here, even if the title changes -- it's set
        # once at creation so already-uploaded images and any
        # published album page URL never move.

        if not album["featured"]:

            # Exclusions only make sense while an album is
            # featured. Un-featuring an album always resets them,
            # so re-featuring it later starts with a clean slate
            # instead of silently carrying over old exclusions.

            for artwork in album.get("artworks", []):

                artwork["excluded_from_random"] = False



        save_json(
            "albums.json",
            data
        )


        # Update the list item's text directly instead of doing
        # a full clear+rebuild -- this shows the new title/★
        # instantly and can never lose the current selection,
        # since nothing about the list's row count or order
        # changed.

        item = self.album_list.item(
            self.current_album
        )

        if item:

            item.setText(
                format_album_title(
                    album
                )
            )


        QMessageBox.information(

            self,

            "Saved",

            "Album saved successfully."

        )




    def delete_album(self):

        index = self.album_list.currentRow()


        if index < 0:

            return



        answer = QMessageBox.question(

            self,

            "Delete Album",

            "Are you sure you want to delete this album?"

        )


        if answer != QMessageBox.Yes:

            return



        data = load_json(
            "albums.json"
        )


        data["albums"].pop(
            index
        )


        save_json(
            "albums.json",
            data
        )


        self.refresh()


        remaining = len(
            data["albums"]
        )


        if remaining:

            new_index = min(
                index,
                remaining - 1
            )

            self.album_list.setCurrentRow(
                new_index
            )

        else:

            self.current_album = -1

            self.title_input.clear()

            self.date_input.clear()

            self.cover_input.clear()

            self.description_input.clear()

            self.featured_checkbox.setChecked(
                False
            )




    def move_up(self):

        index = self.album_list.currentRow()


        if index <= 0:

            return



        data = load_json(
            "albums.json"
        )


        albums = data["albums"]


        albums[index], albums[index-1] = (

            albums[index-1],

            albums[index]

        )


        save_json(
            "albums.json",
            data
        )


        self.refresh()


        self.album_list.setCurrentRow(
            index-1
        )




    def move_down(self):

        index = self.album_list.currentRow()


        data = load_json(
            "albums.json"
        )


        albums = data["albums"]


        if index < 0 or index >= len(albums)-1:

            return



        albums[index], albums[index+1] = (

            albums[index+1],

            albums[index]

        )


        save_json(
            "albums.json",
            data
        )


        self.refresh()


        self.album_list.setCurrentRow(
            index+1
        )
