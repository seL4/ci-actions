#!/bin/sh
#
# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause

set -e

echo "::group::Setting up"
checkout.sh
echo "::endgroup::"

[ -n "${INPUT_DIR}" ] && FILES="-r ${INPUT_DIR}"
[ -n "${INPUT_FILES}" ] && FILES="${INPUT_FILES}"

[ -n "${INPUT_DOC_ROOT}" ] && DROOT="-d ${INPUT_DOC_ROOT}"

[ -n "${INPUT_TIMEOUT}" ] && TIMEOUT="-t ${INPUT_TIMEOUT}"
[ -n "${INPUT_NUM_REQUESTS}" ] && REQ="-c ${INPUT_NUM_REQUESTS}"
[ -n "${INPUT_EXCLUDE}" ] && EXF="-x"

echo
echo liche ${EXF} "${INPUT_EXCLUDE}" ${DROOT} ${REQ} ${TIMEOUT} ${FILES}
/liche ${EXF} "${INPUT_EXCLUDE}" ${DROOT} ${REQ} ${TIMEOUT} ${FILES} \
  && echo "No broken links!"
