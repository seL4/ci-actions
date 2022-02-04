<!--
  Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
  SPDX-License-Identifier: CC-BY-SA-4.0
-->

![CI](https://github.com/seL4/ci-actions/workflows/CI/badge.svg)

# CI actions for seL4 repositories

This repository collects definitions for continuous integration (CI)
tasks/actions for the repositories of the seL4 foundation. While some of these
might be useful more generally, most of them will be specific to the seL4 setup.

The idea is to concentrate most of the GitHub workflow definitions here in a
single repository to avoid duplication, share code between actions, and to make
it easier to replicate a similar CI setup on other platforms.

Currently, everything is fairly GitHub-specific, but that could change over
time.

Shared JavaScript is in [`js/`](js/), and shared shell scripts are in [`scripts/`](scripts/)

## Availabe actions

The following GitHub actions are available:

- [Style](style/)
- [Gitlint](gitlint/)
- [`git diff --check`](git-diff-check/)
- [License Check](license-check/)
- [Link Check](link-check/)
- [Portable Shell Script](bashisms/) check
- [Preprocess](preprocess/) the seL4 source to check for changes to verified configurations.
- [Run Proofs](run-proofs/): check if the proofs still work after a code change.
- [Kernel Compile](standalone-kernel/): standalone seL4 kernel compilation for different compiler/arch/python combinations. 

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
