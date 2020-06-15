#!/bin/sh
#
# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause

set -e

echo "::group::Setting up"
checkout-manifest.sh
# FIXME: make this work for l4v as well:
cd seL4/
fetch-pr.sh
cd ..

# GitHub sets its own HOME, but we have .isabelle data pre-installed in the
# Docker image

if [ "$HOME" != "/root" ]
then
  ln -s /root/.isabelle $HOME/.isabelle
fi

echo "::endgroup::"

export L4V_ARCH=${INPUT_L4V_ARCH}

cd l4v
./run_tests -v ${INPUT_SESSION}
