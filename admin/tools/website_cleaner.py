import os





def get_all_files(folder):

    files = []


    if not os.path.exists(folder):

        return files


    for root, dirs, filenames in os.walk(folder):

        for filename in filenames:

            path = os.path.join(
                root,
                filename
            )


            relative = os.path.relpath(
                path,
                folder
            )


            files.append(
                relative.replace(
                    "\\",
                    "/"
                )
            )


    return files





def clean_empty_folders(folder):

    if not os.path.exists(folder):

        return


    for root, dirs, files in os.walk(
        folder,
        topdown=False
    ):

        for directory in dirs:

            path = os.path.join(
                root,
                directory
            )


            if not os.listdir(path):

                os.rmdir(
                    path
                )





def remove_files_not_in_list(
        folder,
        allowed_files
):

    existing_files = get_all_files(
        folder
    )


    allowed_files = set(
        allowed_files
    )


    for file in existing_files:


        if file not in allowed_files:


            path = os.path.join(
                folder,
                file
            )


            if os.path.exists(path):

                os.remove(
                    path
                )


    clean_empty_folders(
        folder
    )