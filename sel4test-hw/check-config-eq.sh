#!/usr/bin/env bash

# Copyright 2026, Proofcraft Pty Ltd
# SPDX-License-Identifier: BSD-2-Clause

# Check that the cmake config of a verification build is equivalent to a release
# build for the same settings. Intended to be run from within a build directory
# where ../init-build.sh is available and the release build has already been
# configured.
#
# Usage: check-config-eq.sh [init-build.sh args...]
# The args should not include -DRELEASE or -DVERIFICATION flags.

set -e

BASEDIR="$(cd .. && pwd)"
INIT_BUILD="${BASEDIR}/init-build.sh"

BUILD_REL="$(pwd)"
BUILD_VER="${BASEDIR}/build-verification"

# Configure verification build in a separate directory
mkdir -p "${BUILD_VER}"
(cd "${BUILD_VER}" && "${INIT_BUILD}" "$@" -DVERIFICATION=TRUE)

# Options that legitimately differ between verification and release builds
IGNORE="KernelVerificationBuild:\|KernelBinaryVerificationBuild:"
IGNORE="$IGNORE\|CSPEC_DIR\|SKIP_MODIFIES\|SORRY_BITFIELD_PROOFS\|UMM_TYPES"
# dependency-tracking variables
IGNORE="$IGNORE\|_DISABLED:\|_UNAVAILABLE:"

# Extract all NAME:TYPE=VALUE cache entries, drop ignored ones,
# strip the :TYPE part to eliminate BOOL/INTERNAL differences,
# normalise out build dir name
extract_config() {
    grep -E ":[A-Z]+=" "$1/CMakeCache.txt" \
        | grep -v "$IGNORE" \
        | sed 's/:[^=]*=/=/' \
        | sed "s|$1|BUILD_DIR|g" \
        | sort
}

extract_config "${BUILD_VER}" > "${BASEDIR}/cfg-ver.txt"
extract_config "${BUILD_REL}" > "${BASEDIR}/cfg-rel.txt"

if diff "${BASEDIR}/cfg-ver.txt" "${BASEDIR}/cfg-rel.txt"; then
    echo "PASS: configs are equal"
else
    echo "FAIL: configs differ"
    exit 1
fi
