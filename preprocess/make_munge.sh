#!/bin/bash
#
# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause
#

set -e

usage() {
    cat <<EOF 1>&2
USAGE: make_munge.sh [-h|-o <dir>|-p <dir>] [git-ref]
  -o         Output directory
  -p         Path to the repo collection
  -a         Generate AST
  -h         Print help
  git-ref    Use this seL4 ref, default HEAD
EOF
}

fail() {
  echo $1 >&2
  exit 1
}

# Defaults
SEL4REF=HEAD
OUT_DIR=.

# Script directory
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
# If no path given, assume local checkout
REPO_DIR="${SCRIPT_DIR}/../.."


# Argument parsing
while getopts ":hao:p:" opts
do
    case $opts in
        h)
            usage
            exit 0
            ;;
        o)
            OUT_DIR=${OPTARG}
            if [ ! -d "${OUT_DIR}" ]
            then
                fail "-o: ${OUT_DIR} is not a directory (cwd: $(pwd))"
            fi
            ;;
        a)  BUILD_AST=true
            ;;
        p)  REPO_DIR="${OPTARG}"
            if ! [ -d "${REPO_DIR}" ]
            then
                fail "-p: ${REPO_DIR} is not a directory (cwd: $(pwd))"
            fi
            ;;
        *)
            fail "Invalid option: -${OPTARG}"
    esac
done

shift $((OPTIND - 1))
[ $# -gt 0 ] && SEL4REF_RAW=$1 && shift
[ $# -gt 0 ] && echo >&2 "Ignoring arguments: $*"

# Find the l4v/ base folder
: ${L4V_DIR:=$(cd "${REPO_DIR}/l4v" && pwd)}
[ -d "${L4V_DIR}" ] || fail "Couldn't find l4v; tried ${L4V_DIR}"

# Find the c-parser directory
: ${CPARSER_DIR:=$(cd "${L4V_DIR}/tools/c-parser" && pwd)}
[ -d "${CPARSER_DIR}" ] || fail "Couldn't find c-parser; tried ${CPARSER_DIR}"

# Find the seL4/ base folder
: ${SEL4_DIR:=$(cd "${REPO_DIR}/seL4" && pwd)}
[ -d "${SEL4_DIR}" ] || fail "Couldn't find seL4; tried ${SEL4_DIR}"

# Create temporary directory to work in
MUN_TMP=$(mktemp --tmpdir -d munge-seL4.XXXXXXXX) || \
    fail "Error creating temporary directory"
trap "rm -rf ${MUN_TMP}" EXIT
mkdir -p "${MUN_TMP}"

# Defaults
export L4V_ARCH=${L4V_ARCH:="ARM"}

# Useful refs
CKERNEL_DIR=${L4V_DIR}/spec/cspec/c
CKERNEL_REL=build/${L4V_ARCH}/kernel_all.c_pp
CKERNEL=${CKERNEL_DIR}/${CKERNEL_REL}
NAMES_FILE=${MUN_TMP}/ckernel_names.txt
AST_FILE=${MUN_TMP}/ckernel_ast.txt
SEL4_CLONE=${MUN_TMP}/sel4-clone
: ${CPARSER_FLAGS:="--underscore_idents"}

# Clone seL4 repo into temporary folder
git clone -q -n "${SEL4_DIR}" "${SEL4_CLONE}" || \
    fail "Error cloning seL4 repo from \n ${SEL4_DIR}"

# Getting correct reference
if [ -n "${SEL4REF_RAW}" ]
then
    SEL4REF=$(git -C "${SEL4_DIR}" rev-parse --short "${SEL4REF_RAW}") || \
        fail "Error retrieving reference ${SEL4REF_RAW} on local seL4 repo"
fi

# Checking out the reference
git -C "${SEL4_CLONE}" checkout -q "${SEL4REF}" || \
    fail "Error checking out reference in temporary repo"

# Save the current kernel_all.c_pp
if [ -f "${CKERNEL}" ]
then
    mv "${CKERNEL}" "${CKERNEL}.orig"
    # move back kernel_all.c_pp
    trap 'mv "${CKERNEL}.orig" "${CKERNEL}"' EXIT
fi

# build kernel_all.c_pp
make -C "${CKERNEL_DIR}" "SOURCE_ROOT=${SEL4_CLONE}" "${CKERNEL_REL}"

# does the c-parser exist?
CPARSER_EXE_REL=standalone-parser/${L4V_ARCH}/c-parser
CPARSER_EXE=${CPARSER_DIR}/${CPARSER_EXE_REL}
[ -x "${CPARSER_EXE}" ] || (echo "Building c-parser..." ; make -C "${CPARSER_DIR}" "cparser_tools")

# build name munge file
"${CPARSER_EXE}" "${CPARSER_FLAGS}" "--munge_info_fname=${NAMES_FILE}" "${CKERNEL}"
# build ast
[ -z ${BUILD_AST+x} ] || "${CPARSER_EXE}" "${CPARSER_FLAGS}" --ast "${CKERNEL}" >"${AST_FILE}"

mv "${CKERNEL}" "${OUT_DIR}/kernel_all.txt"

# copy generated results to OUT_DIR
cp "${NAMES_FILE}" "${OUT_DIR}/ckernel_names.txt"
[ -z ${BUILD_AST+x} ] || cp "${AST_FILE}" "${OUT_DIR}/ckernel_ast.txt"
