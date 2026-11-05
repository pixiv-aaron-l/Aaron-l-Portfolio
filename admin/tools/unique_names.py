import os
import shutil


# // this is the one place that decides "what should this file be called"
# // whenever the admin is about to put a file into the project (post
# // images, attachments, hosted attachments, artwork images).
# //
# // the old behaviour was a plain copy, so a file with the same name as
# // one already in the folder silently replaced it. Now the name is
# // checked FIRST: if it's taken it becomes name2, then that is checked
# // again (loop), then name3, ... until it's free. Whoever called gets
# // the final name back and must use THAT one everywhere (the post text,
# // the attachment list, the artwork fields), never the original one.


def make_candidate(stem, counter):

    # // report -> report2, but report2 -> report2-2 so it can't be
    # // confused with a file that really is called "report22".

    if counter == 1:

        return stem

    if stem and stem[-1].isdigit():

        return f"{stem}-{counter}"

    return f"{stem}{counter}"


def load_names(folder):

    # // lower case on purpose: Windows treats Photo.PNG and photo.png as
    # // the same file, so "is this name taken" has to ignore case too or
    # // one would still overwrite the other.

    if not os.path.isdir(folder):

        return set()

    return {
        name.lower()
        for name in os.listdir(folder)
    }


def find_free_stem(stem, slots, extra_taken=()):

    """
    Returns the first stem (stem, stem2, stem3, ...) for which NONE of
    the slots is taken. A slot is (folder, extension): the file
    stem + extension must not exist in that folder.

    Several slots are for things saved under two names at once, like an
    artwork's original (a.png in original/) and display image (a.jpg in
    display/): both names have to be free for the same number.
    """

    listings = [
        (extension, load_names(folder))
        for folder, extension in slots
    ]

    extra = {
        name.lower()
        for name in extra_taken
    }

    counter = 1

    while True:

        candidate = make_candidate(
            stem,
            counter
        )

        taken = any(

            (candidate + extension).lower() in names
            or (candidate + extension).lower() in extra

            for extension, names in listings

        )

        if not taken:

            return candidate

        counter += 1


def find_free_name(name, folder, extra_taken=()):

    """
    The name to use for a file called `name` that is about to go into
    `folder`. `extra_taken` = other names that must not be reused even
    though they aren't on disk (names already written in a post, ...).
    """

    stem, extension = os.path.splitext(
        name
    )

    return find_free_stem(
        stem,
        [(folder, extension)],
        extra_taken
    ) + extension


def copy_unique(source, folder, extra_taken=()):

    """
    Copies `source` into `folder` without ever replacing anything and
    returns the name it ended up with. If the file is already sitting in
    that folder (picked from inside it) nothing is copied and its own
    name is returned.
    """

    os.makedirs(
        folder,
        exist_ok=True
    )

    name = os.path.basename(
        source
    )

    source_folder = os.path.normcase(
        os.path.abspath(
            os.path.dirname(source)
        )
    )

    if source_folder == os.path.normcase(
        os.path.abspath(folder)
    ):

        return name

    final_name = find_free_name(
        name,
        folder,
        extra_taken
    )

    shutil.copy2(
        source,
        os.path.join(
            folder,
            final_name
        )
    )

    return final_name
