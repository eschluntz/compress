#!/usr/bin/env python

"""
Tests for the compress repo. This is best executed from `run_tests.sh`
in order to keep parity with what's running in CI.
"""
import json
from typing import Counter
import os

from find_suggested_phrases import (
    get_possible_abbrevs,
    get_best_phrases_to_shorten,
    match_abbrevs_to_phrases,
    corpus_to_ngrams,
    fix_grammer,
)
from generate_autokeys import create_autokey_config_for_abbrev
from parse_slack import extract_slack_msgs, clean_slack_msg
from preset_abbrevs import BLACKLIST


def test_presets():
    # just make sure we can import without crashing
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
        'i think': 'itk', 
        'the': 't', 
        'that': 'tt', 
        'the robot': 'tr', 
        'this': 'ts', 
        'robot': 'r', 
        'need to': 'nt', 
        'in the': 'e', 
        'something': 's', 
        'robots': 'rs', 
        'should': 'sd', 
        'just': 'j', 
        'for': 'f', 
        'with': 'w', 
        'have': 'h', 
        'you': 'y', 
        'of the': 'ot', 
        'think': 'tk', 
        'on the': 'ont'
     }
    presets = {"about": "ab", "and": "n", "i think": "itk"}
    shortcuts = match_abbrevs_to_phrases(input_phrases, presets)
    assert expected == shortcuts


def test_get_top_shortcuts():
    all_counts = Counter({
        ("hello",): 10,
        ("robots",): 3,
        ("hello", "world"): 5,
    })
    out = get_best_phrases_to_shorten(all_counts, 2)
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


def test_fix_grammer():
    for word, expected in [
        ("i think", "I think"),
        ("dont", "don't"),
        ("it doesnt matter", "it doesn't matter"),
    ]:
        assert expected == fix_grammer(word)


def test_autokey_configs():
    # TODO: mock filesystem so none of this touches disk. oh well...
    create_autokey_config_for_abbrev("test_because", "bc")
    result_path = "output/autokey_phrases/"
    main_path = result_path + "testbecause.txt"
    config_path = result_path + ".testbecause.json"

    with open(main_path, 'r', encoding="utf8") as f:
        out = f.readline()
        assert out == "test_because"

    with open(config_path, 'r', encoding="utf8") as f:
        out = json.load(f)
        expected = {'usageCount': 0, 'omitTrigger': False,
            'prompt': False, 'description': 'test_because', 'abbreviation':
            {'wordChars': r"[\w\t'\-&\+]", 'abbreviations': ['bc'], 'immediate': False,
            'ignoreCase': True, 'backspace': True, 'triggerInside': False},
            'hotkey': {'hotKey': None, 'modifiers': []}, 'modes': [1],
            'showInTrayMenu': False, 'matchCase': True, 'filter':
            {'regex': 'google-chrome.Google-chrome', 'isRecursive': False},
            'type': 'phrase', 'sendMode': 'kb'}
        assert out == expected

    # some are only set to work in chrome, to avoid coding mistakes
    create_autokey_config_for_abbrev("test_i", "i")
    result_path = "output/autokey_phrases/"
    main_path = result_path + "testi.txt"
    config_path = result_path + ".testi.json"

    with open(main_path, 'r', encoding="utf8") as f:
        out = f.readline()
        assert out == "test_i"

    with open(config_path, 'r', encoding="utf8") as f:
        out = json.load(f)
        expected = {'usageCount': 0, 'omitTrigger': False,
            'prompt': False, 'description': 'test_i', 'abbreviation':
            {'wordChars': r"[\w\t'\-&\+]", 'abbreviations': ['i'], 'immediate': False,
            'ignoreCase': True, 'backspace': True, 'triggerInside': False},
            'hotkey': {'hotKey': None, 'modifiers': []}, 'modes': [1],
            'showInTrayMenu': False, 'matchCase': True, 'filter':
            {'regex': 'google-chrome.Google-chrome', 'isRecursive': False},
            'type': 'phrase', 'sendMode': 'kb'}
        assert out == expected

    os.remove(main_path)
    os.remove(config_path)
