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


    # // the whole file is prepared in memory FIRST and written to a
    # // temporary file, and only swapped in once that worked. Writing
    # // straight into the real file meant that an error halfway through
    # // (or the app being closed at the wrong moment) left it cut off and
    # // broken, with the old content gone. Now the old file stays exactly
    # // as it was unless the new one is complete.

    try:

        text = json.dumps(

            data,

            indent=4,

            ensure_ascii=False

        )

        temporary_path = path + ".tmp"

        with open(
            temporary_path,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                text
            )

        os.replace(
            temporary_path,
            path
        )


    except Exception as error:

        print(
            "Error saving JSON:",
            filename,
            error
        )
