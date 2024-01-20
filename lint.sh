#!/bin/bash

set -euo pipefail

readarray -t SPELL_FILES_ARRAY < <(git ls-files)
codespell "${SPELL_FILES_ARRAY[@]}"

readarray -t PY_FILES_ARRAY < <(git ls-files '*.py')
ruff check "${PY_FILES_ARRAY[@]}"
ruff format --diff "${PY_FILES_ARRAY[@]}"
pyright "${PY_FILES_ARRAY[@]}"
