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
    QMessageBox
)


from tools.json_manager import load_json, save_json





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

        self.folder_input = QLineEdit()

        self.date_input = QLineEdit()

        self.cover_input = QLineEdit()

        self.description_input = QTextEdit()



        fields = [

            (
                self.title_input,
                "Album title"
            ),

            (
                self.folder_input,
                "Folder name"
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




    def refresh(self):

        self.album_list.clear()


        data = load_json(
            "albums.json"
        )


        for album in data.get(
            "albums",
            []
        ):

            self.album_list.addItem(
                album.get(
                    "title",
                    "Unnamed"
                )
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



        folder = title.lower().replace(
            " ",
            "-"
        )



        data["albums"].append({

            "title": title,

            "folder": folder,

            "date": "",

            "description": "",

            "cover": "",

            "artworks": []

        })



        save_json(
            "albums.json",
            data
        )


        self.refresh()




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


        self.folder_input.setText(
            album.get(
                "folder",
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




    def save_album(self):

        if self.current_album < 0:

            return



        data = load_json(
            "albums.json"
        )


        album = data["albums"][self.current_album]



        album["title"] = self.title_input.text()

        album["folder"] = self.folder_input.text()

        album["date"] = self.date_input.text()

        album["cover"] = self.cover_input.text()

        album["description"] = self.description_input.toPlainText()



        save_json(
            "albums.json",
            data
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