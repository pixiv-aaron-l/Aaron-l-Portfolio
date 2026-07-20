import os
import json
import shutil
from datetime import datetime

from tools.json_manager import load_json


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

    about = load_json(
        "about.json"
    )

    date = about.get(
        "last_updated",
        ""
    )


    if not date:

        return ""


    try:

        parsed = datetime.fromisoformat(
            date
        )

        return parsed.strftime(
            "%d/%m/%Y"
        )

    except ValueError:

        pass


    try:

        parsed = datetime.strptime(
            date,
            "%d/%m/%Y"
        )

        return parsed.strftime(
            "%d/%m/%Y"
        )

    except ValueError:

        return date



def generate_index():

    about = load_json(
        "about.json"
    )


    html = read_template(
        "index_template.html"
    )


    html = replace_values(

        html,

        {

            "{{ABOUT_INTRODUCTION}}":
                about.get(
                    "introduction",
                    ""
                ),

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

        cards += f"""

<a class="album-card" href="albums/{album.get('folder','')}.html">

<div class="album-info">

<h2>{album.get('title','')}</h2>

<p>
{album.get('description','')}
</p>

<p class="album-date">
{album.get('date','')}
</p>

<p class="album-count">
{len(album.get('artworks',[]))} artworks
</p>

</div>

<div class="album-cover">

<img src="images/albums/{album.get('folder','')}/display/{album.get('cover','')}">

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
                    album.get(
                        "title",
                        ""
                    ),

                "{{ALBUM_DATE}}":
                    album.get(
                        "date",
                        ""
                    ),

                "{{ALBUM_DESCRIPTION}}":
                    album.get(
                        "description",
                        ""
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

<a class="artwork-card" href="../artworks/{artwork.get('file','')}.html">

<div class="artwork-thumbnail">

<img src="../images/albums/{album.get('folder','')}/display/{artwork.get('display','')}">

</div>


<div class="artwork-info">

<h3>
{artwork.get('title','')}
</h3>


<div class="artwork-info-bottom">

<span class="artwork-number">
#{artwork.get('number','')}
</span>


<span class="artwork-date">
{artwork.get('date','')}
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
                +
                ".html"

            ),

            html

        )





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


            html = replace_values(

                template,

                {

                    "{{ARTWORK_TITLE}}":
                        artwork.get(
                            "title",
                            ""
                        ),

                    "{{ARTWORK_NUMBER}}":
                        artwork.get(
                            "number",
                            ""
                        ),

                    "{{ARTWORK_DATE}}":
                        artwork.get(
                            "date",
                            ""
                        ),

                    "{{ARTWORK_TIME_SPENT}}":
                        artwork.get(
                            "time_spent",
                            ""
                        ),

                    "{{ARTWORK_NOTES}}":
                        artwork.get(
                            "notes",
                            ""
                        ),

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
                    artworks[index - 1]["file"]
                    +
                    ".html"
                )



            if index < len(artworks) - 1:

                next_page = (
                    "../artworks/"
                    +
                    artworks[index + 1]["file"]
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
def generate_attachments(attachments):

    if not attachments:

        return ""


    html = """

<section class="post-files-card">

<h2>Attachments</h2>

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



        html += f"""

<a class="download-button" href="../attachments/{file}">
{name}
</a>

"""


    html += "</section>"


    return html



def format_post_content(content):

    if not content:

        return ""


    lines = content.splitlines()


    html = ""


    paragraph = []


    for line in lines:

        line = line.strip()


        if line:

            paragraph.append(
                line
            )


        else:

            if paragraph:

                html += f"""

<p>
{" ".join(paragraph)}
</p>

"""

                paragraph = []



    if paragraph:

        html += f"""

<p>
{" ".join(paragraph)}
</p>

"""


    return html






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

<a class="post-card" href="posts/{post.get('file','')}.html">

<h2>{post.get('title','')}</h2>

<p>{post.get('date','')}</p>

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

                    post.get(
                        "title",
                        ""
                    ),



                "{{POST_DATE}}":

                    post.get(
                        "date",
                        ""
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





def get_generated_files():

    files = [

        "index.html",

        "arts.html",

        "posts.html"

    ]


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


    return list(set(files))
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


            path = os.path.join(
                WEBSITE_FOLDER,
                old_file
            )


            if os.path.isfile(path):

                os.remove(path)





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







def clean_empty_folders():

    for root, dirs, files in os.walk(
        WEBSITE_FOLDER,
        topdown=False
    ):


        if root == WEBSITE_FOLDER:

            continue


        if not dirs and not files:

            try:

                os.rmdir(root)

            except OSError:

                pass







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

            indent=4

        )







def generate_website():

    generate_index()

    generate_arts()

    generate_albums()

    generate_artworks()

    generate_posts()



    clean_generated_website()

    clean_unused_attachments()

    clean_unused_album_images()

    clean_unused_album_folders()

    clean_empty_folders()



    save_generated_files()