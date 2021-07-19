<!--
     Copyright 2021, Proofcraft Pty Ltd

     SPDX-License-Identifier: CC-BY-SA-4.0
-->

# seL4 Tutorial tests

This action builds and runs the test suite for the [seL4 Tutorials]. The test
runs can be restricted to specific `arch`, `app`, or full test `name` for use in
a matrix build.

The test runs a build from the default [sel4-tutorials-manifest], advancing the
`sel4-tutorials` repository to the branch of the pull request the test is called
on.

[seL4 Tutorials]: https://github.com/seL4/sel4-tutorials
[sel4-tutorials-manifest]: https://github.com/seL4/sel4-tutorials-manifest

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

- `arch`: comma separated list of architecture to filter on, e.g `arm, x86`.
- `app`: comma separated list of `app` names, e.g. `hello-world`.
- `name`: comma separated list of full test names, e.g. `pc99_hello-world`.
- `matrix`: set to `true` to set the GitHub output variable `matrix` to a list
            of tests fitting the selected criteria

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
    name: Tutorial Solution
    runs-on: ubuntu-latest
    strategy:
      matrix:
        app:
        - capabilities
        - dynamic-1
        - dynamic-2
        - dynamic-3
        - dynamic-4
        - hello-camkes-0
        - hello-camkes-1
        - hello-camkes-2
        - hello-camkes-timer
        - hello-world
        - interrupts
        - ipc
        - mapping
        - notifications
        - untyped
        - threads
        - fault-handlers
        - mcs
    steps:
    - uses: seL4/ci-actions/tutorials@master
      with:
        app: ${{ matrix.app }}
```
