import os
import shutil

from PySide6.QtCore import Qt

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


# ============================================================
# PATHS
# ============================================================

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

POST_IMAGES_FOLDER = os.path.join(
    WEBSITE_FOLDER,
    "images",
    "posts"
)


# ============================================================
# PAGE
# ============================================================

class Page(QWidget):

    def __init__(self):

        super().__init__()

        layout = QHBoxLayout()

        self.setLayout(
            layout
        )

        # ====================================================
        # LEFT - POST LIST
        # ====================================================

        left = QVBoxLayout()

        left.addWidget(
            QLabel("Posts")
        )

        self.post_list = QListWidget()

        self.post_list.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.post_list.setTextElideMode(
            Qt.ElideRight
        )

        left.addWidget(
            self.post_list
        )

        self.create_button = QPushButton(
            "Create Post"
        )

        self.delete_button = QPushButton(
            "Delete Post"
        )

        self.move_up_button = QPushButton(
            "Move Up"
        )

        self.move_down_button = QPushButton(
            "Move Down"
        )

        left.addWidget(
            self.create_button
        )

        left.addWidget(
            self.delete_button
        )

        left.addWidget(
            self.move_up_button
        )

        left.addWidget(
            self.move_down_button
        )

        # ====================================================
        # RIGHT - POST EDITOR
        # ====================================================

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

        # ====================================================
        # INLINE IMAGE
        # ====================================================

        self.insert_image_button = QPushButton(
            "Insert Image"
        )

        right.addWidget(
            self.insert_image_button
        )

        # ====================================================
        # ATTACHMENTS
        # ====================================================

        right.addWidget(
            QLabel("Attachments")
        )

        self.attachments_list = QListWidget()

        self.attachments_list.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.attachments_list.setTextElideMode(
            Qt.ElideRight
        )

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

        # ====================================================
        # SAVE
        # ====================================================

        self.save_button = QPushButton(
            "Save Post"
        )

        right.addWidget(
            self.save_button
        )

        # ====================================================
        # MAIN LAYOUT
        # ====================================================

        layout.addLayout(
            left,
            1
        )

        layout.addLayout(
            right,
            2
        )

        # ====================================================
        # STATE
        # ====================================================

        self.current_post = -1

        # Prevent list refreshes from accidentally changing
        # the currently edited post.
        self.refreshing = False

        # ====================================================
        # SIGNALS
        # ====================================================

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

        self.move_up_button.clicked.connect(
            self.move_up
        )

        self.move_down_button.clicked.connect(
            self.move_down
        )

        self.insert_image_button.clicked.connect(
            self.insert_image
        )

        # Initial list population.
        self.refresh()


    # ========================================================
    # LIVE REFRESH
    #
    # Called by Qt every time this page actually becomes
    # visible (e.g. switching back to the Posts tab). Re-reads
    # posts.json and rebuilds the list while keeping the same
    # post selected, so edits made anywhere else in the admin
    # always show up here without restarting the app.
    # ========================================================

    def showEvent(self, event):

        super().showEvent(event)

        self.refresh(
            self.current_post
        )


    # ========================================================
    # REFRESH
    # ========================================================

    def refresh(self, select_index=None):

        data = load_json(
            "posts.json"
        )

        posts = data.get(
            "posts",
            []
        )

        # If no explicit selection was supplied, preserve the
        # currently selected post.
        if select_index is None:

            select_index = self.current_post

        # Prevent currentRowChanged from firing while the list
        # is being rebuilt.
        self.refreshing = True

        self.post_list.blockSignals(True)

        self.post_list.clear()

        for post in posts:

            self.post_list.addItem(
                post.get(
                    "title",
                    ""
                )
            )

        # Restore the previous selection.
        if (
            select_index is not None
            and 0 <= select_index < len(posts)
        ):

            self.post_list.setCurrentRow(
                select_index
            )

            self.current_post = select_index

        elif posts:

            self.post_list.setCurrentRow(
                0
            )

            self.current_post = 0

        else:

            self.current_post = -1

        self.post_list.blockSignals(False)

        self.refreshing = False

        # Explicitly reload the selected post so the editor
        # remains synchronized with the list.
        if (
            0 <= self.current_post < len(posts)
        ):

            self.load_post(
                self.current_post
            )


    # ========================================================
    # CREATE POST
    # ========================================================

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

        new_index = len(
            data["posts"]
        ) - 1

        self.refresh(
            new_index
        )


    # ========================================================
    # LOAD POST
    # ========================================================

    def load_post(self, index):

        if self.refreshing:

            return

        if index < 0:

            self.current_post = -1

            return

        data = load_json(
            "posts.json"
        )

        posts = data.get(
            "posts",
            []
        )

        if index >= len(posts):

            self.current_post = -1

            return

        self.current_post = index

        post = posts[index]

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

        self.content_input.setPlainText(
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
                        attachment.get(
                            "file",
                            ""
                        )
                    )
                )

            else:

                self.attachments_list.addItem(
                    attachment
                )


    # ========================================================
    # MOVE UP
    # ========================================================

    def move_up(self):

        index = self.post_list.currentRow()

        if index <= 0:

            return

        data = load_json(
            "posts.json"
        )

        posts = data.get(
            "posts",
            []
        )

        posts[index - 1], posts[index] = (
            posts[index],
            posts[index - 1]
        )

        save_json(
            "posts.json",
            data
        )

        new_index = index - 1

        self.refresh(
            new_index
        )


    # ========================================================
    # MOVE DOWN
    # ========================================================

    def move_down(self):

        index = self.post_list.currentRow()

        data = load_json(
            "posts.json"
        )

        posts = data.get(
            "posts",
            []
        )

        if (
            index < 0
            or index >= len(posts) - 1
        ):

            return

        posts[index + 1], posts[index] = (
            posts[index],
            posts[index + 1]
        )

        save_json(
            "posts.json",
            data
        )

        new_index = index + 1

        self.refresh(
            new_index
        )


    # ========================================================
    # INSERT INLINE IMAGE
    # ========================================================

    def insert_image(self):

        file, _ = QFileDialog.getOpenFileName(

            self,

            "Select Image",

            "",

            "Images (*.png *.jpg *.jpeg *.gif *.webp)"

        )

        if not file:

            return

        os.makedirs(
            POST_IMAGES_FOLDER,
            exist_ok=True
        )

        filename = os.path.basename(
            file
        )

        destination = os.path.join(
            POST_IMAGES_FOLDER,
            filename
        )

        try:

            shutil.copy2(
                file,
                destination
            )

        except Exception as error:

            QMessageBox.warning(

                self,

                "Error",

                f"Could not copy image:\n{error}"

            )

            return

        cursor = self.content_input.textCursor()

        cursor.insertText(
            f"[[IMAGE:{filename}]]"
        )

        self.content_input.setTextCursor(
            cursor
        )


    # ========================================================
    # ADD ATTACHMENT
    # ========================================================

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

        existing = [

            self.attachments_list.item(i).text()

            for i in range(
                self.attachments_list.count()
            )

        ]

        for file in files:

            filename = os.path.basename(
                file
            )

            destination = os.path.join(
                ATTACHMENTS_FOLDER,
                filename
            )

            try:

                shutil.copy2(
                    file,
                    destination
                )

            except Exception as error:

                QMessageBox.warning(

                    self,

                    "Error",

                    f"Could not copy attachment:\n{error}"

                )

                continue

            if filename not in existing:

                self.attachments_list.addItem(
                    filename
                )

                existing.append(
                    filename
                )


    # ========================================================
    # REMOVE ATTACHMENT
    # ========================================================

    def remove_attachment(self):

        row = self.attachments_list.currentRow()

        if row >= 0:

            self.attachments_list.takeItem(
                row
            )


    # ========================================================
    # SAVE POST
    # ========================================================

    def save_post(self):

        if self.current_post < 0:

            return

        selected_index = self.current_post

        data = load_json(
            "posts.json"
        )

        posts = data.get(
            "posts",
            []
        )

        if selected_index >= len(posts):

            self.current_post = -1

            return

        post = posts[selected_index]

        post["title"] = (
            self.title_input.text()
        )

        post["file"] = (
            self.file_input.text()
        )

        post["date"] = (
            self.date_input.text()
        )

        post["content"] = (
            self.content_input.toPlainText()
        )

        post["attachments"] = []

        for i in range(
            self.attachments_list.count()
        ):

            filename = (
                self.attachments_list
                .item(i)
                .text()
            )

            if not filename:

                continue

            post["attachments"].append({

                "name": filename,

                "file": filename

            })

        save_json(
            "posts.json",
            data
        )

        # IMPORTANT:
        # Keep the same post selected after saving.
        self.current_post = selected_index

        self.refresh(
            selected_index
        )

        QMessageBox.information(

            self,

            "Saved",

            "Post saved successfully."

        )


    # ========================================================
    # DELETE POST
    # ========================================================

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

        selected_index = self.current_post

        data = load_json(
            "posts.json"
        )

        posts = data.get(
            "posts",
            []
        )

        if selected_index >= len(posts):

            return

        posts.pop(
            selected_index
        )

        save_json(
            "posts.json",
            data
        )

        # Select the nearest remaining post.
        if posts:

            new_index = min(
                selected_index,
                len(posts) - 1
            )

        else:

            new_index = -1

        self.current_post = new_index

        self.title_input.clear()

        self.file_input.clear()

        self.date_input.clear()

        self.content_input.clear()

        self.attachments_list.clear()

        self.refresh(
            new_index if new_index >= 0 else None
        )

        QMessageBox.information(

            self,

            "Deleted",

            "Post deleted."

        )


