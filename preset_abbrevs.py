#!/usr/bin/env python

"""
Abbrevs you definitely want in your set.
Use this list to protect abbreviations that the algorithm 
may assign to other words, or more common abbreviations that deviate
from the algorithm, ie bc -> because.

Use the blacklist to block assignments that you type frequently but aren't words.
"""


PRESET_ABBREVS = {
    "and I": "ni",
    "again": "ag",
    "actually": "ac",
    "anything": "ay",

    "every": "e",
    "everyone": "en",
    "everything": "et",

    "some": "s",
    "someone": "sn",
    "something": "st",

    "hardware": "hw",
    "software": "sw",

    "with": "w",
    "without": "wo",

    "week": "wk",
    "what": "wt",
    "whatever": "wte",
    "when": "wn",
    "whenever": "wne",
    "where": "wr",
    "wherever": "wre",
    "which": "wh",
    "whichever": "whe",

    "maybe": "mb",
    "question": "q",
    "questions": "qs",
    "meeting": "mtg",
    "meetings": "mtgs",
    "very": "v",
    "fix": "x",
    "if I remember correctly": "iirc",
    "let me know": "lmk",
    "definitely": "def",
    "I'll keep you posted": "ikyp",
    "calendar invite": "cali",
    "screenshot": "sc",
    "Can you post a screenshot?": "csc",
}

# these will not be used as abbrevs.
# TODO: these could be taken directly from the corpus
BLACKLIST = set([
    "a", "ai", "alt", "i", "id", "it", "an", "int", "so",
    "is", "re", "we", "the", "in", "as",
    "no", "ie", "eg", "me", "be", "at", "do",
    "talk", "to",
])
