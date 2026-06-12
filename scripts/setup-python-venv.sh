#!/bin/sh
# Copyright 2026, UNSW
#
# SPDX-License-Identifier: BSD-2-Clause

# Sets up a python virtual environment in ${RUNNER_TEMP}/venv
# Does nothing if VIRTUAL_ENV is already set, which means we are in a virtual
# environment already.
# Expects to be sourced with '.' or 'source', as it modifies the environment.
# Does not pass --system-site-packages so is isolated from whatever is installed
# in the system itself.

set -e

if [ -z "${VIRTUAL_ENV}" ]; then
    python3 -m venv "${RUNNER_TEMP}/venv"
    . "${RUNNER_TEMP}/venv/bin/activate"
fi
