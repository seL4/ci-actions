<!--
     Copyright 2021, Proofcraft Pty Ltd

     SPDX-License-Identifier: CC-BY-SA-4.0
-->

# Deploy verification-manifest updates

Deals with automatic updates to the [verification-manifest] repository after
successful builds in either the [seL4] preprocess run or the [l4v] proof test.

[verification-manifest]: https://github.com/seL4/verification-manifest
[seL4]: https://github.com/seL4/seL4
[l4v]: https://github.com/seL4/l4v

## Content

The steps of this action are defined in [steps.sh].

The [staging-manifest] script updates [verification-manifest] from after a
successful [proof run]. This can update the reference of any project in the
[verification-manifest].

The [seL4-pp] script updates the `seL4` reference in [verification-manifest]
after a successful run of the [preprocess] test, this usually means `seL4` was
updated but did not introduce any changes to the code-base used for
verification.

[preprocess]: ../preprocess/
[staging-manifest]: ./staging-manifest
[seL4-pp]: ./seL4-pp
[steps.sh]: ./steps.sh

## Arguments

- `xml`: the manifest file to update to
- `preprocess`: if set, deploy for a preprocess bump instead of proof run

## Environment

- `GH_SSH`: ssh key with write access to [verification-manifest]

## Example

```yml
jobs:
  code:
    runs-on: ubuntu-latest
    outputs:
      xml: ${{ steps.repo.outputs.xml }}
    steps:
    - id: repo
      uses: seL4/ci-actions/repo-checkout@master
      with:
        manifest_repo: verification-manifest
        manifest: devel.xml

  proofs:
    needs: code
    runs-on: ubuntu-latest
    strategy:
      matrix:
        arch: [ARM, ARM_HYP, RISCV64, X64]
    steps:
    - name: Proofs
      uses: seL4/ci-actions/aws-proofs@master
      with:
        L4V_ARCH: ${{ matrix.arch }}
        xml: ${{ needs.code.outputs.xml }}

  deploy:
    runs-on: ubuntu-latest
    needs: [code, proofs]
    steps:
    - uses: seL4/ci-actions/l4v-deploy@master
      with:
        xml: ${{ needs.code.outputs.xml }}
      env:
        GH_SSH: ${{ secrets.CI_SSH }}
```
