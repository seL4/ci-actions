#!/bin/bash
#
# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause

set -e

${SCRIPTS}/install-python.sh

pip3 install -q reuse
PATH=$PATH:$HOME/.local/bin

${SCRIPTS}/checkout.sh

reuse lint
