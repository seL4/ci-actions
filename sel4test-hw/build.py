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

    if build.get_platform().name == "RPI4":
        # The Raspberry Pi 4B model that is used for hardware testing has 4GB
        # of RAM, which we must specify when building the kernel.
        build.settings["RPI4_MEMORY"] = "4096"

    script = [
        ["../init-build.sh"] + build.settings_args(),
    ]

    if verification_equals_release(build) and build.is_release():
        base_args = [arg for arg in build.settings_args()
                     if not arg.startswith('-DRELEASE=')]
        script.append(["check-config-eq.sh"] + base_args)

    script += [
        ["ninja"],
        ["tar", "czf", f"../{build.name}-images.tar.gz", "images/"],
        ["cp", "kernel/kernel.elf", f"../{build.name}-kernel.elf"]
    ]

    return run_build_script(manifest_dir, build, script)


def hw_run(manifest_dir: str, build: Build):
    """Run one hardware test."""

    if build.is_disabled():
        print(f"Build {build.name} disabled, skipping.")
        return SKIP

    if build.is_verification() and build.is_smp:
        print(f"Build {build.name} is verification+SMP, skipping.")
        return SKIP

    script, final = build.hw_run(junit_results)

    return run_build_script(manifest_dir, build, script, final_script=final, junit=True)


def verification_equals_release(build: Build) -> bool:
    """Return whether in this build release and verification settings are equivalent."""

    return build.get_platform().arch == 'riscv'


def build_filter(build: Build) -> bool:
    plat = build.get_platform()

    if plat.no_hw_build:
        return False

    if build.is_verification() and verification_equals_release(build):
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

        # CACHEFLUSH0001 fails on ODROID_XU4: https://github.com/seL4/sel4test/issues/80
        if plat.name == 'ODROID_XU4' and build.is_debug() and build.is_mcs() and \
           build.is_hyp() and build.is_clang() and build.get_mode() == 32:
            return False

        # SCHED_CONTEXT_0014 fails ODROID_C4: https://github.com/seL4/seL4/issues/928
        if plat.name in ['ODROID_C4'] and \
           build.is_mcs() and build.is_smp() and (build.is_verification() or build.is_debug()):
            return False

        # zynqmp 32 does not work with MCS
        if plat.name == 'ZYNQMP' and build.get_mode() == 32 and build.is_mcs():
            return False

    if plat.arch == 'x86':
        # Bamboo config says no VTX for SMP or verification
        if build.is_hyp() and (build.is_smp() or build.is_verification()):
            return False

    if plat.arch == 'riscv':
        # see also https://github.com/seL4/seL4/issues/1160
        if plat.name == 'HIFIVE' and build.is_clang() and build.is_smp() and build.is_release():
            return False

    # run NUM_DOMAINS > 1 tests only on release builds
    if build.is_domains() and not build.is_release():
        return False

    return True


def to_build_matrix(builds: List[Build]) -> str:
    """Return a GitHub build matrix for hw-build jobs as a JSON string.

    Splits by debug-level, compiler, march, and subgroup (if there is more than one).
    """

    sorted_platforms = sorted(set([b.get_platform() for b in builds]), key=lambda p: p.name)
    # Collect unique (march, subgroup) pairs. For most march there is only one subgroup.
    march_subgroups = sorted(set((p.march, p.subgroup) for p in sorted_platforms))

    debug_levels = ["debug", "release", "verification"]
    compilers = ["gcc", "clang"]
    base_entries = [
        {"march": m, "compiler": c, "subgroup": s}
        for m, s in march_subgroups for c in compilers
    ]

    include = [
        {**entry, "debug": d}
        for d in debug_levels for entry in base_entries
    ]

    return json.dumps({"include": include})


def to_matrix(builds: List[Build]) -> tuple[str, int]:
    """Return a GitHub hw-run matrix as a JSON string and max-parallel value.

    The matrix is ordered by debug level with max-parallel set such that debug levels run roughly
    sequentially per board. None of that ordering is guaranteed by GitHub actions, but seems to
    work out Ok. The purpose of sequential runs is to get more fine-grained ability to re-run
    jobs without overloading the machine queue.
    """

    def run_for_plat(plat: Platform) -> List[dict]:
        if plat.no_hw_test or plat.no_hw_build:
            return []

        p = plat.name
        m = plat.march
        s = plat.subgroup

        # separate runs for each compiler on arm
        if plat.arch == 'arm':
            return [
                {"platform": p, "march": m, "subgroup": s, "compiler": "gcc"},
                {"platform": p, "march": m, "subgroup": s, "compiler": "clang"},
            ]

        if plat.arch == 'riscv':
            return [
                {"platform": p, "march": m, "subgroup": s, "compiler": "gcc"},
                {"platform": p, "march": m, "subgroup": s, "compiler": "clang"},
            ]

        # separate runs for each compiler + mode on x86, because we have more machines available
        if plat.arch == 'x86':
            return [
                {"platform": p, "march": m, "subgroup": s, "compiler": "gcc", "mode": 32},
                {"platform": p, "march": m, "subgroup": s, "compiler": "clang", "mode": 32},
                {"platform": p, "march": m, "subgroup": s, "compiler": "gcc", "mode": 64},
                {"platform": p, "march": m, "subgroup": s, "compiler": "clang", "mode": 64},
            ]

    # Sort platforms by name for a stable ordering within each debug level.
    # Uses set for removing duplicates.
    sorted_platforms = sorted(set([b.get_platform() for b in builds]), key=lambda p: p.name)
    base_entries = [run for plat in sorted_platforms for run in run_for_plat(plat)]

    # Split by debug level at the outermost level.
    # Set max-parallel set to len(base_entries) so debug fills all slots first,
    # then each further level starts roughly sequentially as jobs finish.
    debug_levels = ["debug", "release", "verification"]
    include = [
        {**entry, "debug": d}
        for d in debug_levels for entry in base_entries
    ]

    return json.dumps({"include": include}), len(base_entries)


# If called as main, run all builds from builds.yml
if __name__ == '__main__':
    builds = load_builds(os.path.dirname(__file__) + "/builds.yml", filter_fun=build_filter)

    if len(sys.argv) > 1 and sys.argv[1] == '--dump':
        pprint(builds)
        sys.exit(0)

    if len(sys.argv) > 1 and sys.argv[1] == '--matrices':
        run_matrix_json, max_parallel = to_matrix(builds)
        gh_output(f"run_matrix={run_matrix_json}")
        gh_output(f"run_max_parallel={max_parallel}")
        gh_output(f"build_matrix={to_build_matrix(builds)}")
        sys.exit(0)

    if len(sys.argv) > 1 and sys.argv[1] == '--hw':
        sys.exit(run_builds(builds, hw_run))

    if len(sys.argv) > 1 and sys.argv[1] == '--post':
        release_mq_locks(builds)
        sys.exit(0)

    sys.exit(run_builds(builds, hw_build))
