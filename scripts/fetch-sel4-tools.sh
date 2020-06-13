#!/bin/sh
#
# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause

# Fetches the sel4_tools repository and provides location in SEL4_TOOLS

SEL4_TOOLS_URL=https://github.com/seL4/sel4_tools.git
export SEL4_TOOLS=${SCRIPTS}/sel4_tools

echo "Cloning ${SEL4_TOOLS_URL}"
git clone -q --depth 1 --no-tags ${SEL4_TOOLS_URL} ${SEL4_TOOLS}
