#!/bin/bash
#
# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause
#

set -e

function usage () {
    cat <<EOF 1>&2
USAGE: test_munge.sh [-h|-d|-v] <git-ref> [git-ref]
  -d    Preserve files
  -a    AST check
  -v    Verbose
  -c    Colorized output
  -p    Path to th repo collection
  -h    Print help
EOF
}


# Argument parsing
while getopts ":hadvcp:" opts
do
    case $opts in
        h)
            usage
            exit 0
            ;;
        d)
            DUMP=true
            ;;
        v)
            VERBOSE=true
            ;;
        a)  AST=true
            AST_OPTS="-a"
            ;;
        c)  COLOR=''
            ;;
        p)  REPO_DIR="${OPTARG}"
            if ! [ -d "${REPO_DIR}" ]
            then
                echo >&2 "-p: ${REPO_DIR} is not a directory (cwd: $(pwd))"
                exit 1
            fi
            DIR_OPTS="-p ${REPO_DIR}"
            ;;
        *)
            echo "Invalid option: -${OPTARG}" >&2
            ;;
    esac
done

#color
RED=${COLOR+'\033[0;31m'}
YEL=${COLOR+'\033[0;33m'}
GRE=${COLOR+'\033[0;32m'}
NC=${COLOR+'\033[0m'}

shift $((OPTIND - 1))
REF1=$1
REF2=$2

[ -z ${DUMP+x} ] && trap "rm -f ckernel_*.txt" EXIT

[ -z ${REF1} ] && (echo >&2 "At least 1 ref is required"; exit 1)
[ $# -gt 2 ] && echo "Ignoring ${@:3}"

# Find the script directory
SCRIPT_DIR=$(cd $(dirname "$0") && pwd)
[ -d "${SCRIPT_DIR}" ] || (echo >&2 "no script dir"; exit 1)

MAKE_MUNGE=${SCRIPT_DIR}/make_munge.sh

echo -e "${YEL}REF1=seL4@${REF1}"
echo "REF2=seL4@${REF2}"
echo "L4V_ARCH=${L4V_ARCH}"
echo -e "WORKING...${NC}"

if [ -z ${VERBOSE} ]
then
    ${MAKE_MUNGE} ${DIR_OPTS} ${AST_OPTS} ${REF1} >/dev/null
else
    ${MAKE_MUNGE} ${DIR_OPTS} ${AST_OPTS} ${REF1}
fi

sort -o ckernel_names_1.txt ckernel_names.txt
rm ckernel_names.txt
mv kernel_all.txt kernel_all_1.txt
[ -z ${AST+x} ] || mv ckernel_ast.txt ckernel_ast_1.txt

if [ -z ${VERBOSE} ]
then
    ${MAKE_MUNGE} ${DIR_OPTS} ${AST_OPTS} ${REF2} >/dev/null
else
    ${MAKE_MUNGE} ${DIR_OPTS} ${AST_OPTS} ${REF2}
fi
sort -o ckernel_names_2.txt ckernel_names.txt
rm ckernel_names.txt
mv kernel_all.txt kernel_all_2.txt
[ -z ${AST+x} ] || mv ckernel_ast.txt ckernel_ast_2.txt

ERRORS=false
# Check for differences in
echo -en "${RED}"
if ! diff -q ckernel_names_1.txt ckernel_names_2.txt >/dev/null
then
    echo -e "${RED}"
    echo "#################################"
    echo "#   Some symbols have changed   #"
    echo -e "#################################\n"
    echo -e "\n${YEL}Symbols diff:${NC}"
    diff -uw ckernel_names_1.txt ckernel_names_2.txt || true
    ERRORS=true
fi

echo -en "${RED}"
if ! ([ -z ${AST+x} ] || diff -q ckernel_ast_1.txt ckernel_ast_2.txt >/dev/null)
then
    echo -e "${RED}"
    echo "#################################"
    echo "#   The ASTs differ             #"
    echo -e "#################################\n"
    echo -e "${NC}${YEL}"
    ERRORS=true
fi

echo -en "${NC}"

if ! ${ERRORS}
then echo -e "${GRE}Clean diff, test PASSED for L4V_ARCH=${L4V_ARCH}.${NC}"
else
    echo -en "${RED}"
    if ! diff -q kernel_all_1.txt kernel_all_2.txt
    then
        echo -e "${RED}"
        echo "#################################"
        echo "#   Something has changed       #"
        echo -e "#################################\n"
        echo -e "\n${NC}${YEL}kernel_all diff:${NC}"
        grep -v "/tmp/munge-" kernel_all_1.txt > clean_kernel_all_1.txt
        grep -v "/tmp/munge-" kernel_all_2.txt > clean_kernel_all_2.txt
        diff -uw clean_kernel_all_1.txt clean_kernel_all_2.txt || true
    fi
    echo
    echo -e "${RED}Preprocess test FAILED.${NC}"
    exit 1
fi
