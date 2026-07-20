import os
import shutil



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


    return filename