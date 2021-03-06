import json
import os
from typing import List, Dict, Optional, Set, Tuple
from collections import Counter, namedtuple
from nltk.util import ngrams
import enchant
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
        return word + "es"
    if word[-1] == "x":
        return word + "es"
    if word[-1] == "z":
        return word[:-1] + "zes"
    return word + "s"


def get_plural(word : str) -> Optional[str]:
    candidate = try_plural_of_word(word)
    d = enchant.Dict("en_US")
    if candidate is None:
        return None
    elif d.check(candidate):
        return candidate
    else:
        return None


def get_singular(word : str) -> Optional[str]:
    """Note: doesn't work for complex plurals like wolves... todo"""
    candidate = word[:-1]
    d = enchant.Dict("en_US")
    if d.check(candidate) and get_plural(candidate) == word:
        return candidate
    else:
        return None


def is_plural(word : str) -> bool:
    """Check if word is plural.
    defintion of plural is that there exists a singular version"""
    # not always correct, but close enough
    d = enchant.Dict("en_US")
    candidate = word[:-1]
    return word[-1] == "s" and d.check(candidate) and get_plural(candidate) == word


def match_abbrevs_to_phrases(results: List[tuple], blacklist : Set[str], presets : Dict[str, str]) -> Dict[str, str]:
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
    abbrev_set = blacklist
    shortcuts = presets
    for _, v in shortcuts.items():
        abbrev_set.add(v)

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
                abbrev_set.add(abbrev)
                shortcuts[singular] = abbrev

                # add plural
                if plural is not None:
                    abbrev2 = abbrev + "s"
                    if abbrev2 not in abbrev_set and len(abbrev2) < len(plural) - 1:
                        abbrev_set.add(abbrev)
                        shortcuts[plural] = abbrev2
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
                                shortcuts[phrase] = abbrev
                            break
                    break

    return shortcuts



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
    for text in corpus:
        tokenized = text.split()
        for n in range(1, max_n + 1):
            gram = ngrams(tokenized, n)
            all_counts.update(Counter(gram))

    return all_counts


def get_top_shortcuts(all_counts: Counter, n_to_keep: int) -> List[tuple]:
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

    results = sorted(results, reverse=True)
    results = results[:n_to_keep]
    return results


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
    with open("output/suggested_shortcuts.yaml", 'w') as f:
        yaml.dump(shortcuts, f, default_flow_style=False)


if __name__ == "__main__":

    texts = load_corpus()
    all_counts = corpus_to_ngrams(texts, 3)
    top_results = get_top_shortcuts(all_counts, 200)

    for results in top_results:
        print(f"{results[1]:20}:\t{results[0]:6} score\t{results[3]} times")

    shortcuts = match_abbrevs_to_phrases(top_results, BLACKLIST, PRESET_ABBREVS)

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
