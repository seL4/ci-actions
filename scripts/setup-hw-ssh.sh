#!/bin/bash
#
# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause
#

# set up ssh for access to UNSW machine queue

mkdir -p ~/.ssh
echo "login.trustworthy.systems ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBD111xPT6mKt1s+wJvXIGwUXaebbM/B1GE7ztMUgKBqySbO/5AXXFUr/xflvSluH3lYG5tTpGwPYbJyHOmnJGLY=" >> ~/.ssh/known_hosts
echo "tftp.keg.cse.unsw.edu.au ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBEj7X6doSoop91gTvBD7L4O7VGwCO5pLNsu5YAGS1L64MJqo+3wTYgFRdMWTM0hL3YN+1sSabJPICJzKk0EJxkg=" >> ~/.ssh/known_hosts

echo "Host *" >> ~/.ssh/config
echo "ServerAliveInterval 30" >> ~/.ssh/config
echo "ControlMaster auto" >> ~/.ssh/config
echo "ControlPath ~/.ssh/%r@%h:%p-${GITHUB_RUN_ID}-${GITHUB_JOB}-${INPUT_INDEX}" >> ~/.ssh/config
echo "ControlPersist 15" >> ~/.ssh/config
echo >> ~/.ssh/config
echo "Host ts" >> ~/.ssh/config
echo "Hostname login.trustworthy.systems" >> ~/.ssh/config
echo "User sel4_ci" >> ~/.ssh/config
echo >> ~/.ssh/config
echo "Host tftp.keg.cse.unsw.edu.au" >> ~/.ssh/config
echo "User sel4_ci" >> ~/.ssh/config
echo "ProxyJump ts" >> ~/.ssh/config
echo >> ~/.ssh/config

eval $(ssh-agent)
ssh-add -q - <<< "${HW_SSH}"
