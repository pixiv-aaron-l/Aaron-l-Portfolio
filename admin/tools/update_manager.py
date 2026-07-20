from datetime import datetime

from tools.json_manager import load_json, save_json



def update_last_modified():

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