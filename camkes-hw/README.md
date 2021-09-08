<!--
     Copyright 2021, Proofcraft Pty Ltd

     SPDX-License-Identifier: CC-BY-SA-4.0
-->

# CAmkES hardware tests

This action runs the test suite for [CAmkES] on hardware. It depends on
the images built by the [camkes-test] action.

[CAmkES]: https://github.com/seL4/camkes-tool
[camkes-test]: ../camkes-test/

## Content

The entry point is the script [steps.sh].

[Build] configurations are in the respective yaml and python files in this
repository. See these files for config documentation. Both are shared via
symlink with [camkes-test] to make sure these two stay in sync. They are in
separate actions, because they are invoked differently.

The main test driver is [build.py] in this directory.

[steps.sh]: ./steps.sh
[build.py]: ./build.py
[Build]: builds.yml

## Arguments

To add or modify build configurations, edit [builds.yml][Build] in this
directory. To filter the build variants defined there for a specific run,
use one or more of the following:

- `platform`: comma separated list of platform names, e.g `PC99, ODROID_XU`.
- `mode`: comma separated list of modes, e.g. `64`.
- `name`: comma separated list of full test names, e.g. `PC99_cakeml_tipc_64`.
- `matrix`: if set, output build matrix in json and exit.
- `index`:  **(required)** the index in the build matrix. Used to get unique lock names.

## Environment

The action expects the following environment variables to be set.

- `HW_SSH`: secret ssh key for the CI account to use the machine queue at UNSW.


## Example

Put this into a `.github/workflows/` yaml file, e.g. `test.yml`:

```yaml
name: CAmkES

on:
  push:
      - master

jobs:
  build:
    name: Build
    needs: code
    runs-on: ubuntu-latest
    strategy:
      matrix:
        platform:
            - PC99
            - TX2
    steps:
    - uses: seL4/ci-actions/camkes-test@master
      with:
        xml: ${{ needs.code.outputs.xml }}
        platform: ${{ matrix.platform }}
    - name: Upload images
      uses: actions/upload-artifact@v2
      with:
        name: images-${{ matrix.platform }}
        path: '*-images.tar.gz'

  hw-run:
    name: Hardware
    runs-on: ubuntu-latest
    needs: [build]
    strategy:
      matrix:
        platform:
            - PC99
            - TX2
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
          name: images-${{ matrix.platform }}
      - name: Run
        uses: seL4/ci-actions/camkes-hw@master
        with:
          platform: ${{ matrix.platform }}
          index: $${{ strategy.job-index }}
        env:
          HW_SSH: ${{ secrets.HW_SSH }}
```
