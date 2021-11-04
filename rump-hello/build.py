# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Parse builds.yml and run rumprun test on each of the build definitions.

Expects seL4-platforms/ to be co-located or otherwise in the PYTHONPATH.
"""

from builds import Build, run_build_script, run_builds, load_builds, junit_results
from pprint import pprint

import os
import sys


def run_build(manifest_dir: str, build: Build):
    """Run one rumprun-hello test."""

    expect = f"\"{build.success}\""
    build.files = build.get_platform().image_names(build.get_mode(), "roottask")
    del build.settings['BAMBOO']  # not used in this test, avoid warning

    script = [
        ["../init-build.sh"] + build.settings_args(),
        ["ninja"]
    ]

    if build.req == 'sim':
        script.append(
            ["bash", "-c",
             f"expect -c 'spawn ./simulate; set timeout 3000; expect {expect}'"]
        )
    else:
        script.append(["tar", "czf", f"../{build.name}-images.tar.gz", "images/"])
        script.append(["echo", f"hardware run for {build.req}, skipping"])

    return run_build_script(manifest_dir, build, script)


# If called as main, run all builds from builds.yml
if __name__ == '__main__':
    builds = load_builds(os.path.dirname(__file__) + "/builds.yml")

    if len(sys.argv) > 1 and sys.argv[1] == '--dump':
        pprint(builds)
        sys.exit(0)

    sys.exit(run_builds(builds, run_build))
