#!/usr/bin/env python3
#
# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

# Re-generates `notify.yml` from test-repos.yml and current manifest content on
# GitHub

import os
from typing import List
import yaml
import tempfile
from subprocess import run
from xml.etree.ElementTree import parse as xml_parse
from shutil import rmtree


def get_test_repos() -> dict:
    """ Load test-repo.yml mapping from manifest to main test repo. """
    name = os.path.dirname(__file__) + "/test-repos.yml"
    with open(name, 'r') as file:
        return yaml.safe_load(file)


def removesuffix(string: str, suffix: str) -> str:
    """Like .removesuffix in python 3.9"""
    if string.endswith(suffix):
        return string[0:-len(suffix)]
    else:
        return string


def get_manifest(repo: str) -> List[str]:
    """ Return the list of project repos in default.xml of a manifest repo. """

    url = "https://github.com/seL4/" + repo + ".git"

    orig_dir = os.getcwd()
    temp_dir = tempfile.mkdtemp()

    try:
        os.chdir(temp_dir)
        run(['git', 'clone', '--depth', '1', url])
        os.chdir(repo)

        xml = xml_parse("default.xml")
        repos = [prj.attrib['name'] for prj in xml.getroot().findall('project')]
        return [removesuffix(r.lower(), '.git') for r in repos]

    finally:
        os.chdir(orig_dir)
        rmtree(temp_dir)


def add_to_map(map: dict, repos: List[str], notif: str) -> dict:
    """ Add notification to each of the provided repos in the provided map. """

    for r in repos:
        if r.lower() != notif.lower():
            map[r] = map.get(r, []) + [notif]


# file header for generated notif.yml
header = """\
# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

---

# --- GENERATED -- DO NOT EDIT
# run ./gen-notify.py to regenerate this file

"""

if __name__ == '__main__':
    map = {}
    for (manifest, notif) in get_test_repos().items():
        repos = get_manifest(manifest)
        add_to_map(map, repos, notif)

    with open(os.path.dirname(__file__) + "/notify.yml", 'w') as f:
        f.write(header)
        yaml.dump(map, f)
