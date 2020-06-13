#!/bin/bash
#
# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause

set -e

echo "::group::Setting up"
install-python.sh

echo "Installing reuse tool"
pip3 install -q reuse

checkout.sh
echo "::endgroup::"

# Specific to l4v: remove symbolic link `isabelle`, because it leads outside
# the repo.
[ -L isabele ] && rm isabelle

echo
reuse lint
