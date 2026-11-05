import os

from urllib.parse import quote

from tools.json_manager import load_json, save_json
from tools.github_manager import PROJECT_FOLDER, get_github_identity, run_git
from tools.unique_names import copy_unique
from tools.view_types import get_view_kind


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


def add_hosted(source_path):

    if not os.path.isfile(
        source_path
    ):

        raise HostedAttachmentsError(
            "That file couldn't be found."
        )

    # // keeps the file's own name when it's free. If anything already
    # // uses it (another hosted file, a post's attachment, a file already
    # // in the folder) it becomes name2, name3... (re-checked in a loop)
    # // and that final name is what gets remembered.

    try:

        filename = copy_unique(
            source_path,
            ATTACHMENTS_FOLDER,
            get_hosted_filenames() | get_post_filenames()
        )

    except OSError as error:

        raise HostedAttachmentsError(
            f"Couldn't copy that file:\n{error}"
        )

    if filename in get_hosted_filenames():

        # // picked a file that's already hosted (from inside the folder)
        return {

            "name": filename,

            "file": filename

        }

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
    The link to share. For files a browser can show it's the site's
    full-page viewer, for anything else (zip, 7z, ...) it's the file
    itself. Built from the real git remote (same automatic detection the
    rest of the project uses), so there's nothing to type in. Returns ""
    if no remote is set up yet.
    """

    owner, repository, branch = get_github_identity()

    if repository.lower().endswith(
        ".github.io"
    ):

        base = f"https://{repository.lower()}/"

    elif owner and repository:

        base = f"https://{owner.lower()}.github.io/{repository}/"

    else:

        return ""

    filename = entry["file"]

    encoded = quote(
        filename,
        safe=""
    )

    if get_view_kind(
        filename
    ):

        return f"{base}view.html?f={encoded}"

    # // nothing to show in a browser: link straight to the file.
    # // Big archives are stored with git lfs, which the site itself can't
    # // serve, so they use the same github address as the Download
    # // buttons do.

    if filename.lower().endswith(
        (".zip", ".7z")
    ):

        return (
            "https://media.githubusercontent.com/media/"
            f"{owner}/{repository}/{branch}/website/attachments/{encoded}"
        )

    return f"{base}attachments/{encoded}"


def is_live(entry):

    """
    Is this file already on the website, so its web link works? A file is
    live once it's committed AND pushed. Used only to tell the person
    whether the link they just copied works yet, never to block anything.
    Returns False when it isn't (or when git can't tell).
    """

    path = f"website/attachments/{entry['file']}"

    try:

        run_git(
            f'git ls-files --error-unmatch -- "{path}"'
        )

        if run_git(
            f'git status --porcelain -- "{path}"'
        ).strip():

            return False

        try:

            ahead = int(
                run_git(
                    "git rev-list --count @{upstream}..HEAD"
                ).strip()
            )

        except Exception:

            # // no upstream branch set yet: can't tell, assume pushed
            ahead = 0

        return ahead == 0

    except Exception:

        return False
