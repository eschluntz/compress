import json
import yaml
import os


def make_safe_filename_from_string(s : str) -> str:
    """Make a filename safe for use in a file path.
    https://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename"""
    return "".join(x.lower() for x in s if x.isalnum())


def create_autokey_config_for_abbrev(phrase : str, abbrev : str) -> None:
    """Generate configs for Autokey based on an abbreviation.
    https://github.com/autokey/autokey

    these files go in ~/.config/autokey/data/My Phrases/

    Each abbrev gets two files, name.txt and .name.json"""

    result_path = "output/autokey_phrases/"
    filter_regex = "google-chrome.Google-chrome"  # shortcut only in these apps
    words_regex = "[\\w\\t'-]"  # what should not trigger a substitution

    # has any capitals in phrase
    has_capitals = any(c.isupper() for c in phrase)

    name = make_safe_filename_from_string(phrase)

    os.makedirs(result_path, exist_ok=True)

    with open(result_path + f"{name}.txt", 'w') as f:
        f.write(phrase)

    with open(result_path + f".{name}.json", 'w') as f:
        config = {
            "usageCount": 0,
            "omitTrigger": False,
            "prompt": False,
            "description": phrase,
            "abbreviation": {
                "wordChars": words_regex,
                "abbreviations": [
                    abbrev
                ],
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
    shortcuts = yaml.load(open("output/shortcuts.yaml", 'r'))

    for phrase, abbrev in shortcuts.items():
        create_autokey_config_for_abbrev(phrase, abbrev)
