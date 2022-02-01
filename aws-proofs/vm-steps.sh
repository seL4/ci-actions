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

if [ -n "${INPUT_MANIFEST}" ]
then
  export REPO_MANIFEST="${INPUT_MANIFEST}"
fi

TESTBOARD=seL4/gh-testboard
if [ "${GITHUB_REPOSITORY}" = "${TESTBOARD}" ]
then
  export MANIFEST_URL="https://github.com/${TESTBOARD}.git"
  export REPO_BRANCH="${GITHUB_REF}"
fi

checkout-manifest.sh

if [ -n "${INPUT_ISA_BRANCH}" ] && [ -z "${INPUT_XML}" ]
then
  cd isabelle
  echo "Fetching ${INPUT_ISA_BRANCH} from remote \"verification\""
  git fetch -q --depth 1 verification ${INPUT_ISA_BRANCH}
  git checkout -q ${INPUT_ISA_BRANCH}
  cd ..
fi

echo "Testing ${GITHUB_REPOSITORY}"

if [ "${GITHUB_REPOSITORY}" != "${TESTBOARD}" ]
then
  cd $(repo-util path ${GITHUB_REPOSITORY})
  fetch-branch.sh
  cd - >/dev/null
  export INPUT_EXTRA_PRS
  fetch-extra-prs.sh
fi

repo-util hashes

echo "Setting up Isabelle components"
isabelle/bin/isabelle components -a

CACHE_NAME=${INPUT_CACHE_NAME}
if [ -z "${CACHE_NAME}" ]
then
  # construct default cache name
  BRANCH=${INPUT_ISA_BRANCH:-default}
  MANIFEST=${INPUT_MANIFEST:-devel}
  CACHE_NAME="${GITHUB_REPOSITORY}-${BRANCH}-${MANIFEST}-${INPUT_L4V_ARCH}"
fi

echo "::group::Cache"
if [ -n "${INPUT_CACHE_READ}" ]
then
  echo "Getting image cache ${CACHE_NAME}"
  # it's Ok for this command to fail, cache might not yet exist
  aws s3 cp "s3://${INPUT_CACHE_BUCKET}/${CACHE_NAME}.tar.xz" - | tar -C ~/.isabelle -vJx || true
else
  echo "Skipping image cache read"
fi
echo "::endgroup::"

echo "::endgroup::"

echo "::group::Proof run"

export L4V_ARCH=${INPUT_L4V_ARCH}
export SKIP_DUPLICATED_PROOFS=${INPUT_SKIP_DUPS}

FAIL=0

cd l4v
if [ -n "${INPUT_SESSION}" ]
then
  ./run_tests -v ${INPUT_SESSION} || FAIL=1
else
  ./run_tests -v -x AutoCorresSEL4 || FAIL=1
fi
cd ..

echo
echo "Stats:"
~/ci-actions/aws-proofs/kernel-sloc.sh
echo ""
cd l4v; ~/ci-actions/aws-proofs/sorry-count.sh; cd ..

echo "::endgroup::"

echo "::group::Cache and logs"
if [ -n "${INPUT_CACHE_WRITE}" ]
then
  echo "Writing image cache ${CACHE_NAME}"
  # compress not too much; s3 upload is fast and compression winnings are meager
  tar -C ~/.isabelle -vc heaps/ | xz -T0 -3 - | \
    aws s3 cp - "s3://${INPUT_CACHE_BUCKET}/${CACHE_NAME}.tar.xz"
else
  echo "Skipping image cache write"
fi

# bundle up logs for artifact upload outside the VM
# xz compression does help even if there are many .gz files in this set
cd ~/.isabelle/heaps
# usually one of the two globs below will not exist
shopt -s nullglob
# do not fail the test if log collection fails
tar -Jcf ~/logs.tar.xz */log/* */*/log/* || touch ~/logs.tar.xz

# shut down VM 5 min after exiting (leave some time for log upload)
sudo shutdown -h +5
echo "::endgroup::"

exit $FAIL
