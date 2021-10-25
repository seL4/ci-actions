<!--
     Copyright 2021, Proofcraft Pty Ltd

     SPDX-License-Identifier: CC-BY-SA-4.0
-->

# seL4 Benchmark Builds

This action builds [sel4bench] test images.
The test runs can be restricted to specific `arch`, `mode`,
and `march` settings.

It does so by doing a build from the default [sel4bench-manifest] for multiple
configurations, advancing the `sel4bench` repository to the branch of the pull
request the test is called on, and building an image for the selected platform.

[sel4bench]: https://github.com/seL4/sel4bench
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
- `xml`: [sel4bench][sel4bench-manifest] xml manifest to test

## Example

Put this into a `.github/workflows/` yaml file, e.g. `sel4bench.yml`:

```yaml
name: sel4bench

on: [pull_request]

jobs:
  build:
    name: Build
    runs-on: ubuntu-latest
    steps:
    strategy:
          matrix:
            march: ["armv7a, armv8a", nehalem, rv32imac, rv64imac]
    steps:
    - uses: seL4/ci-actions/sel4bench@master
      with:
        march: ${{ matrix.march }}
```
