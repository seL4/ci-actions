# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Parse builds.yml and run CAmkES VM test on each of the build definitions.

Expects seL4-platforms/ to be co-located or otherwise in the PYTHONPATH.
"""

from builds import Build, run_build_script, run_builds, load_builds
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
    del build.settings['BAMBOO']    # not used in this test, avoid warning

    if plat.arch == 'x86':
        del build.settings['PLATFORM']  # not used for x86 in this test, avoid warning
        # build.req set by default in builds.yml for x86
    else:
        build.req = plat.req or plat.name.lower()

    script = [
        ["../init-build.sh"] + build.settings_args(),
        ["ninja"],
        ["tar", "czf", f"../{build.name}-images.tar.gz", "images/"],
    ]

    if plat.simulation_binary:
        script.append(
            ["bash", "-c",
             f"expect -c 'spawn ./simulate; set timeout 3000; expect \"{build.success}\"'"]
        )

    if not plat.disabled:
        script.append(["echo", f"Hardware run for {build.req}, skipping"])
    else:
        script.append(["echo", f"Platform for build {build.name} disabled, skipping"])

    return run_build_script(manifest_dir, build.name, script)


# If called as main, run all builds from builds.yml
if __name__ == '__main__':
    builds = load_builds(os.path.dirname(__file__) + "/builds.yml")

    if len(sys.argv) > 1 and sys.argv[1] == '--dump':
        pprint(builds)
        sys.exit(0)

    sys.exit(run_builds(builds, run_build))
