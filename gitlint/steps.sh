#!/bin/bash
#
# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause

set -e

[ -z ${GITHUB_BASE_REF+x} ] && (echo "Action only works on pull requests"; exit 1)

echo "::group::Setting up"
install-python.sh

echo "Installing gitlint tool"
pip install -q gitlint

checkout.sh
# fetch pull request base
fetch-base.sh

echo "::endgroup::"

echo

HEAD_SHA=$(jq -r '.pull_request.head.sha' ${GITHUB_EVENT_PATH})
gitlint --commits ${GITHUB_BASE_REF}..${HEAD_SHA} lint