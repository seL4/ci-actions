<!--
  Copyright 2021, Data61, CSIRO (ABN 41 687 119 230)
  SPDX-License-Identifier: CC-BY-SA-4.0
-->

# BitBucket PR queue action

This action manages the queueing of PRs into repositories that must pass
through bitbucket.

The process is design to produce minimal spurious messages and to
maintain an order for PRs to progress through review.

## Branch selection and notification

When a branch is pushed to github (e.g., `master` from BitBucket) we
determine the next PR to be a candidate to be merged via bitbucket.
Additionally, when a branch is updated that is the basis of a PR, we
check if it would be the next candidate to be notified and, if it is,
notify it.

The first candidate will be one that is ahead of the target branch, has
approval, and is passing all tests. If such a candidate is found, a
comment is added to that PR to notify the assignee that the PR is the
next to be merged. The _least recent_ such candidate is always chosen.

If a merge candidate cannot be found, a rebase candidate is then
selected. This is a PR that has approval and is passing all tests but
that is not ahead of the target branch. If the PR branch allows
maintainers to push and the trigger was the target branch (rather than
the PR branch), it will be automatically rebased, otherwise a comment
will be left to request that the creator of the PR enable pushing by
maintainers or that they manually rebase against the target.  The _most
recent_ such candidate is always chosen (to avoid selection of stale
PRs).

If a rebase candidate cannot be found, a review candidate is then
selected. This is a PR that is passing all tests but that does not have
approval. A comment will be made to notify the reviewers that the PR
requires review and would be able to proceed through to being merged.
The _most recent_ such candidate is always chosen.

If a review candidate cannot be found, a fix candidate is then selected.
This is a PR that is not passing any tests. A comment will be made to
notify the creator of the PR that they need to resolve tests in order to
get their PR ready for review. The _most recent_ such candidate is
always chosen.

## Content

The action is implemented in [`index.js`](index.js).

## Example

Put this into a `.github/workflows/` yaml file, e.g. `prqueue.yml`:

```yaml
name: PR Queue

on:
  push:
    branches:
      - master
  workflow_dispatch: {}

jobs:
  notify:
    name: Notify PR candidate
    runs-on: ubuntu-latest
    steps:
    - uses: seL4/ci-actions/pr-queue@master
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
```
