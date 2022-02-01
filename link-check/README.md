<!--
  Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
  SPDX-License-Identifier: CC-BY-SA-4.0
-->

# Check links in .md and .html files

This action checks out the target repository, and runs the [liche tool][1] on
it. It is loosely based on <https://github.com/peter-evans/link-checker>.

The action is written for the context of the [seL4][2] repositories, but
should work more generally.

[1]: https://github.com/raviqqe/liche
[2]: https://github.com/seL4/

## Content

This is a minimal Docker action. It mostly uses Docker instead of JavaScript,
so it can run a pre-built `liche` binary.

## Arguments

No arguments are required. The following are available.

* `files`: List of files to check
* `dir`: Directory to check recursively, default `.`
* `exclude`: Regex for which files to exclude
* `exclude_urls`: Regex for which URLs to exclude from check
* `timeout`: Timeout for link response
* `doc_root`: Document root for absolute links
* `num_requests`: Maximum number of concurrent requests
* `verbose`: Print more information if set (default unset)
* `token`: GitHub PA token to authenticate for private repos

## Example

Put this into a `.github/workflows/` yaml file, e.g. `links.yml`:

```yaml
name: Links

on:
  push:
    branches:
      - master
  pull_request:

jobs:
  check:
    name: Link Check
    runs-on: ubuntu-latest
    steps:
    - uses: seL4/ci-actions/link-check@master
```

## Build

Run `make` to build the Docker image for local testing. The image is deployed to dockerhub automatically on push to the `master` branch when relevant files change.
