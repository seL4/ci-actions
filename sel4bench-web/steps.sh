#!/bin/bash
#
# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause
#

echo "::group::Setting up"
export ACTION_DIR="${SCRIPTS}/.."

# python env
sudo apt-get install -y --no-install-recommends libffi-dev
if [ -z "${VIRTUAL_ENV}" ]; then
  python3 -m venv "${GITHUB_WORKSPACE}/venv"
  . "${GITHUB_WORKSPACE}/venv/bin/activate"
fi
pip3 install "junitparser==3.*" sel4-deps
export PYTHONPATH="${ACTION_DIR}/seL4-platforms"
echo "::endgroup::"

# start web page generation
python3 "${ACTION_DIR}/${INPUT_ACTION_NAME}/build.py" --web
