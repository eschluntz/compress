#!/usr/bin/env python

"""
Script to turn a corpus of text into a list of suggested phrases
and abbreviations. 

Reads data from data/corpus/*.txt
Outputs suggested abbreviations to output/suggested_shortcuts.yaml

Terminology:
a 'Shortcut' is a joint 'Phrase' and 'Abbreviation'.
"""

import os
from typing import List, Dict, Tuple
from collections import Counter, namedtuple
from nltk.util import ngrams
import yaml
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


def match_abbrevs_to_phrases(results: List[tuple], presets : Dict[str, str]) -> Dict[str, str]:
    """Find the best abbreviation for each phrase without overlap.

    Returns a dict of phrase -> abbrev, i.e. {'because': 'bc'}.

    Highest scoring phrases get priority for most memorable shortcuts.
    """
    # start with the presets and blacklist
    abbrev_set = BLACKLIST
    shortcut_dict = presets
    for _, v in shortcut_dict.items():
        abbrev_set.add(v)

    for row in results:
        score, phrase = row[0], row[1]

        # skip anything already in the presets
        if phrase in shortcut_dict:
            continue

        posssible_abbrevs = get_possible_abbrevs(phrase)
        for abbrev in posssible_abbrevs:  # ordered best to worst, so we can take the firs that works
            if abbrev not in abbrev_set and len(abbrev) < len(phrase) - 1:  # save at least two chars
                abbrev_set.add(abbrev)
                shortcut_dict[phrase] = abbrev
                break
        else:
            print(f"warning, no abbrev for {phrase} with score {score}")

    return shortcut_dict


def load_corpus(corpus_path="data/corpus/") -> List[str]:
    """Load all txt files under data/corpus, and return as a list of strings"""
    all_lines = []
    found_data = False
    for filename in os.listdir(corpus_path):
        if filename.endswith(".txt"):
            found_data = True
            with open(os.path.join(corpus_path, filename), 'r', encoding="utf8") as f:
                all_lines.extend(f.readlines())
    if not found_data:
        print("Warning: No txt files found in data/corpus/")
    all_lines = [line.strip() for line in all_lines]
    return all_lines


def corpus_to_ngrams(corpus: List[str], max_n: int) -> Counter:
    """Convert a corpus of strings into a Counter of n-grams of various lengths"""
    all_counts = Counter()
    for line in corpus:
        tokenized = line.split()
        for n in range(1, max_n + 1):
            gram = ngrams(tokenized, n)
            all_counts.update(Counter(gram))

    return all_counts


def get_best_phrases_to_shorten(phrase_counts: Counter, n_to_keep: int) -> List[tuple]:
    """Get the best scoring phrases that should be shortened into abbreviations"""
    phrase_data : List[Tuple] = []
    for phrase_tuple, count in phrase_counts.items():
        if count <= 3:  # don't count rare but super long phrases
            continue
        phrase = " ".join(phrase_tuple)
        phrase_len = len(phrase)
        avg_shortcut_len = 2
        score = (phrase_len - avg_shortcut_len) * count  # how many chars will be saved
        phrase_data.append((score, phrase, phrase_len, count))

    phrase_data = sorted(phrase_data, reverse=True)
    phrase_data = phrase_data[:n_to_keep]
    return phrase_data


def fix_grammer(text: str) -> str:
    """Fix grammar in text"""
    words = text.split(" ")
    fixes = {
        "i": "I",
        "dont": "don't",
        "doesnt": "doesn't",
    }
    return " ".join([fixes.get(word, word) for word in words])


def save_shortcuts(shortcuts: Dict[str, str]) -> None:
    """Save the shortcuts to a yaml file"""
    with open("output/suggested_shortcuts.yaml", 'w', encoding="utf8") as f:
        yaml.dump(shortcuts, f, default_flow_style=False)


if __name__ == "__main__":

    texts = load_corpus()
    all_counts = corpus_to_ngrams(texts, 4)
    top_results = get_best_phrases_to_shorten(all_counts, 200)

    shortcuts = match_abbrevs_to_phrases(top_results, PRESET_ABBREVS)

    final_results = []
    for phrase, abbrev in shortcuts.items():
        key = tuple(phrase.split())
        count = all_counts[key]
        score = count * (len(phrase) - len(abbrev))
        final_results.append((score, phrase, abbrev, count))

    final_results = sorted(final_results)

    for score, phrase, abbrev, count in final_results:
        print(f"{score:5}\t{phrase:20}:{abbrev}")

    final_shortcuts = {fix_grammer(phrase): abbrev for _, phrase, abbrev, _ in final_results}
    save_shortcuts(final_shortcuts)
