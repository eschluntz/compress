
from typing import Counter
from preset_abbrevs import BLACKLIST, PRESET_ABBREVS
from parse_slack import extract_slack_msgs, clean_slack_msg
from find_suggested_phrases import (
    get_plural,
    get_possible_abbrevs,
    get_top_shortcuts,
    match_abbrevs_to_phrases,
    match_to_prev_abbrevs,
    corpus_to_ngrams,
    get_singular,
)
from generate_autokeys import create_autokey_config_for_abbrev
import os
import json


def test_presets():
    # just make sure we can import without crashing
    assert "again" in PRESET_ABBREVS
    assert "a" in BLACKLIST


def test_extract_slack_msgs():
    output = extract_slack_msgs("test_export", "erik")
    assert output == ["test_msg_1", "test with words"]


def test_clean_slack_msg():
    msg = "test :slightly_smiling_face: and also :smiling_face: and then <@U01SL713VH8>?"
    out = clean_slack_msg(msg)
    assert out == "test and also and then"


def test_get_abbreviations():
    out = get_possible_abbrevs("an")  # mainly make sure short inputs don't crash
    assert "a" in out

    out = get_possible_abbrevs("the")
    assert "t" in out
    assert "th" in out

    out = get_possible_abbrevs("different")
    assert "dt" in out
    assert "dif" in out
    assert "diff" in out

    out = get_possible_abbrevs("in the robots")
    assert "itr" in out


def test_match_abbrevs():
    input_phrases = [
        # (score, phrase, phrase_len, count)
        (9933, 'the', 3, 9933),
        (6462, 'that', 4, 3231),
        (4128, 'and', 3, 4128),
        (4123, 'the robot', 9, 589),
        (3940, 'this', 4, 1970),
        (3801, 'robot', 5, 1267),
        (3410, 'need to', 7, 682),
        (3020, 'in the', 6, 755),
        (2954, 'something', 9, 422),
        (2952, 'robots', 6, 738),
        (2844, 'should', 6, 711),
        (2824, 'just', 4, 1412),
        (2725, 'for', 3, 2725),
        (2652, 'with', 4, 1326),
        (2644, 'have', 4, 1322),
        (2600, 'i think', 7, 520),
        (2594, 'you', 3, 2594),
        (2508, 'of the', 6, 627),
        (2427, 'think', 5, 809),
        (2372, 'on the', 6, 593)
    ]
    expected = {
        'about': 'ab',
        'and': 'n',
        'the': 't',
        'that': 'tt',
        'this': 'ts',
        'robot': 'r',
        'robots': 'rs',
        'something': 's',
        'somethings': 'ss',
        'should': 'sd',
        'just': 'j',
        'for': 'f',
        'with': 'w',
        'withes': 'ws',
        'have': 'h',
        'haves': 'hs',
        'you': 'y',
        'yous': 'ys',
        'think': 'tk',
        'thinks': 'tks',
        'the robot': 'tr',
        'need to': 'nt',
        'i think': 'itk',
        'of the': 'ot'
    }
    presets = {"about": "ab", "and": "n", "i think": "itk"}
    shortcuts = match_abbrevs_to_phrases(input_phrases, BLACKLIST, presets)
    assert expected == shortcuts


def test_match_to_prev_abbrevs():
    shortcuts = {
        "the": "t",
        "robot": "r"
    }

    # plurals
    out = match_to_prev_abbrevs(shortcuts, "robots")
    assert out == "rs"

    # composites
    out = match_to_prev_abbrevs(shortcuts, "the robot")
    assert out == "tr"

    assert match_to_prev_abbrevs(shortcuts, "asdf") is None


def test_get_top_shortcuts():
    all_counts = Counter({
        ("hello",): 10,
        ("robots",): 3,
        ("hello", "world"): 5,
    })
    out = get_top_shortcuts(all_counts, 2)
    # score, phrase, phrase_len, count
    expected = [
        (45, "hello world", 11, 5),
        (30, "hello", 5, 10)
    ]
    assert out == expected


def test_corpus_to_n_grams():
    corpus = [
        "hello world",
        "hello world goodbye world"
    ]
    out = corpus_to_ngrams(corpus, 2)
    expected = Counter({
        ("hello",): 2,
        ("world",): 3,
        ("goodbye",): 1,
        ("hello", "world"): 2,
        ("world", "goodbye"): 1,
        ("goodbye", "world"): 1,
    })
    assert expected == out


def test_get_plural():
    for word, expected in [
        ("things", None),
        ("wolf", "wolves"),
        ("box", "boxes"),
        ("robot", "robots"),
        ("lady", "ladies"),
        ("ash", "ashes"),
        ("hero", "heroes"),
    ]:
        assert expected == get_plural(word)


def test_get_singular():
    for word, expected in [
        ("things", "thing"),
        ("robots", "robot"),
        ("robot", None),
        ("hello", None),
    ]:
        assert expected == get_singular(word)


def test_autokey_configs():
    # TODO: mock filesystem so none of this touches disk. oh well...
    create_autokey_config_for_abbrev("test_because", "bc")
    result_path = "output/autokey_phrases/"
    main_path = result_path + "testbecause.txt"
    config_path = result_path + ".testbecause.json"

    with open(main_path, 'r') as f:
        out = f.readline()
        assert out == "test_because"

    with open(config_path, 'r') as f:
        out = json.load(f)
        expected = {'usageCount': 0, 'omitTrigger': False,
            'prompt': False, 'description': 'test_because', 'abbreviation':
            {'wordChars': "[\\w'&-]", 'abbreviations': ['bc'], 'immediate': False,
            'ignoreCase': True, 'backspace': True, 'triggerInside': False},
            'hotkey': {'hotKey': None, 'modifiers': []}, 'modes': [1],
            'showInTrayMenu': False, 'matchCase': True, 'filter':
            {'regex': 'google-chrome.Google-chrome', 'isRecursive': False},
            'type': 'phrase', 'sendMode': 'kb'}
        assert out == expected

    os.remove(main_path)
    os.remove(config_path)
