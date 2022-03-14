<!--
     Copyright 2022, Kry10 Limited

     SPDX-License-Identifier: CC-BY-SA-4.0
-->

# Set up credentials for HTTPS access to GitHub repositories

Configures git to use `git-credential-store`, and populates the credential
store for the given GitHub repositories.

Note that this stores credentials in plain text in a file which will be visible
to the workflow runner user in all steps between this action and its clean-up
phase. The clean-up phase removes the file containing the credentials.

# Inputs

The following inputs are required, unless marked optional.

- `username`: The username to use for HTTPS access, e.g. `seL4-ci`.
- `token`:    A personal access token (PAT) owned by the given user, with the
              required access to the given GitHub repositories.
- `repos`:    A space-separated list of GitHub repositories, given as
              organisation/repo pairs, e.g. `seL4/seL4 seL4/l4v`.
- `store_id`: Optional. A unique identifier that is added as a suffix to the
              name of the credential file. May be useful if multiple instances
              of this action need to be nested.

## Example

```yml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - name: Setup Git credentials
      uses: seL4/ci-actions/git-credentials-setup@master
      with:
        username: 'seL4-ci'
        token: ${{ secrets.PRIV_REPO_TOKEN }}
        repos: 'seL4/seL4 seL4/l4v'
    - name: Push branches
      run: |
        (cd seL4 && git push)
        (cd l4v && git push)
```
