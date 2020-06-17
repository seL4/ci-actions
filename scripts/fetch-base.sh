#!/bin/sh
#
# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause

# Fetches all commits between HEAD and GITHUB_BASE_REF (base of a pull request)
# Assumes working dir of repo left by checkout.sh

echo "Fetching ${GITHUB_BASE_REF}"
git fetch -q --no-tags origin +refs/heads/${GITHUB_BASE_REF}:refs/heads/${GITHUB_BASE_REF}

# This only works when the PR comes from the same repo, not a fork
# git fetch -q --no-tags --shallow-exclude ${GITHUB_BASE_REF}

# Fetch everything for now
git fetch -q --no-tags --unshallow
