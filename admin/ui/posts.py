import os
import re
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
from tools.unique_names import copy_unique


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
# AUTOMATIC PAGE NAME
#
# // posts used to have a "File name" box you had to fill in by hand.
# // Now the page name is made from the title when the post is created
# // ("My First Post" -> my-first-post, and my-first-post2 if that's
# // taken), and it never changes after that, so a published post's
# // address stays the same even if you rename it later.
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

        text = "post"

    return text


def generate_unique_post_slug(title, posts_data):

    base_slug = slugify(
        title
    )

    existing = {
        post.get("file", "")
        for post in posts_data.get("posts", [])
    }

    if base_slug not in existing:

        return base_slug

    counter = 2

    while f"{base_slug}{counter}" in existing:

        counter += 1

    return f"{base_slug}{counter}"


# ============================================================
# CLEANING UP POST IMAGES
#
# // taking an [[IMAGE:name]] marker out of a post used to leave the
# // picture sitting in website/images/posts/ forever. Now it's removed
# // when the marker goes (on Save, or when the post is deleted) BUT ONLY
# // if no other post still uses it.
# //
# // this is deliberately NOT a "delete everything that isn't used"
# // sweep: that kind of sweep is what once wiped this whole folder. Only
# // pictures that were just dropped from this post are ever candidates,
# // so a picture you put in the folder yourself is never touched.
# ============================================================

IMAGE_MARKER = re.compile(
    r"\[\[IMAGE:([^\]]+)\]\]"
)


def get_image_names(content):

    return {
        name.strip()
        for name in IMAGE_MARKER.findall(content or "")
    }


def remove_unused_post_images(candidates, posts):

    still_used = set()

    for post in posts:

        still_used |= {
            name.lower()
            for name in get_image_names(
                post.get("content", "")
            )
        }

    removed = []

    for name in candidates:

        # // only plain file names, nothing that could point elsewhere
        if not name or name != os.path.basename(name):

            continue

        if name.lower() in still_used:

            continue

        path = os.path.join(
            POST_IMAGES_FOLDER,
            name
        )

        if os.path.isfile(path):

            try:

                os.remove(path)

                removed.append(name)

            except OSError:

                pass

    return removed


def get_used_attachment_names():

    # // every attachment name a post or the hosting page already uses,
    # // so a new file can never be given the same name as one of them.

    names = set()

    for post in load_json("posts.json").get("posts", []):

        for attachment in post.get("attachments", []):

            if isinstance(attachment, dict):

                names.add(attachment.get("file", ""))

            else:

                names.add(attachment)

    for entry in load_json("hosted_attachments.json").get("files", []):

        names.add(entry.get("file", ""))

    names.discard("")

    return names


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

        # // images inserted into the text editor but not saved yet
        self.pending_images = set()

        layout = QHBoxLayout()

        self.setLayout(
            layout
        )

        # ====================================================
        # LEFT - POST LIST
        # ====================================================

        left = QVBoxLayout()

        left.addWidget(
            make_heading("Posts")
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
            make_heading("Post Editor")
        )

        self.title_input = QLineEdit()

        self.date_input = QLineEdit()

        self.content_input = QTextEdit()

        # // title, file name and date share one row instead of three
        # // stacked ones. No placeholder text: the captions above each
        # // box already say what it is.

        top_row = QHBoxLayout()

        top_row.addLayout(
            make_field("Title", self.title_input),
            3
        )

        top_row.addLayout(
            make_field("Date", self.date_input),
            1
        )

        right.addLayout(
            top_row
        )

        right.addWidget(
            make_caption("Content")
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
            make_heading("Attachments")
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
            "Remove Attachment"
        )

        # // one bar split in two halves: the buttons touch each other
        # // and only the outer corners stay rounded.

        self.add_attachment_button.setStyleSheet("""
            QPushButton {
                border-top-right-radius:0;
                border-bottom-right-radius:0;
            }
        """)

        self.remove_attachment_button.setStyleSheet("""
            QPushButton {
                border-top-left-radius:0;
                border-bottom-left-radius:0;
                border-left:none;
            }
        """)

        attachment_bar = QHBoxLayout()

        attachment_bar.setSpacing(
            0
        )

        attachment_bar.addWidget(
            self.add_attachment_button
        )

        attachment_bar.addWidget(
            self.remove_attachment_button
        )

        right.addLayout(
            attachment_bar
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

        # // called by Qt every time this tab actually becomes
        # // visible again. Reusing refresh() here (the same one the
        # // save/delete/move buttons already call) means posts
        # // edited indirectly -- or just time passing since this
        # // page was last open -- always show up fresh.

        super().showEvent(event)

        self.refresh(
            self.current_post
        )


    # ========================================================
    # REFRESH
    #
    # // this was already written the safe way before I touched
    # // anything else in the admin: block the list's signals while
    # // clearing and rebuilding it, THEN restore the selection. That
    # // ordering is exactly what albums.py and artworks.py were
    # // missing and had to be fixed to match.
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

        filename = generate_unique_post_slug(
            title,
            data
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

        # // the image keeps its own name when that's free. If another image
        # // already has it, this one becomes name2, name3... (checked in a
        # // loop until free) instead of replacing it, and the marker put in
        # // the text uses the FINAL name.

        try:

            filename = copy_unique(
                file,
                POST_IMAGES_FOLDER
            )

        except Exception as error:

            QMessageBox.warning(

                self,

                "Error",

                f"Could not copy image:\n{error}"

            )

            return

        # // remembered until the post is saved: if the marker is deleted
        # // again before saving, the picture is cleaned up at that point.
        self.pending_images.add(
            filename
        )

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

        existing = [

            self.attachments_list.item(i).text()

            for i in range(
                self.attachments_list.count()
            )

        ]

        used_names = get_used_attachment_names() | set(existing)

        for file in files:

            # // same rule as images: never replace a file with the same
            # // name, use name2, name3... and keep the final name.

            try:

                filename = copy_unique(
                    file,
                    ATTACHMENTS_FOLDER,
                    used_names
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

                used_names.add(
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

        # // the page name is never typed in or changed here. It was set
        # // when the post was created. Only a post that somehow has none
        # // (an old one) gets one now.

        if not post.get("file"):

            post["file"] = generate_unique_post_slug(
                post.get("title", ""),
                data
            )

        post["date"] = (
            self.date_input.text()
        )

        # // what the text said before this save, to know which pictures
        # // were just taken out of it
        old_images = get_image_names(
            post.get("content", "")
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

        # // a picture whose marker was just removed from this post (or
        # // that was inserted and removed again before saving) goes away
        # // now, unless another post still uses it.
        remove_unused_post_images(
            old_images | self.pending_images,
            posts
        )

        self.pending_images = set()

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

        deleted_images = get_image_names(
            posts[selected_index].get("content", "")
        )

        posts.pop(
            selected_index
        )

        save_json(
            "posts.json",
            data
        )

        # // pictures only this post used are removed with it
        remove_unused_post_images(
            deleted_images | self.pending_images,
            posts
        )

        self.pending_images = set()

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


