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

# set up ssh:
mkdir -p ~/.ssh
echo "login.trustworthy.systems,129.94.173.83 ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBGJaDmM3/MtDmmLMzh39/xbaWbkiX0RJCGb/aNrlaaqdkW10l20hbzs9zJ1rp1USv2y4YszTXwbJCH7J7PZNqeA=" >> ~/.ssh/known_hosts
echo "tftp.keg.cse.unsw.edu.au ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBEj7X6doSoop91gTvBD7L4O7VGwCO5pLNsu5YAGS1L64MJqo+3wTYgFRdMWTM0hL3YN+1sSabJPICJzKk0EJxkg=" >> ~/.ssh/known_hosts

echo "Host *" >> ~/.ssh/config
echo "ServerAliveInterval 30" >> ~/.ssh/config
echo "ControlMaster auto" >> ~/.ssh/config
echo "ControlPath ~/.ssh/%r@%h:%p-post-${GITHUB_RUN_ID}-${GITHUB_JOB}-${INPUT_INDEX}" >> ~/.ssh/config
echo "ControlPersist 20m" >> ~/.ssh/config
echo >> ~/.ssh/config
echo "Host ts" >> ~/.ssh/config
echo "Hostname login.trustworthy.systems" >> ~/.ssh/config
echo "User kleing" >> ~/.ssh/config
echo >> ~/.ssh/config
echo "Host tftp.keg.cse.unsw.edu.au" >> ~/.ssh/config
echo "User kleing" >> ~/.ssh/config
echo "ProxyJump ts" >> ~/.ssh/config
echo >> ~/.ssh/config

eval $(ssh-agent)
ssh-add -q - <<< "${HW_SSH}"

# python
export ACTION_DIR="${SCRIPTS}/.."
export PYTHONPATH="${ACTION_DIR}/seL4-platforms"
python3 "${ACTION_DIR}/sel4test-hw-run/build.py" --post

echo "::endgroup::"
