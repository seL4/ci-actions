#!/bin/sh
#
# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

# Fetches any PR branches and extra simultaneous PRs if available.
# Skips branch fetching if explicit input manifest XML is present.
# Always print repo summary. Needs a repo checkout.

if [ -z "${INPUT_XML}" ]
then
  cd $(repo-util path ${GITHUB_REPOSITORY})
  fetch-branch.sh
  cd - >/dev/null

  if [ "${GITHUB_EVENT_NAME}" = "pull_request_target" ] ||
     [ "${GITHUB_EVENT_NAME}" = "pull_request" ]
  then
  export INPUT_EXTRA_PRS="$(get-prs)"
  fetch-extra-prs.sh
  fi
fi

repo-util hashes
