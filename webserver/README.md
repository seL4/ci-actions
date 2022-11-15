<!--
     Copyright 2022, Proofcraft Pty Ltd

     SPDX-License-Identifier: CC-BY-SA-4.0
-->

# seL4 web server demo app tests

This action builds and runs the test suite for the [seL4 web server] demo app.
The test runs can be restricted to a specific test `platform` for use in a
matrix build.

[seL4 web server]: https://github.com/seL4/sel4webserver

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

- `platforms`: comma separated list of test platforms, e.g. `ODROID_Xu4`.
- `xml`: explicit manifest to use (instead of `seL4/sel4webserver-manifest`).

## Example

Put this into a `.github/workflows/` yaml file, e.g. `test.yml`:

```yaml
name: Web Server Build

on:
  push:
    branches:
      - master
  pull_request:

jobs:
  test:
    name: Build
    runs-on: ubuntu-latest
    steps:
    - uses: seL4/ci-actions/webserver@master
      with:
        platform: ODROID_XU4
```
