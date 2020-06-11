#!/bin/bash
#
# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause

set -e

../scripts/install-python.sh

pip3 install -q reuse
PATH=$PATH:$HOME/.local/bin

../scripts/checkout.sh

reuse lint
