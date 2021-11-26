import json
import os
from typing import List, Dict, Optional, Tuple
from collections import Counter, namedtuple
import nltk
from nltk.util import ngrams
from preset_abbrevs import PRESET_ABBREVS, BLACKLIST


Shortcut = namedtuple("Shortcut", ["phrase", "abbrev", "score", "count", "len"])


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


def try_plural_of_word(word : str) -> str:
    """Find the plural of a word"""
    if word[-1] == "s":
        return None
    if word[-1] == "y":
        return word[:-1] + "ies"
    if word[-1] == "f":
        return word[:-1] + "ves"
    if word[-1] == "o":
        return word + "es"
    if word[-1] == "h":
        return word[:-1] + "es"
    if word[-1] == "x":
        return word[:-1] + "es"
    if word[-1] == "z":
        return word[:-1] + "zes"
    return word + "s"


def check_if_real_word(word : str) -> bool:
    """Use nltk to find if input is a word"""
    if word in ["robots", "problems"]:  # wtf nltk?
        return True
    elif word in ["abouts"]:
        return False
    return word in nltk.corpus.words.words()


def get_plural(word : str) -> Optional[str]:
    candidate = try_plural_of_word(word)
    if check_if_real_word(candidate):
        return candidate
    else:
        return None


def get_singular(word : str) -> Optional[str]:
    candidate = word[:-1]
    if check_if_real_word(candidate):
        return candidate
    else:
        return None


def is_plural(word : str) -> bool:
    """Check if word is plural"""
    return word[-1] == "s" and word[:-1] in nltk.corpus.words.words()


def match_abbrevs_to_phrases(results: List[tuple]) -> Dict[str, str]:
    """Find the best abbreviation for each phrase.
    Returns a dict of phrase -> abbrev, i.e. {'because': 'bc'}.

    1. start with highest scoring single words
    2. Create abbrev for each one.
    3. create single / plural duplicate as well
    4. go through multi-word phrases and use single word components
    5. if any multi-word phrases overlap, use whichever had the higher score

    the idea here is to end up with sets that are composable:
    the -> t,
    robot -> r,
    robots -> rs,
    the robots -> trs
    """
    # start with the presets
    abbrev_set = BLACKLIST
    shortcuts = PRESET_ABBREVS
    for k, v in shortcuts.items():
        abbrev_set.add(v)
        # print(f"{k:20}:\t{v}")

    # single words first
    for row in results:
        phrase = row[1]
        if " " in phrase:
            continue

        # create singular and plural versions
        # singular is ALWAYS set, but plural is only sometimes
        # defintion of plural is that there exists a singular version
        # ie "the" is singular without a plural
        if is_plural(phrase):
            plural = phrase
            singular = get_singular(phrase)
        else:
            singular = phrase
            plural = get_plural(phrase)

        # anything in the presets already just don't touch
        if singular in shortcuts:
            continue

        posssible_abbrevs = get_possible_abbrevs(singular)
        for abbrev in posssible_abbrevs:  # ordered best to worst
            if abbrev not in abbrev_set and len(abbrev) < len(singular) - 1:
                # print(f"{singular:20}:\t{abbrev}")
                abbrev_set.add(abbrev)
                shortcuts[singular] = abbrev

                # add plural
                if plural is not None:
                    abbrev2 = abbrev + "s"
                    if abbrev2 not in abbrev_set and len(abbrev2) < len(plural) - 1:
                        abbrev_set.add(abbrev)
                        shortcuts[plural] = abbrev2
                        # print(f"{plural:20}:\t{abbrev2}")
                    else:
                        print(f"warning, blocked {plural} as {abbrev2}")
                break
        else:
            print(f"warning, no abbrev for {singular}")

    print("===============================")
    # now handle multi-word shortcuts
    for row in results:
        phrase = row[1]
        if " " not in phrase:
            continue

        # anything in the presets already just don't touch
        if phrase in shortcuts:
            continue

        # construct from other words
        words = phrase.split()
        abbrev = ""
        for word in words:
            abbrev += shortcuts.get(word, word[0])

        if abbrev not in abbrev_set:
            # print(f"{phrase:20}:\t{abbrev}")
            abbrev_set.add(abbrev)
            shortcuts[phrase] = abbrev
        else:
            this_score = row[0]

            # find who has this abbrev, and it's score
            # TODO could clean this up by storing a reverse data structure
            for other_phrase, other_abbrev in shortcuts.items():
                if other_abbrev == abbrev:

                    # now look up the score
                    for row2 in results:
                        if row2[1] == other_phrase:
                            other_score = row2[0]

                            # compare the scores to overwrite
                            if this_score > other_score:
                                # print(f">>>>>>>overwriting: {phrase}:{abbrev} for {this_score} taken by {k} with {other_score}")
                                shortcuts[phrase] = abbrev
                            break
                    break

    return shortcuts


def create_autokey_config_for_abbrev(phrase : str, abbrev : str) -> None:
    """Generate configs for Autokey based on an abbreviation.
    https://github.com/autokey/autokey

    these files go in ~/.config/autokey/data/My Phrases/

    Each abbrev gets two files, name.txt and .name.json"""

    result_path = "output/autokey_phrases/"
    filter_regex = "google-chrome.Google-chrome"  # shortcut only in these apps

    with open(result_path + f"{phrase}.txt", 'w') as f:
        f.write(phrase)

    with open(result_path + f".{phrase}.json", 'w') as f:
        config = {
            "usageCount": 0,
            "omitTrigger": False,
            "prompt": False,
            "description": phrase,
            "abbreviation": {
                "wordChars": "[\\w'&]",  # don't let apostraphes trigger
                "abbreviations": [
                    abbrev
                ],
                "immediate": False,
                "ignoreCase": True,
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
            "matchCase": True,
            "filter": {
                "regex": filter_regex,
                "isRecursive": False
            },
            "type": "phrase",
            "sendMode": "kb"
        }
        json.dump(config, f, indent=4)


def load_corpus() -> List[str]:
    """Load all txt files under data/corpus, and return as a list of strings"""
    corpus_path = "data/corpus/"
    all_lines = []
    for filename in os.listdir(corpus_path):
        if filename.endswith(".txt"):
            with open(corpus_path + filename, 'r') as f:
                all_lines.extend(f.readlines())
    return all_lines


def corpus_to_ngrams(corpus: List[str], max_n: int) -> Counter:
    """Convert a corpus of strings into n-grams"""
    # count N grams of several different Ns
    all_counts = Counter()
    for text in texts:
        tokenized = text.split()
        for n in range(1, max_n):
            gram = ngrams(tokenized, n)
            all_counts.update(Counter(gram))

    return all_counts


def get_top_shortcuts(all_counts: Counter, n: int) -> List[tuple]:
    """Get the top n-grams from the ngrams counter"""
    results : List[Tuple] = []
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
    return results


if __name__ == "__main__":

    texts = load_corpus()
    all_counts = corpus_to_ngrams(texts, 3)
    top_results = get_top_shortcuts(all_counts, 200)

    shortcuts = match_abbrevs_to_phrases(top_results)

    final_results = []
    for phrase, abbrev in shortcuts.items():
        key = tuple(phrase.split())
        count = all_counts[key]
        score = count * (len(phrase) - len(abbrev))
        final_results.append((score, phrase, abbrev, count))

    final_results = sorted(final_results)
    abbrevs = {row[2]: row for row in final_results}
    phrases = {row[1]: row for row in final_results}

    for score, phrase, abbrev, count in final_results:
        print(f"{score:5}\t{phrase:20}:{abbrev}")

    # for phrase, abbrev in shortcuts.items():
    #     create_autokey_config_for_abbrev(phrase, abbrev)
