#!/bin/sh
#
# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause

set -e

CACHE_DIR="cache"
IMAGE_CACHE="${CACHE_DIR}/images.tar.bz2"

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

if [ -e "${IMAGE_CACHE}" ]
then
  echo "Using cached images"
  tar -C ~/.isabelle -xvjf "{IMAGE_CACHE}"
fi
echo "::endgroup::"

export L4V_ARCH=${INPUT_L4V_ARCH}

FAIL=0

cd l4v
if [ "${INPUT_SESSION}" = "CRefine" ]
then
  # special treatment for CRefine session to speed up seL4 code change checks

  # for testing
  cd spec
  make ASpec || FAIL=1

  # cd proof
  # make CRefine || FAIL=1
  cd ..

  # remove large images that will need to be rebuilt anyway next time:
  rm -f ~/.isabelle/$L4V_ARCH/*/CKernel
  rm -f ~/.isabelle/$L4V_ARCH/*/CSpec
  rm -f ~/.isabelle/$L4V_ARCH/*/CBaseRefine
  rm -f ~/.isabelle/$L4V_ARCH/*/CRefine
else
  ./run_tests -v ${INPUT_SESSION} || FAIL=1
fi
cd ..

echo "Tarring up images for caching"
mkdir -p "${CACHE_DIR}"
tar -C "${CACHE_DIR}" -cvjf ~/.isabelle/$L4V_ARCH/ images.tar.bz2

exit $FAIL