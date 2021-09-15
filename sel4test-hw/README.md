<!--
     Copyright 2021, Proofcraft Pty Ltd

     SPDX-License-Identifier: CC-BY-SA-4.0
-->

# seL4Test Hardware Builds

This action builds [sel4test] for the hardware test platforms.
The test runs can be restricted to specific `arch`, `mode`,
and `march` settings.

It does so by doing a build from the default [sel4test-manifest] for multiple
configurations, advancing the seL4 repository to the branch of the pull request
the test is called on, and building an image for the selected platform.

[sel4test]: https://github.com/seL4/sel4test
[sel4test-manifest]: https://github.com/seL4/sel4test-manifest

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
- `compiler`: one of `{gcc, clang}`
- `debug`: comma separated list of debug levels from `{debug, release,
  verification}`  to filter on.
- `xml`: [sel4test][sel4test-manifest] xml manifest to test

## Example

Put this into a `.github/workflows/` yaml file, e.g. `sel4test-hw.yml`:

```yaml
name: seL4Test/HW

on: [pull_request]

jobs:
  cparser:
    name: Build
    runs-on: ubuntu-latest
    steps:
    strategy:
          matrix:
            march: ["armv7a, armv8a", nehalem, rv32imac, rv64imac]
            compiler: [gcc, clang]
    steps:
    - uses: seL4/ci-actions/sel4test-hw@master
      with:
        march: ${{ matrix.march }}
        compiler: ${{ matrix.compiler }}
```
