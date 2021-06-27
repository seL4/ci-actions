<!--
     Copyright 2021, Proofcraft Pty Ltd

     SPDX-License-Identifier: CC-BY-SA-4.0
-->

# C-Parser Check for seL4

This action runs the C Parser used in the proofs on the seL4 repository to check
that the code is in the supported C subset.

It does so by doing a kernel-only build from the default [sel4test-manifest][1]
for multiple configurations, advancing the seL4 repository to the branch of the
pull request the test is called on, and running the C parser on the preprocessed
output of the build. The reason the test uses [sel4test-manifest][1] is to make
sure it captures a standard development build setup.

This check is syntactic only. That means, even if this check succeeds there might
still be additional reasons why specific expressions or statements are outside
the supported subset. But it is a good first approximation.

[1]: https://github.com/seL4/sel4test-manifest

## Content

The entry point is the script [steps.sh][].

[Build](builds.yml) and [platform](../seL4-platforms/platforms.yml)
configurations are in the respective yaml and python files in this repository.
The main test driver is [build.py][] in this directory.

## Arguments

This action currently takes no arguments. To add or modify build configurations,
edit [builds.yml][] in this directory.

## Example

Put this into a `.github/workflows/` yaml file, e.g. `cparser.yml`:

```yaml
name: C Parser

on: [pull_request]

jobs:
  cparser:
    name: C Parser
    runs-on: ubuntu-latest
    steps:
    - uses: seL4/ci-actions/cparser-run@master
```
