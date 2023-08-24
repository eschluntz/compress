#!/bin/bash
# Used to refresh autokey to pick up new shorcuts

pkill autokey
python generate_autokeys.py
autokey &
