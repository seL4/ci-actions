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
  # For deployment after test, we can only deal with the default devel.xml and a
  # potentially provided mcs-devel.xml, but no other input manifests.
  if [ -n "${INPUT_MANIFEST}" ] && [ "${INPUT_MANIFEST}" != "mcs-devel.xml" ]
  then
    echo "Error: INPUT_MANIFEST was set, but not mcs-devel.xml for a non-preprocess deployment" >&2
    exit 1
  fi

  if [ "${INPUT_MANIFEST}" == "mcs-devel.xml" ]; then
    # for checkout-manifest.sh; read input from mcs-devel.xml
    export REPO_MANIFEST="$INPUT_MANIFEST"
    # deploy hashes to mcs.xml
    declare -a MANIFEST_FILE=("--manifest-file" "mcs.xml")
  else
    declare -a MANIFEST_FILE
  fi

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
  staging-manifest "${MANIFEST_FILE[@]}" ssh://git@github.com/seL4/verification-manifest.git
  echo "::endgroup::"
else
  if [ -n "${INPUT_MANIFEST}" ]; then
    # for checkout-manifest.sh
    export REPO_MANIFEST="$INPUT_MANIFEST"
    # for sel4-pp
    declare -a MANIFEST_FILE=("--manifest-file" "${INPUT_MANIFEST}")
  else
    declare -a MANIFEST_FILE
  fi

  echo "::group::Repo checkout"
  checkout-manifest.sh
  repo-util hashes
  echo "::endgroup::"

  echo "::group::Deploy"
  seL4-pp --verification-path . "${MANIFEST_FILE[@]}"
  echo "::endgroup::"
fi
