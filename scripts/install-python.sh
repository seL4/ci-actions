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
pip3 install -q --upgrade pip setuptools==70.0.0 launchpadlib wheel
