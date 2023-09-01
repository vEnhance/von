#!/bin/bash

set -euo pipefail

readarray -t SPELL_FILES_ARRAY < <(git ls-files)
codespell "${SPELL_FILES_ARRAY[@]}"

readarray -t PY_FILES_ARRAY < <(git ls-files '*.py')
pyright "${PY_FILES_ARRAY[@]}"
pyflakes "${PY_FILES_ARRAY[@]}"
black --check "${PY_FILES_ARRAY[@]}"
isort --check --profile black "${PY_FILES_ARRAY[@]}"
