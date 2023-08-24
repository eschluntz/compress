[![codecov](https://codecov.io/gh/eschluntz/compress/branch/master/graph/badge.svg?token=CML5P28ELL)](https://codecov.io/gh/eschluntz/compress)

[![Build Status](https://github.com/eschluntz/compress/actions/workflows/run_tests.yml/badge.svg)](https://github.com/eschluntz/compress/actions)

# Compress
This is a tool for automatically creating typing shortcuts from a corpus of your own writing! For example when I want to write:

`What's the problem with this robot? What debugging steps have you tried?` 

I physically type:

`wts tpm w ts r? wt db steps h y tried?`.

This repo can parse a corpus of text and suggest what shortcuts you should use to save the most letters while typing. It then generates config files for [Autokey](https://github.com/autokey/autokey), a linux program that implements keyboard shortcuts!

It also contains a tool for parsing a Slack Data Export of your messages to create a corpus.

# What phrases to abbreviate?
The code looks through the corpus to find common n-grams that can be replaced with much shorter phrases. The suggestions are ranked by `[characters saved] * [frequency of phrase]`. 

I was surprised that very short and frequent words topped this list, such as `t -> the`, as well as longer phrases that I use a lot, such as `wdytk -> what do you think`.

Just reading through the results was amusing to see how repetitive some of my writing is :)

# How to pick the abbreviation?
This is largely preferences and heuristics to try to generate memorable abbreviations for different phrases. Some of my design philosphies were:

1. The abbrev cannot be a word that I want to type. Right now this is done with a dictionary, but I should change it to use my actual corpus.
2. The goal is being memorable. 1st letter is top choice, and 1st letter + last letter is next choice.
3. More common phrases get priority for more memorable abbrevs.
4. Plurals should have the same abbrev as the singular, but with an "s". For example `r -> robot` and `rs -> robots`. 
5. If a word has an abbrev, a phrase that contains that word should contain the abbrev. For example:
```
t -> the
r -> robot
tr -> the robot
```
6. Don't try to be perfect. These suggestions are meant to cover a lot of ground and then let you manually edit your favorites before use.

# Instructions

1. run `install.sh` to install dependencies
1. Put any corpus of your text that you want to compress in `data/corpus/*.txt`
2. If you want to use your slack history as a corpus:
    1. export it to a folder called `data/slack_export`. Only slack workspace admins can do this (and it only exports public channels).
    2. Change `USERNAME_TO_EXPORT` at the top of the file to your slack username.
    3. Run `parse_slack.py`. This will generate a new corpus document in `data/corpus/`
    4. DELETE YOUR SLACK EXPORT WITH `srm` 
3. Run `find_suggested_phrases.py`. This will generate a list of the top 200 suggested shortcuts to `output/suggested_shortcuts.yaml`
4. Edit or add any shortcuts that you want, then copy the file to `shortcuts.yaml`. 
    - This is a manual step so you can customize it without it being blown out every time you run the script again. 
    - It's also saved in git even though it's an output so that I can keep it in sync across multiple of my computers :) 
    - If you're starting out, I suggest just going with 10-20 shortcuts to make it easier to remember them
5. Run `generate_autokeys.py` to convert `shortcuts.yaml` into actual config files for `autokey`.
6. Install [Autokey](https://github.com/autokey/autokey)
7. Symlink the output into autokey's config: `ln -s output/autokey_phrases ~/.config/autokey/data/My Phrases/`
8. From now on when you edit `shortcuts.yaml` you can re-generate and reload autokey with `reload.sh` 

# Notes
[Autokey](https://github.com/autokey/autokey) Uses simulated keyboard input to replace phrases with your abbreviations. I tried several chrome extensions but this worked much more reliably without conflicting with sites' own javascript.

The config files I generate are set to only apply when Chrome is in focus because that's where I do most of my english typing. I found that keeping this active in terminal and vscode caused way more problems than it was solved because my abbreviations overlapped with common short linux commands and variable names i.e. `t`. 