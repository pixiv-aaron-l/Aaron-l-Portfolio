from tools.json_manager import load_json


# // site_config.json is the one file that holds "who is this website for"
# // type settings, as opposed to the actual content (albums, posts, etc).
# // Everything in here has a safe fallback, so a totally empty or missing
# // site_config.json never breaks anything -- it just falls back to a
# // generic default until someone actually opens the admin and sets it.

DEFAULT_SITE_NAME = "My Portfolio"


def get_site_name():

    """
    Returns the configured site/corner branding name, falling
    back to a generic default if none has been set yet.

    Used both by the website generator (corner text, post
    bylines, etc.) and by the admin UI itself (window title,
    dashboard welcome message), so the whole tool consistently
    reflects whatever name the user has actually chosen, and a
    fresh copy of this project never ships with someone else's
    name hardcoded into it.
    """

    config = load_json(
        "site_config.json"
    )

    site_name = config.get(
        "site_name",
        ""
    ).strip()

    if not site_name:

        site_name = DEFAULT_SITE_NAME

    return site_name


def get_since_year():

    """
    Returns the configured "since <year>" value, or an empty
    string if none has been set. An empty result means the
    "since" text should simply not be displayed at all.
    """

    config = load_json(
        "site_config.json"
    )

    return config.get(
        "since_year",
        ""
    ).strip()
