<!--
     Copyright 2021, Proofcraft Pty Ltd

     SPDX-License-Identifier: CC-BY-SA-4.0
-->

# Trigger test on main repository

Typically repos in the seL4 org are part of some Google repo manifest
constellation. Each of these manifests has a main test suite that is running on
one of the participating repositories (the "main" repo).

Take for instance a simplified form of the manifest in `sel4test-manifest`:

```xml
<manifest>
  ...
  <project name="seL4" ... />
  <project name="seL4_libs"  ... />
  <project name="seL4_tools" ... >
  ...
</manifest>
```

and in addition a simplified version of the manifest `sel4bench-manifest`:

```xml
<manifest>
  ...
  <project name="seL4" ... />
  <project name="seL4_libs"  ... />
  <project name="sel4bench"  ... />
  ...
</manifest>
```

The main test suite for the `sel4test-manifest` repo is implemented in the
GitHub workflows of the `seL4` repo. On pushes to the master branch of that
repo, tests will run and a new `default.xml` manifest is deployed to
`sel4test-manifest` when successful. The main test suite for
`sel4bench-manifest` is in the `sel4bench` repository.

Without further action, changes in the `seL4_libs` or `seL4_tools` repos will not
trigger any test or manifest deployments, neither in `seL4` nor in `sel4bench`.
Instead of duplicating the full test setup we have in the `seL4` and `seL4bench`
repos, we instead use the `trigger` action implemented here to notify the `seL4`
and `sel4bench` repos that a new test run should be kicked off.

The `trigger` action implemented here knows which repositories each manifest
contains (`seL4`, `seL4_libs`, `seL4_tools`, `sel4bench` etc), and where the
main tests are for each manifest (e.g. in `seL4` and `sel4bench`). Test triggers
are then sent to these test repos.

The file [test-repos.yml] stores the information which manifests exist and where
the main tests for each of these are. The information which messages to send on
which changes is generated from that and the manifest files, and stored in
[notify.yml].

[seL4]: https://github.com/seL4/seL4
[sel4test-manifest]: https://github.com/seL4/sel4test-manifest

## Content

The steps of this action are defined in [steps.sh], which in this case only
calls [dispatch.py].

For speed, [notify.yml] is generated statically and needs to be re-generated
manually when projects are added/removed to/from manifests. Use [gen-notify.py]
to do this.

[steps.sh]: ./steps.sh
[gen-notify.py]: ./gen-notify.py
[dispatch.py]: ./dispatch.py
[notify.yml]: ./notify.yml
[test-repos.yml]: ./test-repos.yml

## Arguments

- `token`: authentication token with repo scope for repositories the
           repository_dispatch event is sent to.

## Example

```yml
on:
  push:
    branches: [master]

jobs:
  trigger:
    runs-on: ubuntu-latest
    steps:
    - uses: seL4/ci-actions/trigger@master
      with:
        token: $${{ secrets.REPO_TOKEN }}
```
