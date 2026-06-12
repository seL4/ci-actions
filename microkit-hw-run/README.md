<!--
     Copyright 2026, UNSW

     SPDX-License-Identifier: CC-BY-SA-4.0
-->

# Microkit Hardware Test Runs

This action runs test examples for the [microkit] hardware test platforms.
The tests can be restricted to specific `board`, `config`, and `march` configurations,
which we use to create a GitHub actions runner matrix.

The test expects pre-built images produced by the [microkit-hw-build] action,
and performs the necessary steps to run this image on the [machine queue] at
UNSW.

The Microkit HW builds & tests are different to many of the other actions in
this repository; rather than the builds being driven by a 'build.yml' and
'platforms.yml' file within this repository, it extracts a list of test cases
/ platforms from the Microkit SDK build system directly. This is the `TEST_CASES`
variable that expects a JSON file used in both [microkit-hw-build] and here.

The [microkit-hw-build] action does not build the Microkit SDK, but instead
a particular example for a particular board from a pre-built Microkit SDK.
The unpacked Microkit SDK is passed in as the `MICROKIT_SDK` environment variable
from earlier steps within a GitHub actions workflow. In the Microkit repo's CI
environment, this is built from source directly, but could be fetched from
an active release as desired.

[microkit]: https://docs.sel4.systems/projects/microkit/
[microkit-hw-build]: ../microkit-hw-build/README.md
[machine queue]: https://github.com/seL4/machine_queue

## Content

The entry point is the script [steps.sh].

The main test driver [build.py] in this directory is shared with microkit-hw-matrix
and microkit-hw-builds.

[steps.sh]: ./steps.sh
[build.py]: ./build.py

## Arguments

To add or modify platform options, create a PR to the [Microkit repository].

[Microkit repository]: https://github.com/seL4/microkit

To filter the build variants defined there for a specific run, use one or more
of the following action inputs:

- `board`: comma separated list of Microkit board names to filter, e.g. `maaxboard,star64`.
- `config`: comma separated list of Microkit config names, e.g. `debug,release`.
- `march`: comma separated list of Microkit board architectures, e.g. `aarch64,riscv64,x86_64`.
- `index`: **(required)** job index in matrix builds (use 0 if no matrix build)

## Environment

The action expects the following environment variables to be set:

- `HW_SSH`: secret SSH key for the CI account to use the machine queue at UNSW.
- `TEST_CASES`: the JSON output from the [microkit-hw-matrix] 'test_cases' GitHub output.
- `MICROKIT_SDK`: the path to the microkit SDK containing the examples

[microkit-hw-matrix]: ../microkit-hw-matrix/README.md
