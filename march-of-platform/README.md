<!--
     Copyright 2021, Proofcraft Pty Ltd

     SPDX-License-Identifier: CC-BY-SA-4.0
-->

# Print march for platform

This is an auxiliary action that can provide information about platform names
to other steps in a GitHub workflow.

## Content

The entry point is the script [steps.sh], the interface to the
[platform] yaml configurations are in [march.py].

[steps.sh]: ./steps.sh
[march.py]: ./march.py
[platform]: ../seL4-platforms/platforms.yml

## Arguments

To add or modify build configurations, edit [builds.yml][Build] in this
directory. To filter the build variants defined there for a specific run,
use one or more of the following:

Input:

- `platform`: the platform name.

Output:

- `march`: the march of the provided platform. Empty if platform is not found.

## Example

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - id: plat
      uses: seL4/ci-actions/march-of-platform@master
      with:
        platform: sabre
    - run: echo ${{ plat.outputs.march }}
```
