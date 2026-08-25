import os
import json
import re
import shutil

from datetime import datetime
from urllib.parse import quote

from tools.json_manager import load_json


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

TEMPLATE_FOLDER = os.path.join(
    BASE_FOLDER,
    "templates"
)

GENERATED_LIST = os.path.join(
    BASE_FOLDER,
    "data",
    "generated_files.json"
)


# ============================================================
# GITHUB CONFIGURATION
# ============================================================

GITHUB_OWNER = "pixiv-aaron-l"

GITHUB_REPOSITORY = "Aaron-l-Portfolio"

GITHUB_BRANCH = "main"

GITHUB_MEDIA_BASE = (
    "https://media.githubusercontent.com/media/"
    f"{GITHUB_OWNER}/"
    f"{GITHUB_REPOSITORY}/"
    f"{GITHUB_BRANCH}/"
)


# ============================================================
# TEMPLATE FUNCTIONS
# ============================================================

def read_template(name):

    path = os.path.join(
        TEMPLATE_FOLDER,
        name
    )

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return file.read()


def write_file(path, content):

    os.makedirs(
        os.path.dirname(path),
        exist_ok=True
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(content)


def replace_values(html, values):

    for key, value in values.items():

        html = html.replace(
            key,
            str(value)
        )

    return html


def get_last_updated():

    return datetime.now().strftime(
        "%d/%m/%Y"
    )


# ============================================================
# HTML HELPERS
# ============================================================

def escape_html(text):

    if text is None:
        return ""

    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def format_text(text):

    """
    Converts normal text into HTML.

    Features:
    - clickable http/https links
    - normal line breaks
    - paragraphs separated by a line containing *
    """

    if not text:

        return ""

    text = str(text)

    # --------------------------------------------------------
    # Temporarily protect URLs
    # --------------------------------------------------------

    urls = []

    def protect_url(match):

        index = len(urls)

        urls.append(
            match.group(0)
        )

        return f"__URL_{index}__"

    text = re.sub(
        r"https?://[^\s<]+",
        protect_url,
        text
    )

    # --------------------------------------------------------
    # Escape normal HTML
    # --------------------------------------------------------

    text = escape_html(
        text
    )

    # --------------------------------------------------------
    # Restore URLs as clickable links
    # --------------------------------------------------------

    for index, url in enumerate(urls):

        safe_url = escape_html(
            url
        )

        link = (
            f'<a href="{safe_url}" '
            f'target="_blank" '
            f'rel="noopener noreferrer">'
            f'{safe_url}'
            f'</a>'
        )

        text = text.replace(
            f"__URL_{index}__",
            link
        )

    # --------------------------------------------------------
    # Split paragraphs
    # --------------------------------------------------------

    paragraphs = re.split(
        r"\n\s*\*\s*\n",
        text
    )

    html = ""

    for paragraph in paragraphs:

        paragraph = paragraph.strip()

        if not paragraph:

            continue

        paragraph = paragraph.replace(
            "\n",
            "<br>"
        )

        html += (
            "<p>\n"
            + paragraph
            + "\n</p>\n"
        )

    return html


# ============================================================
# ATTACHMENT URL
# ============================================================

def get_attachment_url(filename):

    if not filename:

        return ""

    encoded_filename = quote(
        filename,
        safe=""
    )

    # --------------------------------------------------------
    # Git LFS archives
    # --------------------------------------------------------

    if filename.lower().endswith(
        (".zip", ".7z")
    ):

        return (
            GITHUB_MEDIA_BASE
            + "website/attachments/"
            + encoded_filename
        )

    # --------------------------------------------------------
    # Normal attachments
    # --------------------------------------------------------

    return (
        "../attachments/"
        + encoded_filename
    )


# ============================================================
# INDEX
# ============================================================

def generate_index():

    about = load_json(
        "about.json"
    )

    html = read_template(
        "index_template.html"
    )

    introduction = format_text(
        about.get(
            "introduction",
            ""
        )
    )

    html = replace_values(

        html,

        {

            "{{ABOUT_INTRODUCTION}}":
                introduction,

            "{{PIXIV_LINK}}":
                about.get(
                    "links",
                    {}
                ).get(
                    "pixiv",
                    ""
                ),

            "{{REDDIT_LINK}}":
                about.get(
                    "links",
                    {}
                ).get(
                    "reddit",
                    ""
                ),

            "{{DISCORD_LINK}}":
                about.get(
                    "links",
                    {}
                ).get(
                    "discord",
                    ""
                ),

            "{{LAST_UPDATED}}":
                get_last_updated()

        }

    )

    write_file(

        os.path.join(
            WEBSITE_FOLDER,
            "index.html"
        ),

        html

    )


# ============================================================
# ARTS
# ============================================================

def generate_arts():

    albums = load_json(
        "albums.json"
    )

    html = read_template(
        "arts_template.html"
    )

    cards = ""

    for album in albums.get(
        "albums",
        []
    ):

        description = format_text(
            album.get(
                "description",
                ""
            )
        )

        cards += f"""

<a class="album-card" href="albums/{quote(album.get('folder', ''), safe='')}.html">

<div class="album-info">

<h2>
{escape_html(album.get('title', ''))}
</h2>

<div>
{description}
</div>

<p class="album-date">
{escape_html(album.get('date', ''))}
</p>

<p class="album-count">
{len(album.get('artworks', []))} artworks
</p>

</div>

<div class="album-cover">

<img src="images/albums/{quote(album.get('folder', ''), safe='')}/display/{quote(album.get('cover', ''), safe='')}">

</div>

</a>

"""

    html = html.replace(
        "{{ALBUM_LIST}}",
        cards
    )

    html = html.replace(
        "{{LAST_UPDATED}}",
        get_last_updated()
    )

    write_file(

        os.path.join(
            WEBSITE_FOLDER,
            "arts.html"
        ),

        html

    )


# ============================================================
# ALBUMS
# ============================================================

def generate_albums():

    albums = load_json(
        "albums.json"
    )

    template = read_template(
        "album_template.html"
    )

    for album in albums.get(
        "albums",
        []
    ):

        html = replace_values(

            template,

            {

                "{{ALBUM_TITLE}}":
                    escape_html(
                        album.get(
                            "title",
                            ""
                        )
                    ),

                "{{ALBUM_DATE}}":
                    escape_html(
                        album.get(
                            "date",
                            ""
                        )
                    ),

                "{{ALBUM_DESCRIPTION}}":
                    format_text(
                        album.get(
                            "description",
                            ""
                        )
                    ),

                "{{ARTWORK_COUNT}}":
                    len(
                        album.get(
                            "artworks",
                            []
                        )
                    ),

                "{{LAST_UPDATED}}":
                    get_last_updated()

            }

        )

        grid = ""

        artworks = sorted(

            album.get(
                "artworks",
                []
            ),

            key=lambda x: int(
                x.get(
                    "number",
                    0
                )
            )

        )

        for artwork in artworks:

            grid += f"""

<a class="artwork-card" href="../artworks/{quote(artwork.get('file', ''), safe='')}.html">

<div class="artwork-thumbnail">

<img src="../images/albums/{quote(album.get('folder', ''), safe='')}/display/{quote(artwork.get('display', ''), safe='')}">

</div>

<div class="artwork-info">

<h3>
{escape_html(artwork.get('title', ''))}
</h3>

<div class="artwork-info-bottom">

<span class="artwork-number">
#{escape_html(artwork.get('number', ''))}
</span>

<span class="artwork-date">
{escape_html(artwork.get('date', ''))}
</span>

</div>

</div>

</a>

"""

        html = html.replace(
            "{{ARTWORK_GRID}}",
            grid
        )

        write_file(

            os.path.join(

                WEBSITE_FOLDER,

                "albums",

                album.get(
                    "folder",
                    "album"
                )
                + ".html"

            ),

            html

        )


# ============================================================
# ARTWORKS
# ============================================================

def generate_artworks():

    albums = load_json(
        "albums.json"
    )

    template = read_template(
        "artwork_template.html"
    )

    for album in albums.get(
        "albums",
        []
    ):

        artworks = album.get(
            "artworks",
            []
        )

        for index, artwork in enumerate(
            artworks
        ):

            notes = format_text(
                artwork.get(
                    "notes",
                    ""
                )
            )

            html = replace_values(

                template,

                {

                    "{{ARTWORK_TITLE}}":
                        escape_html(
                            artwork.get(
                                "title",
                                ""
                            )
                        ),

                    "{{ARTWORK_NUMBER}}":
                        escape_html(
                            artwork.get(
                                "number",
                                ""
                            )
                        ),

                    "{{ARTWORK_DATE}}":
                        escape_html(
                            artwork.get(
                                "date",
                                ""
                            )
                        ),

                    "{{ARTWORK_TIME_SPENT}}":
                        escape_html(
                            artwork.get(
                                "time_spent",
                                ""
                            )
                        ),

                    "{{ARTWORK_NOTES}}":
                        notes,

                    "{{ALBUM_FOLDER}}":
                        album.get(
                            "folder",
                            ""
                        ),

                    "{{ARTWORK_DISPLAY}}":
                        artwork.get(
                            "display",
                            ""
                        ),

                    "{{ARTWORK_ORIGINAL}}":
                        artwork.get(
                            "original",
                            ""
                        ),

                    "{{LAST_UPDATED}}":
                        get_last_updated()

                }

            )

            previous = "#"

            next_page = "#"

            if index > 0:

                previous = (

                    "../artworks/"
                    +
                    artworks[index - 1].get(
                        "file",
                        ""
                    )
                    +
                    ".html"

                )

            if index < len(artworks) - 1:

                next_page = (

                    "../artworks/"
                    +
                    artworks[index + 1].get(
                        "file",
                        ""
                    )
                    +
                    ".html"

                )

            html = html.replace(
                "{{PREVIOUS_ARTWORK}}",
                previous
            )

            html = html.replace(
                "{{NEXT_ARTWORK}}",
                next_page
            )

            keyboard_script = f"""

<script>

document.addEventListener("keydown", function(event) {{

    if (
        event.key === "ArrowLeft"
        &&
        "{previous}" !== "#"
    ) {{

        window.location.href = "{previous}";

    }}

    if (
        event.key === "ArrowRight"
        &&
        "{next_page}" !== "#"
    ) {{

        window.location.href = "{next_page}";

    }}

}});

</script>

"""

            if "</body>" in html:

                html = html.replace(

                    "</body>",

                    keyboard_script
                    +
                    "\n</body>"

                )

            else:

                html += keyboard_script

            write_file(

                os.path.join(

                    WEBSITE_FOLDER,

                    "artworks",

                    artwork.get(
                        "file",
                        "artwork"
                    )
                    +
                    ".html"

                ),

                html

            )


# ============================================================
# POST ATTACHMENTS
# ============================================================

def generate_attachments(attachments):

    if not attachments:

        return ""

    html = """

<section class="post-files-card">

<h2>
Attachments
</h2>

"""

    for attachment in attachments:

        if isinstance(
            attachment,
            dict
        ):

            name = attachment.get(
                "name",
                ""
            )

            file = attachment.get(
                "file",
                ""
            )

        else:

            name = attachment

            file = attachment

        if not file:

            continue

        url = get_attachment_url(
            file
        )

        display_name = escape_html(
            name
        )

        html += f"""

<a
    class="download-button"
    href="{url}"
>
    {display_name}
</a>

"""

    html += """

</section>

"""

    return html


# ============================================================
# POST CONTENT
# ============================================================

def format_post_content(content):

    if not content:

        return ""

    pattern = r"\[\[IMAGE:([^\]]+)\]\]"

    parts = re.split(
        pattern,
        content
    )

    html = ""

    for index, part in enumerate(parts):

        if not part:

            continue

        # ----------------------------------------------------
        # INLINE IMAGE
        # ----------------------------------------------------

        if index % 2 == 1:

            filename = part.strip()

            encoded_filename = quote(
                filename,
                safe=""
            )

            html += f"""

<div class="post-inline-image">

<img
    src="../images/posts/{encoded_filename}"
    alt=""
>

</div>

"""

        # ----------------------------------------------------
        # TEXT
        # ----------------------------------------------------

        else:

            html += format_text(
                part
            )

    return html


# ============================================================
# POSTS
# ============================================================

def generate_posts():

    posts = load_json(
        "posts.json"
    )

    html = read_template(
        "posts_template.html"
    )

    cards = ""

    for post in posts.get(
        "posts",
        []
    ):

        cards += f"""

<a class="post-card" href="posts/{quote(post.get('file', ''), safe='')}.html">

<h2>
{escape_html(post.get('title', ''))}
</h2>

<p>
{escape_html(post.get('date', ''))}
</p>

</a>

"""

    html = html.replace(
        "{{POST_LIST}}",
        cards
    )

    html = html.replace(
        "{{LAST_UPDATED}}",
        get_last_updated()
    )

    write_file(

        os.path.join(
            WEBSITE_FOLDER,
            "posts.html"
        ),

        html

    )

    template = read_template(
        "post_template.html"
    )

    for post in posts.get(
        "posts",
        []
    ):

        page = replace_values(

            template,

            {

                "{{POST_TITLE}}":
                    escape_html(
                        post.get(
                            "title",
                            ""
                        )
                    ),

                "{{POST_DATE}}":
                    escape_html(
                        post.get(
                            "date",
                            ""
                        )
                    ),

                "{{POST_CONTENT}}":
                    format_post_content(
                        post.get(
                            "content",
                            ""
                        )
                    ),

                "{{ATTACHMENTS}}":
                    generate_attachments(
                        post.get(
                            "attachments",
                            []
                        )
                    ),

                "{{LAST_UPDATED}}":
                    get_last_updated()

            }

        )

        write_file(

            os.path.join(

                WEBSITE_FOLDER,

                "posts",

                post.get(
                    "file",
                    "post"
                )
                +
                ".html"

            ),

            page

        )


# ============================================================
# GENERATED FILE LIST
# ============================================================

def get_generated_files():

    files = [

        "index.html",

        "arts.html",

        "posts.html"

    ]

    # --------------------------------------------------------
    # ALBUMS / ARTWORKS
    # --------------------------------------------------------

    albums = load_json(
        "albums.json"
    )

    for album in albums.get(
        "albums",
        []
    ):

        folder = album.get(
            "folder",
            ""
        )

        files.append(

            os.path.join(
                "albums",
                folder + ".html"
            ).replace(
                "\\",
                "/"
            )

        )

        for artwork in album.get(
            "artworks",
            []
        ):

            files.append(

                os.path.join(
                    "artworks",
                    artwork.get(
                        "file",
                        ""
                    )
                    +
                    ".html"
                ).replace(
                    "\\",
                    "/"
                )

            )

            if artwork.get(
                "display"
            ):

                files.append(

                    os.path.join(

                        "images",
                        "albums",
                        folder,
                        "display",
                        artwork.get(
                            "display"
                        )

                    ).replace(
                        "\\",
                        "/"
                    )

                )

            if artwork.get(
                "original"
            ):

                files.append(

                    os.path.join(

                        "images",
                        "albums",
                        folder,
                        "original",
                        artwork.get(
                            "original"
                        )

                    ).replace(
                        "\\",
                        "/"
                    )

                )

        cover = album.get(
            "cover",
            ""
        )

        if cover:

            files.append(

                os.path.join(

                    "images",
                    "albums",
                    folder,
                    "display",
                    cover

                ).replace(
                    "\\",
                    "/"
                )

            )

    # --------------------------------------------------------
    # POSTS
    # --------------------------------------------------------

    posts = load_json(
        "posts.json"
    )

    for post in posts.get(
        "posts",
        []
    ):

        files.append(

            os.path.join(

                "posts",

                post.get(
                    "file",
                    ""
                )
                +
                ".html"

            ).replace(
                "\\",
                "/"
            )

        )

        # ----------------------------------------------------
        # POST INLINE IMAGES
        #
        # IMPORTANT:
        # These are recorded as generated files, but they are
        # NEVER cleaned automatically.
        # ----------------------------------------------------

        content = post.get(
            "content",
            ""
        )

        image_pattern = r"\[\[IMAGE:([^\]]+)\]\]"

        for image_filename in re.findall(
            image_pattern,
            content
        ):

            image_filename = image_filename.strip()

            if image_filename:

                files.append(

                    os.path.join(

                        "images",
                        "posts",
                        image_filename

                    ).replace(
                        "\\",
                        "/"
                    )

                )

        # ----------------------------------------------------
        # POST ATTACHMENTS
        # ----------------------------------------------------

        for attachment in post.get(
            "attachments",
            []
        ):

            if isinstance(
                attachment,
                dict
            ):

                filename = attachment.get(
                    "file",
                    ""
                )

            else:

                filename = attachment

            if filename:

                files.append(

                    os.path.join(
                        "attachments",
                        filename
                    ).replace(
                        "\\",
                        "/"
                    )

                )

    return list(
        set(files)
    )


# ============================================================
# CLEAN GENERATED WEBSITE
# ============================================================

def clean_generated_website():

    if not os.path.exists(
        GENERATED_LIST
    ):

        return

    with open(
        GENERATED_LIST,
        "r",
        encoding="utf-8"
    ) as file:

        old_files = json.load(file).get(
            "files",
            []
        )

    current_files = get_generated_files()

    for old_file in old_files:

        if old_file not in current_files:

            # ------------------------------------------------
            # SAFETY:
            #
            # NEVER delete anything inside images/posts.
            #
            # Old versions of generated_files.json may not
            # contain these images, so we explicitly protect
            # this directory.
            # ------------------------------------------------

            normalized = old_file.replace(
                "\\",
                "/"
            )

            if normalized.startswith(
                "images/posts/"
            ):

                continue

            path = os.path.join(
                WEBSITE_FOLDER,
                old_file
            )

            if os.path.isfile(path):

                os.remove(path)


# ============================================================
# CLEAN UNUSED ATTACHMENTS
# ============================================================

def clean_unused_attachments():

    attachments_folder = os.path.join(
        WEBSITE_FOLDER,
        "attachments"
    )

    if not os.path.exists(
        attachments_folder
    ):

        return

    used_files = set()

    posts = load_json(
        "posts.json"
    )

    for post in posts.get(
        "posts",
        []
    ):

        for attachment in post.get(
            "attachments",
            []
        ):

            if isinstance(
                attachment,
                dict
            ):

                filename = attachment.get(
                    "file",
                    ""
                )

            else:

                filename = attachment

            if filename:

                used_files.add(
                    filename
                )

    for filename in os.listdir(
        attachments_folder
    ):

        path = os.path.join(
            attachments_folder,
            filename
        )

        if (

            filename not in used_files

            and os.path.isfile(path)

        ):

            os.remove(path)


# ============================================================
# CLEAN UNUSED ALBUM IMAGES
# ============================================================

def clean_unused_album_images():

    albums_folder = os.path.join(
        WEBSITE_FOLDER,
        "images",
        "albums"
    )

    if not os.path.exists(
        albums_folder
    ):

        return

    used_files = set()

    albums = load_json(
        "albums.json"
    )

    for album in albums.get(
        "albums",
        []
    ):

        folder = album.get(
            "folder",
            ""
        )

        for artwork in album.get(
            "artworks",
            []
        ):

            display = artwork.get(
                "display",
                ""
            )

            original = artwork.get(
                "original",
                ""
            )

            if display:

                used_files.add(

                    os.path.join(
                        folder,
                        "display",
                        display
                    ).replace(
                        "\\",
                        "/"
                    )

                )

            if original:

                used_files.add(

                    os.path.join(
                        folder,
                        "original",
                        original
                    ).replace(
                        "\\",
                        "/"
                    )

                )

        cover = album.get(
            "cover",
            ""
        )

        if cover:

            used_files.add(

                os.path.join(
                    folder,
                    "display",
                    cover
                ).replace(
                    "\\",
                    "/"
                )

            )

    for root, dirs, files in os.walk(
        albums_folder
    ):

        for filename in files:

            full_path = os.path.join(
                root,
                filename
            )

            relative = os.path.relpath(
                full_path,
                albums_folder
            ).replace(
                "\\",
                "/"
            )

            if relative not in used_files:

                os.remove(
                    full_path
                )


# ============================================================
# CLEAN UNUSED ALBUM FOLDERS
# ============================================================

def clean_unused_album_folders():

    albums_folder = os.path.join(
        WEBSITE_FOLDER,
        "images",
        "albums"
    )

    if not os.path.exists(
        albums_folder
    ):

        return

    used = set()

    albums = load_json(
        "albums.json"
    )

    for album in albums.get(
        "albums",
        []
    ):

        folder = album.get(
            "folder",
            ""
        )

        if folder:

            used.add(
                folder
            )

    for folder in os.listdir(
        albums_folder
    ):

        path = os.path.join(
            albums_folder,
            folder
        )

        if (

            os.path.isdir(path)

            and folder not in used

        ):

            shutil.rmtree(
                path
            )


# ============================================================
# CLEAN EMPTY FOLDERS
# ============================================================

def clean_empty_folders():

    for root, dirs, files in os.walk(

        WEBSITE_FOLDER,

        topdown=False

    ):

        if root == WEBSITE_FOLDER:

            continue

        # ----------------------------------------------------
        # NEVER remove the post image directory.
        # ----------------------------------------------------

        normalized_root = os.path.abspath(
            root
        )

        post_images_root = os.path.abspath(
            os.path.join(
                WEBSITE_FOLDER,
                "images",
                "posts"
            )
        )

        if normalized_root == post_images_root:

            continue

        if not dirs and not files:

            try:

                os.rmdir(
                    root
                )

            except OSError:

                pass


# ============================================================
# SAVE GENERATED FILE LIST
# ============================================================

def save_generated_files():

    os.makedirs(

        os.path.dirname(
            GENERATED_LIST
        ),

        exist_ok=True

    )

    with open(

        GENERATED_LIST,

        "w",

        encoding="utf-8"

    ) as file:

        json.dump(

            {
                "files": get_generated_files()
            },

            file,

            indent=4,

            ensure_ascii=False

        )


# ============================================================
# MAIN GENERATOR
# ============================================================

def generate_website():

    clean_generated_website()

    generate_index()

    generate_arts()

    generate_albums()

    generate_artworks()

    generate_posts()

    clean_unused_attachments()

    clean_unused_album_images()

    clean_unused_album_folders()

    clean_empty_folders()

    save_generated_files()