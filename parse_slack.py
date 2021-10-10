import json
import os
import re
from typing import List, Set, Dict, Optional
from collections import Counter, namedtuple
import nltk
from nltk.util import ngrams

Shortcut = namedtuple("Shortcut", ["phrase", "abbrev", "score", "count", "len"])


def extract_slack_msgs(export_root_path : str, username : str) -> List[str]:
    """extract all text from the users messages as a list of strings"""
    file_strs : List[str] = []
    for (dirpath, dirnames, filenames) in os.walk(export_root_path):
        file_strs += [os.path.join(dirpath, file) for file in filenames]

    msgs : List[str] = []
    for file_str in file_strs:
        with open(file_str) as file:
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


def get_blacklist() -> Set[str]:
    """Create set of words that can't be used for abreviations"""
    all_words = set([
        "a", "i", "it", "an", "int", "so",
        "is", "re", "we", "the", "in", "as",
        "no", "ie", "eg", "me",
    ])
    return all_words


def get_preset_abbrevs() -> Dict[str, str]:
    """List of hardcoded abbreviations I want to use"""

    return {
        "and": "n",
        "actually": "ac",
        "think": "tk",
        "about": "ab",
        "wifibox": "wb",
        "wifiboxes": "wbs",
        "hardware": "hw",
        "software": "sw"
    }


def get_possible_abbrevs(phrase: str) -> List[str]:
    """Get possible short abbreviations for a phrase, in order of preference"""
    words = phrase.split()
    out: List[str] = []

    if len(words) > 1:
        out.append("".join([w[0] for w in words]))  # acryonym
        out.append(words[0][0] + words[1][0])
        out.append(words[0][:2] + words[1][0])

    phrase = phrase.replace(" ", "")

    out += [
        phrase[0],
        phrase[0] + phrase[-1],
        phrase[:2],
        phrase[1],
        phrase[-1],
        phrase[1],
        phrase[:3],
        phrase[:2] + phrase[-1],
        phrase[0] + phrase[-2:],
        phrase[:4],
        phrase[:2] + phrase[-2:]
    ]

    return out


def match_to_prev_abbrevs(shortcuts: Dict[str, str], phrase) -> Optional[str]:
    """We want abbrevs to be consistent with each other with
    compositions of other abbrevs, and plurals.
    i.e: robot -> r, and robots -> rs.
    i.e. the -> t, robot -> r, the robot -> tr"""

    # plurals
    if phrase[-1] == "s" and phrase[:-1] in shortcuts:
        return shortcuts[phrase[:-1]] + "s"

    # composite
    words = phrase.split()
    if len(words) > 1:
        if all(word in shortcuts for word in words):
            return "".join([shortcuts[word] for word in words])

    return None


def match_abbrevs_to_phrases(results: List[tuple]) -> Dict[str, str]:
    """Find the best abbreviation for each phrase"""
    # auto suggest abbreviations
    word_set = get_blacklist()
    shortcuts = get_preset_abbrevs()
    for _, v in shortcuts.items():
        word_set.add(v)

    results = sorted(results, key=lambda x: -x[0])

    # greedy approach
    print("Score\tCount\tPhrase\tAbbrev")
    index = 0
    for row in results:
        index += 1
        score = row[0]
        phrase = row[1]
        count = row[3]
        posssible_abbrevs = get_possible_abbrevs(phrase)

        # see if it matches previous abbrevs for consistency
        prev_abbrev = match_to_prev_abbrevs(shortcuts, phrase)
        if prev_abbrev is not None:
            posssible_abbrevs.insert(0, prev_abbrev)

        # see if in preset list
        if phrase in shortcuts:
            abbrev = shortcuts[phrase]
            print(f"{index}\t{score}\t{count}\t{phrase:20}:\t{abbrev}")
            continue

        # pick best suggested
        for abbrev in posssible_abbrevs:
            if abbrev not in word_set and len(abbrev) < len(phrase):
                print(f"{index}\t{score}\t{count}\t{phrase:20}:\t{abbrev}")
                word_set.add(abbrev)
                shortcuts[phrase] = abbrev
                break
        else:
            print(f"{score}\t{count}\t{phrase:20}:\t________")
    return shortcuts


# def create_config_for_abbrev()


if __name__ == "__main__":
    export_root = "data/slack_export"
    msgs = extract_slack_msgs(export_root, "erik")

    # clean up msgs
    texts = [clean_slack_msg(m) for m in msgs]

    # count N grams of several different Ns
    all_counts = Counter()
    for text in texts:
        tokenized = text.split()
        for n in range(1, 7):
            gram = ngrams(tokenized, n)
            all_counts.update(Counter(gram))

    # score counts
    results : List[Shortcut] = []
    for k, count in all_counts.items():
        if count <= 3:  # don't count rare but super long phrases
            continue
        phrase = " ".join(k)
        phrase_len = len(phrase)
        avg_shortcut_len = 2
        score = (phrase_len - avg_shortcut_len) * count  # how many chars will be saved
        results.append((score, phrase, phrase_len, count))

    n_to_keep = 200
    results = sorted(results, reverse=True)
    results = results[:n_to_keep]

    shortcuts = match_abbrevs_to_phrases(results)
