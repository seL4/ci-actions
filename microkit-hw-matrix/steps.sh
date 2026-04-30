#!/bin/bash
#
# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause
#

# generic steps to invoke hardware builds on the machine queue
# expects a standard `build.py --hw` invocation to work in directory INPUT_ACTION_NAME

set -e

echo "::group::Setting up"
export ACTION_DIR="${SCRIPTS}/.."
export PYTHONPATH="${ACTION_DIR}/seL4-platforms"

# python env
sudo apt-get install -y --no-install-recommends libffi-dev
if [ -z "${VIRTUAL_ENV}" ]; then
  python3 -m venv "${GITHUB_WORKSPACE}/venv"
  . "${GITHUB_WORKSPACE}/venv/bin/activate"
fi
pip3 install "junitparser==3.*" sel4-deps

echo "::endgroup::"

cd microkit
  python3 build_sdk.py --sel4=../seL4 --matrix=../build_sdk_matrix.json

  export TEST_CASES=$(cat ../build_sdk_matrix.json)

  echo "test_cases=${TEST_CASES}" >> "${GITHUB_OUTPUT}"
cd -

# exports the gh_output
python3 "${ACTION_DIR}/${INPUT_ACTION_NAME}/build.py" --matrix
