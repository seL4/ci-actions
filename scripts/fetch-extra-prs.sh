#!/bin/sh
#
# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

# Fetch extra pull requests in $INPUT_EXTRA_PRS unless $INPUT_XML is set
# Expect INPUT_EXTRA_PRS to be space separated list of org/repo#num

if [ -z "${INPUT_XML}" ] && [ -n "${INPUT_EXTRA_PRS}" ]
then

  for PR in ${INPUT_EXTRA_PRS}
  do
    REPO=${PR%#*}
    ID=${PR#*#}

    URL="https://github.com/${REPO}.git"
    REF="refs/pull/${ID}/head"

    cd $(repo-util path ${REPO})
    echo "Fetching ${REF} from ${URL}"
    git fetch -q --depth 1 ${URL} ${REF}:${REF}
    git checkout -q ${REF}
    cd - > /dev/null
  done

fi
