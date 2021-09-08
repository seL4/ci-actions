#!/bin/bash
#
# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause
#

# Always try to release mq lock at the end in case the job was cancelled

echo "::group::Releasing mq lock"
# mq setup
export PATH="$(pwd)/machine_queue":$PATH
. setup-hw-ssh.sh

# python
export ACTION_DIR="${SCRIPTS}/.."
export PYTHONPATH="${ACTION_DIR}/seL4-platforms"
python3 "${ACTION_DIR}/camkes-hw/build.py" --post

echo "::endgroup::"
