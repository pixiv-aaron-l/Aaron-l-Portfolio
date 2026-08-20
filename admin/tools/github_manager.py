import subprocess
import os


BASE_FOLDER = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


PROJECT_FOLDER = os.path.dirname(
    BASE_FOLDER
)


def run_git(command):

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

    # Make sure Git LFS is installed.
    run_git(
        "git lfs install"
    )


    # Stage everything, including ZIP files.
    run_git(
        "git add ."
    )


    status = run_git(
        "git status --porcelain"
    )


    if not status.strip():

        return (
            "No changes to publish."
        )


    # Commit normal files and LFS pointers.
    run_git(
        f'git commit -m "{message}"'
    )


    # Push the Git commit.
    run_git(
        "git push"
    )


    # Explicitly push the actual LFS objects.
    run_git(
        "git lfs push origin --all"
    )


    return (
        "Website published successfully."
    )