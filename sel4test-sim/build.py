# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Parse builds.yml and run sel4test build + simulation on each of the build definitions.

Expects seL4-platforms/ to be co-located or otherwise in the PYTHONPATH.
"""

from builds import Build, run_build_script, run_builds, load_builds, junit_results, sanitise_junit
from pprint import pprint

import os
import sys


def run_simulation(manifest_dir: str, build: Build):
    """Run one simulation build and test."""

    expect = f"\"{build.success}\""

    script = [
        ["../init-build.sh"] + build.settings_args(),
        ["ninja"],
        ["bash", "-c",
         f"expect -c 'spawn ./simulate; set timeout 3000; expect {expect}' | tee {junit_results}"]
    ]

    return run_build_script(manifest_dir, build, script, junit=True)


# If called as main, run all builds from builds.yml
if __name__ == '__main__':
    builds = load_builds(os.path.dirname(__file__) + "/builds.yml")

    if len(sys.argv) > 1 and sys.argv[1] == '--dump':
        pprint(builds)
        sys.exit(0)

    sys.exit(run_builds(builds, run_simulation))
