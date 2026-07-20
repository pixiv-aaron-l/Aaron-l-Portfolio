import os

from PIL import Image



BASE_FOLDER = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)



WEBSITE_FOLDER = os.path.join(
    BASE_FOLDER,
    "website"
)



def get_album_image_folder(album_folder):

    return os.path.join(
        WEBSITE_FOLDER,
        "images",
        "albums",
        album_folder
    )



def create_album_folders(album_folder):

    base = get_album_image_folder(
        album_folder
    )


    folders = [

        base,

        os.path.join(
            base,
            "display"
        ),

        os.path.join(
            base,
            "original"
        )

    ]


    for folder in folders:

        os.makedirs(
            folder,
            exist_ok=True
        )



def create_display_image(source, destination):

    image = Image.open(
        source
    )


    image.thumbnail(
        (
            1200,
            1200
        )
    )


    if image.mode in (
        "RGBA",
        "LA"
    ):

        background = Image.new(
            "RGB",
            image.size,
            (255,255,255)
        )


        background.paste(
            image,
            mask=image.getchannel("A")
        )


        image = background


    elif image.mode != "RGB":

        image = image.convert(
            "RGB"
        )


    image.save(
        destination,
        "JPEG",
        quality=90
    )