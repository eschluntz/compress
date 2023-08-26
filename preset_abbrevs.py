#!/usr/bin/env python

"""
Abbrevs you definitely want in your set.
you can set None if you want to pick one automatically
you're responsible for creating any plurals here
"""


PRESET_ABBREVS = {
#     "right now": "rn",
#     "again": "ag",
#     "actually": "ac",
#     "anything": "ay",
#     "every": "e",
#     "everyone": "en",
#     "everything": "et",
#     "some": "s",
#     "someone": "sn",
#     "something": "st",
#     "hardware": "hw",
#     "software": "sw",
#     "without": "wo",
#     "maybe": "mb",
#     "question": "q",
#     "questions": "qs",
#     "meeting": "mtg",
#     "meetings": "mtgs",
#     "very": "v",
#     "fix": "x",
#     "if i remember correctly": "iirc",
#     "let me know": "lmk",
#     "definitely": "def",
#     "I'll keep you posted": "ikyp",
#     """Best,
# - Erik""": "bst",
#     "calendar invite": "cali",
#     "screenshot": "sc",
#     "Can you post a screenshot?": "csc",
}

# these will not be used as abbrevs
BLACKLIST = set([
    "a", "i", "it", "an", "int", "so",
    "is", "re", "we", "the", "in", "as",
    "no", "ie", "eg", "me", "be", "at", "do",
    "talk", "to",
])
