from datetime import datetime

from tools.json_manager import load_json, save_json


def update_last_modified():

    # // stamps about.json with today's date, shown in the footer of
    # // every generated page ("Last updated: ..."). Called whenever
    # // the About page gets saved.
    #
    # // format is day/month/year (French-style date order), not the
    # // US month/day/year -- just a personal formatting preference,
    # // easy to flip if you'd rather have it the other way round.

    data = load_json(
        "about.json"
    )


    data["last_updated"] = datetime.now().strftime(
        "%d/%m/%Y"
    )


    save_json(
        "about.json",
        data
    )
