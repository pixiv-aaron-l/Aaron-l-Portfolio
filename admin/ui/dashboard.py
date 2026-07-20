from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QFrame
)


from tools.json_manager import load_json



class Page(QWidget):

    def __init__(self):

        super().__init__()


        layout = QVBoxLayout()

        self.setLayout(layout)



        title = QLabel("Dashboard")


        title.setStyleSheet("""
            QLabel {

                font-size:32px;
                font-weight:bold;

            }
        """)


        layout.addWidget(title)



        about = load_json("about.json")

        albums = load_json("albums.json")

        posts = load_json("posts.json")



        album_count = len(
            albums.get("albums", [])
        )


        post_count = len(
            posts.get("posts", [])
        )


        artwork_count = 0


        for album in albums.get("albums", []):

            artwork_count += len(
                album.get("artworks", [])
            )



        description = QLabel(
            "Welcome to the Aaron-l Portfolio administration panel."
        )


        description.setStyleSheet("""
            QLabel {

                color:#aaaaaa;
                font-size:16px;

            }
        """)


        layout.addWidget(description)



        # Statistics

        stats_layout = QHBoxLayout()


        stats = [

            ("Albums", album_count),

            ("Artworks", artwork_count),

            ("Posts", post_count)

        ]



        for name, number in stats:


            box = QFrame()


            box.setStyleSheet("""

                QFrame {

                    background-color:#242424;
                    border-radius:10px;

                }

            """)


            box_layout = QVBoxLayout()


            box.setLayout(box_layout)



            label = QLabel(name)

            label.setStyleSheet("""
                QLabel {

                    color:#aaaaaa;
                    font-size:16px;

                }
            """)



            value = QLabel(str(number))

            value.setStyleSheet("""
                QLabel {

                    color:#b3374c;
                    font-size:32px;
                    font-weight:bold;

                }
            """)



            box_layout.addWidget(label)

            box_layout.addWidget(value)



            stats_layout.addWidget(box)



        layout.addLayout(stats_layout)


        layout.addStretch()