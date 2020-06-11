#!/bin/bash
#
# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause

# Installs python 3.7; assumes GitHub's ubuntu-latest

echo "Installing python 3.7"
sudo apt-get install -qq python3.7 > /dev/null
