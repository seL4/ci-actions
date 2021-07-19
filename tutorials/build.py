# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Parse builds.yml and run sel4test build + simulation on each of the build definitions.

Expects seL4-platforms/ to be co-located or otherwise in the PYTHONPATH.
"""

from builds import Build, run_build_script, run_builds, load_builds, junit_results
from pprint import pprint

import json
import os
import sys

# do not run listed apps for platform:
disable_for = {
    'PC99': ['hello-camkes-timer', 'interrupts'],
    'ZYNQ7000': ['camkes-vm-linux', 'camkes-vm-crossvm', 'mapping', 'notifications', 'mcs']
}


def run_simulation(manifest_dir: str, build: Build):
    """Run one tutorial test."""

    script = [
        ["chown", "root", "/github/home"],  # otherwise Haskell `stack` crashes
        ["bash", "-c",
         f"../projects/sel4-tutorials/test.py --app={build.app} "
         f"--config={build.get_platform().name.lower()} | tee {junit_results}"]
    ]

    return run_build_script(manifest_dir, build.name, script, junit=True)


def build_filter(build: Build) -> bool:
    return not build.app in disable_for.get(build.get_platform().name, [])


def to_json(builds: list) -> dict:
    """Return a GitHub build matrix as GitHub set-output.

    Basically just returns a list of build names that we can then
    filter on."""

    matrix = {"include": [{"name": b.name} for b in builds]}
    return "::set-output name=matrix::" + json.dumps(matrix)


# If called as main, run all builds from builds.yml
if __name__ == '__main__':
    builds = load_builds(os.path.dirname(__file__) + "/builds.yml", build_filter)

    if len(sys.argv) > 1 and sys.argv[1] == '--dump':
        pprint(builds)
        sys.exit(0)
    elif len(sys.argv) > 1 and sys.argv[1] == '--matrix':
        print(to_json(builds))
        sys.exit(0)

    sys.exit(run_builds(builds, run_simulation))
