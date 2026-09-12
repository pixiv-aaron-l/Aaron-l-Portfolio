import os
import shutil


# // handles copying downloadable attachment files into a post's own
# // folder under website/files/posts/<post name>/. Small/normal files
# // only -- the big .zip/.7z LFS handling lives over in
# // website_generator.py's get_attachment_url(), this file doesn't
# // need to know anything about that.

BASE_FOLDER = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


WEBSITE_FOLDER = os.path.join(
    BASE_FOLDER,
    "website"
)



def get_post_file_folder(post_name):

    return os.path.join(

        WEBSITE_FOLDER,

        "files",

        "posts",

        post_name

    )



def create_post_folder(post_name):

    folder = get_post_file_folder(
        post_name
    )


    # // exist_ok=True so calling this again for a post that already
    # // has a folder is a harmless no-op instead of an error.

    os.makedirs(
        folder,
        exist_ok=True
    )


    return folder



def copy_file_to_post(
    source,
    post_name
):

    folder = create_post_folder(
        post_name
    )


    filename = os.path.basename(
        source
    )


    destination = os.path.join(
        folder,
        filename
    )


    shutil.copy(
        source,
        destination
    )


    # // handing back just the filename (not the full path) since
    # // that's what actually gets stored in posts.json -- the post
    # // name itself already tells you which folder it's in.

    return filename
