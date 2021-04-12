#!/bin/bash
#
# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause

set -e

echo "::group::Setting up"
echo "Installing python 2.7"
sudo apt-get install -qq python2-dev > /dev/null
sudo update-alternatives --install /usr/bin/python python /usr/bin/python2 1
python --version
hg --version

echo "Setting up correct version of hg-git"
ACTION_DIR="${SCRIPTS}/../${INPUT_ACTION_NAME}"

cd "${ACTION_DIR}"
export IM_DIR="$(pwd)"

"${IM_DIR}/bin/im-setup"

rm -rf repos lib
echo "::endgroup::"

echo "::group::Running mirror script"

exec "$IM_DIR/bin/im-env" "$IM_DIR" im-main https://${ISA_MIRROR_TOKEN}@github.com

echo "::endgroup::"
