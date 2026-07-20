import json
import os


DATA_FOLDER = os.path.join(
    os.path.dirname(__file__),
    "..",
    "data"
)



def load_json(filename):

    path = os.path.join(
        DATA_FOLDER,
        filename
    )


    if not os.path.exists(path):

        return {}



    try:

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)



    except json.JSONDecodeError:

        print(
            "Warning: Invalid JSON detected in:",
            filename
        )

        return {}



    except Exception as error:

        print(
            "Error loading JSON:",
            filename,
            error
        )

        return {}





def save_json(filename, data):

    path = os.path.join(
        DATA_FOLDER,
        filename
    )


    try:

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as file:


            json.dump(

                data,

                file,

                indent=4,

                ensure_ascii=False

            )



    except Exception as error:

        print(
            "Error saving JSON:",
            filename,
            error
        )