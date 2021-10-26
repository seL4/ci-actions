#!/bin/bash
#
# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause
#

# CAmkES VM hardware runs

set -e

echo "::group::Setting up"
# make machine queue available
export PATH="$(pwd)/machine_queue":$PATH
. setup-hw-ssh.sh

export ACTION_DIR="${SCRIPTS}/.."

# python env
sudo apt-get install -y --no-install-recommends libffi-dev
pip3 install --user junitparser sel4-deps
export PYTHONPATH="${ACTION_DIR}/seL4-platforms"
echo "::endgroup::"

# start test
python3 "${ACTION_DIR}/camkes-vm-hw/build.py" --hw
