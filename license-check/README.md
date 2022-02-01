<!--
  Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
  SPDX-License-Identifier: CC-BY-SA-4.0
-->

# REUSE License Check action

This action checks out the target repository, and runs the FSFE [reuse
tool][1] on it. It roughly speaking combines

    actions/checkout@v2
    fsfe/reuse-action@master

The action is written for the context of the seL4 repositories, but should
work more generally, although you might want to prefer the offical [FSFE
action][2], which also provides arguments and parameters (but does not check
out the target repository).

[1]: https://github.com/fsfe/reuse-tool
[2]: https://github.com/fsfe/reuse-action

## Content

The main action happens in [`steps.sh`](steps.sh), the JavaScript entry point
just calls this script.

## Arguments

- `token`: GitHub PA token to authenticate for private repos (optional)

## Example

Put this into a `.github/workflows/` yaml file, e.g. `license.yml`:

```yaml
name: License

on:
  push:
    branches:
      - master
  pull_request:

jobs:
  check:
    name: License Check
    runs-on: ubuntu-latest
    steps:
    - uses: seL4/ci-actions/license-check@master
```
