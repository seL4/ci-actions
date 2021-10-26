#!/bin/bash
#
# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause
#

set -e

echo "::group::Setting up"
mkdir -p ~/bin
curl https://storage.googleapis.com/git-repo-downloads/repo > ~/bin/repo
chmod a+x ~/bin/repo

PATH=~/bin:"${SCRIPTS}/../l4v-deploy":$PATH

pip3 install --user lxml

eval $(ssh-agent)
ssh-add -q - <<< "${GH_SSH}"
echo "::endgroup::"

if [ -z "${INPUT_PREPROCESS}" ]
then
  echo "::group::Repo checkout"
  export REPO_DEPTH=0
  checkout-manifest.sh

  echo "Fetching Isabelle tags"
  cd $(repo-util path seL4/isabelle)
  git fetch verification --tags
  cd - > /dev/null

  repo-util hashes
  echo "::endgroup::"

  echo "::group::Deploy"
  staging-manifest ssh://git@github.com/seL4/verification-manifest.git
  echo "::endgroup::"
else
  echo "::group::Repo checkout"
  checkout-manifest.sh
  repo-util hashes
  echo "::endgroup::"

  echo "::group::Deploy"
  seL4-pp --verification-path .
  echo "::endgroup::"
fi