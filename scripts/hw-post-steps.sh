#!/bin/bash
#
# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause
#

# generic steps to release mq lock at the end of a hardware run in case the job was cancelled
# expects a standard `build.py --post` invocation to work in directory INPUT_ACTION_NAME

# python env
echo "::group::Setting up"
export ACTION_DIR="${SCRIPTS}/.."
sudo apt-get install -y --no-install-recommends libffi-dev
. ${SCRIPTS}/setup-python-venv.sh
pip3 install "junitparser==3.*"
export PYTHONPATH="${ACTION_DIR}/seL4-platforms"
echo "::endgroup::"

echo "::group::Releasing mq lock"
# mq setup
export PATH="$(pwd)/machine_queue":$PATH
. setup-hw-ssh.sh

python3 "${ACTION_DIR}/${INPUT_ACTION_NAME}/build.py" --post

echo "::endgroup::"
