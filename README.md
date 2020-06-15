<!--
  Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
  SPDX-License-Identifier: CC-BY-SA-4.0
-->

![CI](https://github.com/lsf37/ci-actions/workflows/CI/badge.svg)

# CI actions for seL4 repositories

This repository collects definitions for continuous integration (CI)
tasks/actions for the repositories of the seL4 foundation.

The idea is to concentrate most of the GitHub workflow definitions here in a
single repository to avoid duplication and to make it easier to replicate a
similar CI setup on other platforms.

Currently, everything is fairly GitHub-specific, but that could change over
time.

Shared JavaScript is in [`js/`](js/), and shared shell scripts in [`scripts/`](scripts/)

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