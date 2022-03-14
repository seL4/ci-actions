#!/bin/bash
#
# Copyright 2022, Kry10 Limited
#
# SPDX-License-Identifier: BSD-2-Clause
#

set -e

GIT_CREDENTIALS="${HOME}/.git-credentials-${INPUT_STORE_ID:-seL4}"

if [ -e "${GIT_CREDENTIALS}" ]; then
  echo "error: ${GIT_CREDENTIALS} already exists."
  exit 1
fi

echo "::group::Storing credentials"

touch "${GIT_CREDENTIALS}"
chmod 0600 "${GIT_CREDENTIALS}"

for REPO in ${INPUT_REPOS}; do
  cat <<< "https://${INPUT_USERNAME}:${INPUT_TOKEN}@github.com/${REPO}"
  echo
done >> "${GIT_CREDENTIALS}"

echo "::endgroup::"

echo "::group::Configuring git to use stored credentials"

for REPO in ${INPUT_REPOS}; do
   git config --global \
     "credential.\"https://github.com/${REPO}\".helper" \
     "store --file=\"${GIT_CREDENTIALS}\""
done

echo "::endgroup::"
