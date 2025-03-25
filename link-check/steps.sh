#!/bin/bash
#
# Copyright 2025, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

set -e

echo "::group::Setting up"
mkdir -p /repo
cd /repo
checkout.sh

# get ignored input files from .linkcheck-ignore.yml
IGNORE_FILES=""
if [ -r .linkcheck-ignore.yml ]; then
  echo "Getting ignored files from .linkcheck-ignore.yml"
  readarray FILES < <(yq '.files[]' .linkcheck-ignore.yml)
  for FILE in "${FILES[@]}"
  do
    if [ -z "${IGNORE_FILES}" ]
    then
      IGNORE_FILES="${FILE%%[[:space:]]}"
    else
      IGNORE_FILES="${IGNORE_FILES}\\|${FILE%%[[:space:]]}"
    fi
  done
fi

# make a .lycheeignore file from .linkcheck-ignore.yml
if [ -r .linkcheck-ignore.yml ]; then
  echo "Creating .lycheeignore file from .linkcheck-ignore.yml"
  yq '.urls[]' .linkcheck-ignore.yml > .lycheeignore
fi

echo "::endgroup::"

IGNORE_FILES=${IGNORE_FILES:-^$}
INPUT_DIR=${INPUT_DIR:-.}

echo "Checking links"

FILES=$(mktemp /tmp/files.XXXXXX)

find "${INPUT_DIR}" -type f \( -name "*.md" -or -name "*.html" \) | \
  grep -v "${IGNORE_FILES}" > "${FILES}"

if [ -s "${FILES}" ]; then
  echo "Checking links in the following files:"
  echo "::group::Files"
  cat "${FILES}"
  echo "::group::Files"
else
  echo "No files to check"
  rm -f "${FILES}"
  exit 0
fi

(set -x; \
  cat "${FILES}" | tr '\n' '\000' | \
  xargs -0 lychee -n \
         ${INPUT_EXCLUDE:+--exclude-path "${INPUT_EXCLUDE}"} \
         ${INPUT_TIMEOUT:+-t "${INPUT_TIMEOUT}"} \
         ${INPUT_NUM_REQUESTS:+--max-concurrency "${INPUT_NUM_REQUESTS}"} \
         ${INPUT_EXCLUDE_URLS:+--exclude "${INPUT_EXCLUDE_URLS}"} \
         ${INPUT_VERBOSE:+-v} \
         ${INPUT_DOC_ROOT:+--root-dir "${INPUT_DOC_ROOT}"}) \
  && echo "No broken links!"
