#!/usr/bin/env python3
#
# Copyright 2021, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause
#

import re
import json
import argparse
import sys

DESCRIPTION = 'Check Isabelle theory files for unwanted outer syntax commands'

# ignore content of parenthesised comments and Isabelle cartouches
start_exp = re.compile(r'\(\*|\{\*|\\<open>')
end_exp = re.compile(r'\*\)|\*\}|\\<close>')

# ignore content of strings and inner syntax; we don't track cartouches/comments within strings
string_delimiter = '"'


def regexp_of(words):
    """Turn word list into regexp.

    Turn a list of word(ish) regexp strings into a compiled regexp that is the big union of
    whole-word matches, with Isabelle-ish conventions for word boundaries. In particular,
    count \' as a letter.
    """
    return re.compile('|'.join(r'\b(?<!\')(?:{0})\b(?!\')'.format(x) for x in words))


diag_words = (
    # title
    "Interactive diagnostic command",
    # message
    "This command is usually used interactively only and should only be checked in for "
    "demonstration purposes.",
    # word(ish) regexps that should be flagged as warnings
    regexp_of([
        'ML_val',
        'class_deps',
        'code_deps',
        'code_thms',
        'find_consts',
        'find_theorems',
        'find_unused_assms',
        'full_prf',
        'help',
        'locale_deps',
        'prf',
        'print_ML_antiquotations',
        'print_abbrevs',
        'print_antiquotations',
        'print_attributes',
        'print_bnfs',
        'print_bundles',
        'print_case_translations',
        'print_cases',
        'print_claset',
        'print_classes',
        'print_codeproc',
        'print_codesetup',
        'print_coercions',
        'print_commands',
        'print_context',
        'print_definitions',
        'print_defn_rules',
        'print_facts',
        'print_induct_rules',
        'print_inductives',
        'print_interps',
        'print_locale',
        'print_locales',
        'print_methods',
        'print_options',
        'print_orders',
        'print_quot_maps',
        'print_quotconsts',
        'print_quotients',
        'print_quotientsQ3',
        'print_quotmapsQ3',
        'print_record',
        'print_rules',
        'print_simpset',
        'print_state',
        'print_statement',
        'print_syntax',
        'print_term_bindings',
        'print_theorems',
        'print_theory',
        'print_trans_rules',
        'smt_status',
        'thm_deps',
        'thm_oracles',
        'thy_deps',
        'unused_thms',
        'value',
        'values',
        'welcome',
        'term',
        'prop',
        'thm',
        'typ',
    ])
)

find_proof_words = (
    # title
    "Proof/counterexample finder",
    # message
    "This command is usually used interactively only to find a proof or counter example, "
    "but only its result should be checked in.",
    # word(ish) regexps that should be flagged as warnings
    regexp_of([
        'nitpick',
        'nunchaku',
        'quickcheck',
        'sledgehammer',
        'solve_direct',
        'try',
        'try0',
    ])
)

sorry_words = (
    # title
    "Unfinished proof",
    # message
    "This command indicates an unfinished or aborted proof.",
    # word(ish) regexps that should be flagged as warnings
    regexp_of([
        '\\\<proof>',
        'sorry',
        'oops'
    ])
)

axiom_words = (
    # title
    "Axioms",
    # message
    "Locales or definitions should usually be preferred to axioms, because axioms may make the "
    "logic inconsistent. Merely introducing a new constant (without new laws) is fine, though.",
    # word(ish) regexps that should be flagged as warnings
    regexp_of([
        'axiomatization',
    ])
)

style_words = (
    # title
    "Style",
    # message
    "This command is considered bad style and should be avoided.",
    # word(ish) regexps that should be flagged as warnings
    regexp_of([
        'apply_end',
        'back'
    ])
)

all_words = [diag_words, find_proof_words, sorry_words, axiom_words, style_words]


def print_matches(matches):
    """Pretty print matches to std out"""
    for m in matches:
        line = m['line_content']
        start = m['start_column']
        end = m['end_column']
        print('> ' + line, end='')
        print('  ', end='')
        for x in range(start):
            print(' ', end='')
        for x in range(end-start):
            print('^', end='')
        print()
        print("{2}, line {0}: {1}".format(m['line'], m['title'], m['file_name']))
        print(m['message'])
        print()


def matches_to_json(matches):
    """Convert matches to json in github annotation format"""
    # https://docs.github.com/en/free-pro-team@latest/rest/reference/checks#annotations-items
    annotations = []
    for m in matches:
        del m['line_content']
        a = {'annotation_level': 'warning'}
        a = {**a, **m}
        annotations.append(a)
    return json.dumps(annotations)


def match_chunk(line, chunk, offset, line_num, matches):
    """Run all regexp classes on a chunk of text and record all matches.

    Updates argument 'matches' by side effect.
    """
    for (title, msg, regex) in all_words:
        for match in regex.finditer(chunk):
            matches.append({'line': line_num,
                            'start_column': offset+match.start(),
                            'end_column': offset+match.end(),
                            'line_content': line,
                            'title': title,
                            'message':  msg})


def lint_file(file_name):
    """Run the linter on one file; return a list of all matches for this file."""
    # how many nested levels of comments we're currently ignoring
    ignoring = 0
    # ignoring content, because we're inside a string
    in_string = False
    # current line number
    line_num = 0
    # list of matches of warning regexps
    matches = []

    with open(file_name) as file:
        for line in file:
            line_num += 1
            # each line can have multiple chunks of non-string or non-comment text we are interested in
            chunk = line
            # offset of the chunk from the beginning of the original line
            offset = 0
            while chunk != '':
                if ignoring > 0:
                    # find end of comment, but also register any start of new nested comments
                    end_match = end_exp.search(chunk)
                    start_match = start_exp.search(chunk)
                    if (start_match and end_match and start_match.start() < end_match.start()) or \
                       (start_match and not end_match):
                        # nested comment:
                        ignoring += 1
                        chunk = chunk[start_match.end()+1:]
                        offset += start_match.end()+1
                    else:
                        if end_match:
                            chunk = chunk[end_match.end()+1:]
                            offset += end_match.end()+1
                            ignoring -= 1
                        else:
                            chunk = ''

                if in_string:
                    # inside a potentially multi-line string:
                    str_end = chunk.find(string_delimiter)
                    in_string = str_end < 0
                    chunk = chunk[str_end+1:] if not in_string else ''
                    offset += str_end+1  # unused if str_end < 0

                if ignoring == 0 and not in_string:
                    # actual content to match, but only until the next comment start or string:
                    string_match = chunk.find(string_delimiter)
                    string_found = string_match >= 0
                    # turn -1 into len(chunk) for use with "min" belown
                    string_match = len(chunk) if string_match < 0 else string_match

                    ignore_match = start_exp.search(chunk)
                    ignore_match_start = min(string_match,
                                             ignore_match.start() if ignore_match else len(chunk))
                    ignore_match_end = min(string_match,
                                           ignore_match.end() if ignore_match else len(chunk)) + 1

                    match_chunk(line, chunk[:ignore_match_start], offset, line_num, matches)
                    chunk = chunk[ignore_match_end:]
                    offset += ignore_match_end

                    if ignore_match and ignore_match_start < string_match:
                        ignoring += 1
                    elif string_found and string_match <= ignore_match_start:
                        in_string = True

    for m in matches:
        m['file_name'] = file_name

    return matches


def main():
    """Command line parsing and linter invocation."""
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('--json',
                        help="produce json output for github", action='store_true')
    parser.add_argument('files',
                        help="select these tests to run (defaults to all tests)", nargs="+")

    args = parser.parse_args()

    matches = []
    for file in args.files:
        matches += lint_file(file)

    if args.json:
        print(matches_to_json(matches))
    else:
        print_matches(matches)

    sys.exit(matches != [])


if __name__ == '__main__':
    main()
