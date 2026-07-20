from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QLineEdit,
    QPushButton,
    QMessageBox
)


from tools.json_manager import load_json, save_json
from tools.update_manager import update_last_modified



class Page(QWidget):

    def __init__(self):

        super().__init__()


        self.data = load_json(
            "about.json"
        )



        layout = QVBoxLayout()

        self.setLayout(
            layout
        )



        title = QLabel(
            "About Editor"
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



        # Introduction

        intro_label = QLabel(
            "Introduction"
        )

        layout.addWidget(
            intro_label
        )


        self.introduction = QTextEdit()


        self.introduction.setText(
            self.data.get(
                "introduction",
                ""
            )
        )


        layout.addWidget(
            self.introduction
        )



        # Links

        links = self.data.get(
            "links",
            {}
        )



        pixiv_label = QLabel(
            "Pixiv"
        )

        layout.addWidget(
            pixiv_label
        )


        self.pixiv = QLineEdit()


        self.pixiv.setText(
            links.get(
                "pixiv",
                ""
            )
        )


        layout.addWidget(
            self.pixiv
        )



        reddit_label = QLabel(
            "Reddit"
        )

        layout.addWidget(
            reddit_label
        )


        self.reddit = QLineEdit()


        self.reddit.setText(
            links.get(
                "reddit",
                ""
            )
        )


        layout.addWidget(
            self.reddit
        )



        discord_label = QLabel(
            "Discord"
        )

        layout.addWidget(
            discord_label
        )


        self.discord = QLineEdit()


        self.discord.setText(
            links.get(
                "discord",
                ""
            )
        )


        layout.addWidget(
            self.discord
        )



        # Save button

        save_button = QPushButton(
            "Save About"
        )


        save_button.clicked.connect(
            self.save
        )


        layout.addWidget(
            save_button
        )



        layout.addStretch()



    def save(self):

        data = {

            "introduction":
                self.introduction.toPlainText(),


            "links": {

                "pixiv":
                    self.pixiv.text(),

                "reddit":
                    self.reddit.text(),

                "discord":
                    self.discord.text()

            },


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