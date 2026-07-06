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

import copy
import json
import os
import sys
import subprocess
from datetime import datetime, timezone
import time


METRICS_FILE = "sel4bench-results/metrics.yml"


def load_metrics() -> List[dict]:
    """Load metrics definitions from METRICS_FILE."""

    try:
        metrics = load_yaml(METRICS_FILE)["metrics"]
    except FileNotFoundError:
        printc(ANSI_RED, f"Could not find metrics file {METRICS_FILE}.")
        sys.exit(1)
    except Exception as e:
        printc(ANSI_RED, f"Failed to parse metrics file {METRICS_FILE}: {e}")
        sys.exit(1)

    return metrics


def adjust_build_settings(build: Build):
    if 'BAMBOO' in build.settings:
        del build.settings['BAMBOO']  # not used in this build, avoid warning

    # allow the number of benchmark iterations to be overridden via the action input
    iterations = os.getenv('INPUT_ITERATIONS')
    if iterations:
        build.settings['ITERATIONS'] = iterations

    if build.settings['ITERATIONS']:
        scale = max(1, float(build.settings['ITERATIONS']) * 0.75)
        build.timeout = round(build.timeout * scale)

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

    # Make sure there is at least one JSON OUTPUT block. This can happen when
    # mq.sh fails catastrophically at its job, sel4bench gets interrupted, something
    # else boots and runs instead, produces "All is well", but no sel4bench output.
    # This should really not be necessary, but here we are.
    if subprocess.run(f"grep -q 'JSON OUTPUT' {results}", shell=True).returncode != 0:
        printc(ANSI_RED, f"Run {run.name} produced no JSON OUTPUT results.")
        sys.stdout.flush()
        return REPEAT

    # Only extract the first JSON OUTPUT block. In rare cases (mq failure to
    # detect boot completion), there can be two, and both are valid results.
    res = subprocess.run(
        f"cat {results} | "
        f"sed -n '/JSON OUTPUT/,/END JSON OUTPUT/p; /END JSON OUTPUT/q' | "
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

    adjust_build_settings(run.build)

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

    # Read metrics definitions and turn the metrics list into a dict
    metrics_by_key = {m['key']: m for m in load_metrics()}

    # Map table column name to metrics.yml key
    metric_of_col = {
        'irq': 'irq_switch_early',
        'call': 'ipc_call',
        'reply': 'ipc_reply',
        'notify': 'notify_process',
        'call_fpu': 'ipc_call_fpu',
        'reply_fpu': 'ipc_reply_fpu',
    }

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
            with open(f"results/{run.name}.json") as f:
                try:
                    run_data = json.load(f)
                except json.JSONDecodeError as e:
                    sys.exit(f"Failed to parse JSON from {f.name}: {e}")
            for col, key in metric_of_col.items():
                iterations = find_benchmark(run_data, metrics_by_key[key])
                value = iterations[0]  # for now show only first iteration on web
                row[col] = (value[3], round(value[6]))  # 3 = mean, 6 = stddev

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


def find_in_iteration(entries: List[dict], metric: dict) -> Optional[List]:
    """Find the benchmark specified by the metric dict (name + row matches)
       within the entries of a single iteration, and extract [min, q1, median,
       mean, q3, max, stddev, n]. Return None if not found."""

    for bench in entries:
        if bench['Benchmark'] != metric['benchmark']:
            continue
        for row in bench['Results']:
            if all(row.get(k) == v for k, v in metric['match'].items()):
                mean = round(row['Mean'])
                stddev = round(row['Stddev'], 1)
                n = row['Samples']
                if metric.get('distribution'):
                    return [round(row['Min']), round(row['1st quantile']),
                            round(row['Median']), mean, round(row['3rd quantile']),
                            round(row['Max']), stddev, n]
                return [0, 0, 0, mean, 0, 0, stddev, n]

    return None


def find_benchmark(data: List[dict], metric: dict) -> Optional[List[List]]:
    """Find the benchmark specified by the metric dict (name + row matches) and
       return a list of result arrays [min, q1, median, mean, q3, max, stddev,
       n], one per iteration."""

    # group by iteration first, so we can keep the iteration matching separate
    # from the benchmark name matching
    by_iteration = {}
    for bench in data:
        by_iteration.setdefault(bench.get('Iteration', 0), []).append(bench)

    results = []
    for iteration in sorted(by_iteration):
        value = find_in_iteration(by_iteration[iteration], metric)
        if value is not None:
            results.append(value)

    return results if results else None


def jsonl_path(run: Run) -> str:
    year = datetime.now(timezone.utc).year
    platform = run.build.get_platform().name.lower()
    if run.req:
        platform = f"{platform}-{run.req[0]}"
    return f"sel4bench-results/{year}/{platform}/{run.name}.jsonl"


def add_metrics(runs: List[Run]) -> None:
    """Read all generated JSON run results, reduce them according to metrics.yml in
       seL4/sel4bench-results, and append to time series in files in sel4bench-results.

       Does not commit/push. Expects JSON to be present in results/ and the results repo
       to be checked out under sel4bench-results/"""

    time_stamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    header = {'ts': time_stamp}
    header['sha'] = os.getenv('INPUT_MANIFEST_SHA')[0:8]
    header['sha_kernel'] = os.getenv('INPUT_SEL4_SHA')[0:8]
    header['sha_bench'] = os.getenv('INPUT_SEL4BENCH_SHA')[0:8]
    header['run_id'] = int(os.getenv('GITHUB_RUN_ID'))

    metrics = load_metrics()

    for run in runs:
        results_file = f"results/{run.name}.json"
        if not os.path.exists(results_file):
            # not all potential runs are in the CI run/build matrix
            continue

        with open(results_file) as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                sys.exit(f"Failed to parse JSON from {f.name}: {e}")

        entry = copy.deepcopy(header)
        for metric in metrics:
            value = find_benchmark(data, metric)
            if value is not None:
                entry[metric['key']] = value

        out_file = jsonl_path(run)
        os.makedirs(os.path.dirname(out_file), exist_ok=True)
        with open(out_file, 'a') as f:
            f.write(json.dumps(entry, separators=(',', ':')) + "\n")


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

    if len(sys.argv) > 1 and sys.argv[1] == '--metrics':
        add_metrics(make_runs(builds))
        sys.exit(0)

    sys.exit(run_builds(builds, hw_build))
