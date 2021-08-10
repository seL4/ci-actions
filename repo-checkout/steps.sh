#!/bin/bash
#
# Copyright 2021, Proofcfraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause
#

set -e

echo "::group::Setting up"

mkdir -p ~/bin
curl https://storage.googleapis.com/git-repo-downloads/repo > ~/bin/repo
chmod a+x ~/bin/repo
PATH=~/bin:$PATH

echo "::endgroup::"

echo "::group::Repo checkout"

export REPO_MANIFEST="${INPUT_MANIFEST}"
export MANIFEST_URL="https://github.com/seL4/${INPUT_MANIFEST_REPO}"
checkout-manifest.sh

cd $(repo-util path ${GITHUB_REPOSITORY})
fetch-branch.sh
cd - >/dev/null

repo-util hashes

echo "::endgroup::"

XML="$(repo manifest -r --suppress-upstream-revision | nl-escape.sh)"
echo "::set-output name=xml::${XML}"
