#!/usr/bin/env python3
#
# Copyright 2020, Data61, CSRIO
# SPDX-License-Identifier: BSD-2-Clause
#
# Common utils.

import sys
import subprocess


def run_command(*args, **kwargs):
    '''Trivial wrapper for subprocess.check_output'''
    return subprocess.check_output(*args, **kwargs)


def loud_command(*args, **kwargs):
    '''Echo command then run it'''
    print("[Command] %s" % args[0])
    return run_command(*args, **kwargs)


def indent(s, indent='    '):
    '''Indent all lines in a string'''
    return '\n'.join(indent + l for l in s.splitlines())


def format_commit_message(msg):
    '''Add a standard header and footer to a commit message'''
    msg = "[CI] " + msg
    return msg

# Common settings.


git_commit_user = 'seL4 CI'
git_commit_email = 'ci@sel4.systems'


def set_repo_email(repo='.', user=git_commit_user, email=git_commit_email):
    loud_command(['git', 'config', 'user.name', user], cwd=repo)
    loud_command(['git', 'config', 'user.email', email], cwd=repo)
    loud_command(['git', 'config', '--add', 'gerrit.createChangeId', '0'], cwd=repo)
