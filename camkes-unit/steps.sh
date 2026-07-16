#!/bin/sh
#
# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

set -e

echo "::group::Setting up"

git clone https://github.com/seL4/capdl

mkdir camkes-tool
cd camkes-tool
checkout.sh
cd - > /dev/null

if [ "${GITHUB_EVENT_NAME}" = "pull_request_target" ] ||
   [ "${GITHUB_EVENT_NAME}" = "pull_request" ]
then
  export INPUT_EXTRA_REFS="$(get-prs)"
  export EXTRA_REFS_PATHS="seL4/capdl=capdl"
  fetch-extra-refs.sh
fi

echo
echo "Repo summary:"
echo "camkes-tool: $(git -C camkes-tool rev-parse --short HEAD)"
echo "      capdl: $(git -C capdl rev-parse --short HEAD)"

cd camkes-tool
export PYTHONPATH=../capdl/python-capdl-tool
echo "::endgroup::"

python3 alltests.py
