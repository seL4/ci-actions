# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Parse builds.yml and run sel4test hardware builds and runs on each of the build definitions.

Expects seL4-platforms/ to be co-located or otherwise in the PYTHONPATH.
"""

from builds import Build, run_build_script, run_builds, load_builds, junit_results, release_mq_locks
from pprint import pprint

import os
import sys


def hw_build(manifest_dir: str, build: Build):
    """Run one hardware build."""

    script = [
        ["../init-build.sh"] + build.settings_args(),
        ["ninja"],
        ["tar", "czf", f"../{build.name}-images.tar.gz", "images/"]
    ]

    return run_build_script(manifest_dir, build.name, script)


def hw_run(manifest_dir: str, build: Build):
    """Run one hardware test."""

    if build.is_disabled():
        print(f"Build {build.name} disabled, skipping.")
        return True

    script, final = build.hw_run(junit_results)

    return run_build_script(manifest_dir, build.name, script, final_script=final, junit=True)


def build_filter(build: Build) -> bool:
    plat = build.get_platform()

    if plat.no_hw_build:
        return False

    if plat.arch == 'arm':
        # Bamboo config says no MCS for arm_hyp 64:
        if build.is_mcs() and build.is_hyp() and build.get_mode() == 64:
            return False
        # Bamboo says: don't build release for hikey when in aarch64 arm_hyp mode
        if build.is_hyp() and build.get_mode() == 64 and build.is_release() and \
           plat.name == 'HIKEY':
            return False
        # No MCS + SMP for platforms with global timer for now (see seL4/seL4#513)
        if plat.name == 'SABRE' and build.is_smp() and build.is_mcs():
            return False

    if plat.arch == 'x86':
        # Bamboo config says no VTX for SMP or verification
        if build.is_hyp() and (build.is_smp() or build.is_verification()):
            return False
        # Bamboo config says no MCS for debug+SMP on x86_64
        if build.is_mcs() and build.get_mode() == 64 and build.is_smp() and \
           not build.is_release():
            return False

    return True


# If called as main, run all builds from builds.yml
if __name__ == '__main__':
    builds = load_builds(os.path.dirname(__file__) + "/builds.yml", filter_fun=build_filter)

    if len(sys.argv) > 1 and sys.argv[1] == '--dump':
        pprint(builds)
        sys.exit(0)

    if len(sys.argv) > 1 and sys.argv[1] == '--hw':
        sys.exit(run_builds(builds, hw_run))

    if len(sys.argv) > 1 and sys.argv[1] == '--post':
        release_mq_locks(builds)
        sys.exit(0)

    sys.exit(run_builds(builds, hw_build))
