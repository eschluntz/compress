#!/bin/bash

pkill autokey
python3 generate_autokeys.py
autokey &
