# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Parse builds.yml and run l4v C Parser test on each of the build definitions.

Expects seL4-platforms/ to be co-located or otherwise in the PYTHONPATH.
"""

from platforms import load_ver_builds

import os
import shutil
import subprocess
import sys


def run(args: list):
    """Echo + run command with arguments; raise exception on exit != 0"""

    print("+++ " + " ".join(args))
    print(subprocess.check_output(args, text=True, stderr=subprocess.STDOUT))


def run_build_script(manifest_dir: str, script: list) -> bool:
    """Run a build script in a separate build/ directory

    A build script is a list of commands, which itself is a list of command and
    arguments passed to subprocess.run().

    The build stops at the first failing step (or the end) and fails if any
    step fails.
    """

    print(f"::group::{build.name}")
    print(f"-----------[ start test {build.name} ]-----------")

    os.chdir(manifest_dir)

    build_dir = 'build'
    try:
        shutil.rmtree(build_dir)
    except IOError:
        pass

    os.mkdir(build_dir)
    os.chdir(build_dir)

    success = True
    try:
        for line in script:
            run(line)
    except subprocess.CalledProcessError:
        success = False

    print("SUCCESS" if success else "FAILED")
    print(f"-----------[ end test {build.name} ]-----------\n")
    print("::endgroup::")

    return success


def run_cparser(manifest_dir: str, build):
    """Single run of the C Parser test, for one build definition"""

    script = [
        ["../init-build.sh"] + build.settings_args(),
        ["ninja", "kernel_all_pp_wrapper"],
        ["/c-parser/standalone-parser/c-parser", build.l4v_arch,
         '--underscore_idents', 'kernel/kernel_all_pp.c'],
    ]

    return run_build_script(manifest_dir, script)


# If called as main, run all builds from builds.yml
if __name__ == '__main__':
    builds = load_ver_builds(os.path.dirname(__file__) + "/builds.yml")

    manifest_dir = os.getcwd()
    successes = []
    fails = []
    for build in builds:
        (successes if run_cparser(manifest_dir, build) else fails).append(build.name)

    print("Successful tests: " + ", ".join(successes))
    if fails != []:
        print("FAILED tests: " + ", ".join(fails))

    sys.exit(0 if fails == [] else 1)
