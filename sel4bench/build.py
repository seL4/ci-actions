# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Parse builds.yml and either build sel4bench images or run sel4bench images.

Expects seL4-platforms/ to be co-located or otherwise in the PYTHONPATH.
"""

from builds import Build, Run, run_build_script, run_builds, load_builds, load_yaml
from builds import release_mq_locks, filtered, get_env_filters, printc, ANSI_RED

from pprint import pprint
from typing import List

import os
import sys
import subprocess


def hw_build(manifest_dir: str, build: Build):
    """Do one hardware build."""

    del build.settings['BAMBOO']  # not used in this build, avoid warning

    if build.is_smp():
        build.settings['HARDWARE'] = 'FALSE'
        build.settings['FAULT'] = 'FALSE'

    script = [
        ["../init-build.sh"] + build.settings_args(),
        ["ninja"],
        ["tar", "czf", f"../{build.name}-images.tar.gz", "images/"]
    ]

    return run_build_script(manifest_dir, build.name, script)


def extract_json(results: str, run: Run) -> bool:
    """Process test logs to extract JSON results."""

    res = subprocess.run(
        f"cat {results} | "
        f"sed -e '/JSON OUTPUT/,/END JSON OUTPUT/!d' | "
        f"sed 's/END JSON OUTPUT//' | sed 's/JSON OUTPUT//' | jq '.' "
        f" > ../{run.name}.json",
        shell=True
    )

    return res.returncode == 0


def hw_run(manifest_dir: str, run: Run):
    """Run one hardware test."""

    if run.build.is_disabled():
        print(f"Run {run.name} disabled, skipping.")
        return True

    results = 'results.txt'
    script, final = run.hw_run(results)

    success = run_build_script(manifest_dir, run.name, script, final_script=final)

    # parse and store results
    if success:
        success = extract_json(results, run)
        if not success:
            printc(ANSI_RED, f"Run {run.name} failed to parse JSON results.")
            sys.stdout.flush()

    return success


def build_filter(build: Build) -> bool:
    plat = build.get_platform()

    if plat.no_hw_build:
        return False

    # sel4bench not yet set up for MCS+SMP
    if build.is_mcs() and build.is_smp():
        return False

    # no MCS on ia32
    if plat.name == 'PC99' and build.is_mcs() and build.get_mode() == 32:
        return False

    return True


def make_runs(builds: List[Build]) -> List[Run]:
    """Split PC99 builds into runs for haswell3 and skylake, no changes to the rest"""

    # could filter more generically, but we're really only interested in REQ here,
    # and so far only for PC99
    req = os.getenv('INPUT_REQ')

    # specific benchmarking machines for PC99:
    pc99_reqs = ['skylake', 'haswell3']

    runs = []

    for build in builds:
        if build.get_platform().name == 'PC99':
            for r in pc99_reqs:
                if not req or r == req:
                    runs.append(Run(build, '_' + r, [r]))
        else:
            runs.append(Run(build))

    return runs


# If called as main, run all builds from builds.yml
if __name__ == '__main__':
    yml = load_yaml(os.path.dirname(__file__) + "/builds.yml")
    builds = load_builds(None, filter_fun=build_filter, yml=yml)

    # add additional builds; run only env filter, trusting that manual builds
    # don't need to be filtered further
    default_build = yml.get("default", {})
    env_filters = get_env_filters()
    more_builds = [Build(b, default_build) for b in yml.get("more_builds", [])]
    builds.extend([b for b in more_builds if b and filtered(b, env_filters)])

    if len(sys.argv) > 1 and sys.argv[1] == '--dump':
        pprint(builds)
        sys.exit(0)

    if len(sys.argv) > 1 and sys.argv[1] == '--hw':
        sys.exit(run_builds(make_runs(builds), hw_run))

    if len(sys.argv) > 1 and sys.argv[1] == '--post':
        release_mq_locks(builds)
        sys.exit(0)

    sys.exit(run_builds(builds, hw_build))
