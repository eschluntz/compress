#!/bin/bash

pkill autokey
python generate_autokeys.py
autokey &
