<!--
     Copyright 2021, Proofcraft Pty Ltd

     SPDX-License-Identifier: CC-BY-SA-4.0
-->

# Build seL4 Manual

This action builds a PDF of the seL4 reference manual from the seL4 repository.

It expects to be run from push or pull-request events in that repository.

## Content

The entry point is the script [`steps.sh`](steps.sh/)

## Arguments

None

## Example

Put this into a `.github/workflows/` yaml file, e.g. `manual.yml`:

```yaml
name: Manual

on: [pull_request]

jobs:
  manual:
    name: Build Manual
    runs-on: ubuntu-latest
    steps:
    - uses: seL4/ci-actions/manual@master
```
