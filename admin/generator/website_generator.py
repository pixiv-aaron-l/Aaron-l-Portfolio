import os
import json
import re
import shutil
import zipfile

from datetime import datetime
from urllib.parse import quote

from tools.json_manager import load_json
from tools.site_config import get_site_name, get_since_year
from tools.github_manager import get_github_identity
from tools.mht_converter import mht_to_html
from tools.hosted_attachments import list_hosted, VIEW_SUFFIX


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
#
# Owner/repository/branch are configured from the admin
# (Dashboard -> Website Settings), not hardcoded here, so
# forking this project for a different site never requires
# editing any code.
# ============================================================

def get_github_media_base():

    """
    Base URL for Git LFS raw media (used for large .zip/.7z
    attachments). Owner/repository/branch are auto-detected from
    the actual git remote (see tools.github_manager), not
    entered anywhere -- there is nothing to configure.
    """

    owner, repository, branch = get_github_identity()

    return (
        "https://media.githubusercontent.com/media/"
        f"{owner}/"
        f"{repository}/"
        f"{branch}/"
    )


def get_site_base_path():

    """
    GitHub Pages base path.

    GitHub Pages hosts a repository named "<owner>.github.io"
    at the domain root ("/"). Any other repository name is
    hosted as a project site under "/<repository>/" instead.

    This matters specifically for 404.html: GitHub Pages
    serves that one file for ANY unmatched URL, no matter how
    deeply nested the requested path was, but the browser still
    resolves relative links in it based on the REQUESTED path,
    not on 404.html's real location. Without a fixed base, a
    404 triggered at the site root looks fine while one
    triggered from e.g. "/albums/some-typo" silently breaks
    every relative link and the stylesheet.

    The repository name is auto-detected from the actual git
    remote (see tools.github_manager) -- nothing to configure.
    """

    _, repository, _ = get_github_identity()

    if repository.lower().endswith(".github.io"):

        return "/"

    return f"/{repository}/"


# ============================================================
# SITE-WIDE BRANDING CONFIGURATION
# ============================================================

def build_since_text(since_year):

    """
    Builds the opposite-corner "since <year>" header text.
    Returns an empty string if no year has been configured, so
    the element simply doesn't appear at all.
    """

    if not since_year:

        return ""

    return (
        '<span class="since-text">since '
        + escape_html(since_year)
        + "</span>"
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

        html = file.read()

    # Every template automatically gets the site branding
    # placeholders filled in, so no individual generate_*
    # function needs to remember to do it, and any future
    # template gets this for free too.

    html = html.replace(
        "{{SITE_NAME}}",
        escape_html(
            get_site_name()
        )
    )

    html = html.replace(
        "{{SINCE_TEXT}}",
        build_since_text(
            get_since_year()
        )
    )

    return html


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
    #
    # // the tricky bit here: URLs get pulled OUT and replaced with
    # // a plain placeholder like __URL_0__ before the HTML-escaping
    # // step below runs. If this ran the other way around,
    # // escape_html would mangle the "&" in any URL that has query
    # // parameters (turning it into "&amp;" and breaking the link).
    # // Putting the real, already-escaped URL back in as a proper
    # // <a> tag only happens after escaping is done.
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
            get_github_media_base()
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

def build_about_links_section(links):

    """
    Builds the entire "Links" section of the About Me page,
    including the heading, from the about.json "links" list.

    Links are fully manual: every entry is added directly from
    the admin as {"text": "...", "url": "..."}. Only entries
    that have both a non-empty text and a non-empty URL are
    included.

    If there are no links at all, an empty string is returned
    so the section (and its heading) simply doesn't appear.
    """

    if not isinstance(
        links,
        list
    ):

        links = []

    link_tags = ""

    for entry in links:

        if not isinstance(
            entry,
            dict
        ):

            continue

        text = entry.get(
            "text",
            ""
        ).strip()

        url = entry.get(
            "url",
            ""
        ).strip()

        if not text or not url:

            continue

        link_tags += (
            f'<a href="{escape_html(url)}" '
            f'target="_blank" '
            f'rel="noopener noreferrer">\n'
            f'{escape_html(text)}\n'
            f'</a>\n\n'
        )

    if not link_tags:

        return ""

    return (
        '<section class="box">\n\n\n'
        "<h2>Links</h2>\n\n\n"
        '<div class="links">\n\n\n'
        + link_tags +
        "</div>\n\n\n"
        "</section>\n"
    )


# ============================================================
# RANDOM ARTWORK SECTION
# ============================================================

RANDOM_ART_MINIMUM = 20

RANDOM_ART_COUNT = 20


def get_featured_artwork_pool(albums):

    """
    Returns a flat list of (album, artwork) pairs for every
    artwork inside every album currently marked "featured" in
    the admin, excluding any artwork individually marked
    "excluded_from_random". Shared between the generator (to
    build the section) and the admin dashboard (to show pool
    size/status), so the two never drift out of sync.
    """

    pool = []

    for album in albums.get(
        "albums",
        []
    ):

        if not album.get(
            "featured",
            False
        ):

            continue

        for artwork in album.get(
            "artworks",
            []
        ):

            if artwork.get(
                "excluded_from_random",
                False
            ):

                continue

            pool.append(
                (album, artwork)
            )

    return pool


def build_random_artwork_section(albums):

    """
    Builds the optional "Random Artworks" section on the About
    Me page: a 4-row x 5-column grid of randomly picked
    artworks drawn from every album marked "featured".

    Only appears once the featured pool has MORE than
    RANDOM_ART_MINIMUM artworks available, so there's always
    enough variety and the grid never looks sparse or
    repetitive.

    The random selection happens client-side, in the browser,
    every time the page is loaded or refreshed: the ENTIRE
    featured pool is embedded as JSON, and a small inline script
    picks RANDOM_ART_COUNT of them at random and fills the grid.
    This is a static site with no server to re-roll anything on
    each request, so client-side JS is what makes "changes every
    time you open/refresh the page" possible at all.
    """

    pool = get_featured_artwork_pool(
        albums
    )

    if len(pool) <= RANDOM_ART_MINIMUM:

        return ""

    pool_data = []

    for album, artwork in pool:

        folder = quote(
            album.get("folder", ""),
            safe=""
        )

        file = quote(
            artwork.get("file", ""),
            safe=""
        )

        display = quote(
            artwork.get("display", ""),
            safe=""
        )

        pool_data.append({

            "url": f"artworks/{file}.html",

            "image":
                f"images/albums/{folder}/display/{display}",

            "title": artwork.get("title", "")

        })

    # "</" is escaped so a title/filename containing it could
    # never prematurely close the <script> tag it's embedded in.

    pool_json = json.dumps(
        pool_data,
        ensure_ascii=False
    ).replace(
        "</",
        "<\\/"
    )

    script = f"""
<script>
(function() {{

    var randomArtworkPool = {pool_json};

    var RANDOM_ART_COUNT = {RANDOM_ART_COUNT};

    function escapeHtml(text) {{
        var div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }}

    function pickRandomArtworks(pool, count) {{
        var shuffled = pool.slice();
        for (var i = shuffled.length - 1; i > 0; i--) {{
            var j = Math.floor(Math.random() * (i + 1));
            var temp = shuffled[i];
            shuffled[i] = shuffled[j];
            shuffled[j] = temp;
        }}
        return shuffled.slice(0, count);
    }}

    function renderRandomArtworks() {{
        var container = document.getElementById(
            'random-artwork-grid'
        );
        if (!container) return;
        var selection = pickRandomArtworks(
            randomArtworkPool,
            RANDOM_ART_COUNT
        );
        container.innerHTML = selection.map(function(item) {{
            return '<a class="artwork-card" href="' + item.url + '">'
                + '<div class="artwork-thumbnail">'
                + '<img src="' + item.image + '" alt="' + escapeHtml(item.title) + '">'
                + '</div>'
                + '<div class="artwork-info">'
                + '<h3>' + escapeHtml(item.title) + '</h3>'
                + '</div>'
                + '</a>';
        }}).join('');
    }}

    renderRandomArtworks();

}})();
</script>
"""

    return (
        '<section class="box">\n\n\n'
        "<h2>Random Artworks</h2>\n\n\n"
        '<div class="random-artwork-grid" '
        'id="random-artwork-grid"></div>\n\n\n'
        "</section>\n"
        + script
    )


def generate_index():

    about = load_json(
        "about.json"
    )

    albums = load_json(
        "albums.json"
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

    links_section = build_about_links_section(
        about.get(
            "links",
            []
        )
    )

    random_artwork_section = build_random_artwork_section(
        albums
    )

    html = replace_values(

        html,

        {

            "{{ABOUT_INTRODUCTION}}":
                introduction,

            "{{ABOUT_LINKS_SECTION}}":
                links_section,

            "{{RANDOM_ARTWORK_SECTION}}":
                random_artwork_section,

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

<img src="images/albums/{quote(album.get('folder', ''), safe='')}/display/{quote(album.get('cover', ''), safe='')}" alt="{escape_html(album.get('title', ''))}">

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

<img src="../images/albums/{quote(album.get('folder', ''), safe='')}/display/{quote(artwork.get('display', ''), safe='')}" alt="{escape_html(artwork.get('title', ''))}">

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

# ============================================================
# ATTACHMENT VIEWING
#
# // every attachment gets [ Download | View ]. Download is a real
# // forced download. View opens view.html?f=<file>: ONE shared page
# // (written once by generate_view_page) that shows the file full
# // screen with just a Return button. No per-file pages, no preview
# // folder.
# //
# // text, html, pdf and images are shown straight from the file. The
# // rest (mht, zip, 7z, anything else) can't be shown by a browser as
# // it is, so a small page about the file is written NEXT TO it as
# // "<file>.view.html" and that is what the viewer shows instead:
# // the web page for an .mht, the list of files inside for a zip/7z,
# // just the name and size for anything else.
# ============================================================

TEXT_VIEW_TYPES = (".txt", ".md", ".log", ".csv")

HTML_VIEW_TYPES = (".html", ".htm")

PDF_VIEW_TYPES = (".pdf",)

IMAGE_VIEW_TYPES = (".png", ".jpg", ".jpeg", ".gif", ".webp")

MHT_VIEW_TYPES = (".mht", ".mhtml")

# // bump this whenever the look of the generated "<file>.view.html"
# // pages changes, so pages made by an older version get rebuilt
# // instead of being kept because they look "up to date".
VIEW_PAGE_VERSION = 2

# // an archive's top level is normally a handful of items. This only
# // matters for a weird one with a huge number of items in its root.
MAX_TOP_LEVEL_ITEMS = 100


def get_view_kind(filename):

    # // "page" = needs a generated "<file>.view.html" to be shown.
    # // Keep these lists in step with the ones in view_template.html.

    extension = os.path.splitext(
        filename
    )[1].lower()

    if extension in TEXT_VIEW_TYPES:

        return "text"

    if extension in HTML_VIEW_TYPES:

        return "html"

    if extension in PDF_VIEW_TYPES:

        return "pdf"

    if extension in IMAGE_VIEW_TYPES:

        return "image"

    return "page"


def get_view_support_paths(filename):

    # // the generated helper page(s) of an attachment, relative to
    # // website/, so the file tracking/cleanup knows about them.

    if get_view_kind(filename) == "page":

        return [
            f"attachments/{filename}{VIEW_SUFFIX}"
        ]

    return []


def format_file_size(size):

    value = float(size)

    for unit in ("B", "KB", "MB"):

        if value < 1024:

            if unit == "B":

                return f"{int(value)} B"

            return f"{value:.1f} {unit}"

        value /= 1024

    return f"{value:.1f} GB"


def list_archive_entries(source, extension):

    # // returns [(name, size), ...] or None when it can't be read.
    # // .zip works out of the box. .7z needs the optional "py7zr"
    # // package (pip install py7zr), without it the page just shows
    # // the file's name and size instead of its contents.

    try:

        if extension == ".zip":

            with zipfile.ZipFile(
                source
            ) as archive:

                return [
                    (info.filename, info.file_size)
                    for info in archive.infolist()
                    if not info.is_dir()
                ]

        if extension == ".7z":

            import py7zr

            with py7zr.SevenZipFile(
                source,
                mode="r"
            ) as archive:

                return [
                    (info.filename, int(info.uncompressed or 0))
                    for info in archive.list()
                    if not info.is_directory
                ]

    except Exception:

        return None

    return None


def summarize_archive(entries):

    # // what's actually useful to know about an archive: how big it is,
    # // how many files, and what's at its top level. NOT a flat list of
    # // every file inside (that was long and told you nothing).

    paths = [
        (name.replace("\\", "/").strip("/"), size)
        for name, size in entries
    ]

    total_files = len(paths)

    total_size = sum(
        size
        for _, size in paths
    )

    # // very often everything sits inside one single folder
    # // ("myfolder/..."). Looking at just that folder would be a useless
    # // one-line summary, so step inside it (a few levels at most).

    inside = ""

    while inside.count("/") < 3:

        has_root_files = any(
            "/" not in path
            for path, _ in paths
        )

        tops = {
            path.split("/")[0]
            for path, _ in paths
            if "/" in path
        }

        if has_root_files or len(tops) != 1:

            break

        top = next(
            iter(tops)
        )

        inside += top + "/"

        paths = [
            (path[len(top) + 1:], size)
            for path, size in paths
        ]

    folders = {}

    files = []

    for path, size in paths:

        if "/" in path:

            top = path.split("/")[0]

            count_and_size = folders.setdefault(
                top,
                [0, 0]
            )

            count_and_size[0] += 1

            count_and_size[1] += size

        else:

            files.append(
                (path, size)
            )

    rows = []

    for name in sorted(
        folders,
        key=str.lower
    ):

        count, size = folders[name]

        plural = "" if count == 1 else "s"

        rows.append(
            (
                name + "/",
                f"{count} file{plural}, {format_file_size(size)}"
            )
        )

    for name, size in sorted(
        files,
        key=lambda item: item[0].lower()
    ):

        rows.append(
            (name, format_file_size(size))
        )

    plural = "" if total_files == 1 else "s"

    details = (
        f'<p class="note">{total_files} file{plural}, '
        f"{format_file_size(total_size)} once unpacked</p>"
    )

    if inside:

        details += (
            '<p class="note">Everything is inside '
            f"{escape_html(inside)}</p>"
        )

    shown = rows[:MAX_TOP_LEVEL_ITEMS]

    table_rows = "".join(
        "<tr><td>" + escape_html(name) + "</td>"
        '<td class="size">' + escape_html(info) + "</td></tr>"
        for name, info in shown
    )

    details += f"<table>{table_rows}</table>"

    if len(rows) > len(shown):

        details += (
            '<p class="note">...and '
            f"{len(rows) - len(shown)} more items.</p>"
        )

    return details


VIEW_SUPPORT_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="robots" content="noindex, nofollow">
<title>%%TITLE%%</title>
<style>
    body {
        margin:0;
        padding:30px 30px 90px 30px;
        background:#111111;
        color:#eeeeee;
        font-family:Arial,Helvetica,sans-serif;
    }
    h1 {
        color:#b3374c;
        overflow-wrap:anywhere;
    }
    .note {
        color:#aaaaaa;
    }
    table {
        border-collapse:collapse;
        width:100%;
    }
    td {
        padding:8px 12px;
        border-top:1px solid #2a2a2a;
        overflow-wrap:anywhere;
    }
    td.size {
        color:#aaaaaa;
        text-align:right;
        white-space:nowrap;
    }
</style>
</head>
<body>
<h1>%%TITLE%%</h1>
<p class="note">%%SIZE%%</p>
%%DETAILS%%
</body>
</html>
"""


def build_view_support_html(filename, source):

    extension = os.path.splitext(
        filename
    )[1].lower()

    if extension in MHT_VIEW_TYPES:

        # // a saved web page: rebuilt as one normal self-contained
        # // page (see tools/mht_converter.py).

        converted = mht_to_html(
            source
        )

        if converted is not None:

            return converted

    entries = list_archive_entries(
        source,
        extension
    )

    if entries is None:

        details = (
            '<p class="note">No preview is available for this '
            "type of file, but it can be downloaded.</p>"
        )

    elif not entries:

        details = '<p class="note">This archive is empty.</p>'

    else:

        details = summarize_archive(
            entries
        )

    page = VIEW_SUPPORT_TEMPLATE

    for marker, value in (
        ("%%TITLE%%", escape_html(filename)),
        ("%%SIZE%%", format_file_size(os.path.getsize(source))),
        ("%%DETAILS%%", details)
    ):

        page = page.replace(
            marker,
            value
        )

    return page


def ensure_view_support(filename):

    if get_view_kind(filename) != "page":

        return

    source = os.path.join(
        WEBSITE_FOLDER,
        "attachments",
        filename
    )

    if not os.path.isfile(
        source
    ):

        return

    target = source + VIEW_SUFFIX

    marker = f"<!-- view-page-version: {VIEW_PAGE_VERSION} -->"

    # // converting a big .mht or reading a big archive is slow-ish, so
    # // reuse the previous result while the original hasn't changed AND
    # // the page was made by this version of the generator.

    if (
        os.path.exists(target)
        and os.path.getmtime(target) >= os.path.getmtime(source)
    ):

        with open(
            target,
            "r",
            encoding="utf-8",
            errors="replace"
        ) as file:

            if marker in file.read(120):

                return

    write_file(
        target,
        marker + "\n" + build_view_support_html(
            filename,
            source
        )
    )


def generate_view_page():

    write_file(

        os.path.join(
            WEBSITE_FOLDER,
            "view.html"
        ),

        read_template(
            "view_template.html"
        )

    )


def generate_hosted_attachments():

    # // hosted attachments (tools/hosted_attachments.py) aren't in any
    # // post, but their web link opens the viewer too, so they need the
    # // same helper pages.

    for entry in list_hosted():

        ensure_view_support(
            entry["file"]
        )


def generate_attachments(attachments):

    if not attachments:

        return ""

    # // no heading and no lines between rows: attachments just sit
    # // under the post, one per line.

    html = """

<section class="post-files-card">

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

        ensure_view_support(
            file
        )

        view_link = (
            "../view.html?f="
            + quote(file, safe="")
        )

        # // "[ Download | View ]  name": one rounded pill split in two
        # // halves, then the attachment's name.

        pill = (
            f'<a href="{url}" '
            f'download="{escape_html(file)}">Download</a>'
            f'<a href="{view_link}">View</a>'
        )

        html += f"""

<div class="attachment-row">

<div class="attachment-actions">{pill}</div>

<span class="attachment-name">
{escape_html(name)}
</span>

</div>

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

            # No post title is available in this scope, so the
            # filename itself (cleaned up a little) is the best
            # description available for this inline image.

            alt_text = escape_html(
                os.path.splitext(filename)[0]
                .replace("-", " ")
                .replace("_", " ")
            )

            html += f"""

<div class="post-inline-image">

<img
    src="../images/posts/{encoded_filename}"
    alt="{alt_text}"
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
# CUSTOM 404 / LOST ARTWORK PAGE
# ============================================================

def generate_404():

    """
    Generates the custom 404 page shown by GitHub Pages for any
    unmatched URL (nonexistent artwork, post, album, or typo'd
    link). GitHub Pages automatically serves a file named
    404.html at the site root for this purpose, so no extra
    hosting configuration is required.

    Kept deliberately simple: a general "page not found"
    message. Navigation is handled entirely by the header nav,
    which is already present on every page including this one.
    """

    html = read_template(
        "404_template.html"
    )

    html = replace_values(

        html,

        {

            "{{SITE_BASE_PATH}}":
                get_site_base_path(),

            "{{LAST_UPDATED}}":
                get_last_updated()

        }

    )

    write_file(

        os.path.join(
            WEBSITE_FOLDER,
            "404.html"
        ),

        html

    )


# ============================================================
# GENERATED FILE LIST
# ============================================================

def get_generated_files():

    files = [

        "index.html",

        "arts.html",

        "posts.html",

        "404.html",

        "view.html"

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

                # // helper page (if this kind of file needs one)
                files.extend(
                    get_view_support_paths(
                        filename
                    )
                )

    # // hosted attachments are normal files in the attachments folder
    # // that no post uses, so they must be listed here too or the
    # // cleanup would treat them as strays.

    for entry in list_hosted():

        hosted_name = entry["file"]

        files.append(
            f"attachments/{hosted_name}"
        )

        files.extend(
            get_view_support_paths(
                hosted_name
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

    # // hosted attachments stay even though no post uses them
    for entry in list_hosted():

        used_files.add(
            entry["file"]
        )

    # // and so do the helper pages ("<file>.view.html") of whatever stays
    for filename in list(used_files):

        used_files.add(
            filename + VIEW_SUFFIX
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

    generate_404()

    generate_view_page()

    generate_hosted_attachments()

    clean_unused_attachments()

    clean_unused_album_images()

    clean_unused_album_folders()

    clean_empty_folders()

    save_generated_files()


