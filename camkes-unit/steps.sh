#!/bin/sh
#
# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

set -e

echo "::group::Setting up"

git clone https://github.com/seL4/capdl

mkdir camkes-tool
cd camkes-tool
checkout.sh

echo
echo "Repo summary:"
echo "camkes-tool: $(git rev-parse --short HEAD)"
echo "      capdl: $(git -C ../capdl rev-parse --short HEAD)"

export PYTHONPATH=../capdl/python-capdl-tool
echo "::endgroup::"

nosetests --exe --ignore-file=testvisualcamkes.py
