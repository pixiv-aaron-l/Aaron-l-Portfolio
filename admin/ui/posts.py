import os
import shutil

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QLineEdit,
    QTextEdit,
    QHBoxLayout,
    QInputDialog,
    QMessageBox,
    QFileDialog
)

from tools.json_manager import load_json, save_json



BASE_FOLDER = os.path.dirname(
    os.path.dirname(__file__)
)


WEBSITE_FOLDER = os.path.join(
    BASE_FOLDER,
    "..",
    "website"
)


ATTACHMENTS_FOLDER = os.path.join(
    WEBSITE_FOLDER,
    "attachments"
)



class Page(QWidget):

    def __init__(self):

        super().__init__()


        layout = QHBoxLayout()

        self.setLayout(layout)



        # LEFT SIDE

        left = QVBoxLayout()


        left.addWidget(
            QLabel("Posts")
        )


        self.post_list = QListWidget()


        left.addWidget(
            self.post_list
        )


        self.create_button = QPushButton(
            "Create Post"
        )


        self.delete_button = QPushButton(
            "Delete Post"
        )


        left.addWidget(
            self.create_button
        )


        left.addWidget(
            self.delete_button
        )



        # RIGHT SIDE

        right = QVBoxLayout()


        right.addWidget(
            QLabel("Post Editor")
        )



        self.title_input = QLineEdit()

        self.file_input = QLineEdit()

        self.date_input = QLineEdit()

        self.content_input = QTextEdit()



        self.title_input.setPlaceholderText(
            "Title"
        )

        self.file_input.setPlaceholderText(
            "File name"
        )

        self.date_input.setPlaceholderText(
            "Date"
        )

        self.content_input.setPlaceholderText(
            "Content"
        )



        right.addWidget(
            self.title_input
        )

        right.addWidget(
            self.file_input
        )

        right.addWidget(
            self.date_input
        )

        right.addWidget(
            self.content_input
        )



        # ATTACHMENTS

        right.addWidget(
            QLabel("Attachments")
        )


        self.attachments_list = QListWidget()


        right.addWidget(
            self.attachments_list
        )


        self.add_attachment_button = QPushButton(
            "Add Attachment"
        )


        self.remove_attachment_button = QPushButton(
            "Remove Selected Attachment"
        )


        right.addWidget(
            self.add_attachment_button
        )


        right.addWidget(
            self.remove_attachment_button
        )



        self.save_button = QPushButton(
            "Save Post"
        )


        right.addWidget(
            self.save_button
        )



        layout.addLayout(
            left,
            1
        )


        layout.addLayout(
            right,
            2
        )



        self.current_post = -1



        self.refresh()



        self.post_list.currentRowChanged.connect(
            self.load_post
        )


        self.create_button.clicked.connect(
            self.create_post
        )


        self.delete_button.clicked.connect(
            self.delete_post
        )


        self.save_button.clicked.connect(
            self.save_post
        )


        self.add_attachment_button.clicked.connect(
            self.add_attachment
        )


        self.remove_attachment_button.clicked.connect(
            self.remove_attachment
        )



    def refresh(self):

        self.post_list.clear()


        data = load_json(
            "posts.json"
        )


        for post in data.get(
            "posts",
            []
        ):

            self.post_list.addItem(
                post.get(
                    "title",
                    ""
                )
            )



    def create_post(self):

        title, ok = QInputDialog.getText(
            self,
            "Create Post",
            "Title:"
        )


        if not ok or not title:

            return



        data = load_json(
            "posts.json"
        )


        if "posts" not in data:

            data["posts"] = []



        filename = title.lower().replace(
            " ",
            "-"
        )


        data["posts"].append({

            "title": title,

            "file": filename,

            "date": "",

            "content": "",

            "attachments": []

        })



        save_json(
            "posts.json",
            data
        )


        self.refresh()



    def load_post(self, index):

        self.current_post = index


        if index < 0:

            return



        data = load_json(
            "posts.json"
        )


        post = data["posts"][index]



        self.title_input.setText(
            post.get(
                "title",
                ""
            )
        )


        self.file_input.setText(
            post.get(
                "file",
                ""
            )
        )


        self.date_input.setText(
            post.get(
                "date",
                ""
            )
        )


        self.content_input.setText(
            post.get(
                "content",
                ""
            )
        )



        self.attachments_list.clear()



        for attachment in post.get(
            "attachments",
            []
        ):

            if isinstance(
                attachment,
                dict
            ):

                self.attachments_list.addItem(
                    attachment.get(
                        "name",
                        ""
                    )
                )

            else:

                self.attachments_list.addItem(
                    attachment
                )



    def add_attachment(self):

        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Attachments"
        )


        if not files:

            return



        os.makedirs(
            ATTACHMENTS_FOLDER,
            exist_ok=True
        )



        for file in files:

            filename = os.path.basename(
                file
            )


            destination = os.path.join(
                ATTACHMENTS_FOLDER,
                filename
            )


            shutil.copy2(
                file,
                destination
            )


            existing = [

                self.attachments_list.item(i).text()

                for i in range(
                    self.attachments_list.count()
                )

            ]


            if filename not in existing:

                self.attachments_list.addItem(
                    filename
                )



    def remove_attachment(self):

        row = self.attachments_list.currentRow()


        if row >= 0:

            self.attachments_list.takeItem(
                row
            )



    def save_post(self):

        if self.current_post < 0:

            return



        data = load_json(
            "posts.json"
        )


        post = data["posts"][self.current_post]



        post["title"] = self.title_input.text()

        post["file"] = self.file_input.text()

        post["date"] = self.date_input.text()

        post["content"] = self.content_input.toPlainText()



        post["attachments"] = []


        for i in range(
            self.attachments_list.count()
        ):

            filename = self.attachments_list.item(i).text()


            post["attachments"].append({

                "name": filename,

                "file": filename

            })



        save_json(
            "posts.json",
            data
        )


        QMessageBox.information(
            self,
            "Saved",
            "Post saved successfully."
        )



    def delete_post(self):

        if self.current_post < 0:

            return



        answer = QMessageBox.question(

            self,

            "Delete Post",

            "Are you sure you want to delete this post?"

        )


        if answer != QMessageBox.Yes:

            return



        data = load_json(
            "posts.json"
        )


        data["posts"].pop(
            self.current_post
        )


        save_json(
            "posts.json",
            data
        )


        self.refresh()


        QMessageBox.information(
            self,
            "Deleted",
            "Post deleted."
        )