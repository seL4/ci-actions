<!--
  Copyright 2021, Data61, CSIRO (ABN 41 687 119 230)
  SPDX-License-Identifier: CC-BY-SA-4.0
-->

# Isabelle mirror action

This is a scheduled action running from this repository to mirror the upstream
Isabelle mercurial repository to GitHub.

## Content

The main action happens in [`steps.sh`](steps.sh), the JavaScript entry point
just calls this script.

## Arguments

There are no arguments to this action and it should most likely not be called
outside this repository.
