#!/bin/bash
#
# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause

# Escape %, \n, \r for GitHub value setting. It is un-escaped automatically by GH.

# portable sed is no good for newline replacement, but there is always perl
perl -pe 's/%/%25/g' | perl -pe 's/\n/%0A/g' | perl -pe 's/\r/%0D/g'
