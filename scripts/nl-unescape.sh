#!/bin/bash
#
# Copyright 2022, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

# Un-Escape %, \n, \r for GitHub value setting.

perl -pe 's/%0D/\r/g' | perl -pe 's/%0A/\n/g' | perl -pe 's/%25/%/g'
