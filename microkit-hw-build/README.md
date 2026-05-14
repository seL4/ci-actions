<!--
     Copyright 2026, UNSW

     SPDX-License-Identifier: CC-BY-SA-4.0
-->

# Microkit Hardware Builds

This action builds test examples for the [microkit] hardware test platforms.

Refer to the [microkit-hw-run README] for more information.

[microkit]: https://docs.sel4.systems/projects/microkit/
[microkit-hw-run README]: ../microkit-hw-run/README.md

## Content

The entry point is the script [steps.sh].

The main test driver [build.py] in this directory is shared with (a symlink to)
the [microkit-hw-run build.py] to make sure the same filters are applied.

[steps.sh]: ./steps.sh
[build.py]: ./build.py
[microkit-hw-run build.py]: ../microkit-hw-run/build.py

## Arguments

To add or modify platform options, create a PR to the [Microkit repository].

[Microkit repository]: https://github.com/seL4/microkit

To filter the build variants defined there for a specific run, use one or more
of the following action inputs:

- `board`: comma separated list of Microkit board names to filter, e.g. `maaxboard,star64`.
- `config`: comma separated list of Microkit config names, e.g. `debug,release`.
- `march`: comma separated list of Microkit board architectures, e.g. `aarch64,riscv64,x86_64`.

## Environment

The action expects the following environment variables to be set:

- `TEST_CASES`: the JSON output from the [microkit-hw-matrix] 'test_cases' GitHub output.
- `MICROKIT_SDK`: the path to the prebuild Microkit SDK.

[microkit-hw-matrix]: ../microkit-hw-matrix/README.md
