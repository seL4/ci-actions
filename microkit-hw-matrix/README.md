<!--
     Copyright 2026, UNSW

     SPDX-License-Identifier: CC-BY-SA-4.0
-->

# Microkit Hardware Run Matrix

This action generates a GitHub build matrix for the [microkit-hw-run] action from
the information available in the [Microkit SDK build system]. For more details,
see the [microkit-hw-run README].

[microkit-hw-run]: ../microkit-hw-run/README.md
[Microkit SDK build system]: https://github.com/seL4/microkit/blob/main/build_sdk.py

## Content

The entry point is the script [steps.sh].

The main test driver [build.py] in this directory is shared with (a symlink to)
the [microkit-hw-run build.py] to make sure the same filters are applied.

[steps.sh]: ./steps.sh
[build.py]: ./build.py
[microkit-hw-run build.py]: ../microkit-hw-run/build.py

## Arguments

This action has no input arguments. It expects the current working directory to
contain a folder called 'microkit' containing the Microkit source and a folder
called 'seL4' containing the seL4 kernel source code.
