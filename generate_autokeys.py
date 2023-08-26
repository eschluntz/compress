#!/usr/bin/env python

"""
Script to turn the json file of output/shortcuts.yaml into config files for Autokey
"""


import json
import os
import yaml


def make_safe_filename_from_string(s : str) -> str:
    """Make a filename safe for use in a file path.
    https://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename"""
    return "".join(x.lower() for x in s if x.isalnum())


def create_autokey_config_for_shortcut(phrase : str, abbrev : str) -> None:
    """Generate configs for Autokey based on a shortcut from phrase to abbreviation.
    https://github.com/autokey/autokey

    abbrev can be a string, or a comma separated list of abbreviations.

    these files go in ~/.config/autokey/data/My Phrases/

    Each abbrev gets two files, name.txt and .name.json"""

    file_extensions = ["py"]  # add '.' as a word character for any of these abbrevs.
    if abbrev in file_extensions:
        extra_word_chars = r"\."
    else:
        extra_word_chars = ""
    words_regex = rf"[\w\t'{extra_word_chars}\-&\+]"  # what should not trigger a substitution

    result_path = "output/autokey_phrases/"

    filter_regex = "google-chrome.Google-chrome"  # shortcut only in these apps

    # has any capitals in phrase
    has_capitals = any(c.isupper() for c in phrase)

    name = make_safe_filename_from_string(phrase)

    os.makedirs(result_path, exist_ok=True)

    abbrevs = [a.strip() for a in abbrev.split(",")]

    with open(os.path.join(result_path, f"{name}.txt"), 'w', encoding="utf8") as f:
        f.write(phrase)

    with open(os.path.join(result_path, f".{name}.json"), 'w', encoding="utf8") as f:
        config = {
            "usageCount": 0,
            "omitTrigger": False,
            "prompt": False,
            "description": phrase,
            "abbreviation": {
                "wordChars": words_regex,
                "abbreviations": abbrevs,
                "immediate": False,
                "ignoreCase": not has_capitals,
                "backspace": True,
                "triggerInside": False
            },
            "hotkey": {
                "hotKey": None,
                "modifiers": []
            },
            "modes": [
                1
            ],
            "showInTrayMenu": False,
            "matchCase": not has_capitals,
            "filter": {
                "regex": filter_regex,
                "isRecursive": False
            },
            "type": "phrase",
            "sendMode": "kb"
        }
        json.dump(config, f, indent=4)


if __name__ == "__main__":

    with open("output/shortcuts.yaml", 'r', encoding="utf8") as file:
        shortcuts = yaml.load(file, Loader=yaml.FullLoader)

        for phrase, abbrev in shortcuts.items():
            create_autokey_config_for_shortcut(phrase, abbrev)
