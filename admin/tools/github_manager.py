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





def publish_changes(message="Update website"):


    run_git(
        "git add ."
    )


    status = run_git(
        "git status --porcelain"
    )


    if not status.strip():

        return "No changes to publish."



    run_git(
        f'git commit -m "{message}"'
    )


    run_git(
        "git push"
    )


    return "Website published successfully."