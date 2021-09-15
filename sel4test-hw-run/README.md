<!--
     Copyright 2021, Proofcraft Pty Ltd

     SPDX-License-Identifier: CC-BY-SA-4.0
-->

# seL4Test Hardware Test Runs

This action runs [sel4test] images on the hardware test platforms.
The test runs can be restricted to specific `arch`, `mode`, `march`,
and `platform` settings. For machine queue locks, the action needs to
know the index number of the current job in matrix builds.

The test run expects a pre-built image produced by the [sel4test-hw]
action, determines which board the test is for, reserves the machine
queue at UNSW for that and runs the image.

Currently, authentication is via ssh and needs an active UNSW account
with access to the machine queue server.

[sel4test]: https://github.com/seL4/sel4test
[sel4test-hw]: ../sel4test-hw/

## Content

The entry point is the script [steps.sh].

[Build] and [platform] configurations are in the respective yaml and python
files in this repository. They are shared with the [sel4test-hw] action to
make sure these stay in sync.

The main test driver is [build.py] in this directory, also shared with the
[sel4test-hw] action to make sure the same filters are applied.

[steps.sh]: ./steps.sh
[build.py]: ./build.py
[platform]: ../seL4-platforms/platforms.yml
[Build]: builds.yml

## Arguments

To add or modify configurations, edit [builds.yml][Build] in this
directory. To filter the build variants defined there for a specific run,
use one or more of the following:

- `arch`: comma separated list of architecture to filter on, e.g `arm, riscv`.
- `march`: comma separated list of `march` flags, e.g. `armv7a, nehalem`
- `mode`: one of `{32, 64}`
- `compiler`: one of `{gcc, clang}`
- `debug`: comma separated list of debug levels from `{debug, release,
  verification}`  to filter on.
- `platform`: platform name for a test run
- `index`: **(required)** job index in matrix builds (use 0 if no matrix build)

## Environment

The action expects the following environment variables to be set.

- `HW_SSH`: secret ssh key for the CI account to use the machine queue at UNSW.

See the [seL4/seL4](https://github.com/seL4/seL4) repository for an example.
