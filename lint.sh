#!/bin/bash

readarray -t SPELL_FILES_ARRAY < <(git ls-files)
codespell "${SPELL_FILES_ARRAY[@]}"
pyright .
