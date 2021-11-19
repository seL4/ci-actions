<!--
     Copyright 2021, Proofcraft Pty Ltd

     SPDX-License-Identifier: CC-BY-SA-4.0
-->

# seL4Test Hardware Run Matrix

This action generates a GitHub build matrix for the [sel4test-hw-run] action from
the hardware platforms listed as available in [platforms.yml][] in this repo.

[platforms.yml]: ../seL4-platforms/platforms.yml
[sel4test-hw-run]: ../sel4test-hw-run/README.md

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
[sel4test-hw]: ../sel4test-hw/README.md

## Arguments

This action has no input arguments.
