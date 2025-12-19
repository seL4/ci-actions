# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Parse builds.yml and either build sel4bench images or run sel4bench images.

Expects seL4-platforms/ to be co-located or otherwise in the PYTHONPATH.
"""

from builds import Build, Run, run_build_script, run_builds, load_builds, load_yaml
from builds import release_mq_locks, filtered, get_env_filters, printc, ANSI_RED
from builds import SKIP, SUCCESS, REPEAT, FAILURE

from pprint import pprint
from typing import List, Optional

import json
import os
import sys
import subprocess
import time


def adjust_build_settings(build: Build):
    if 'BAMBOO' in build.settings:
        del build.settings['BAMBOO']  # not used in this build, avoid warning

    # see discussion on https://github.com/seL4/sel4bench/pull/20 for hifive exclusion
    if build.is_smp() or build.get_platform().name == 'HIFIVE':
        build.settings['HARDWARE'] = 'FALSE'
        build.settings['FAULT'] = 'FALSE'


def hw_build(manifest_dir: str, build: Build):
    """Do one hardware build."""

    adjust_build_settings(build)

    script = [
        ["../init-build.sh"] + build.settings_args(),
        ["ninja"],
        ["tar", "czf", f"../{build.name}-images.tar.gz", "images/"]
    ]

    return run_build_script(manifest_dir, build, script)


def extract_json(results: str, run: Run) -> int:
    """Process test logs to extract JSON results."""

    res = subprocess.run(
        f"cat {results} | "
        f"sed -e '/JSON OUTPUT/,/END JSON OUTPUT/!d' | "
        f"sed 's/END JSON OUTPUT//' | sed 's/JSON OUTPUT//' | jq '.' "
        f" > ../{run.name}.json",
        shell=True
    )

    if res.returncode != 0:
        printc(ANSI_RED, f"Run {run.name} failed to parse JSON results.")
        sys.stdout.flush()

    # If the JSON output is not wellformed, repeat this test.
    # Likely just a garbled character on the serial console.
    return SUCCESS if res.returncode == 0 else REPEAT


def hw_run(manifest_dir: str, run: Run):
    """Run one hardware test."""

    if run.build.is_disabled():
        print(f"Run {run.name} disabled, skipping.")
        return SKIP

    tries = 3
    results = 'results.txt'

    while tries > 0:
        tries -= 1

        script, final = run.hw_run(results)
        result = run_build_script(manifest_dir, run, script, final_script=final)

        if result == SUCCESS:
            result = extract_json(results, run)
            if result == SUCCESS:
                return SUCCESS
            elif result == REPEAT and tries > 0:
                time.sleep(10)
                continue
            else:
                return FAILURE
        else:
            return result


def build_filter(build: Build) -> bool:
    plat = build.get_platform()

    if plat.no_hw_build:
        return False

    # temporarily remove QUARTZ64 until build failure is resolved
    if plat.name == 'QUARTZ64':
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


def get_results(run: Run) -> List[float]:
    """Get the benchmark results from JSON for a specific run."""

    with open(f"{run.name}.json") as f:
        data = json.load(f)

    ipc_call = 0
    ipc_call_fpu = 0
    ipc_reply = 0
    ipc_reply_fpu = 0
    irq_invoke = 0
    notify = 0
    notify_s = '?'

    for bench in data:
        if bench['Benchmark'].startswith('One way IPC microbenchmarks'):
            results = bench['Results']
            for result in results:
                if result['Function'] == 'seL4_Call' and not result['Same vspace?'] and \
                   result['Direction'] == 'client->server' and result['IPC length'] == 0:
                    ipc_call = round(result['Mean'])
                    ipc_call_s = round(result['Stddev'])
                elif result['Function'] == 'seL4_Call (FPU)' and not result['Same vspace?'] and \
                        result['Direction'] == 'client->server' and result['IPC length'] == 0:
                    ipc_call_fpu = round(result['Mean'])
                    ipc_call_fpu_s = round(result['Stddev'])
                elif result['Function'] == 'seL4_ReplyRecv' and not result['Same vspace?'] and \
                        result['Direction'] == 'server->client' and result['IPC length'] == 0:
                    ipc_reply = round(result['Mean'])
                    ipc_reply_s = round(result['Stddev'])
                elif result['Function'] == 'seL4_ReplyRecv (FPU)' and not result['Same vspace?'] and \
                        result['Direction'] == 'server->client' and result['IPC length'] == 0:
                    ipc_reply_fpu = round(result['Mean'])
                    ipc_reply_fpu_s = round(result['Stddev'])
        if bench['Benchmark'].startswith('Signal to process of higher prio'):
            results = bench['Results']
            for result in results:
                if result['Prio'] == 1:
                    notify = round(result['Mean'])
                    notify_s = round(result['Stddev'])

        if bench['Benchmark'].startswith('IRQ path cycle count'):
            results = bench['Results']
            for result in results:
                if result['Type'] == 'With context switch (early processing)':
                    irq_invoke = round(result['Mean'])
                    irq_invoke_s = round(result['Stddev'])

        if ipc_call > 0 and ipc_call_fpu > 0 and ipc_reply > 0 and ipc_reply_fpu > 0 and irq_invoke > 0 and notify > 0:
            break

    return [irq_invoke, irq_invoke_s, ipc_call, ipc_call_s, ipc_reply, ipc_reply_s, notify, notify_s,
            ipc_call_fpu, ipc_call_fpu_s, ipc_reply_fpu, ipc_reply_fpu_s]


def get_run(runs: List[Run], name: str) -> Optional[Run]:
    """Get a run by name."""

    for run in runs:
        if run.name == name:
            return run

    print(f"Run {name} not found.")
    return None


def gen_json(runs: List[Run], yml, file_name: str):
    """Generate json with benchmark results according to the set defined in builds.yml"""

    manifest_sha = os.getenv('INPUT_MANIFEST_SHA')

    boards = yml["boards"]
    sections = yml["results"]

    # Data columns (column header, key)
    data_cols = [
        ('ISA', 'isa'),
        ('Mode', 'mode'),
        ('Core/SoC/Board', 'name'),
        ('Clock', 'clock'),
        ('IRQ Invoke', 'irq'),
        ('IPC call', 'call'),
        ('IPC reply', 'reply'),
        ('Notify', 'notify'),
    ]

    # Compilation details (column header, key)
    comp_cols = [
        ('ISA', 'isa'),
        ('Mode', 'mode'),
        ('Core/SoC/Board', 'name'),
        ('Compiler', 'compiler'),
        ('Build command', 'build_command'),
    ]

    # Results
    data = {}
    for section_name in sections:
        data[section_name] = []
        for result in sections[section_name]:
            board_name = result['board']
            board = boards.get(board_name)
            if not board:
                print(f'Board {board_name} not found in builds.yml')
                continue
            run = get_run(runs, result['run'])
            if not run:
                print(f'Run {run} not found.')
                continue
            row = {}
            row['board'] = board_name
            row['run'] = result['run']
            row['isa'] = run.build.getISA()
            row['mode'] = run.build.get_mode()
            if board.get('core'):
                row['name'] = f"{board['core']}/{board['soc']}/{board_name}"
            else:
                row['name'] = f"{board['soc']}/{board_name}"
            note = board.get('note')
            if note:
                row['note'] = board.get('note')
            row['clock'] = board.get('clock')
            row['compiler'] = board['compiler']
            results = get_results(run)
            row['irq'] = (results[0], results[1])
            row['call'] = (results[2], results[3])
            row['reply'] = (results[4], results[5])
            row['notify'] = (results[6], results[7])
            row['call_fpu'] = (results[8], results[9])
            row['reply_fpu'] = (results[10], results[11])

            adjust_build_settings(run.build)
            build_command = " ".join(["init-build.sh"] + run.build.settings_args())
            row['build_command'] = build_command

            data[section_name].append(row)

    final = {}
    final['data_cols'] = data_cols
    final['comp_cols'] = comp_cols
    final['data'] = data
    if manifest_sha:
        final['sha'] = manifest_sha[0:8]

    with open(file_name, 'w') as f:
        json.dump(final, f, indent=2)


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

    if len(sys.argv) > 1 and sys.argv[1] == '--web':
        gen_json(make_runs(builds), yml, "benchmarks.json")
        sys.exit(0)

    sys.exit(run_builds(builds, hw_build))
