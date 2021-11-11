#!/bin/bash
#
# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause
#

set -e

echo "::group::Setting up"
echo "Installing 'repo'"
mkdir -p ~/bin
curl https://storage.googleapis.com/git-repo-downloads/repo > ~/bin/repo
chmod a+x ~/bin/repo

PATH=~/bin:"${GITHUB_WORKSPACE}/seL4_release":$PATH

echo "Setting up ssh"
eval $(ssh-agent)
ssh-add -q - <<< "${GH_SSH}"

echo "Fetching seL4_release repo"
git clone --depth 1 ssh://git@github.com/seL4/seL4_release

echo "Installing python dependencies"
pip3 install --user -r ${GITHUB_WORKSPACE}/seL4_release/requirements.txt

echo "Install doxygen"
sudo apt-get install -qq doxygen
echo "::endgroup::"

echo "::group::Repo checkout"
export MANIFEST_URL="ssh://git@github.com/seL4/${INPUT_MANIFEST_REPO}.git"
export REPO_MANIFEST=master.xml
export REPO_DEPTH=0
checkout-manifest.sh
repo-util hashes
echo "::endgroup::"

echo "::group::Deploy"
releaseit nightly --release
echo "::endgroup::"

SHA=$(git -C .repo/manifests rev-parse HEAD)
echo "::set-output name=manifest_sha::${SHA}"
