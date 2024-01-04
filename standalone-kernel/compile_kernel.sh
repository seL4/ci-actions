#!/bin/bash
#
# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause
#

echo "Arch: $INPUT_ARCH"
echo "Comp: $INPUT_COMPILER"

set -eu

gcc_cfg=""
llvm_triple=""
case "${INPUT_ARCH}" in
    ARM|ARM_HYP)
        gcc_cfg="AARCH32"
        llvm_triple="arm-linux-gnueabi"
        ;;
    AARCH64)
        gcc_cfg="AARCH64"
        llvm_triple="aarch64-linux-gnu"
        ;;
    RISCV32)
        gcc_cfg="RISCV32"
        # the 64-bit toolchain can build for 32-bit also.
        llvm_triple="riscv64-unknown-elf"
        ;;
    RISCV64)
        gcc_cfg="RISCV64"
        llvm_triple="riscv64-unknown-elf"
        ;;
    IA32|X64)
        # just use the standard host compiler
        ;;
    *)
        echo "Unknown ARCH '${INPUT_ARCH}'"
        exit 1
        ;;
esac

toolchain_flags=""
case "${INPUT_COMPILER}" in
    gcc)
        if [ ! -z "${gcc_cfg}" ]; then
            toolchain_flags="-D${gcc_cfg}=TRUE"
        fi
        ;;
    llvm)
        if [ ! -z "${llvm_triple}" ]; then
            toolchain_flags="-DTRIPLE=${llvm_triple}"
        fi
        ;;
    *)
        echo "Unknown COMPILER '${INPUT_COMPILER}'"
        exit 1
        ;;
esac
toolchain_flags="-DCMAKE_TOOLCHAIN_FILE=${INPUT_COMPILER}.cmake ${toolchain_flags}"

do_compile_kernel()
{
    variant=${1:-}

    build_folder="build"
    config_file="configs/${INPUT_ARCH}_verified.cmake"
    variant_info=""
    extra_params=""

    if [ ! -z "${variant}" ]; then
        case "${variant}" in
            MCS)
                build_folder="${build_folder}-${variant}"
                variant_info=" (${variant})"
                extra_params="${extra_params} -DKernelIsMCS=TRUE"
                ;;
            *)
                echo "Unknown variant '${variant}'"
                exit 1
                ;;
        esac
    fi

    # Unfortunately, CMake does not halt with a nice and clear error if the
    # config file does not exist. Instead, it logs an error that it could not
    # process the file and continues as if the file was empty. This causes some
    # rather odd errors then, so it's better to fail here with a clear message.
    if [ ! -f "${config_file}" ]; then
        echo "missing config file '${config_file}'"
        exit 1
    fi

    echo "::group::Run CMake${variant_info}"
    ( # run in sub shell
        set -x
        cmake -G Ninja -B ${build_folder} -C ${config_file} ${toolchain_flags} ${extra_params}
    )
    echo "::endgroup::"

    echo "::group::Run Ninja${variant_info}"
    ( # run in sub shell
        set -x
        ninja -C ${build_folder} kernel.elf
    )
    echo "::endgroup::"
}

# build standard kernel
do_compile_kernel
# build MCS kernel
do_compile_kernel "MCS"
