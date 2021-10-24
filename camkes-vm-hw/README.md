<!--
     Copyright 2021, Proofcraft Pty Ltd

     SPDX-License-Identifier: CC-BY-SA-4.0
-->

# CAmkES VM hardware tests

This action runs the test suite for [CAmkES VMs] on hardware. It expects images
built by the [camkes-vm] action to be available.

[CAmkES VMs]: https://github.com/seL4/camkes-vm-examples
[camkes-vm]: ../camkes-vm/README.md

## Content

The entry point is the script [steps.sh].

[Build] configurations are in the respective yaml and python files in this
repository. See these files for config documentation.

The main test driver is [build.py] in this directory.

[steps.sh]: ./steps.sh
[build.py]: ./build.py
[Build]: builds.yml

## Arguments

To add or modify build configurations, edit [builds.yml][Build] in this
directory. To filter the build variants defined there for a specific run,
use one or more of the following:

- `name`: comma separated list of full test names, e.g. `optiplex9020`.
- `march`: comma separated list of march, e.g. `armv7a, armv8a`.

## Example

Put this into a `.github/workflows/` yaml file, e.g. `test.yml`:

```yaml
name: CAmkES VM

on:
  push:
    branches:
      - master
  pull_request:

jobs:
  build:
    name: Build
    runs-on: ubuntu-latest
    steps:
    strategy:
    - matrix:
        name:
            - optiplex9020
    - uses: seL4/ci-actions/camkes-vm@master
      with:
        name: ${{ matrix.name }}
    - name: Upload images
      uses: actions/upload-artifact@v2
      with:
        name: images-${{ matrix.name }}
        path: '*-images.tar.gz'

  hw-run:
    name: Hardware
    runs-on: ubuntu-latest
    needs: [build]
    strategy:
      matrix:
        name:
            - optiplex9020
    concurrency: camkes-hw-${{ strategy.job-index }}
    steps:
      - name: Get machine queue
        uses: actions/checkout@v2
        with:
          repository: seL4/machine_queue
          path: machine_queue
          token: ${{ secrets.PRIV_REPO_TOKEN }}
      - name: Download image
        uses: actions/download-artifact@v2
        with:
          name: images-${{ matrix.name }}
      - name: Run
        uses: seL4/ci-actions/camkes-hw@master
        with:
          name: ${{ matrix.name }}
          index: $${{ strategy.job-index }}
        env:
          HW_SSH: ${{ secrets.HW_SSH }}
```
