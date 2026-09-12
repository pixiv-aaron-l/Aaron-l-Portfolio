import os

from PIL import Image


# // every album gets its own image folder under
# // website/images/albums/<album folder>/, split into "original"
# // (whatever you uploaded, untouched) and "display" (the resized
# // JPEG actually used on the website).

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

    # // this is what turns whatever image format you uploaded into
    # // a consistent, web-sized JPEG. 1200x1200 and quality=90 are
    # // just reasonable defaults for a display image on this site --
    # // big enough to look sharp, small enough to load fast. Nothing
    # // personal to any one user in these numbers, so they're left
    # // as plain constants here rather than pushed into config.

    image = Image.open(
        source
    )


    image.thumbnail(
        (
            1200,
            1200
        )
    )


    # // PNGs (and some other formats) can have transparency, but
    # // JPEG can't -- so any transparent area gets flattened onto a
    # // plain white background before saving, instead of coming out
    # // as random garbage colors.

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
