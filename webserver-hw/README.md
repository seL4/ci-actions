<!--
     Copyright 2022, Proofcraft Pty Ltd

     SPDX-License-Identifier: CC-BY-SA-4.0
-->

# seL4 web server demo app hardware tests

This action runs the test suite for the [seL4 web server] on hardware. It expects images
built by the [webserver] action to be available.

[seL4 web server]: https://github.com/seL4/sel4webserver
[webserver]: ../webserver/README.md

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

- `platform`: comma separated list of platforms to filter on, e.g. `ODROID_XU4`.
- `index`: index of the hardware job in the build matrix.

## Example

Put this into a `.github/workflows/` yaml file, e.g. `test.yml`:

```yaml
name: seL4 Web Server

on:
  push:
    branches:
      - master
  pull_request_target:

jobs:
  build:
    name: Build
    runs-on: ubuntu-latest
    steps:
    strategy:
    - matrix:
        platform:
            - ODROID_XU4
    - uses: seL4/ci-actions/webserver@master
      with:
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
            - ODROID_XU4
    concurrency: webserver-hw-${{ strategy.job-index }}
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
          index: ${{ strategy.job-index }}
      - name: Run
        uses: seL4/ci-actions/webserver-hw@master
        with:
          platform: ${{ matrix.platform }}
          index: $${{ strategy.job-index }}
        env:
          HW_SSH: ${{ secrets.HW_SSH }}
```
