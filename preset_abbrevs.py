#!/usr/bin/env python

"""
Abbrevs you definitely want in your set.
you can set None if you want to pick one automatically
you're responsible for creating any plurals here
"""


PRESET_ABBREVS = {
    "right now": "rn",
    "ansible": "ans",
    "again": "ag",
    "actually": "ac",
    "anything": "ay",
    "elevator": "el",
    "elevators": "els",
    "every": "e",
    "everyone": "en",
    "everything": "et",
    "some": "s",
    "someone": "sn",
    "something": "st",
    "wifibox": "wb",
    "wifiboxes": "wbs",
    "top board": "tb",
    "top boards": "tbs",
    "bottom board": "bb",
    "bottom boards": "bbs",
    "hardware": "hw",
    "software": "sw",
    "without": "wo",
    "maybe": "mb",
    "question": "q",
    "questions": "qs",
    "meeting": "mtg",
    "meetings": "mtgs",
    "very": "v",
    "fix": "x",
    "fixes": "xs",
    "localization": "z",
    "if i remember correctly": "iirc",
    "let me know": "lmk",
    "definitely": "def",
    "erik@cobaltrobotics.com": "e@c",
    "eschluntz@gmail.com": "e@g",
    "I'll keep you posted": "ikyp",
    "Anything else I can help with?": "ayel",
    """Best,
- Erik""": "bst",
    "You can pick a time for us to chat here: https://calendly.com/eschluntz/30min": "cal30",
    "You can pick a time for us to chat here: https://calendly.com/eschluntz/45min": "cal45",
    "You can pick a time for us to chat here: https://calendly.com/eschluntz/60min": "cal60",
    "calendar invite": "cali",
    "screenshot": "sc",
    "Can you post a screenshot?": "csc",
}

# these will not be used as abbrevs
BLACKLIST = set([
    "a", "i", "it", "an", "int", "so",
    "is", "re", "we", "the", "in", "as",
    "no", "ie", "eg", "me", "be", "at", "do",
    "talk", "to",
])
