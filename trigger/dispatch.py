#!/usr/bin/env python3
#
# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

import os
import yaml
import requests
import sys

if __name__ == '__main__':
    token = os.environ.get('INPUT_TOKEN')
    if not token:
        print("Need $INPUT_TOKEN for authentication.")
        sys.exit(1)

    src_repo = os.environ.get('GITHUB_REPOSITORY')
    if not src_repo:
        print("GITHUB_REPOSITORY not set.")
        sys.exit(1)

    if not src_repo.startswith('seL4/'):
        print("This action is only for repositories in the seL4 GitHub org.")
        sys.exit(1)

    # remove 'seL4/' prefix and standardise case for lookup in notify.yml
    src_repo = src_repo[5:].lower()

    name = os.path.dirname(__file__) + "/notify.yml"
    with open(name, 'r') as f:
        notif = yaml.safe_load(f)

    targets = notif.get(src_repo, [])

    if targets == []:
        print(f"No notification targets for {src_repo}.")

    user = 'seL4-ci'
    msg = {"event_type": "deps-update", "client_payload": {"sender": src_repo}}

    print("Sending repository_dispatches:")

    for repo in targets:
        print(f"  Creating repository_dispatch for {repo}...", end='')
        url = f"https://api.github.com/repos/seL4/{repo}/dispatches"
        r = requests.post(url, auth=(user, token), json=msg, timeout=10)
        if r.ok:
            print(" done.")
        else:
            print(" failed.")

    print("Done.")
