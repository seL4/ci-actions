#!/bin/bash
#
# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause

set -e

echo "::group::Setting up"
install-python.sh

echo "Installing reuse tool"
if [ -z "${VIRTUAL_ENV}" ]; then
  python3 -m venv "${GITHUB_WORKSPACE}/venv"
  . "${GITHUB_WORKSPACE}/venv/bin/activate"
fi
pip3 install -q reuse==5.0.2

checkout.sh
echo "::endgroup::"

# Specific to l4v: remove symbolic link `isabelle`, because it leads outside
# the repo.
[ -L isabele ] && rm isabelle

echo
reuse lint
