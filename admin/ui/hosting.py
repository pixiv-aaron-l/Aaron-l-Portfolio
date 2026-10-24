import os

from PySide6.QtCore import Qt, QTimer

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QMessageBox,
    QFileDialog
)


from tools.hosted_attachments import (
    HostedAttachmentsError,
    add_hosted,
    delete_hosted,
    list_hosted,
    get_web_link
)


# // this page is deliberately tiny: a list of hosted files and three
# // buttons. A hosted attachment is just a normal attachment that isn't
# // in any post (the file goes in website/attachments/ with its normal
# // name). All the real work lives in tools/hosted_attachments.py, this
# // file only deals with buttons and lists.

COPY_TEXT = "Copy Web Link"


class Page(QWidget):

    def __init__(self):

        super().__init__()


        self.entries = []


        layout = QVBoxLayout()

        self.setLayout(
            layout
        )


        title = QLabel(
            "Hosting Attachments"
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


        description = QLabel(
            "Put a file on your website without adding it to a post. "
            "Select it, then copy its web link to share it anywhere."
        )

        description.setWordWrap(
            True
        )

        description.setStyleSheet("""
            QLabel {

                color:#aaaaaa;
                font-size:16px;

            }
        """)

        layout.addWidget(
            description
        )


        self.file_list = QListWidget()

        self.file_list.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.file_list.setTextElideMode(
            Qt.ElideRight
        )

        layout.addWidget(
            self.file_list,
            1
        )


        buttons = QHBoxLayout()


        self.add_button = QPushButton(
            "Add Attachment"
        )

        self.copy_button = QPushButton(
            COPY_TEXT
        )

        self.delete_button = QPushButton(
            "Delete"
        )


        buttons.addWidget(
            self.add_button
        )

        buttons.addWidget(
            self.copy_button
        )

        buttons.addWidget(
            self.delete_button
        )


        layout.addLayout(
            buttons
        )


        self.refresh()


        self.file_list.currentRowChanged.connect(
            self.update_buttons
        )

        self.add_button.clicked.connect(
            self.add_attachment
        )

        self.copy_button.clicked.connect(
            self.copy_link
        )

        self.delete_button.clicked.connect(
            self.delete_attachment
        )



    def showEvent(self, event):

        # // refresh whenever this page is shown, like every other page
        # // in the admin.

        super().showEvent(event)

        self.refresh()



    def current_entry(self):

        row = self.file_list.currentRow()

        if 0 <= row < len(self.entries):

            return self.entries[row]

        return None



    def refresh(self, select_file=None):

        if select_file is None:

            entry = self.current_entry()

            if entry:

                select_file = entry.get(
                    "file"
                )

        self.entries = list_hosted()

        # // signals blocked while rebuilding, same reason as the other
        # // lists: clearing a list would otherwise wipe the selection.

        self.file_list.blockSignals(
            True
        )

        self.file_list.clear()

        for entry in self.entries:

            self.file_list.addItem(
                entry.get(
                    "name",
                    entry.get("file", "")
                )
            )

        self.file_list.blockSignals(
            False
        )

        target = -1

        for index, entry in enumerate(
            self.entries
        ):

            if entry.get("file") == select_file:

                target = index

        if target >= 0:

            self.file_list.setCurrentRow(
                target
            )

        else:

            self.update_buttons(
                -1
            )



    def update_buttons(self, row):

        has_selection = 0 <= row < len(self.entries)

        self.copy_button.setEnabled(
            has_selection
        )

        self.delete_button.setEnabled(
            has_selection
        )



    def add_attachment(self):

        path, _ = QFileDialog.getOpenFileName(

            self,

            "Choose a file to host",

            "",

            "All files (*.*)"

        )

        if not path:

            return


        try:

            entry = add_hosted(
                path
            )

        except HostedAttachmentsError as error:

            QMessageBox.critical(

                self,

                "Couldn't add file",

                str(error)

            )

            return

        except Exception as error:

            QMessageBox.critical(

                self,

                "Couldn't add file",

                f"Something unexpected went wrong:\n{error}"

            )

            return


        self.refresh(
            entry["file"]
        )



    def copy_link(self):

        entry = self.current_entry()

        if not entry:

            return

        link = get_web_link(
            entry
        )

        if not link:

            QMessageBox.warning(

                self,

                "No link yet",

                "No GitHub remote was found, so there's no web "
                "address to build a link from yet."

            )

            return

        QApplication.clipboard().setText(
            link
        )

        # // no popup and no status line: the button itself says it
        # // worked for a moment, then goes back to normal.

        self.copy_button.setText(
            "Copied!"
        )

        QTimer.singleShot(
            1500,
            lambda: self.copy_button.setText(
                COPY_TEXT
            )
        )



    def delete_attachment(self):

        entry = self.current_entry()

        if not entry:

            return


        answer = QMessageBox.question(

            self,

            "Delete Attachment",

            f"Delete \"{entry.get('name', '')}\"?\n\n"
            "Its web link stops working after the next Publish."

        )

        if answer != QMessageBox.Yes:

            return


        try:

            delete_hosted(
                entry["file"]
            )

        except HostedAttachmentsError as error:

            QMessageBox.critical(

                self,

                "Couldn't delete",

                str(error)

            )

            return


        self.refresh()
