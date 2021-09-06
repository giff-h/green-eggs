#!/bin/bash
set -e

# Establish context first
if [ "$0" != "-bash" ]; then
  readonly SCRIPT_NAME="$(basename $0)"
  readonly REPO_BASE_DIR="$(cd "$(dirname "${SCRIPT_NAME}")" && pwd)"
  readonly DOCFORMATTER_OPTS="-i -r --wrap-summaries 120 --wrap-descriptions 120 --pre-summary-newline --make-summary-multi-line"

  ci_lint_check_test () {
    cd "${REPO_BASE_DIR}"
    poetry run mypy .
    poetry run docformatter --check ${DOCFORMATTER_OPTS} .
    poetry run isort --check .
    poetry run black --check .

    rm -rf htmlcov/
    poetry run nox -s tests_pyenv # FIXME Replace with CI session once CI is setup
  }

  local_lint_clean_test () {
    cd "${REPO_BASE_DIR}"
    poetry run mypy .
    poetry run docformatter ${DOCFORMATTER_OPTS} .
    poetry run isort .
    poetry run black .

    rm -rf htmlcov/
    poetry run nox -s tests_pyenv
  }

  pre_commit_stash_and_clean () {
    echo "${REPO_BASE_DIR}"
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
