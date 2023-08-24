#!/bin/bash
# Unified script to run identical checks locally and in CI

# exit when any command fails
set -e

# linter
# pylint $(git ls-files '*.py')

# tests
pytest