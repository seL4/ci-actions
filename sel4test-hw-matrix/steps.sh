#!/bin/bash
#
# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause
#

set -e

echo "::group::Setting up"
export ACTION_DIR="${SCRIPTS}/.."

# python env
sudo apt-get install -y --no-install-recommends libffi-dev
. ${SCRIPTS}/setup-python-venv.sh
pip3 install "junitparser==3.*" sel4-deps
export PYTHONPATH="${ACTION_DIR}/seL4-platforms"
echo "::endgroup::"

case "${INPUT_MATRIX}" in
  build) MATRIX_ARG="--build-matrix" ;;
  *)     MATRIX_ARG="--matrix" ;;
esac

python3 "${ACTION_DIR}/${INPUT_ACTION_NAME}/build.py" "${MATRIX_ARG}"
