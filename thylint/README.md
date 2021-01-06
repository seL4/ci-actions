<!--
  Copyright 2021, Data61, CSIRO (ABN 41 687 119 230)
  SPDX-License-Identifier: CC-BY-SA-4.0
-->

# thylint action

This action runs the thylint linter for Isabelle theory files. Works on pull requests only.

## Content

This action checks out the repository and runs the linter on the `.thy` files mentioned in the diff of the pull request. It reports the results as source file annotations.

## Arguments

The action takes no arguments.

## Example

Put this into a `.github/workflows/` yaml file, e.g. `thylint.yml`:

```yaml
name: thylint

on: [pull_request]

jobs:
  thylint:
    name: thylint
    runs-on: ubuntu-latest
    steps:
    - uses: seL4/ci-actions/thylint@master
```
