<!--
     Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)

     SPDX-License-Identifier: CC-BY-SA-4.0
-->

# Preprocess Check for seL4

This action checks whether a change to the seL4 code could affect the proofs.
It compares the preprocessed sources for the verified configurations of seL4
with the most recent verified version in
<https://github.com/seL4/verification-manifest/>.

If nothing relevant changed, the change is safe to accept with respect to the
proofs, after the usual review, quality control, and tests.

If the test fails, it does not mean the proofs are necessarily affected, it
only means the full proofs should be run on the changed version to see if
they break. If they do break, they may still be easy to fix. Feel free to
ping the seL4 @verification team in that case, so they can take a look.

## Content

The entry point is the script [`steps.sh`](steps.sh/)

## Arguments

### L4V_ARCH

The `L4V_ARCH` input is the architecture tag that selects the verified
configuration to be test. Valid values are `ARM`, `ARM_HYP`, `AARCH64`,
`RISCV64`, `X64`.

They are best used in a matrix to run the test for all architectures
concurrently.

## Example

Put this into a `.github/workflows/` yaml file, e.g. `preprocess.yml`:

```yaml
name: Preprocess

on: [pull_request]

jobs:
  preprocess:
    name: Preprocess
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        arch: [ARM, ARM_HYP, AARCH64, RISCV64, X64]
    steps:
    - uses: seL4/ci-actions/preprocess@master
      with:
        L4V_ARCH: ${{ matrix.arch }}
```

## What does the check do?

The main test script is [`test_munge.sh`](test_munge.sh/) (named such,
because in the distant past it was about name munging only).

The script expects to run in the verification repo manifest context and
takes two git revisions of the `seL4` repository:

 - TIP: the latest revision for which the proofs work;
    usually from `verification-manifest`

 - HEAD: the changed revision; usually the head revision of
    the pull request

With this the script

1. clones both TIP and HEAD next to each other,
2. generates `kernel_all.c_pp` for both (for `$L4V_ARCH`)
3. runs the standalone C-parser from `l4v/tools` on both versions, generating:
   - a list of names assigned to variables and their types
   - the AST of the whole kernel
4. compares these files using basic `diff`

The test succeeds if there are no differences and fails with an error message
otherwise.

Remarks:

 - This is just a fancy and somewhat syntax-aware diff between 2 versions of `kernell_all.c_pp`

 - If the diff contains only changes to comments, whitespace or formatting,
   it's still fine to accept the change despite preprocess test failure,
   unless the comment in question contains verification annotations such
   as `AUXUPD`, `GHOSTUPD`, or `MODIFIES`

 - No Isabelle proofs are performed in this check. They may still be
    unaffected by the change, or easy to update.

 - No proof engineers are harmed while performing this test. Have fun!
