#!/bin/bash
#
# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause

set -e

echo "::group::Setting up"
checkout.sh
echo "::endgroup::"

INP=()

[ -n "${INPUT_DOC_ROOT}" ] && INP+=("-d" "${INPUT_DOC_ROOT}")
[ -n "${INPUT_TIMEOUT}" ] && INP+=("-t" "${INPUT_TIMEOUT}")
[ -n "${INPUT_NUM_REQUESTS}" ] && INP+=("-c" "${INPUT_NUM_REQUESTS}")
[ -n "${INPUT_EXCLUDE}" ] && INP+=("-x" "${INPUT_EXCLUDE}")
[ -n "${INPUT_VERBOSE}" ] && INP+=("-v")


if [ -n "${INPUT_FILES}" ]
then
  INP+=("${INPUT_FILES}")
elif [ -n "${INPUT_DIR}" ]
then
  INP+=("-r" "${INPUT_DIR}")
fi


echo
set -x
/liche ${INP[@]} && set +x && echo "No broken links!"
