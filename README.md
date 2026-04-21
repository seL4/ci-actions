<!--
  Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
  SPDX-License-Identifier: CC-BY-SA-4.0
-->

[![CI](https://github.com/seL4/ci-actions/actions/workflows/push.yml/badge.svg)](https://github.com/seL4/ci-actions/actions/workflows/push.yml)

# CI actions and Workflows for seL4 repositories

This repository collects definitions for continuous integration (CI)
tasks/actions for the repositories of the seL4 Foundation. While some of these
might be useful more generally, most of them will be specific to the seL4 setup.

The idea is to concentrate most of the GitHub workflow definitions here in a
single repository to avoid duplication, share code between actions, and to make
it easier to replicate a similar CI setup on other platforms.

Shared JavaScript is in [`js/`](js/), and shared shell scripts are in [`scripts/`](scripts/)

This repository also defines a number of GitHub action workflows that can be
called from other repositories. These are all files in `.github/workflows` that
define an `on: workflow_call` trigger. In particular:

- [pr.yml](.github/workflows/pr.yml) for standard pull requests checks (gitlint,
  whitespace, shell checks, style)
- [push.yml](.github/workflows/push.yml) for standard push checks (links, licenses)
- [sel4test-sim.yml](.github/workflows/sel4test-sim.yml) for running the
  seL4 simulation tests
- [sel4test-hw.yml](.github/workflows/sel4test-hw.yml) for running the
  seL4 hardware tests
- [sel4bench-hw.yml](.github/workflows/sel4bench-hw.yml) for running the
  seL4 hardware benchmarks

## Available actions

The following GitHub actions are available:

- [AWS Proofs](aws-proofs/): run the l4v proofs on AWS
- [Bashisms](bashisms/): check shell for non-portable shell scripts
- [CAmkES Hardware Test](camkes-hw/): CAmkES test hardware runs
- [CAmkES Tests](camkes-test/): CAmkES test builds and simulations
- [CAmkES Unit Tests](camkes-unit/): unit tests for the `camkes-tool` repository
- [CAmkES VM Tests](camkes-vm/): CAmkES VM tests
- [CAmkES VM Hardware Tests](camkes-vm-hw/): CAmkES VM hardware runs
- [CParser Run](cparser-run/): check seL4 PRs for C verification subset
- [Git Diff Check](git-diff-check/): check for trailing whitespace and merge conflict markers
- [Gitlint](gitlint/): run gitlint on pull requests
- [Isabelle Mirror](isabelle-mirror/): mirrors the upstream Isabelle repository to git
- [L4v Deploy](l4v-deploy/): deploys l4v default.xml manifest after successful proof runs
- [License Check](license-check/): runs the FSFE reuse license tool
- [Link Check](link-check/): checks links in `.md` and `.html` files
- [Manifest Deploy](manifest-deploy/): deploys default.xml manifests after successful tests
- [m-arch of Platform](march-of-platform/): outputs the `march` of a given platform
- [microkit Hardware Builds](microkit-hw-build/): microkit image builds
- [microkit Hardware Runs](microkit-hw-run/): microkit hardware runs
- [microkit Hardware Run Matrix](microkit-hw-matrix/): matrix for microkit hardware runs
- [Preprocess](preprocess/): run AST diff on preprocessed source for verified configurations
- [Repo Checkout](repo-checkout/): checks out a `repo` collection
- [RumpRun](rump-hello/): rumprun hello-world simulation test
- [RumpRun Hardware](rump-hello-hw/): rumprun hello-world test on hardware
- [Run Proofs](run-proofs/): run the l4v proofs in docker (not used in CI)
- [seL4 Benchmark Builds](sel4bench/): sel4bench image builds
- [seL4 Benchmark Runs](sel4bench-hw/): run sel4bench images on hardware
- [seL4 Benchmark Results](sel4bench-web/): publish sel4bench results to the seL4 website
- [seL4 Manual](seL4-manual/): build seL4 PDF manual
- [seL4Test Hardware Builds](sel4test-hw/): sel4test image builds
- [seL4Test Hardware Runs](sel4test-hw-run/): sel4test hardware runs
- [seL4Test Hardware Run Matrix](sel4test-hw-matrix/): matrix for sel4test hardware runs
- [seL4Test Simulation](sel4test-sim/): sel4test simulations for platforms with a simulation binary
- [Standalone Kernel](standalone-kernel/): standalone seL4 kernel compilation
- [Style](style/): coding style checks of the seL4 Foundation
- [Thylint](thylint/): basic Isabelle theory file linter
- [Trigger](trigger/): triggers a test run in the main repository of a repo manifest set
- [Tutorials](tutorials/): run the seL4 tutorial tests (simulation only)
- [Webserver Tests](webserver/): builds for the seL4 webserver demo app
- [Webserver Hardware Tests](webserver-hw/): hardware runs for the seL4 webserver demo app

## Contributing

Contributions are welcome!

See [open issues][issues] for things than need work, there is also a list of
[good first issues][first-issues] if you are new to all this and want to get
involved.

See the file [CONTRIBUTING.md](CONTRIBUTING.md) for more information.

[issues]: https://github.com/seL4/ci-actions/issues?q=is%3Aopen+is%3Aissue+no%3Aassignee
[first-issues]: https://github.com/seL4/ci-actions/issues?q=is%3Aopen+is%3Aissue+no%3Aassignee+label%3A%22good+first+issue%22

## License

See the directory [LICENSES/](LICENSES/) for a list of the licenses used in this
repository, and the SPDX tag in file headers for the license of each file.
