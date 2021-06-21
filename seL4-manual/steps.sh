#!/bin/bash
#
# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause
#

# Docker entrypoint for seL4 manual test

set -e

# actions:
echo "::group::Setting up"
checkout.sh
echo "::endgroup::"

# start test

cd manual
make markdown
# set draft mode:
sed -i '~'"s/%\\\\Drafttrue/\\\\Drafttrue/" manual.tex
make
