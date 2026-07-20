import sys

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QStackedWidget,
    QMessageBox
)


from ui.dashboard import Page as DashboardPage
from ui.about import Page as AboutPage
from ui.albums import Page as AlbumsPage
from ui.artworks import Page as ArtworksPage
from ui.posts import Page as PostsPage


from generator.website_generator import generate_website
from tools.github_manager import publish_changes





class AdminWindow(QWidget):

    def __init__(self):

        super().__init__()


        self.setWindowTitle(
            "Aaron-l Portfolio Admin"
        )


        self.resize(
            1000,
            600
        )



        main_layout = QHBoxLayout()

        self.setLayout(
            main_layout
        )



        # SIDEBAR

        sidebar = QVBoxLayout()



        self.dashboard_button = QPushButton(
            "Dashboard"
        )


        self.about_button = QPushButton(
            "About"
        )


        self.albums_button = QPushButton(
            "Albums"
        )


        self.artworks_button = QPushButton(
            "Artworks"
        )


        self.posts_button = QPushButton(
            "Posts"
        )


        self.generate_button = QPushButton(
            "Generate Website"
        )


        self.publish_button = QPushButton(
            "Publish Website"
        )



        for button in [

            self.dashboard_button,

            self.about_button,

            self.albums_button,

            self.artworks_button,

            self.posts_button,

            self.generate_button,

            self.publish_button

        ]:

            sidebar.addWidget(
                button
            )



        sidebar.addStretch()



        main_layout.addLayout(
            sidebar
        )





        # PAGES


        self.pages = QStackedWidget()



        self.dashboard_page = DashboardPage()

        self.about_page = AboutPage()

        self.albums_page = AlbumsPage()

        self.artworks_page = ArtworksPage()

        self.posts_page = PostsPage()



        self.pages.addWidget(
            self.dashboard_page
        )

        self.pages.addWidget(
            self.about_page
        )

        self.pages.addWidget(
            self.albums_page
        )

        self.pages.addWidget(
            self.artworks_page
        )

        self.pages.addWidget(
            self.posts_page
        )



        main_layout.addWidget(
            self.pages
        )





        # CONNECTIONS


        self.dashboard_button.clicked.connect(

            lambda:
            self.pages.setCurrentWidget(
                self.dashboard_page
            )

        )


        self.about_button.clicked.connect(

            lambda:
            self.pages.setCurrentWidget(
                self.about_page
            )

        )


        self.albums_button.clicked.connect(

            lambda:
            self.pages.setCurrentWidget(
                self.albums_page
            )

        )


        self.artworks_button.clicked.connect(

            lambda:
            self.pages.setCurrentWidget(
                self.artworks_page
            )

        )


        self.posts_button.clicked.connect(

            lambda:
            self.pages.setCurrentWidget(
                self.posts_page
            )

        )


        self.generate_button.clicked.connect(
            self.update_website
        )


        self.publish_button.clicked.connect(
            self.publish_website
        )







    def update_website(self):

        try:

            generate_website()


            QMessageBox.information(

                self,

                "Website Generated",

                "Website files have been updated locally."

            )


        except Exception as error:


            QMessageBox.critical(

                self,

                "Generation Error",

                str(error)

            )







    def publish_website(self):

        try:

            # Create latest website files

            generate_website()



            # Commit and push to GitHub

            result = publish_changes()



            QMessageBox.information(

                self,

                "Published",

                result

            )


        except Exception as error:


            QMessageBox.critical(

                self,

                "Publish Error",

                str(error)

            )








if __name__ == "__main__":


    app = QApplication(
        sys.argv
    )



    app.setStyleSheet("""


        QWidget {

            background-color:#111111;
            color:#eeeeee;
            font-size:14px;

        }


        QPushButton {

            background-color:#1b1b1b;
            border:1px solid #8b2635;
            padding:8px;
            border-radius:6px;

        }


        QPushButton:hover {

            background-color:#8b2635;

        }


        QLineEdit,
        QTextEdit,
        QListWidget {

            background-color:#1b1b1b;
            color:white;
            border:1px solid #333333;
            border-radius:5px;

        }


        QLabel {

            color:#eeeeee;

        }

    """)



    window = AdminWindow()


    window.show()


    sys.exit(
        app.exec()
    )