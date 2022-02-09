<!--
  Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
  SPDX-License-Identifier: CC-BY-SA-4.0
-->

# Style check action

This action runs the [seL4 code style tools][1] on pull requests or push.

[1]: https://github.com/seL4/seL4_tools/tree/master/misc

## Content

The main action happens in [`steps.sh`](steps.sh), the JavaScript entry point
just calls this script.

## Arguments

- `diff_only`: by default this action checks changed files on pull requests, and
               all files on `push`. Set `diff_only` to true to only check the
               diff on `push` as well. The diff is between the head of the branch
               before the push and the current head of the branch. This breaks for
               force-push, where the previous head of the branch might not exist
               any more.
- `token`: GitHub PA token to authenticate for private repos (optional)

## Example

Put this into a `.github/workflows/` yaml file, e.g. `style.yml`:

```yaml
name: Style

on:
  push:
    branches:
      - master
  pull_request:

jobs:
  style:
    name: Style Check
    runs-on: ubuntu-latest
    steps:
    - uses: seL4/ci-actions/style@master
```
