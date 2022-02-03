<!--
     Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)

     SPDX-License-Identifier: CC-BY-SA-4.0
-->

# Stand-alone kernel compilation

This action checks whether a change to the seL4 code breaks compilation.
It compiles the kernel as a stand-alone item on all the verified configurations
of seL4. It is considered 'stand-alone' because it does not compile anything else,
so there is no user-space or supporting code.

If no exit codes are thrown, it means that the change was able to compile successfully.

## Content

The entry point is the script [`compile_kernel.sh`](compile_kernel.sh/)

## Arguments

### ARCH

The `ARCH` input is the architecture tag that selects the configuration to be compiled.
Valid values are `ARM`, `ARM_HYP`, `AARCH64`, `RISCV64`, `X64`.

### COMPILER

The `COMPILER` input is the the choice of which compiler suite is to be used.
Valid values are `gcc`, `llvm`.
Note that not all `ARCH`s support all compilers.

They are best used in a matrix to run the test for all architectures
concurrently.

## Example

Put this into a `.github/workflows/` yaml file, e.g. `stand-alone-compile.yml`:

```yaml
standalone_kernel:
    name: Compile kernel
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        arch: [ARM, ARM_HYP, AARCH64, RISCV64, X64]
        compiler: [gcc, llvm]
        exclude:
          # llvm RISCV64 compilation is not currently supported
          - arch: RISCV64
            compiler: llvm
    steps:
    - uses: actions/checkout@v2
    - uses: seL4/ci-actions/standalone-kernel@master
      with:
        ARCH: ${{ matrix.arch }}
        COMPILER: ${{ matrix.compiler }}
```
