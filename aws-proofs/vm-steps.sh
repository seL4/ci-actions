#!/bin/bash
#
# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause
#

# test driver inside the VM; expects to be called by "run"

set -e

echo "::group::Setting up"
export PATH=/home/test-runner/ci-actions/scripts:/home/test-runner/.local/bin:/home/test-runner/.bin:$PATH
mkdir ver
cd ver

if [ -n ${INPUT_MANIFEST} ]
then
  export REPO_MANIFEST="${INPUT_MANIFEST}"
fi

checkout-manifest.sh

if [ -n "${INPUT_ISA_BRANCH}" ]
then
  cd isabelle
  echo "Fetching ${INPUT_ISA_BRANCH} from remote \"verification\""
  git fetch -q --depth 1 verification ${INPUT_ISA_BRANCH}
  git checkout -q ${INPUT_ISA_BRANCH}
  cd ..
fi

cd $(repo-util path ${GITHUB_REPOSITORY})
echo "Testing ${GITHUB_REPOSITORY}"

if [ -z ${GITHUB_BASE_REF} ]
then
  fetch-branch.sh
else
  fetch-pr.sh
fi
cd - >/dev/null

repo-util hashes

echo "Setting up Isabelle components"
isabelle/bin/isabelle components -a

CACHE_NAME=${INPUT_CACHE_NAME}
if [ -n "${INPUT_CACHE_READ}" ] && [ -z "${CACHE_NAME}" ]
then
  # construct default cache name
  BRANCH=${INPUT_ISA_BRANCH:-default}
  MANIFEST=${INPUT_MANIFEST:-devel}
  CACHE_NAME="${GITHUB_REPOSITORY}-${BRANCH}-${MANIFEST}-${INPUT_L4V_ARCH}"
fi

if [ -n ${CACHE_NAME} ]
then
  echo "Getting image cache ${CACHE_NAME}"
  # it's Ok for this command to fail, cache might not yet exist
  aws s3 cp "s3://isabelle-images/${CACHE_NAME}.tar.xz" - | tar -C ~/.isabelle -vJx || true
else
  echo "Skipping image cache read"
fi


echo "::endgroup::"

export L4V_ARCH=${INPUT_L4V_ARCH}

FAIL=0

cd l4v
if [ "${INPUT_SESSION}" = "CRefine" ]
then
  # special treatment for CRefine session to speed up seL4 code change checks

  cd proof
  make CRefine || FAIL=1
  cd ..

elif [ -n ${INPUTSESSION} ]
then
  ./run_tests -v ${INPUT_SESSION} || FAIL=1
else
  ./run_tests -v -x AutoCorresSEL4 || FAIL=1
fi
cd ..

if [ -n "${CACHE_NAME}" ] && [ -n "${INPUT_CACHE_WRITE}" ]
then
  echo "Writing image cache ${CACHE_NAME}"
  # compress not too much; s3 upload is fast and compression winnings are meager
  tar -C ~/.isabelle -vc heaps/ | xz -T0 -3 - | \
    aws s3 cp - "s3://isabelle-images/${CACHE_NAME}.tar.xz"
else
  echo "Skipping image cache write"
fi

# shut down test VM 1min after exiting this script
sudo shutdown -h +1

exit $FAIL
