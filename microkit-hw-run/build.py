# Copyright 2021, Proofcraft Pty Ltd
# Copyright 2026, UNSW
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Parse builds.yml and run sel4test hardware builds and runs on each of the build definitions.

Expects seL4-platforms/ to be co-located or otherwise in the PYTHONPATH.
Expects TEST_CASES environment variable to be a JSON.
"""

from builds import Build, Run, run_build_script, run_builds, filtered, get_env_filters
from builds import release_mq_locks, SKIP, build_for_platform
from platforms import Platform, platforms as sel4_platforms, gh_output

from pathlib import Path
from pprint import pprint
from typing import List, Any, Optional

import copy
import json
import os
import sys


class MicrokitRun(Run):
    def hw_run(self, log):
        build = self.build

        script, final = super().hw_run(log)

        try:
            if script[0][0] == "tar":
                script.pop(0)
        except IndexError:
            pass

        return (script, final)


class MicrokitBuild(Build):
    def __init__(self, board: str, config: str, march: str, defaults: dict):
        board_upper = board.upper()

        if sel4_platforms.get(board_upper):
            platform = board_upper
        else:
            for platform_obj in sel4_platforms.values():
                # print(f"considering sel4 platform board {platform_obj} for board {board}")
                if board in platform_obj.microkit_boards:
                    platform = platform_obj.name
                    break
            else:
                raise Exception(
                    f"unknown platforms.yml entry for microkit board '{board}'"
                )

        super().__init__(
            {
                f"{board_upper}_{config}": {
                    "platform": platform,
                    # always 64-bit for microkit at this time
                    "mode": 64,
                    "microkit_board": board,
                    "microkit_config": config,
                    "microkit_march": march,
                }
            },
            defaults,
        )
        self.update_settings()

        self.files = [self.get_image_path()]
        if march == "x86_64":
            self.files.insert(
                0,
                (
                    Path(os.environ["MICROKIT_SDK"])
                    / "board"
                    / board
                    / config
                    / "elf"
                    / "sel4_32.elf"
                ).as_posix(),
            )

    def get_image_path(self) -> str:
        return (
            Path(os.environ["GITHUB_WORKSPACE"]) / f"{self.name}.loader.img"
        ).as_posix()

    def is_disabled(self) -> bool:
        platform = self.get_platform()
        return platform.microkit_no_hw_test or ("debug" not in self.microkit_config)

    def hw_run(self, log):
        return MicrokitRun(self).hw_run(log)


def hw_run(manifest_dir: str, build: MicrokitBuild) -> int:
    """Run one hardware test."""

    if build.is_disabled():
        print(f"Test {build.name} disabled, skipping.")
        return SKIP

    script, final = build.hw_run(f"{build.name}")

    return run_build_script(
        manifest_dir, build, script, final_script=final, junit=False
    )


def test_filter(build: MicrokitBuild) -> bool:
    plat = build.get_platform()

    if plat.microkit_no_hw_build:
        return False

    return True


def hw_build(manifest_dir: str, build: MicrokitBuild) -> int:
    """Run one hardware build"""

    MICROKIT_SDK = Path(os.environ["MICROKIT_SDK"])
    GITHUB_WORKSPACE = Path(os.environ["GITHUB_WORKSPACE"])
    BUILD_DIR = GITHUB_WORKSPACE / "builds" / build.name
    microkit_board = build.microkit_board
    microkit_config = build.microkit_config

    script = [
        ["mkdir", "-p", BUILD_DIR.as_posix()],
        [
            "make",
            "-C",
            (MICROKIT_SDK / "example" / "hello").as_posix(),
            f"BUILD_DIR={BUILD_DIR}",
            f"MICROKIT_SDK={MICROKIT_SDK}",
            f"MICROKIT_BOARD={microkit_board}",
            f"MICROKIT_CONFIG={microkit_config}",
        ],
        ["cp", (BUILD_DIR / "loader.img").as_posix(), build.get_image_path()],
    ]

    return run_build_script(manifest_dir, build, script)


def load_builds_microkit(filter_fun=lambda x: True) -> List[MicrokitBuild]:
    test_cases: list[dict[str, str]] = json.loads(os.environ["TEST_CASES"])

    # keep in sync with action.yml
    env_filters = get_env_filters(keys=["board", "march", "config"])

    DEFAULTS = {
        "success": "hello, world",
        # these should finish quickly
        "timeout": 120,
    }

    builds = []
    for test_case in test_cases:
        board = test_case["board"]
        config = test_case["config"]
        march = test_case["march"]

        build: Optional[MicrokitBuild] = MicrokitBuild(board, config, march, DEFAULTS)

        build = build if filter_fun(build) else None
        build = filtered(build, env_filters)
        if build:
            builds.append(build)

    return builds


def to_json(builds: List[MicrokitBuild]) -> str:
    """Return a GitHub build matrix per enabled hardware platform as GitHub output assignment."""

    boards = sorted(set([(b.microkit_board, b.microkit_march) for b in builds]))
    matrix = {
        "include": [{"board": board, "march": march} for (board, march) in boards]
    }

    return "gh_matrix=" + json.dumps(matrix)


# If called as main, run all builds from builds.yml
if __name__ == "__main__":
    builds = load_builds_microkit(filter_fun=test_filter)

    if len(builds) == 0:
        raise Exception("no builds available")

    if len(sys.argv) > 1 and sys.argv[1] == "--dump":
        pprint(builds)
        sys.exit(0)

    if len(sys.argv) > 1 and sys.argv[1] == "--matrix":
        gh_output(to_json(builds))
        sys.exit(0)

    if len(sys.argv) > 1 and sys.argv[1] == "--hw":
        sys.exit(run_builds(builds, hw_run))

    if len(sys.argv) > 1 and sys.argv[1] == "--post":
        release_mq_locks(builds)
        sys.exit(0)

    sys.exit(run_builds(builds, hw_build))
