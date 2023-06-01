# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Parse builds.yml and run sel4test hardware builds and runs on each of the build definitions.

Expects seL4-platforms/ to be co-located or otherwise in the PYTHONPATH.
"""

from builds import Build, run_build_script, run_builds, load_builds, junit_results
from builds import release_mq_locks, SKIP
from platforms import Platform, gh_output

from pprint import pprint
from typing import List

import json
import os
import sys


def hw_build(manifest_dir: str, build: Build):
    """Run one hardware build."""

    settings = build.settings_args()
    if build.name == "RPI4":
        # The Raspberry Pi 4B model that is used for hardware testing has 4GB
        # of RAM, which we must specify when building the kernel.
        settings += " -DRPI4_MEMORY=4096"

    script = [
        ["../init-build.sh"] + settings,
        ["ninja"],
        ["tar", "czf", f"../{build.name}-images.tar.gz", "images/"]
    ]

    return run_build_script(manifest_dir, build, script)


def hw_run(manifest_dir: str, build: Build):
    """Run one hardware test."""

    if build.is_disabled():
        print(f"Build {build.name} disabled, skipping.")
        return SKIP

    script, final = build.hw_run(junit_results)

    return run_build_script(manifest_dir, build, script, final_script=final, junit=True)


def build_filter(build: Build) -> bool:
    plat = build.get_platform()

    if plat.no_hw_build:
        return False

    if plat.arch == 'arm':
        # Bamboo says: don't build release for hikey when in aarch64 arm_hyp mode
        if build.is_hyp() and build.get_mode() == 64 and build.is_release() and \
           plat.name == 'HIKEY':
            return False

        # MCS exclusions:
        # No MCS + SMP for platforms with global timer for now (see seL4/seL4#513)
        if plat.name == 'SABRE' and build.is_smp() and build.is_mcs():
            return False
        # SCHED_CONTEXT_0014 fails on TX2 and ODROID_C4: https://github.com/seL4/seL4/issues/928
        if (plat.name == 'TX2' or plat.name == 'ODROID_C4') and \
           build.is_mcs() and build.is_smp() and build.is_hyp() and build.is_clang():
            return False
        # CACHEFLUSH0001 fails on ODROID_XU4: https://github.com/seL4/sel4test/issues/80
        if plat.name == 'ODROID_XU4' and build.is_debug() and build.is_mcs() and \
           build.is_hyp() and build.is_clang() and build.get_mode() == 32:
            return False
        # IMX8MM_EVK is failing multicore tests for MCS + SMP:
        if plat.name == 'IMX8MM_EVK' and build.is_mcs() and build.is_smp():
            return False

    if plat.arch == 'x86':
        # Bamboo config says no VTX for SMP or verification
        if build.is_hyp() and (build.is_smp() or build.is_verification()):
            return False

    # run NUM_DOMAINS > 1 tests only on release builds
    if build.is_domains() and not build.is_release():
        return False

    return True


def to_json(builds: List[Build]) -> str:
    """Return a GitHub build matrix per enabled hardware platform as GitHub output assignment."""

    def run_for_plat(plat: Platform) -> List[dict]:
        if plat.disabled or plat.no_hw_build:
            return []

        # separate runs for each compiler on arm
        if plat.arch == 'arm':
            return [
                {"platform": plat.name, "march": plat.march, "compiler": "gcc"},
                {"platform": plat.name, "march": plat.march, "compiler": "clang"},
            ]

        # no clang for RISC-V yet
        if plat.arch == 'riscv':
            return [
                {"platform": plat.name, "march": plat.march, "compiler": "gcc"},
            ]

        # separate runs for each compiler + mode on x86, because we have more machines available
        if plat.arch == 'x86':
            return [
                {"platform": plat.name, "march": plat.march, "compiler": "gcc", "mode": 32},
                {"platform": plat.name, "march": plat.march, "compiler": "clang", "mode": 32},
                {"platform": plat.name, "march": plat.march, "compiler": "gcc", "mode": 64},
                {"platform": plat.name, "march": plat.march, "compiler": "clang", "mode": 64},
            ]

    platforms = set([b.get_platform() for b in builds])
    matrix = {"include": [run for plat in platforms for run in run_for_plat(plat)]}

    return "matrix=" + json.dumps(matrix)


# If called as main, run all builds from builds.yml
if __name__ == '__main__':
    builds = load_builds(os.path.dirname(__file__) + "/builds.yml", filter_fun=build_filter)

    if len(sys.argv) > 1 and sys.argv[1] == '--dump':
        pprint(builds)
        sys.exit(0)

    if len(sys.argv) > 1 and sys.argv[1] == '--matrix':
        gh_output(to_json(builds))
        sys.exit(0)

    if len(sys.argv) > 1 and sys.argv[1] == '--hw':
        sys.exit(run_builds(builds, hw_run))

    if len(sys.argv) > 1 and sys.argv[1] == '--post':
        release_mq_locks(builds)
        sys.exit(0)

    sys.exit(run_builds(builds, hw_build))
