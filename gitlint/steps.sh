#!/bin/bash
#
# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause

set -e

[ -z ${GITHUB_BASE_REF+x} ] && (echo "Action only works on pull requests"; exit 1)

echo "::group::Setting up"
install-python.sh

echo "Installing gitlint tool"
pip3 install -q gitlint

checkout.sh
# fetch pull request base
fetch-base.sh

# determine .gitlint config
if [ -n "${INPUT_CONFIG}" ]
then
  echo "Using arg ${INPUT_CONFIG}"
  CONFIG="--config ${INPUT_CONFIG}"
elif [ ! -r .gitlint ]
then
  . ${SCRIPTS}/fetch-sel4-tools.sh
  CONFIG_PATH="misc/.gitlint"
  CONFIG="--config ${SEL4_TOOLS}/${CONFIG_PATH}"
  echo "Using default sel4_tools/${CONFIG_PATH}"
else
  echo "Using target repo .gitlint"
fi
echo "::endgroup::"

echo

HEAD_SHA=$(jq -r '.pull_request.head.sha' ${GITHUB_EVENT_PATH})
RANGE=${GITHUB_BASE_REF}..${HEAD_SHA}

echo "Checking the following commits:"
git log --oneline ${RANGE}

echo
gitlint ${CONFIG} --commits ${RANGE} lint && echo "Gitlint successful!"
