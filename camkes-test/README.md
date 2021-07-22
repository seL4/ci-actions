<!--
     Copyright 2021, Proofcraft Pty Ltd

     SPDX-License-Identifier: CC-BY-SA-4.0
-->

# CAmkES tests

This action builds and runs the test suite for [CAmkES]. The test runs can be
restricted to specific hardware `platform`/`mode`, or full test `name` for use
in a matrix build.

[CAmkES]: https://github.com/seL4/camkes-tool

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

- `platform`: comma separated list of platform names, e.g `PC99, ODROID_XU`.
- `mode`: comma separated list of modes, e.g. `64`.
- `name`: comma separated list of full test names, e.g. `PC99_cakeml_tipc_64`.
- `matrex`: if set, output build matrix in json and exit.

## Example

Put this into a `.github/workflows/` yaml file, e.g. `test.yml`:

```yaml
name: CAmkES

on:
  push:
    branches:
      - master
  pull_request:

jobs:
  test:
    name: Test
    runs-on: ubuntu-latest
    steps:
    - uses: seL4/ci-actions/camkes-test@master
```
