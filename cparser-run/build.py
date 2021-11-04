# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Parse builds.yml and run l4v C Parser test on each of the build definitions.

Expects seL4-platforms/ to be co-located or otherwise in the PYTHONPATH.
"""

from builds import run_build_script, run_builds, load_builds
from pprint import pprint

import os
import sys


def run_cparser(manifest_dir: str, build):
    """Single run of the C Parser test, for one build definition"""

    script = [
        ["../init-build.sh"] + build.settings_args(),
        ["ninja", "kernel_all_pp_wrapper"],
        ["/c-parser/standalone-parser/c-parser", build.l4v_arch,
         '--underscore_idents', 'kernel/kernel_all_pp.c'],
    ]

    return run_build_script(manifest_dir, build, script)


# If called as main, run all builds from builds.yml
if __name__ == '__main__':
    builds = load_builds(os.path.dirname(__file__) + "/builds.yml")

    if len(sys.argv) > 1 and sys.argv[1] == '--dump':
        pprint(builds)
        sys.exit(0)

    sys.exit(run_builds(builds, run_cparser))
