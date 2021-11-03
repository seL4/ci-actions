#!/bin/bash
#
# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause
#

# generic steps to invoke hardware runs on the machine queue
# expects a standard `build.py --hw` invocation to work in directory INPUT_ACTION_NAME

set -e

echo "::group::Setting up"
# make machine queue available
export PATH="$(pwd)/machine_queue":$PATH
. setup-hw-ssh.sh

# for junit output prep:
mkdir projects
cd projects
git clone --depth 1 https://github.com/seL4/seL4_libs.git
cd ..

export ACTION_DIR="${SCRIPTS}/.."

# python env
sudo apt-get install -y --no-install-recommends libffi-dev
pip3 install --user junitparser sel4-deps
export PYTHONPATH="${ACTION_DIR}/seL4-platforms"
echo "::endgroup::"

# start test
python3 "${ACTION_DIR}/${INPUT_ACTION_NAME}/build.py" --hw
