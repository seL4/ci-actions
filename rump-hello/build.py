# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Parse builds.yml and run rumprun test on each of the build definitions.

Expects seL4-platforms/ to be co-located or otherwise in the PYTHONPATH.
"""

from builds import Build, run_build_script, run_builds, load_builds
from builds import release_mq_locks, SKIP
from pprint import pprint

import os
import sys


def adjust_build(build: Build):
    build.files = build.get_platform().image_names(build.get_mode(), "roottask")
    del build.settings['BAMBOO']  # not used in this test, avoid warning


def run_build(manifest_dir: str, build: Build):
    """Run one rumprun-hello test."""

    adjust_build(build)

    script = [
        ["../init-build.sh"] + build.settings_args(),
        ["ninja"]
    ]

    if build.req == 'sim':
        script.append(
            ["bash", "-c",
             f"expect -c 'spawn ./simulate; set timeout 3000; expect \"{build.success}\"'"]
        )
    else:
        script.append(["tar", "czf", f"../{build.name}-images.tar.gz", "images/"])

    return run_build_script(manifest_dir, build, script)


def hw_run(manifest_dir: str, build: Build):
    """Run one hardware test."""

    adjust_build(build)

    if build.is_disabled():
        print(f"Build {build.name} disabled, skipping.")
        return SKIP

    script, final = build.hw_run('log.txt')

    return run_build_script(manifest_dir, build, script, final_script=final)


# If called as main, run all builds from builds.yml
if __name__ == '__main__':
    builds = load_builds(os.path.dirname(__file__) + "/builds.yml")

    if len(sys.argv) > 1 and sys.argv[1] == '--dump':
        pprint(builds)
        sys.exit(0)

    if len(sys.argv) > 1 and sys.argv[1] == '--hw':
        sys.exit(run_builds(builds, hw_run))

    if len(sys.argv) > 1 and sys.argv[1] == '--post':
        release_mq_locks(builds)
        sys.exit(0)

    sys.exit(run_builds(builds, run_build))
