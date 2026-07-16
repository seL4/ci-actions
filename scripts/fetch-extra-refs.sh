#!/bin/sh
#
# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

# Fetch extra refs in $INPUT_EXTRA_REFS unless $INPUT_XML is set.
# Expects INPUT_EXTRA_REFS to be a space separated list of:
#   org/repo#num  - pull request (fetched from refs/pull/<num>/head)
#   org/repo@ref  - branch name or commit SHA (fetched as <ref>)
#
# If EXTRA_REFS_PATHS is set, assume plain git clones under these paths.
# Otherwise assume a repo manifest checkout. Specs in EXTRA_REFS_PATHS take
# precedence if both are present.
#
# Expects EXTRA_REFS_PATHS to be unset or a space separated list of:
#   org/repo=path - path of that repo, relative to the current directory

# Print the path of repo $1 ("org/repo") or nothing if not present.
repo_dir() {
  # treat repo names as case-insensitive for comparison, as in repo-util
  NAME=$(echo "$1" | tr '[:upper:]' '[:lower:]')

  for P in ${EXTRA_REFS_PATHS}
  do
    # extract the part before "=" (org/repo), case insensitive
    KEY=$(echo "${P%=*}" | tr '[:upper:]' '[:lower:]')
    if [ "${KEY}" = "${NAME}" ]
    then
      # return the part after "=" (path)
      echo "${P#*=}"
      return
    fi
  done

  # fall through to repo-util, we could in theory do both (plain checkout plus manifest)
  if [ -d .repo ]
  then
    repo-util path "$1" 2>/dev/null
  fi
}

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

    DIR=$(repo_dir "${REPO}")
    if [ -z "${DIR}" ]
    then
      echo "Skipping ${R}: ${REPO} is not part of this checkout/manifest"
      continue
    fi

    REPO_PATH="github.com/${REPO}.git"

    if [ -n "${INPUT_TOKEN}" ]
    then
      URL="https://${INPUT_TOKEN}@${REPO_PATH}"
      REPO_PATH="token@${REPO_PATH}"
    else
      URL="https://${REPO_PATH}"
    fi

    cd "${DIR}"
    echo "Fetching ${REF} from ${REPO_PATH}"
    git fetch -q --depth 1 ${URL} ${FETCH}
    git checkout -q ${CHECKOUT}
    cd - > /dev/null
  done

fi
