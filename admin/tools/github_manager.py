import subprocess
import os
import re


# // BASE_FOLDER is admin/, PROJECT_FOLDER is the repo root one level up
# // (the folder that actually contains .git). Every git command below
# // runs with that as its working directory, same as if you'd cd'd
# // there yourself in a terminal.

BASE_FOLDER = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


PROJECT_FOLDER = os.path.dirname(
    BASE_FOLDER
)


def run_git(command):

    # // tiny wrapper so every git call in this file goes through one
    # // place. If git fails (bad command, no repo, whatever), this
    # // turns that into a normal Python exception instead of silently
    # // returning nothing, so callers can just try/except it.

    result = subprocess.run(

        command,

        cwd=PROJECT_FOLDER,

        shell=True,

        capture_output=True,

        text=True

    )

    if result.returncode != 0:

        raise Exception(
            result.stderr
        )

    return result.stdout


def publish_changes(
    message="Update website"
):

    # // Make sure Git LFS is installed. -- cheap to run every time,
    # // and saves someone from a confusing failure later if they
    # // forgot this step when first setting up.
    run_git(
        "git lfs install"
    )


    # // stage everything, including the big .zip/.7z files -- LFS
    # // hooks into git add automatically once "git lfs install" and
    # // .gitattributes have done their job, so this is just a normal
    # // add.
    run_git(
        "git add ."
    )


    status = run_git(
        "git status --porcelain"
    )


    if not status.strip():

        # // nothing staged means nothing changed since the last
        # // publish -- bail out instead of creating an empty commit.
        return (
            "No changes to publish."
        )


    # // commits both normal files and the LFS pointer files in one go.
    run_git(
        f'git commit -m "{message}"'
    )


    # // push the actual commit first...
    run_git(
        "git push"
    )


    # // ...then explicitly push the LFS objects themselves. A plain
    # // "git push" only sends the small pointer files, not the real
    # // binary content, so this second push is what actually gets the
    # // .zip/.7z bytes up to GitHub.
    run_git(
        "git lfs push origin --all"
    )


    return (
        "Website published successfully."
    )


# ============================================================
# AUTOMATIC GITHUB IDENTITY DETECTION
#
# This project's owner/repository/branch used to be hardcoded
# constants in the generator, then briefly became a manual
# admin settings field -- neither is right, since this project
# is already a git repository connected to GitHub (that's how
# publishing works). This reads it straight from the actual
# git configuration instead, so forking/reusing this project
# never needs any code edit OR any manual data entry: cloning
# the repo and setting a normal git remote is the only setup
# step, and that's something anyone using git already has to
# do regardless of this tool.
# ============================================================

_cached_identity = None


def parse_owner_and_repository(remote_url):

    """
    Extracts (owner, repository) from a GitHub remote URL,
    handling both common formats:

        https://github.com/owner/repository.git
        git@github.com:owner/repository.git
    """

    url = remote_url.strip()

    if url.endswith(".git"):

        url = url[:-4]

    match = re.search(
        r"github\.com[:/]([^/]+)/([^/]+)$",
        url
    )

    if not match:

        return "", ""

    return match.group(1), match.group(2)


def get_github_identity():

    """
    Returns (owner, repository, branch), read from the actual
    git repository this project lives in, and cached for the
    rest of this app session (repeated git subprocess calls
    during a single website generation would otherwise add up).

    Falls back to empty owner/repository and branch "main" if
    git isn't available or no remote is configured yet, rather
    than raising, so a brand-new clone that hasn't set a remote
    yet doesn't crash website generation -- attachment/LFS URLs
    and the 404 base path just won't be correct until a remote
    is added.
    """

    global _cached_identity

    # // once we've successfully looked this up once, there's no
    # // reason to keep re-running git commands for the rest of this
    # // app session -- the remote isn't going to change mid-session.
    if _cached_identity is not None:

        return _cached_identity

    owner = ""

    repository = ""

    branch = "main"

    try:

        remote_url = run_git(
            "git config --get remote.origin.url"
        ).strip()

        owner, repository = parse_owner_and_repository(
            remote_url
        )

        detected_branch = run_git(
            "git rev-parse --abbrev-ref HEAD"
        ).strip()

        if detected_branch:

            branch = detected_branch

    except Exception:

        # // no remote set up yet, git not installed, whatever the
        # // reason -- just fall back to the empty/"main" defaults
        # // above rather than blowing up website generation over it.
        pass

    _cached_identity = (owner, repository, branch)

    return _cached_identity
