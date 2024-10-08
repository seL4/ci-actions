# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Parse builds.yml and run CAmkES VM test on each of the build definitions.

Expects seL4-platforms/ to be co-located or otherwise in the PYTHONPATH.
"""

from builds import Build, run_build_script, run_builds, load_builds, release_mq_locks, SKIP, sim_script
from pprint import pprint

import os
import sys


# See also builds.yml for how builds are split up in this test. We use the build
# matrix and filtering for the hardware builds, and an explicit list for the
# simulation builds.

# The only thing this really has in common with a "Build" is the "name" field.

def run_build(manifest_dir: str, build: Build):
    """Run one CAmkES VM test."""

    plat = build.get_platform()

    build.files = plat.image_names(build.get_mode(), "capdl-loader")
    build.settings['CAMKES_VM_APP'] = build.app or build.name
    if 'BAMBOO' in build.settings:
        del build.settings['BAMBOO']    # not used in this test, avoid warning

    if plat.arch == 'x86':
        del build.settings['PLATFORM']  # not used for x86 in this test, avoid warning

    # if vm_platform is set, the init-build.sh script expects a different platform name.
    if build.vm_platform:
        build.settings['PLATFORM'] = build.vm_platform

    script = [
        ["../init-build.sh"] + build.settings_args(),
        ["ninja"],
        ["tar", "czf", f"../{build.name}-images.tar.gz", "images/"],
    ]

    if plat.has_simulation and plat.name != 'PC99':
        script.append(sim_script(build.success, failure=build.error))

    return run_build_script(manifest_dir, build, script)


def hw_run(manifest_dir: str, build: Build):
    """Run one hardware test."""

    if build.is_disabled():
        print(f"Build {build.name} disabled, skipping.")
        return SKIP

    plat = build.get_platform()
    build.files = plat.image_names(build.get_mode(), "capdl-loader")

    script, final = build.hw_run('log.txt')

    return run_build_script(manifest_dir, build, script, final_script=final)


# If called as main, run all builds from builds.yml
if __name__ == '__main__':
    builds = load_builds(os.path.dirname(__file__) + "/builds.yml")

    if len(sys.argv) > 1 and sys.argv[1] == '--dump':
        pprint(builds)
        sys.exit(0)
    elif len(sys.argv) > 1 and sys.argv[1] == '--hw':
        sys.exit(run_builds(builds, hw_run))
    elif len(sys.argv) > 1 and sys.argv[1] == '--post':
        release_mq_locks(builds)
        sys.exit(0)

    sys.exit(run_builds(builds, run_build))
