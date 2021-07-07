<!--
  Copyright 2021, Proofcraft Pty Ltd
  SPDX-License-Identifier: CC-BY-SA-4.0
-->

# Run CAmkES Unit tests

This action expects to be run in the `camkes-tool` repository. It checks out
the repo next to the `seL4/capdl` repo and runs the CAmkES unit tests. The
action uses the PR or push branch for `camkes-tool` and the `master` branch
for `capdl`.

## Arguments

None

## Example

Put this into a `.github/workflows/` yaml file, e.g. `cli.yml`:

```yaml
name: Unit

on:
  push:
    branches: master
  pull_request:

jobs:
  unit:
    name: Unit Tests
    runs-on: ubuntu-latest
    steps:
    - uses: seL4/ci-actions/camkes-unit@master
```

## Build

Run `make` to build the Docker image for local testing. The image is deployed to
dockerhub automatically on push to the `master` branch when relevant files
change.
