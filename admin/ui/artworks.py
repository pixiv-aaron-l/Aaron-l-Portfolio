import os
import re
import shutil

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
    QMessageBox,
    QFileDialog
)

from tools.json_manager import load_json, save_json

from tools.image_manager import (
    create_album_folders,
    create_display_image,
    get_album_image_folder
)


# ============================================================
# SMALL LABEL HELPERS
#
# // headings are a bit bigger/bolder than normal text, and each field
# // in an editor gets a small grey caption above it. Placeholder text
# // disappears as soon as you type something, so without the caption
# // you can't tell which box is which once a form is filled in.
# ============================================================

HEADING_STYLE = """
    QLabel {
        font-size:16px;
        font-weight:bold;
    }
"""

CAPTION_STYLE = """
    QLabel {
        color:#aaaaaa;
        font-size:12px;
        margin-top:4px;
    }
"""


def make_heading(text):

    label = QLabel(
        text
    )

    label.setStyleSheet(
        HEADING_STYLE
    )

    return label


def make_caption(text):

    label = QLabel(
        text
    )

    label.setStyleSheet(
        CAPTION_STYLE
    )

    return label


def make_field(caption, widget):

    # // a small caption stacked right on top of its box. Several of these
    # // side by side in one row is how the editors save vertical space.

    column = QVBoxLayout()

    column.setSpacing(
        2
    )

    column.addWidget(
        make_caption(caption)
    )

    column.addWidget(
        widget
    )

    return column


# ============================================================
# AUTOMATIC PAGE SLUGS
#
# Artwork page filenames used to be typed in by hand (a "File
# name" field), which meant two artworks with the same title
# (e.g. two pieces both called "Mokou") silently collided --
# the only way around it was manually typing "mokou2",
# "mokou3", etc. This makes that fully automatic instead: a
# slug is derived from the title, and disambiguated the same
# way if it's already taken by another artwork anywhere in the
# project (artwork pages all live in one flat website/artworks/
# folder regardless of album, so uniqueness has to be checked
# across every album, not just the current one).
# ============================================================

def slugify(text):

    # // lowercase, spaces/punctuation become dashes, no leading or
    # // trailing dash left over.

    text = text.lower().strip()

    text = re.sub(
        r"[^a-z0-9]+",
        "-",
        text
    )

    text = text.strip("-")

    if not text:

        # // an empty/symbols-only title would otherwise slugify
        # // down to nothing, which would be a broken filename.

        text = "artwork"

    return text


def generate_unique_artwork_slug(title, albums_data):

    base_slug = slugify(
        title
    )

    existing_slugs = set()

    for album in albums_data.get(
        "albums",
        []
    ):

        for artwork in album.get(
            "artworks",
            []
        ):

            existing_slugs.add(
                artwork.get(
                    "file",
                    ""
                )
            )

    if base_slug not in existing_slugs:

        return base_slug

    counter = 2

    while f"{base_slug}{counter}" in existing_slugs:

        counter += 1

    return f"{base_slug}{counter}"


def format_album_title(album):

    title = album.get(
        "title",
        ""
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

        layout = QHBoxLayout()

        self.setLayout(layout)


        # LEFT

        left = QVBoxLayout()

        left.addWidget(
            make_heading("Albums")
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


        left.addWidget(
            make_heading("Artworks")
        )

        self.artwork_list = QListWidget()

        self.artwork_list.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.artwork_list.setTextElideMode(
            Qt.ElideRight
        )

        left.addWidget(
            self.artwork_list
        )


        self.create_button = QPushButton(
            "Add Artwork"
        )

        self.delete_button = QPushButton(
            "Delete Artwork"
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


        layout.addLayout(
            left,
            1
        )


        # RIGHT

        right = QVBoxLayout()

        right.addWidget(
            make_heading("Artwork Editor")
        )


        self.title_input = QLineEdit()

        self.display_input = QLineEdit()

        self.original_input = QLineEdit()

        self.date_input = QLineEdit()

        self.time_input = QLineEdit()

        self.notes_input = QTextEdit()

        # // the only hint left is the date's shape. Everything else has
        # // a caption above it, so no placeholder text is needed.
        # // (There's no Number box: the number is kept right by adding,
        # // moving and deleting artworks, nobody types it.)

        self.date_input.setPlaceholderText(
            "__/__/__"
        )

        # // title, date and time spent on one row ...

        first_row = QHBoxLayout()

        first_row.addLayout(
            make_field("Title", self.title_input),
            3
        )

        first_row.addLayout(
            make_field("Date", self.date_input),
            1
        )

        first_row.addLayout(
            make_field("Time spent", self.time_input),
            1
        )

        right.addLayout(
            first_row
        )

        # // ... and the two image names (filled in by Choose Image) on
        # // the next one.

        second_row = QHBoxLayout()

        second_row.addLayout(
            make_field("Display image", self.display_input),
            1
        )

        second_row.addLayout(
            make_field("Original image", self.original_input),
            1
        )

        right.addLayout(
            second_row
        )

        right.addWidget(
            make_caption("Notes")
        )

        right.addWidget(
            self.notes_input,
            1
        )


        # --------------------------------------------------------
        # EXCLUDE FROM RANDOM ARTWORKS
        #
        # Only meaningful while this artwork's album is featured,
        # since the random pool only ever draws from featured
        # albums in the first place. Fully HIDDEN (not just
        # disabled) whenever the album isn't featured, so it
        # never shows up as an irrelevant option.
        # --------------------------------------------------------

        self.exclude_checkbox = QCheckBox(
            "Exclude from Random Artworks"
        )

        self.exclude_checkbox.setVisible(
            False
        )

        right.addWidget(
            self.exclude_checkbox
        )


        self.image_button = QPushButton(
            "Choose Image"
        )

        self.save_button = QPushButton(
            "Save Artwork"
        )


        right.addWidget(
            self.image_button
        )

        right.addWidget(
            self.save_button
        )


        layout.addLayout(
            right,
            2
        )


        self.current_album = -1

        self.current_artwork = -1

        self.current_album_featured = False


        self.refresh()


        self.album_list.currentRowChanged.connect(
            self.load_album
        )

        self.artwork_list.currentRowChanged.connect(
            self.load_artwork
        )

        self.date_input.textEdited.connect(
            self.format_date_while_typing
        )

        self.create_button.clicked.connect(
            self.create_artwork
        )

        self.delete_button.clicked.connect(
            self.delete_artwork
        )

        self.save_button.clicked.connect(
            self.save_artwork
        )

        self.image_button.clicked.connect(
            self.choose_image
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
        visible (e.g. switching back to the Artworks tab).
        Re-reads albums.json and rebuilds the album list while
        keeping the same album selected (which in turn reloads
        that album's artworks fresh too), so edits made anywhere
        else in the admin always show up here without restarting
        the app.
        """

        super().showEvent(event)

        selected = self.album_list.currentRow()

        self.refresh()

        if 0 <= selected < self.album_list.count():

            self.album_list.setCurrentRow(
                selected
            )


    def refresh(self):

        self.album_list.blockSignals(
            True
        )

        self.album_list.clear()

        data = load_json(
            "albums.json"
        )

        for album in data.get("albums", []):

            self.album_list.addItem(
                format_album_title(
                    album
                )
            )

        self.album_list.blockSignals(
            False
        )


    def format_artwork_title(self, artwork):

        # // only the exclude marker shows here -- the featured star
        # // used to also show on every artwork in a featured album,
        # // but that got noisy fast (every single artwork in the
        # // album showing a star isn't really telling you anything
        # // new). The star still shows on the album itself, just not
        # // repeated on every artwork underneath it.

        symbols = ""

        if artwork.get(
            "excluded_from_random",
            False
        ):

            symbols += "✕"

        title = artwork.get(
            "title",
            ""
        )

        if symbols:

            title = symbols + " " + title

        return title


    def load_album(self, index):

        self.current_album = index

        self.current_artwork = -1

        self.artwork_list.blockSignals(
            True
        )

        self.artwork_list.clear()


        if index < 0:

            self.current_album_featured = False

            self.artwork_list.blockSignals(
                False
            )

            self.exclude_checkbox.setVisible(
                False
            )

            return


        data = load_json(
            "albums.json"
        )

        album = data["albums"][index]

        self.current_album_featured = album.get(
            "featured",
            False
        )


        for artwork in album.get("artworks", []):

            self.artwork_list.addItem(
                self.format_artwork_title(
                    artwork
                )
            )


        self.artwork_list.blockSignals(
            False
        )

        self.exclude_checkbox.setVisible(
            self.current_album_featured
        )


    def create_artwork(self):

        if self.current_album < 0:

            return


        title, ok = QInputDialog.getText(
            self,
            "Artwork",
            "Title:"
        )


        if not ok or not title:

            return


        data = load_json(
            "albums.json"
        )


        artworks = data["albums"][self.current_album]["artworks"]


        slug = generate_unique_artwork_slug(
            title,
            data
        )


        artworks.append({

            "title": title,

            "file": slug,

            "display": "",

            "original": "",

            "number": 0,

            "date": "",

            "time_spent": "",

            "notes": "",

            "excluded_from_random": False

        })


        self.renumber_artworks(
            artworks
        )


        new_index = len(artworks) - 1


        save_json(
            "albums.json",
            data
        )


        self.load_album(
            self.current_album
        )

        self.artwork_list.setCurrentRow(
            new_index
        )


    def load_artwork(self, index):

        self.current_artwork = index


        if index < 0:

            self.exclude_checkbox.setChecked(
                False
            )

            return


        data = load_json(
            "albums.json"
        )


        artwork = data["albums"][self.current_album]["artworks"][index]


        self.title_input.setText(
            artwork.get("title", "")
        )

        self.display_input.setText(
            artwork.get("display", "")
        )

        self.original_input.setText(
            artwork.get("original", "")
        )

        self.date_input.setText(
            artwork.get("date", "")
        )

        self.time_input.setText(
            artwork.get("time_spent", "")
        )

        self.notes_input.setText(
            artwork.get("notes", "")
        )


        if self.current_album_featured:

            self.exclude_checkbox.setChecked(
                artwork.get(
                    "excluded_from_random",
                    False
                )
            )

        else:

            self.exclude_checkbox.setChecked(
                False
            )


    def save_artwork(self):

        if self.current_artwork < 0:

            return


        data = load_json(
            "albums.json"
        )


        artwork = data["albums"][self.current_album]["artworks"][self.current_artwork]


        artwork["title"] = self.title_input.text()

        artwork["display"] = self.display_input.text()

        artwork["original"] = self.original_input.text()

        artwork["date"] = self.date_input.text()

        artwork["time_spent"] = self.time_input.text()

        artwork["notes"] = self.notes_input.toPlainText()

        # The checkbox is hidden (and forced unchecked) whenever
        # the album isn't featured, so this always saves False in
        # that case without needing a separate check here.
        # Note: the page slug ("file") is intentionally never
        # changed here, even if the title changes -- it's set
        # once at creation so a published page's URL never moves.

        artwork["excluded_from_random"] = self.exclude_checkbox.isChecked()


        save_json(
            "albums.json",
            data
        )


        # Update the list item's text directly instead of doing
        # a full clear+rebuild -- this shows the new title/
        # symbols instantly and can never lose the current
        # selection, since nothing about the list's row count or
        # order changed.

        item = self.artwork_list.item(
            self.current_artwork
        )

        if item:

            item.setText(
                self.format_artwork_title(
                    artwork
                )
            )


        QMessageBox.information(
            self,
            "Saved",
            "Artwork saved successfully."
        )


    def format_date_while_typing(self, text):

        # // just type the digits and the slashes appear by themselves:
        # // 280326 becomes 28/03/26. Up to 8 digits are accepted so a
        # // full year (28/03/2026) still fits. Anything that isn't only
        # // digits and slashes (an old date written some other way) is
        # // left exactly as it is, nothing gets cut or rewritten.

        if not re.fullmatch(
            r"[\d/]*",
            text
        ):

            return

        digits = re.sub(
            r"\D",
            "",
            text
        )[:8]

        formatted = digits[:2]

        if len(digits) > 2:

            formatted += "/" + digits[2:4]

        if len(digits) > 4:

            formatted += "/" + digits[4:]

        if formatted != text:

            self.date_input.setText(
                formatted
            )


    def renumber_artworks(self, artworks):

        for index, artwork in enumerate(artworks):

            artwork["number"] = index + 1


    def move_up(self):

        if self.current_artwork <= 0:

            return


        data = load_json(
            "albums.json"
        )


        artworks = data["albums"][self.current_album]["artworks"]


        index = self.current_artwork


        artworks[index], artworks[index - 1] = (

            artworks[index - 1],

            artworks[index]

        )


        self.renumber_artworks(
            artworks
        )


        save_json(
            "albums.json",
            data
        )


        self.load_album(
            self.current_album
        )


        self.artwork_list.setCurrentRow(
            index - 1
        )


    def move_down(self):

        data = load_json(
            "albums.json"
        )


        artworks = data["albums"][self.current_album]["artworks"]


        index = self.current_artwork


        if index < 0 or index >= len(artworks) - 1:

            return


        artworks[index], artworks[index + 1] = (

            artworks[index + 1],

            artworks[index]

        )


        self.renumber_artworks(
            artworks
        )


        save_json(
            "albums.json",
            data
        )


        self.load_album(
            self.current_album
        )


        self.artwork_list.setCurrentRow(
            index + 1
        )


    def delete_artwork(self):

        if self.current_artwork < 0:

            return


        answer = QMessageBox.question(
            self,
            "Delete Artwork",
            "Are you sure you want to delete this artwork?"
        )


        if answer != QMessageBox.Yes:

            return


        data = load_json(
            "albums.json"
        )


        artworks = data["albums"][self.current_album]["artworks"]


        deleted_index = self.current_artwork


        artworks.pop(
            deleted_index
        )


        self.renumber_artworks(
            artworks
        )


        save_json(
            "albums.json",
            data
        )


        self.load_album(
            self.current_album
        )


        remaining = len(
            artworks
        )


        if remaining:

            new_index = min(
                deleted_index,
                remaining - 1
            )

            self.artwork_list.setCurrentRow(
                new_index
            )


        QMessageBox.information(
            self,
            "Deleted",
            "Artwork deleted successfully."
        )


    def choose_image(self):

        if self.current_album < 0:

            return


        file, _ = QFileDialog.getOpenFileName(

            self,

            "Choose Artwork",

            "",

            "Images (*.png *.jpg *.jpeg *.webp)"

        )


        if not file:

            return


        data = load_json(
            "albums.json"
        )


        album = data["albums"][self.current_album]


        create_album_folders(
            album["folder"]
        )


        filename = os.path.basename(
            file
        )


        original_path = os.path.join(

            get_album_image_folder(
                album["folder"]
            ),

            "original",

            filename

        )


        shutil.copy(
            file,
            original_path
        )


        display_name = os.path.splitext(filename)[0] + ".jpg"


        display_path = os.path.join(

            get_album_image_folder(
                album["folder"]
            ),

            "display",

            display_name

        )


        create_display_image(

            original_path,

            display_path

        )


        self.original_input.setText(
            filename
        )


        self.display_input.setText(
            display_name
        )
