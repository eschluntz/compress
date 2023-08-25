#!/usr/bin/env python

"""
Parses a slack export folder, cleans up the slack messages found for your user
and then exports them into a file in corpus.
"""

import json
import os
import re
from typing import List

USERNAME_TO_EXPORT = "erik"


def extract_slack_msgs(export_root_path : str, username : str) -> List[str]:
    """extract all text from the users messages as a list of strings"""
    file_strs : List[str] = []
    for (dirpath, _, filenames) in os.walk(export_root_path):
        file_strs += [os.path.join(dirpath, file) for file in filenames]

    msgs : List[str] = []
    for file_str in file_strs:
        with open(file_str, encoding="utf8") as file:
            channel = json.load(file)

        for msg in channel:
            try:
                user = msg["user_profile"]["name"]
                text = msg["text"]
            except KeyError:
                # there's some other junk that we don't care about
                continue

            if user == username:
                msgs.append(text)
    return msgs


def clean_slack_msg(text: str) -> str:
    """cleans up a slack msg to do NLP on it."""
    text = re.sub(r"<.*?>", "", text)  # filter slack tags
    text = re.sub(r":\S*:", "", text)  # filter emojis
    text = re.sub(r"'", "", text)  # don't bother with contractions
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)  # get rid of other non text
    text = re.sub(r'\s{2,}', ' ', text)  # compress whitespace
    text = text.strip()
    text = text.lower()
    return text


if __name__ == "__main__":
    slack_export_root = "data/slack_export"
    msgs = extract_slack_msgs(slack_export_root, USERNAME_TO_EXPORT)

    # clean up msgs
    texts = [clean_slack_msg(m) for m in msgs]

    # write each msg as a line to a file
    with open("data/corpus/slack_msgs.txt", 'w', encoding="utf8") as f:
        for text in texts:
            f.write(text + "\n")
