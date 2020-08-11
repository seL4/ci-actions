#!/bin/bash
#
# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause
#

echo "Arch: $INPUT_ARCH"
echo "Comp: $INPUT_COMPILER"
echo "Pyth: $INPUT_PYTHON"

set -e

mkdir build
cd build

extra_config=""

case $INPUT_ARCH in
    ARM*)
        case $INPUT_COMPILER in
            gcc)
                extra_config="${extra_config} -DAARCH32=TRUE"
                ;;
            llvm)
                extra_config="${extra_config} -DTRIPLE=arm-linux-gnueabi"
                ;;
            *)
                echo "Unknown input compiler"
                exit 1
        esac
        ;;
    RISCV64)
        extra_config="${extra_config} -DRISCV64=TRUE"
        ;;
    X64)
        # no config needed
        ;;
    *)
        echo "Unknown ARCH"
        exit 1
esac

if [ "$INPUT_PYTHON" = "py3" ]; then
    extra_config="${extra_config} -DPYTHON=python3"
fi

echo "::group::Run CMake"
set -x
cmake -DCMAKE_TOOLCHAIN_FILE="$INPUT_COMPILER".cmake -G Ninja -C ../configs/"$INPUT_ARCH"_verified.cmake $extra_config ../
set +x
echo "::endgroup::"

echo "::group::Run Ninja"
set -x
ninja kernel.elf
set +x
echo "::endgroup::"
