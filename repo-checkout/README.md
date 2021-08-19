<!--
     Copyright 2021, Proofcraft Pty Ltd

     SPDX-License-Identifier: CC-BY-SA-4.0
-->

# Repo manifest checkout and version

A separate action to check out a repo manifest, such as [sel4test-manifest], to
advance the manifest to the state of a PR or branch (currently for a single repo
only), and to record that state for later use by other actions.

This mostly exists to make sure that separate jobs in a matrix build see exactly
the same sources, especially when there are job dependencies and one or more jobs
could start significantly (hours) later than others. If manifests or branches are
updated in between, the later job might otherwise see different sources.

[sel4test-manifest]: https://github.com/seL4/sel4test-manifest

## Content

The steps of this action are defined in [steps.sh].

[steps.sh]: ./steps.sh

## Arguments

- `manifest_repo` (required): the manifest repository to check out (e.g. 'sel4test-manifest')
- `manifest`: the manifest file to use (default `master.xml`)
- `sha:`: override sha to advance PR repo to (e.g. sha for `seL4` repo in `seL4/sel4test-manifest`
          if seL4 is the repo the action is called from)

## Outputs

- `xml`: the output of `repo manifest -r` in the PR/branch state.

## Example

```yml
jobs:
  test:
    runs-on: ubuntu-latest
    outputs:
      xml: ${{ steps.repo.outputs.xml }}
    steps:
    - uses: seL4/ci-actions/repo-checkout@repo
      id: repo
      with:
        manifest_repo: sel4test-manifest

  test2:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - run: echo "${XML}"
        env:
          XML: ${{ needs.test.outputs.xml }}
```
