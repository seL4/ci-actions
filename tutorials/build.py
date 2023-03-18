# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Parse builds.yml and run sel4test build + simulation on each of the build definitions.

Expects seL4-platforms/ to be co-located or otherwise in the PYTHONPATH.
"""

from builds import Build, load_builds, run_build_script, run_builds, junit_results
from platforms import load_yaml, gh_output
from pprint import pprint

import json
import os
import sys


def run_simulation(manifest_dir: str, build: Build):
    """Run one tutorial test."""

    script = [
        ["bash", "-c",
         f"../projects/sel4-tutorials/test.py --app={build.app} "
         f"--config={build.get_platform().name.lower()} | tee {junit_results}"]
    ]

    return run_build_script(manifest_dir, build, script, junit=True)


def build_filter(build: Build) -> bool:
    return build.app not in disable_app_for.get(build.get_platform().name, [])


def to_json(builds: list) -> str:
    """Return a GitHub build matrix as GitHub output assignment.

    Basically just returns a list of build names that we can then
    filter on."""

    matrix = {"include": [{"name": b.name} for b in builds]}
    return "matrix=" + json.dumps(matrix)


# If called as main, run all builds from builds.yml
if __name__ == '__main__':
    yml = load_yaml(os.path.dirname(__file__) + "/builds.yml")
    disable_app_for = yml['disable_app_for']

    builds = load_builds(None, build_filter, yml)

    if len(sys.argv) > 1 and sys.argv[1] == '--dump':
        pprint(builds)
        sys.exit(0)
    elif len(sys.argv) > 1 and sys.argv[1] == '--matrix':
        gh_output(to_json(builds))
        sys.exit(0)

    sys.exit(run_builds(builds, run_simulation))
