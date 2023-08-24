#!/bin/bash
# unified install script for local and CI

sudo apt-get -y install libenchant-2-dev

pip install --upgrade pip
pip install -r requirements.txt