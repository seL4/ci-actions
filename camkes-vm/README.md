<!--
     Copyright 2021, Proofcraft Pty Ltd

     SPDX-License-Identifier: CC-BY-SA-4.0
-->

# CAmkES VM tests

This action builds and runs the test suite for [CAmkES VMs]. The test runs can
be restricted to a specific test `name` for use in a matrix build.

[CAmkES VMs]: https://github.com/seL4/camkes-vm-examples

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
- `xml`: explicit manifest to use (instead of `seL4/camkes-vm-examples-manifest`).

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
  test:
    name: Test
    runs-on: ubuntu-latest
    steps:
    - uses: seL4/ci-actions/camkes-vm@master
      with:
        name: optiplex9020
```
