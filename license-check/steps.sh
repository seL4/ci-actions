#!/bin/bash
#
# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause

set -e

sudo apt-get -qq install -qq python3.7 > /dev/null

pip3 install -q reuse
PATH=$PATH:$HOME/.local/bin

git clone -q --no-tags --depth 1 "https://github.com/${GITHUB_REPOSITORY}.git" .

reuse lint
