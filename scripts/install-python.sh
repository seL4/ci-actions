#!/bin/bash
#
# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause

# Installs python 3.10; assumes GitHub's ubuntu-latest

echo "Installing python 3.10"
sudo apt-get install -qq python3.10 > /dev/null
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
python3 --version

# setuptools and wheel versions must be matched to working releases
# we need an old version of setuptools (see PR seL4/ci-actions#381)
# and newer versions of wheel removes the bdist_wheel implementation
# that setuptools used to use, but no longer does in newer versions.
pip3 install -q --upgrade pip setuptools==70.0.0 wheel==0.45.1 launchpadlib
