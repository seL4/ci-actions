#!/bin/bash
#
# Copyright 2022, Kry10 Limited
#
# SPDX-License-Identifier: BSD-2-Clause
#

set -e

GIT_CREDENTIALS="${HOME}/.git-credentials-${INPUT_STORE_ID:-seL4}"

echo "::group::Removing Git credentials"

for REPO in "${INPUT_REPOS}"; do
  git config --global --remove-section "credential.\"https://github.com/${REPO}\""
done

rm -f "${GIT_CREDENTIALS}"

echo "::endgroup::"
