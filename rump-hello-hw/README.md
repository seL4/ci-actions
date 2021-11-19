<!--
     Copyright 2021, Proofcraft Pty Ltd

     SPDX-License-Identifier: CC-BY-SA-4.0
-->

# seL4 Rumprun Hello World tests (hardware run)

This action runs images produced by the [rump-hello] action
on hardware.

[rump-hello]: ../rump-hello/README.md

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

- `req`: comma separated list of hardware requirements, e.g `haswell3`.
- `mode`: comma separated list of modes, e.g. `32`.
- `name`: comma separated list of full test names, e.g. `PC99_32_sim`.
