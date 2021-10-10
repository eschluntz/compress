from parse_slack import *


def test_create_word_set():
    all_words = get_blacklist()
    assert "i" in all_words
    assert "a" in all_words
    assert "is" in all_words
    assert "b" not in all_words
    assert "I" not in all_words


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
        (100, "zzz", 0, 0),
        (90, "zzzzz", 0, 0),
        (80, "zz xx", 0, 0),
    ]
    presets = get_preset_abbrevs()
    expected = {
        "zzz": "z",
        "zzzzz": "zz",
        "zz xx": "zx",
    }
    expected.update(presets)
    shortcuts = match_abbrevs_to_phrases(input_phrases)
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
