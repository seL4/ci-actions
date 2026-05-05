#!/bin/sh
#
# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

# Fetch extra refs in $INPUT_EXTRA_REFS unless $INPUT_XML is set.
# Expects INPUT_EXTRA_REFS to be a space separated list of:
#   org/repo#num  - pull request (fetched from refs/pull/<num>/head)
#   org/repo@ref  - branch name or commit SHA (fetched as <ref>)

if [ -z "${INPUT_XML}" ] && [ -n "${INPUT_EXTRA_REFS}" ]
then
  echo "extra refs: ${INPUT_EXTRA_REFS}"

  for R in ${INPUT_EXTRA_REFS}
  do
    case "${R}" in
      *#*)
        REPO=${R%#*}
        ID=${R#*#}
        REF="refs/pull/${ID}/head"
        FETCH="${REF}:${REF}"
        CHECKOUT="${REF}"
        ;;
      *@*)
        REPO=${R%@*}
        REF=${R#*@}
        FETCH="${REF}"
        CHECKOUT="FETCH_HEAD"
        ;;
      *)
        echo "Unrecognized extra-ref token: ${R}" >&2
        exit 1
        ;;
    esac

    REPO_PATH="github.com/${REPO}.git"

    if [ -n "${INPUT_TOKEN}" ]
    then
      URL="https://${INPUT_TOKEN}@${REPO_PATH}"
      REPO_PATH="token@${REPO_PATH}"
    else
      URL="https://${REPO_PATH}"
    fi

    cd $(repo-util path ${REPO})
    echo "Fetching ${REF} from ${REPO_PATH}"
    git fetch -q --depth 1 ${URL} ${FETCH}
    git checkout -q ${CHECKOUT}
    cd - > /dev/null
  done

fi
