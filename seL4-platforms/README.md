<!--
     Copyright 2021, Proofcraft Pty Ltd

     SPDX-License-Identifier: CC-BY-SA-4.0
-->

# Platform and build definitions for seL4

The file [platforms.yml][] defines a list of available architectures, modes, and
platforms for seL4 builds, and [platforms.py][] is a Python module for parsing
and representing these.

See [platforms.yml][] for which data these definitions contains, and the
function `validate()` in [platforms.py][] for which constraints they are
expected to satisfy.

The script [platforms.py][] will dump out the interpreted contents of the yaml
file if invoked on the command line with

```sh
python3 platforms.py
```

It will look for the yaml file in the same directory the file `platforms.py`
resides.

There are no specific seL4 tests or GitHub actions in this directory, it just
collects common definitions.
