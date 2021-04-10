<!--
  Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
  SPDX-License-Identifier: CC-BY-SA-4.0
-->

# Run the seL4 proofs

This action checks out the verification manifest
<https://github.com/seL4/verification-manifest>, updates the relevant
repository to the pull request state, and runs the specified proof images.

## Arguments

* `L4V_ARCH` (required): which architecture to run the proofs for. One of `ARM`, `ARM_HYP`, `RISCV64`, `X64`
* `session`: which session to run (default `CRefine`)

## Example

Put this into a `.github/workflows/` yaml file, e.g. `links.yml`:

```yaml
name: Proofs

on: [pull_request]

jobs:
  check:
    name: Run Proofs
    runs-on: ubuntu-latest
    strategy:
          fail-fast: false
          matrix:
            arch: [ARM, ARM_HYP, RISCV64, X64]
    steps:
    - uses: seL4/ci-actions/run-proofs@master
      with:
        L4V_ARCH: ${{ matrix.arch }}
```

## Build

Run `make` to build the Docker image for local testing. The image is deployed to dockerhub automatically on push to the `master` branch when relevant files change.
