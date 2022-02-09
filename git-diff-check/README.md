<!--
  Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
  SPDX-License-Identifier: CC-BY-SA-4.0
-->

# Git Diff Check action

This action runs `git diff --check` on pull requests to check
for trailing whitespace and potentially left-over merge conflict
markers.

## Content

The main action happens in [`steps.sh`](steps.sh)

## Arguments

- `token`: GitHub PA token to authenticate for private repos (optional)

## Example

Put this into a `.github/workflows/` yaml file, e.g. `git.yml`:

```yaml
name: 'Git Diff Check'

on: [pull_request]

jobs:
  gitlint:
    name: 'Trailing Whitepace Check'
    runs-on: ubuntu-latest
    steps:
    - uses: seL4/ci-actions/git-diff-check@master
```
