<!--
     Copyright 2021, Proofcraft Pty Ltd

     SPDX-License-Identifier: CC-BY-SA-4.0
-->

# Deploy manifest updates

Deals with automatic updates to the `default.xml` file in manifest repositories
such as [sel4test-manifest] after successful tests.

[sel4test-manifest]: https://github.com/seL4/sel4test-manifest

## Content

The steps of this action are defined in [steps.sh].

The main manifest update work happens in the `releaseit` script of the
seL4_release repository that is currently still private (to be published).

[steps.sh]: ./steps.sh

## Arguments

- `xml`: the manifest file to update to
- `manifest_repo`: the manifest repository to deploy to

## Environment

- `GH_SSH`: ssh key with write access to the manifest repository

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
        manifest_repo: sel4test-manifest
        manifest: master.xml

  test:
    needs: code
    runs-on: ubuntu-latest
    steps:
    - uses: seL4/ci-actions/...@master
      with:
        xml: ${{ needs.code.outputs.xml }}

  deploy:
    runs-on: ubuntu-latest
    needs: [code, test]
    steps:
    - uses: seL4/ci-actions/manifest-deploy@master
      with:
        xml: ${{ needs.code.outputs.xml }}
        manifest_repo: sel4test-manifest
      env:
        GH_SSH: ${{ secrets.CI_SSH }}
```
