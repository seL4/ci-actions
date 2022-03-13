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

export L4V_ARCH=${INPUT_L4V_ARCH}
export L4V_FEATURES=${INPUT_L4V_FEATURES}

CACHE_NAME=${INPUT_CACHE_NAME}
if [ -z "${CACHE_NAME}" ]
then
  # construct default cache name
  BRANCH=${INPUT_ISA_BRANCH:-default}
  MANIFEST=${INPUT_MANIFEST:-devel}
  CACHE_NAME="${GITHUB_REPOSITORY}-${BRANCH}-${MANIFEST}-${L4V_ARCH}${L4V_FEATURES:+-${L4V_FEATURES}}"
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

export SKIP_DUPLICATED_PROOFS=${INPUT_SKIP_DUPS}

FAIL=0

L4V_DIR="$PWD/l4v"
if [ -n "${INPUT_SESSION}" ]
then
  do_run_tests() { (cd "$L4V_DIR" && ./run_tests -v ${INPUT_SESSION} "$@"); }
else
  do_run_tests() { (cd "$L4V_DIR" && ./run_tests -v -x AutoCorresSEL4 "$@"); }
fi

do_run_tests || FAIL=1

echo
echo "Stats:"
~/ci-actions/aws-proofs/kernel-sloc.sh
echo ""
cd l4v; ~/ci-actions/aws-proofs/sorry-count.sh; cd ..

echo "::endgroup::"

echo "::group::Cache"
if [ -n "${INPUT_CACHE_WRITE}" ]
then
  echo "Writing image cache ${CACHE_NAME}"
  # compress not too much; s3 upload is fast and compression winnings are meager
  tar -C ~/.isabelle -vc heaps/ | xz -T0 -3 - | \
    aws s3 cp - "s3://${INPUT_CACHE_BUCKET}/${CACHE_NAME}.tar.xz"
else
  echo "Skipping image cache write"
fi
echo "::endgroup::"

# Prepare artifacts for upload outside the VM
mkdir -p ~/artifacts

# Export C graph-lang for binary verification
if [ -n "$INPUT_SIMPL_EXPORT" ]; then
  echo "::group::C graph-lang export"
  SIMPL_EXPORT_FILE="$L4V_DIR/proof/asmrefine/export/$L4V_ARCH/CFunDump.txt"
  if [ -f "$SIMPL_EXPORT_FILE" ]; then
    echo "Found CFunctions.txt"
    xz < "$SIMPL_EXPORT_FILE" > ~/artifacts/CFunctions.txt.xz
  elif do_run_tests -L | grep -q SimplExportAndRefine; then
    # SimplExportAndRefine was among the tests that should have run,
    # which means we want a C graph export.
    # However, we didn't get one, because the SimplExportAndRefine
    # image was cached.
    # So we force another export, but don't need to check refinement.
    echo "Regenerating CFunctions.txt"
    cd "$L4V_DIR/proof" && make SimplExport
    xz < "$SIMPL_EXPORT_FILE" > ~/artifacts/CFunctions.txt.xz
  else
    echo "Nothing to export"
  fi
  echo "::endgroup::"
fi

# Collect logs.
echo "::group::Logs"
# xz compression does help even if there are many .gz files in this set
cd ~/.isabelle/heaps
# usually one of the two globs below will not exist
shopt -s nullglob
# do not fail the test if log collection fails
tar -Jcf ~/logs.tar.xz */log/* */*/log/* || touch ~/logs.tar.xz
echo "::endgroup::"

# shut down VM 5 min after exiting (leave some time for artifact upload)
sudo shutdown -h +5

exit $FAIL
