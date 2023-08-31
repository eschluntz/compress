#!/bin/bash
# Used to refresh autokey to pick up new shorcuts

pkill autokey
python generate_autokeys.py

# if your autokey config is somewhere else, change this line:
cp -r output/autokey_phrases ~/.config/autokey/data/My\ Phrases
autokey &
