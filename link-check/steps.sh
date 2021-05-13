#!/bin/sh
#
# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause

set -e

echo "::group::Setting up"
mkdir -p /repo
cd /repo
checkout.sh
echo "::endgroup::"

INPUT_EXCLUDE=${INPUT_EXCLUDE:-^$}

echo "Checking links"

(set -x; \
  find "${INPUT_DIR}" -type f \( -name "*.md" -or -name "*.html" \) | \
  grep -v "${INPUT_EXCLUDE}" | tr '\n' '\000' | \
  xargs -0 /liche ${INPUT_DOC_ROOT:+-d "${INPUT_DOC_ROOT}"} \
         ${INPUT_TIMEOUT:+-t "${INPUT_TIMEOUT}"} \
         ${INPUT_NUM_REQUESTS:+-c "${INPUT_NUM_REQUESTS}"} \
         ${INPUT_EXCLUDE_URLS:+-x "${INPUT_EXCLUDE_URLS}"} \
         ${INPUT_VERBOSE:+-v} ) \
  && echo "No broken links!"
