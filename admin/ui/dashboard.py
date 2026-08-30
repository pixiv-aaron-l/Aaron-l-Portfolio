from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QFrame,
    QLineEdit,
    QPushButton,
    QMessageBox
)


from tools.json_manager import load_json, save_json
from tools.site_config import get_site_name
from generator.website_generator import (
    get_featured_artwork_pool,
    RANDOM_ART_MINIMUM
)


# ============================================================
# Shared header style for section labels inside the dashboard
# (Website Settings, Random Artworks), matching the same look
# used on the About page.
# ============================================================

SECTION_LABEL_STYLE = """
    QLabel {
        font-size:18px;
        font-weight:bold;
        margin-top:12px;
    }
"""


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



        self.description_label = QLabel("")


        self.description_label.setStyleSheet("""
            QLabel {

                color:#aaaaaa;
                font-size:16px;

            }
        """)


        layout.addWidget(self.description_label)



        # --------------------------------------------------------
        # Statistics
        # --------------------------------------------------------

        stats_layout = QHBoxLayout()


        self.stat_value_labels = {}


        for name in ["Albums", "Artworks", "Posts"]:


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



            value = QLabel("0")

            value.setStyleSheet("""
                QLabel {

                    color:#b3374c;
                    font-size:32px;
                    font-weight:bold;

                }
            """)


            self.stat_value_labels[name] = value



            box_layout.addWidget(label)

            box_layout.addWidget(value)



            stats_layout.addWidget(box)



        layout.addLayout(stats_layout)



        # --------------------------------------------------------
        # Website Settings (corner branding text + since year)
        #
        # Lives here, under the stat boxes, rather than as its
        # own sidebar page, since it's a small amount of config.
        # --------------------------------------------------------

        settings_label = QLabel(
            "Website Settings"
        )

        settings_label.setStyleSheet(
            SECTION_LABEL_STYLE
        )

        layout.addWidget(
            settings_label
        )


        self.site_name_input = QLineEdit()

        self.site_name_input.setPlaceholderText(
            "Corner branding text (e.g. Aaron-l Gallery)"
        )

        layout.addWidget(
            self.site_name_input
        )


        self.since_year_input = QLineEdit()

        self.since_year_input.setPlaceholderText(
            "Since year (e.g. 2025) — leave empty to hide"
        )

        layout.addWidget(
            self.since_year_input
        )


        save_settings_button = QPushButton(
            "Save Settings"
        )

        save_settings_button.clicked.connect(
            self.save_settings
        )

        layout.addWidget(
            save_settings_button
        )



        # --------------------------------------------------------
        # Random Artworks status
        #
        # The random artworks section on the About Me page is
        # fully automatic: it draws from every album marked
        # "featured", and only appears once that pool has more
        # than RANDOM_ART_MINIMUM artworks. There's nothing to
        # configure here, but showing the current pool size and
        # whether the section is currently active helps explain
        # why it may or may not be showing up on the site.
        # --------------------------------------------------------

        random_art_label = QLabel(
            "Random Artworks"
        )

        random_art_label.setStyleSheet(
            SECTION_LABEL_STYLE
        )

        layout.addWidget(
            random_art_label
        )

        self.random_art_status_label = QLabel(
            ""
        )

        layout.addWidget(
            self.random_art_status_label
        )


        layout.addStretch()


        # Populate everything with real data right away, then
        # keep it live from here on (see showEvent below).

        self.refresh_data()


    def showEvent(self, event):

        """
        Called by Qt every time this page actually becomes
        visible, which includes every time the person clicks
        "Dashboard" in the sidebar (QStackedWidget shows this
        widget again). Refreshing here means renaming the site,
        featuring an album, adding a post, etc. all show up on
        the dashboard the next time it's opened, without needing
        to restart the app.
        """

        super().showEvent(event)

        self.refresh_data()


    def refresh_data(self):

        about = load_json("about.json")

        albums = load_json("albums.json")

        posts = load_json("posts.json")

        self.site_config_data = load_json(
            "site_config.json"
        )


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


        self.description_label.setText(
            f"Welcome to the {get_site_name()} "
            f"administration panel."
        )

        self.stat_value_labels["Albums"].setText(
            str(album_count)
        )

        self.stat_value_labels["Artworks"].setText(
            str(artwork_count)
        )

        self.stat_value_labels["Posts"].setText(
            str(post_count)
        )


        self.site_name_input.setText(
            self.site_config_data.get(
                "site_name",
                ""
            )
        )

        self.since_year_input.setText(
            self.site_config_data.get(
                "since_year",
                ""
            )
        )


        featured_pool = get_featured_artwork_pool(
            albums
        )

        featured_album_count = sum(

            1
            for album in albums.get("albums", [])
            if album.get("featured", False)

        )

        pool_size = len(
            featured_pool
        )

        if pool_size > RANDOM_ART_MINIMUM:

            status_text = (
                f"Enabled — {pool_size} artworks across "
                f"{featured_album_count} featured album(s)."
            )

            status_color = "#7fbf7f"

        else:

            status_text = (
                f"Disabled — {pool_size} artworks across "
                f"{featured_album_count} featured album(s) "
                f"(needs more than {RANDOM_ART_MINIMUM})."
            )

            status_color = "#aaaaaa"

        self.random_art_status_label.setText(
            status_text
        )

        self.random_art_status_label.setStyleSheet(f"""
            QLabel {{

                color:{status_color};
                font-size:14px;

            }}
        """)


    def save_settings(self):

        data = {

            "site_name":
                self.site_name_input.text().strip(),

            "since_year":
                self.since_year_input.text().strip()

        }

        save_json(
            "site_config.json",
            data
        )

        self.refresh_data()

        # Refresh the admin window title immediately too, so a
        # renamed site doesn't require restarting the app to
        # see it reflected there.

        self.window().setWindowTitle(
            f"{get_site_name()} Admin"
        )

        QMessageBox.information(

            self,

            "Saved",

            "Website settings saved."

        )
