#!/bin/bash
# Unified script to run identical checks locally and in CI

# exit when any command fails
set -e

# tests
pytest --cov

# linter
pylint $(git ls-files '*.py')