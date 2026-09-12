import json
import os


# // every JSON data file (about.json, albums.json, posts.json,
# // site_config.json, etc) lives in admin/data/. This is the one
# // place that knows that, so nothing else in the project has to
# // hardcode that path.

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


    # // a missing file (fresh project, or a brand new file like
    # // site_config.json before anyone's saved anything yet) is
    # // completely normal -- just hand back an empty dict rather
    # // than crashing. Every caller already reads from this with
    # // .get(...) and a sensible default, so an empty dict here is
    # // a safe starting point either way.

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

        # // someone hand-edited the file and broke the JSON syntax,
        # // or it got cut off mid-write somehow -- don't take the
        # // whole admin app down over it, just warn and carry on as
        # // if the file were empty.

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


            # // indent=4 so the file stays readable if you ever open
            # // it by hand. ensure_ascii=False keeps accented
            # // letters, curly quotes, etc. written as actual
            # // characters instead of \uXXXX escape codes.

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
