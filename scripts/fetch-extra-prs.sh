#!/bin/sh
#
# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

# Fetch extra pull requests in $INPUT_EXTRA_PRS unless $INPUT_XML is set
# Expect INPUT_EXTRA_PRS to be space separated list of org/repo#num

if [ -z "${INPUT_XML}" ] && [ -n "${INPUT_EXTRA_PRS}" ]
then
  echo "extra PRs: ${INPUT_EXTRA_PRS}"

  for PR in ${INPUT_EXTRA_PRS}
  do
    REPO=${PR%#*}
    ID=${PR#*#}

    REPO_PATH="github.com/${REPO}.git"

    if [ -n "${INPUT_TOKEN}" ]
    then
      URL="https://${INPUT_TOKEN}@${REPO_PATH}"
      REPO_PATH="token@${REPO_PATH}"
    else
      URL="https://${REPO_PATH}"
    fi

    REF="refs/pull/${ID}/head"

    cd $(repo-util path ${REPO})
    echo "Fetching ${REF} from ${REPO_PATH}"
    git fetch -q --depth 1 ${URL} ${REF}:${REF}
    git checkout -q ${REF}
    cd - > /dev/null
  done

fi
