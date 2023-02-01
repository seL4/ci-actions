<!--
  Copyright 2023 Kry10 Limited
  SPDX-License-Identifier: BSD-2-Clause
-->

# Await remote workflow artifacts

A GitHub action to wait for named artifacts to become available in
another workflow, and to optionally download them in the current
workflow. Downloaded artifacts are unpacked into the nominated
directory.

This can be useful when one workflow issues a `repository_dispatch`
event to start a second workflow, and the first workflow creates
artifacts needed in the second workflow.

In this situation, there is a race: The second workflow may start as
soon as the first workflow issues the `repository_dispatch` event, but
the artifacts do not become visible in the GitHub API until after the
first workflow has finished. The second workflow might therefore need to
wait for the artifacts to appear.

## Example usage

Suppose we have a first workflow that uploads some artifacts, and then
issues a `repository_dispatch` event:

```yaml
name: First workflow

on:
  push:

jobs:
  workflow-1:
    name: First workflow job
    runs-on: ubuntu-latest
    steps:
      - name: Create some files
        run: |
          mkdir -p artifact-1/dir-1 artifact-2/dir-2
          echo hello > artifact-1/dir-1/file-1
          echo hello > artifact-2/dir-2/file-2
      - name: Upload artifact-1
        uses: actions/upload-artifact@v3
        with:
          name: artifact-1
          path: artifact-1
      - name: Upload artifact-2
        uses: actions/upload-artifact@v3
        with:
          name: artifact-2
          path: artifact-2
      - name: Issue repository-dispatch
        uses: peter-evans/repository-dispatch@v2
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          repository: ${{ github.repository }}
          event-type: my-event
          client-payload: |
            { "run_id": "${{ github.run_id }}" }
      - name: Sleep a while
        run: sleep 60
```

Notice that this first workflow sleeps for a minute after issuing the
`repository_dispatch` event. This means that the artifacts will not
immediately be visible in the GitHub API.

The first workflow passes its own `run_id` in the `client-payload` for
the `repository_dispatch` event, so the second workflow can locate it.

Then, suppose we also have a second workflow in the same repository,
that is triggered by the `respository_dispatch` event. We'll use this
action to download the artifacts created in the first workflow:

```yaml
name: Second workflow

on:
  repository_dispatch:
    types:
      - my-event

jobs:
  workflow-2:
    name: Second workflow job
    runs-on: ubuntu-latest
    steps:
      - name: Download artifacts
        uses: seL4/ci-actions/await-remote-artifacts@master
        with:
          repo: ${{ github.repository }}
          run-id: ${{ github.event.client_payload.run_id }}
          artifact-names: artifact-1 artifact-2
          token: ${{ secrets.GITHUB_TOKEN }}
          download-dir: artifacts
      - name: List downloaded artifacts
        run: |
          # List downloaded artifacts
          find artifacts -type f
```

Notice that artifacts are downloaded as zip files. Once unpacked, the
`find` command in the last step produces the following output:

```
artifacts/artifact-1/dir-1/file-1
artifacts/artifact-2/dir-2/file-2
```

This action can also be used to download artifacts when the first and
second workflows are in different repositories. However, in that case,
you'll need to use tokens with appropriate access.

## Known issues

- Artifacts are downloaded to memory before being saved to disk, so this
  may not work for large artifacts.
- The action currently makes no attempt to avoid GitHub API rate limits,
  so it might fail when the target workflow has many artifacts.
