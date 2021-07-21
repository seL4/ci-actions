<!--
     Copyright 2021, Proofcraft Pty Ltd

     SPDX-License-Identifier: CC-BY-SA-4.0
-->

# seL4 Rumprun Hello World tests

This action builds and runs the test suite for seL4 [RumpRun]. The test runs can
be restricted to specific hardware `req`, `mode`, or full test `name` for use in
a matrix build.

[RumpRun]: https://github.com/seL4/rumprun-sel4-demoapps

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

- `req`: comma separated list of hardware requirements, e.g `sim, haswell`.
- `mode`: comma separated list of modes, e.g. `32`.
- `name`: comma separated list of full test names, e.g. `PC99_32_sim`.

## Example

Put this into a `.github/workflows/` yaml file, e.g. `test.yml`:

```yaml
name: Test

on:
  push:
    branches:
      - master
  pull_request:

jobs:
  test:
    name: RumpRun
    runs-on: ubuntu-latest
    steps:
    - uses: seL4/ci-actions/rump-hello@master
```
