import os
import shutil

from urllib.parse import quote

from tools.json_manager import load_json, save_json
from tools.github_manager import PROJECT_FOLDER, get_github_identity


# // "hosted attachments" are just normal attachments that don't belong
# // to any post: the file goes in website/attachments/ with its normal
# // name, and its name is remembered in admin/data/hosted_attachments.json
# // so the generator knows to keep it. Nothing links to it from the
# // site, you share its web link yourself (see get_web_link).


DATA_FILE = "hosted_attachments.json"

ATTACHMENTS_FOLDER = os.path.join(
    PROJECT_FOLDER,
    "website",
    "attachments"
)

# // the generator may create "<file>.view.html" next to an attachment
# // (for zip / 7z / mht / ... that a browser can't show as is). Same
# // suffix the generator uses, kept here so deleting a hosted file can
# // clean that helper page up too.
VIEW_SUFFIX = ".view.html"


class HostedAttachmentsError(Exception):

    """A problem worth showing to the person using the admin as is."""


def list_hosted():

    data = load_json(
        DATA_FILE
    )

    return [
        entry
        for entry in data.get(
            "files",
            []
        )
        if isinstance(entry, dict) and entry.get("file")
    ]


def get_hosted_filenames():

    return {
        entry["file"]
        for entry in list_hosted()
    }


def get_post_filenames():

    # // every file name some post already uses as an attachment

    names = set()

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

                name = attachment.get(
                    "file",
                    ""
                )

            else:

                name = attachment

            if name:

                names.add(
                    name
                )

    return names


def make_unique_filename(name):

    # // keep the normal name whenever possible. If something already
    # // uses it (another hosted file, a post's attachment, or any file
    # // already sitting in the attachments folder), add a number:
    # // report.pdf -> report2.pdf -> report3.pdf

    taken = get_hosted_filenames() | get_post_filenames()

    if os.path.isdir(
        ATTACHMENTS_FOLDER
    ):

        taken |= set(
            os.listdir(
                ATTACHMENTS_FOLDER
            )
        )

    if name not in taken:

        return name

    stem, extension = os.path.splitext(
        name
    )

    counter = 2

    while f"{stem}{counter}{extension}" in taken:

        counter += 1

    return f"{stem}{counter}{extension}"


def add_hosted(source_path):

    if not os.path.isfile(
        source_path
    ):

        raise HostedAttachmentsError(
            "That file couldn't be found."
        )

    filename = make_unique_filename(
        os.path.basename(
            source_path
        )
    )

    os.makedirs(
        ATTACHMENTS_FOLDER,
        exist_ok=True
    )

    shutil.copy(
        source_path,
        os.path.join(
            ATTACHMENTS_FOLDER,
            filename
        )
    )

    data = load_json(
        DATA_FILE
    )

    files = data.get(
        "files",
        []
    )

    entry = {

        "name": filename,

        "file": filename

    }

    files.append(
        entry
    )

    save_json(
        DATA_FILE,
        {
            "files": files
        }
    )

    return entry


def delete_hosted(filename):

    data = load_json(
        DATA_FILE
    )

    files = [
        entry
        for entry in data.get(
            "files",
            []
        )
        if not (isinstance(entry, dict) and entry.get("file") == filename)
    ]

    save_json(
        DATA_FILE,
        {
            "files": files
        }
    )

    # // if a post happens to use the very same file, it must stay.
    if filename in get_post_filenames():

        return

    # // file names come from our own json, but never trust them to
    # // build a path to delete: only plain names inside the folder.
    if (
        not filename
        or filename != os.path.basename(filename)
    ):

        raise HostedAttachmentsError(
            "That file name doesn't look right, nothing was deleted."
        )

    for name in (
        filename,
        filename + VIEW_SUFFIX
    ):

        path = os.path.join(
            ATTACHMENTS_FOLDER,
            name
        )

        if os.path.isfile(
            path
        ):

            os.remove(
                path
            )


def get_web_link(entry):

    """
    The link to share: the site's full-page viewer showing this
    file. Built from the real git remote (same automatic detection
    the rest of the project uses), so there's nothing to type in.
    Returns "" if no remote is set up yet.
    """

    owner, repository, _ = get_github_identity()

    if repository.lower().endswith(
        ".github.io"
    ):

        base = f"https://{repository.lower()}/"

    elif owner and repository:

        base = f"https://{owner.lower()}.github.io/{repository}/"

    else:

        return ""

    return (
        f"{base}view.html?f="
        f"{quote(entry['file'], safe='')}"
    )
