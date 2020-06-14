#!/bin/sh
#
# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause

set -e

echo "::group::Setting up"
checkout.sh
echo "::endgroup::"

[ -n "${INPUT_FILES}" ] && unset INPUT_DIR

echo
(set -x; \
  /liche ${INPUT_DOC_ROOT:+-d "${INPUT_DOC_ROOT}"} \
         ${INPUT_TIMEOUT:+-t "${INPUT_TIMEOUT}"} \
         ${INPUT_NUM_REQUESTS:+-c "${INPUT_NUM_REQUESTS}"} \
         ${INPUT_EXCLUDE:+-x "${INPUT_EXCLUDE}"} \
         ${INPUT_VERBOSE:+-v} \
         ${INPUT_DIR:+-r "${INPUT_DIR}"} \
         ${INPUT_FILES:+"${INPUT_FILES}"}
) && echo "No broken links!"
