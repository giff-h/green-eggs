#!/bin/bash
set -e

# Establish context first
if [ "$0" != "-bash" ]; then
  local_lint_clean_test () {
    poetry check
    poetry run stubgen -p green_eggs -o stubs
    poetry run docformatter -i -r --wrap-summaries 120 --wrap-descriptions 120 --pre-summary-newline --make-summary-multi-line .
    poetry run isort .
    poetry run black .
    poetry run mypy .

    rm -rf htmlcov/
    poetry run nox -s tests_pyenv
  }

  pre_commit_stash_and_clean () {
    if [ "$(git status --porcelain=v1 | grep '^.[^ ]' | wc -l)" = "0" ]; then
      # All changes are in index, no need to stash
      local_lint_clean_test
      git add --all
    else
      readonly UID_BIT=$(uuidgen -r | cut -d'-' -f1)
      readonly MESSAGE="Stash ${UID_BIT} of changes not staged before commit"
      git stash push -k -m "${MESSAGE}"
      readonly STASH_ID=$(git stash list | grep "${MESSAGE}" | cut -d':' -f1)

      local_lint_clean_test

      git add --all
    fi
  }
else
  echo "ERROR - this script may only be used by other scripts as an inclusion"
  exit 99
fi
