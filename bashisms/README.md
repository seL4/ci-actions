<!--
  Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
  SPDX-License-Identifier: CC-BY-SA-4.0
-->

# Shell script check action

This action runs the check for [portable shell code][1] from
<https://github.com/seL4/sel4_tools> on pull requests.

[1]: https://github.com/seL4/seL4_tools/tree/master/misc/is-valid-shell-script

## Content

The main action happens in [`steps.sh`](steps.sh), the JavaScript entry point
just calls this script.

## Arguments

- `token`: GitHub PA token to authenticate for private repos (optional)

## Example

Put this into a `.github/workflows/` yaml file, e.g. `style.yml`:

```yaml
name: Style

on: [pull_request]

jobs:
  style:
    name: Shell
    runs-on: ubuntu-latest
    steps:
    - uses: seL4/ci-actions/bashisms@master
```

### Maintenance

The `checkbashism` script in `../scripts` is directly extracted from
<https://deb.debian.org/debian/pool/main/d/devscripts/devscripts_2.21.7.tar.xz>.
Installing it via `apt-get` takes forever, because the rest of the devscripts
has lots of dependencies.
