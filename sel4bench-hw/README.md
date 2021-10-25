<!--
     Copyright 2021, Proofcraft Pty Ltd

     SPDX-License-Identifier: CC-BY-SA-4.0
-->

# seL4 Benchmark Runs

This action runs [sel4bench] test images on hardware.
The test runs can be restricted to specific `arch`, `mode`,
and `march` settings or a specific machine requirement `req`.

The action expects an image built by the [sel4bench][sel4bench-img] action.

[sel4bench]: https://github.com/seL4/sel4bench
[sel4bench-img]: ../sel4bench/README.md
[sel4bench-manifest]: https://github.com/seL4/sel4bench-manifest

## Content

The entry point is the script [steps.sh].

[Build] and [platform] configurations are in the respective yaml and python
files in this repository. See these files for config documentation.

The main test driver is [build.py] in this directory.

[steps.sh]: ./steps.sh
[build.py]: ./build.py
[platform]: ../seL4-platforms/platforms.yml
[Build]: builds.yml

## Arguments

To add or modify build configurations, edit [builds.yml][Build] in this
directory. To filter the build variants defined there for a specific run,
use one or more of the following:

- `arch`: comma separated list of architecture to filter on, e.g `arm, riscv`.
- `march`: comma separated list of `march` flags, e.g. `armv7a, nehalem`
- `mode`: one of `{32, 64}`
- `platform`: platform name, e.g. `pc99`
- `req`: machine name, e.g. `haswell3`

## Example

See for instance the [seL4/sel4bench] workflow file.

[seL4/sel4bench]: https://github.com/seL4/sel4bench/blob/master/.github/workflows/sel4bench.yml
