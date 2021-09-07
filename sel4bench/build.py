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

from datetime import datetime

import json
import os
import sys
import subprocess
import time


def adjust_build_settings(build: Build):
    del build.settings['BAMBOO']  # not used in this build, avoid warning

    if build.is_smp():
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
    ipc_reply = 0
    irq_invoke = 0

    for bench in data:
        if bench['Benchmark'].startswith('One way IPC microbenchmarks'):
            results = bench['Results']
            for result in results:
                if result['Function'] == 'seL4_Call' and not result['Same vspace?'] and \
                   result['Direction'] == 'client->server' and result['IPC length'] == 0:
                    ipc_call = round(result['Mean'])
                    ipc_call_s = round(result['Stddev'])
                elif result['Function'] == 'seL4_ReplyRecv' and not result['Same vspace?'] and \
                        result['Direction'] == 'server->client' and result['IPC length'] == 0:
                    ipc_reply = round(result['Mean'])
                    ipc_reply_s = round(result['Stddev'])
        if bench['Benchmark'].startswith('IRQ path cycle count'):
            results = bench['Results']
            for result in results:
                if result['Type'] == 'Without context switch':
                    irq_invoke = round(result['Mean'])
                    irq_invoke_s = round(result['Stddev'])

        if ipc_call > 0 and ipc_reply > 0 and irq_invoke > 0:
            break

    return [irq_invoke, irq_invoke_s, ipc_call, ipc_call_s, ipc_reply, ipc_reply_s]


def get_run(runs: List[Run], name: str) -> Optional[Run]:
    """Get a run by name."""

    for run in runs:
        if run.name == name:
            return run

    print(f"Run {name} not found.")
    return None


def gen_web(runs: List[Run], yml, file_name: str):
    """Generate web page for benchmark results according to the set defined in builds.yml"""

    manifest_sha = os.getenv('INPUT_MANIFEST_SHA')

    boards = yml["boards"]
    sections = yml["results"]

    th_style = {
        0: 'style=""',
        1: 'style="text-align: center;"',
        2: 'style="text-align: center;"'
    }

    # (column name, th_style, span, width)
    cols = [
        ('ISA', 0, 1, "8ex"),
        ('Mode', 2, 1, "4ex"),
        ('Core/SoC/Board', 0, 1, "40%"),
        ('Clock', 1, 1, "8ex"),
        ('IRQ Invoke', 1, 2, ""),
        ('IPC call', 1, 2, ""),
        ('IPC reply', 1, 2, "")
    ]

    with open(file_name, 'w') as f:
        f.write('<!-- <title>seL4 benchmarks</title> -->\n')
        f.write('<!--\n')
        f.write('Copyright 2021 seL4 Project a Series of LF Projects, LLC.\n')
        f.write('SPDX-License-Identifier: CC-BY-SA-4.0\n')
        f.write('-->\n\n')

        f.write('<h1>Performance</h1>\n')
        f.write('<p>This page displays the latest benchmark numbers for seL4 from the publicly\n')
        f.write('available <a href="https://github.com/seL4/sel4bench">sel4bench repository</a>.\n')
        f.write('The following times are reported as mean and standard deviation in\n')
        f.write('the format <em>mean (std dev)</em>, both rounded to the nearest integer.</p>\n')

        f.write('<ul>')
        f.write('<li><strong>IRQ invoke</strong>: ')
        f.write('Time in cycles to invoke a user-level interrupt handler running in the same\n')
        f.write('address space as the interrupted thread.</li>\n')

        f.write('<li><strong>IPC call</strong>: ')
        f.write('Time in cycles for invoking a server in a different address space on the same core.</li>\n')

        f.write('<li><strong>IPC reply</strong>: ')
        f.write('Time in cycles for a server replying to a client in a different address space on\n')
        f.write('the same core.</li>\n')
        f.write('</ul>')

        # Results
        for section_name in sections:
            f.write(f'<h2>{section_name}</h2>\n')
            f.write(f'<table class="data-table">\n')
            f.write(f'  <tr>\n')
            for (col, style, span, width) in cols:
                if width:
                    the_style = th_style[style][:-1] + f' width: {width};"'
                else:
                    the_style = th_style[style]
                f.write(f'    <th {the_style} colspan="{span}">{col}</th>\n')
            f.write(f'  </tr>')

            for result in sections[section_name]:
                board_name = result['board']
                board = boards.get(board_name)
                if not board:
                    print(f'Board {board_name} not found in builds.yml')
                    continue
                run = get_run(runs, result['run'])
                if not run:
                    continue
                results = get_results(run)
                f.write(f'  <tr>\n')
                f.write(f'    <td>{run.build.getISA()}</td>\n')
                f.write(f'    <td class="data-table-right">{run.build.get_mode()}</td>\n')
                if board.get('core'):
                    f.write(f"    <td>{board['core']}/{board['soc']}/{board_name}")
                else:
                    f.write(f"    <td>{board['soc']}/{board_name}")
                note = board.get('note')
                if note:
                    f.write(f' {note}')
                f.write(f'</td>\n')
                f.write(f"    <td class=\"data-table-right\">{board['clock']}</td>\n")
                f.write(f'    <td class="data-mean">{results[0]}</td>\n')
                f.write(f'    <td class="data-stddev">({results[1]})</td>\n')
                f.write(f'    <td class="data-mean">{results[2]}</td>\n')
                f.write(f'    <td class="data-stddev">({results[3]})</td>\n')
                f.write(f'    <td class="data-mean">{results[4]}</td>\n')
                f.write(f'    <td class="data-stddev">({results[5]})</td>\n')
                f.write(f'  </tr>')

            f.write(f'</table>\n\n')

        # Compilation details
        cols = ['ISA', 'Mode', 'Core/SoC/Board', 'Clock', 'Compiler', 'Build command']

        f.write(f'<h2>Compilation Details</h2>\n')

        f.write(f'<p>')
        f.write(f'All benchmarks were built using the trustworthy-systems/sel4\n')
        f.write(f'docker image from the <a href="https://github.com/seL4/seL4-CAmkES-L4v-dockerfiles">seL4\n')
        f.write(f'docker file repository</a>')
        f.write(f'</p>')

        for section_name in sections:
            f.write(f'<h3>{section_name}</h3>\n')
            f.write(f'<table class="data-table">\n')
            f.write(f'  <tr>\n')
            for col in cols:
                f.write(f'    <th>{col}</th>\n')
            f.write(f'  </tr>')

            for result in sections[section_name]:
                board_name = result['board']
                board = boards.get(board_name)
                if not board:
                    print(f'Board {board_name} not found in builds.yml')
                    continue
                run = get_run(runs, result['run'])
                if not run:
                    continue
                adjust_build_settings(run.build)
                build_command = " ".join(["init-build.sh"] + run.build.settings_args())

                f.write(f'  <tr>\n')
                f.write(f'    <td>{run.build.getISA()}</td>\n')
                f.write(f'    <td class="data-table-right">{run.build.get_mode()}</td>\n')
                if board.get('core'):
                    f.write(f"    <td>{board['core']}/{board['soc']}/{board_name}</td>\n")
                else:
                    f.write(f"    <td>{board['soc']}/{board_name}</td>\n")
                f.write(f"    <td class=\"data-table-right\">{board['clock']}</td>\n")
                f.write(f"    <td>{board['compiler']}</td>\n")
                f.write(f'    <td>{build_command}</td>\n')
                f.write(f'  </tr>')

            f.write(f'</table>\n\n')

        f.write(f'<h2>Source Code</h2>\n')
        date = datetime.now().strftime('%Y-%m-%d')
        f.write(f'<p>This page was generated on {date}')
        if manifest_sha:
            f.write(' for sel4bench-manifest <a href="')
            f.write(f'https://github.com/seL4/sel4bench-manifest/blob/{manifest_sha}/default.xml">')
            f.write(f'{manifest_sha[0:8]}</a>')
        f.write('.</p>')


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
        gen_web(make_runs(builds), yml, "home.pml")
        sys.exit(0)

    sys.exit(run_builds(builds, hw_build))
