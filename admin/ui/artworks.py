import os
import shutil

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QLineEdit,
    QTextEdit,
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


class Page(QWidget):

    def __init__(self):

        super().__init__()

        layout = QHBoxLayout()

        self.setLayout(layout)


        # LEFT

        left = QVBoxLayout()

        left.addWidget(
            QLabel("Albums")
        )

        self.album_list = QListWidget()

        left.addWidget(
            self.album_list
        )


        left.addWidget(
            QLabel("Artworks")
        )

        self.artwork_list = QListWidget()

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
            QLabel("Artwork Editor")
        )


        self.title_input = QLineEdit()

        self.file_input = QLineEdit()

        self.display_input = QLineEdit()

        self.original_input = QLineEdit()

        self.number_input = QLineEdit()

        self.date_input = QLineEdit()

        self.time_input = QLineEdit()

        self.notes_input = QTextEdit()


        fields = [

            (self.title_input, "Title"),

            (self.file_input, "File name"),

            (self.display_input, "Display image"),

            (self.original_input, "Original image"),

            (self.number_input, "Number"),

            (self.date_input, "Date"),

            (self.time_input, "Time spent"),

            (self.notes_input, "Notes")

        ]


        for widget, placeholder in fields:

            widget.setPlaceholderText(
                placeholder
            )

            right.addWidget(
                widget
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


        self.refresh()


        self.album_list.currentRowChanged.connect(
            self.load_album
        )

        self.artwork_list.currentRowChanged.connect(
            self.load_artwork
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


    def refresh(self):

        self.album_list.clear()

        data = load_json(
            "albums.json"
        )

        for album in data.get("albums", []):

            self.album_list.addItem(
                album.get("title", "")
            )
    def load_album(self, index):

        self.current_album = index

        self.current_artwork = -1

        self.artwork_list.clear()


        if index < 0:

            return


        data = load_json(
            "albums.json"
        )


        for artwork in data["albums"][index].get("artworks", []):

            self.artwork_list.addItem(
                artwork.get("title", "")
            )



    def create_artwork(self):

        if self.current_album < 0:

            return


        title, ok = QInputDialog.getText(
            self,
            "Artwork",
            "Title:"
        )


        if not ok:

            return


        data = load_json(
            "albums.json"
        )


        artworks = data["albums"][self.current_album]["artworks"]


        artworks.append({

            "title": title,

            "file": title.lower().replace(
                " ",
                "-"
            ),

            "display": "",

            "original": "",

            "number": 0,

            "date": "",

            "time_spent": "",

            "notes": ""

        })


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



    def load_artwork(self, index):

        self.current_artwork = index


        if index < 0:

            return


        data = load_json(
            "albums.json"
        )


        artwork = data["albums"][self.current_album]["artworks"][index]


        self.title_input.setText(
            artwork.get("title", "")
        )

        self.file_input.setText(
            artwork.get("file", "")
        )

        self.display_input.setText(
            artwork.get("display", "")
        )

        self.original_input.setText(
            artwork.get("original", "")
        )

        self.number_input.setText(
            str(
                artwork.get("number", "")
            )
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



    def save_artwork(self):

        if self.current_artwork < 0:

            return


        data = load_json(
            "albums.json"
        )


        artwork = data["albums"][self.current_album]["artworks"][self.current_artwork]


        artwork["title"] = self.title_input.text()

        artwork["file"] = self.file_input.text()

        artwork["display"] = self.display_input.text()

        artwork["original"] = self.original_input.text()

        artwork["number"] = self.number_input.text()

        artwork["date"] = self.date_input.text()

        artwork["time_spent"] = self.time_input.text()

        artwork["notes"] = self.notes_input.toPlainText()


        save_json(
            "albums.json",
            data
        )


        QMessageBox.information(
            self,
            "Saved",
            "Artwork saved successfully."
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


        artworks.pop(
            self.current_artwork
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