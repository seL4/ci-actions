<!--
  Copyright 2021, Proofcraft Pty Ltd

  SPDX-License-Identifier: CC-BY-SA-4.0
-->

# Run the seL4 proofs on AWS

This action checks out the verification manifest from
<https://github.com/seL4/verification-manifest>, updates the relevant repository
to the pull request state, and runs the specified proof images on AWS. It
automatically spins up and terminates the corresponding AWS instance.

## Arguments

- `L4V_ARCH` (required): which architecture to run the proofs for. One of `ARM`,
                 `ARM_HYP`, `RISCV64`, `X64`
- `session`:     which session to run (e.g. `CRefine` or `ASpec`, or `ASpec
                 CRefine`, i.e. a space-separated string). Runs all sessions if
                 unset.
- `isa-branch`:  which branch of the Isabelle repo (e.g. `ts-2020`, default as in
                 manifest)
- `manifest`:    which manifest file (e.g. `devel.xml`, `mcs.xml`, `default.xml`)
- `cache_bucket`: name of the AWS S3 bucket to use for isabelle images (optional).
- `cache_read`:  whether to read Isabelle images from cache. Default true. Set to
                 empty string to skip.
- `cache_write`: whether to write Isabelle images to cache. Default true. Set to
                 empty string to skip.
- `cache_name`:  optional custom name for image cache. Should at least contain
                 `L4V_ARCH`. Default is distinguishes separate caches for separate
                 values of `isa-branch`, `manifest`, and `L4V_ARCH`.
- `skip_dups`:   skip duplicated proofs (default true).
                 Set to empty string to also run proofs that are already checked
                 in other proof sessions.
- `token`:       GitHub PA token to authenticate for private repos (optional)

## Environment

The action expects the following environment variables to be set.

- `AWS_ACCESS_KEY_ID`: AWS user with sufficient rights to start and stop instances
- `AWS_SECRET_ACCESS_KEY`: secret access key for that user
- `AWS_SSH`: secret ssh key for `test-runner` user on AWS instance
- `GH_HEAD_REF`: the head of the pull request, if a pull request target

## Example

Put this into a `.github/workflows/` yaml file, e.g. `proofs.yml`:

```yaml
name: Proofs

on: [pull_request_target]

jobs:
  check:
    name: Proofs
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        arch: [ARM, ARM_HYP, RISCV64, X64]
    steps:
    - uses: seL4/ci-actions/aws-proofs@master
      with:
        L4V_ARCH: ${{ matrix.arch }}
      env:
        AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
        AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        AWS_SSH: ${{ secrets.AWS_SSH }}
        GH_HEAD_SHA: ${{ github.event.pull_request.head.sha }}
```

## Build

To test this action locally, you need a valid AWS access key and secret. Provide
these via the environment variables `AWS_ACCESS_KEY_ID` and
`AWS_SECRET_ACCESS_KEY`, set the variables `GITHUB_REPOSITORY` and `GITHUB_REF`,
as well as at least `INPUT_L4V_ARCH` (plus optionally any other `INPUT`
variables defined in `action.yml`).

After that, run `./steps.sh` from this directory, which will spin up the
instance and start the test. If you interrupt the test, make sure to terminate
the AWS instance manually either in the AWS console, or by running
`post-steps.sh`.
