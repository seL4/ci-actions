#!/bin/bash
#
# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause

set -e

echo "::group::Setting up"
echo "Installing python 2.7"

echo "  > Installing python build dependencies"
sudo apt-get update
sudo apt-get install -qq make build-essential libssl-dev zlib1g-dev \
                         libbz2-dev libreadline-dev libsqlite3-dev curl git \
                         libncursesw5-dev xz-utils tk-dev libxml2-dev \
                         libxmlsec1-dev libffi-dev liblzma-dev

echo "  > Installing pyenv"
git clone -b v2.6.1 --depth 1 https://github.com/pyenv/pyenv.git ~/.pyenv
export PYENV_ROOT="$HOME/.pyenv"
[ -d $PYENV_ROOT/bin ] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init - bash)"

echo "  > Installing python 2.7"
pyenv install 2.7
pyenv global 2.7

echo "  > Versions"
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
