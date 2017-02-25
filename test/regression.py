#!/usr/bin/env python3
# Copyright (c) 2017 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import argparse
import subprocess
import sys
import os
import json
import time

from framework.print.buffer import PrintBuffer
from framework.cmd.repository import RepositoryCmd
from framework.git.parameter import add_git_repository_parameter

###############################################################################
# test single commands with a single repo as a target
###############################################################################

def test_single_report(cmd):
    output = subprocess.check_output(cmd.split(' ')).decode('utf-8')
    print(output)


def test_single_report_json(cmd):
    output = subprocess.check_output(cmd.split(' ')).decode('utf-8')
    output_loaded = json.loads(output)
    print(json.dumps(output_loaded))


def test_single_check_fails(cmd):
    try:
        subprocess.call(cmd.split(' '))
    except subprocess.CalledProcessError as e:
        print("exit: %d" % e.returncode)
        assert e.returncode == 1
        output = e.output.decode('utf-8')
        assert "Traceback" not in output


def test_single_check_fails_json(cmd):
    try:
        subprocess.call(cmd.split(' '))
    except subprocess.CalledProcessError as e:
        print("exit: %d" % e.returncode)
        assert e.returncode == cmd
        output = e.output.decode('utf-8')
        assert "Traceback" not in output
        output_loaded = json.loads(output)
        print(json.dumps(output_loaded))


def test_single_check_passes(cmd):
    output = subprocess.check_output(cmd.split(' ')).decode('utf-8')
    print(output)


def test_single_check_passes_json(cmd):
    output = subprocess.check_output(cmd.split(' ')).decode('utf-8')
    output_loaded = json.loads(output)
    print(json.dumps(output_loaded))


test_single_cmds = [
    # test with and without '--json' and with different '--jobs' values
    {'cmd':  'bin/basic_style.py report --json %s',
     'test': test_single_report_json},
    {'cmd':  'bin/basic_style.py report -j8 %s',
     'test': test_single_report},
    {'cmd':  'bin/basic_style.py check -j8 %s',
     'test': test_single_check_fails},
    {'cmd':  'bin/basic_style.py check --json %s',
     'test': test_single_check_fails_json},
    {'cmd':  'bin/basic_style.py check %s/src/init.cpp',
     'test': test_single_check_passes},
    {'cmd':  'bin/basic_style.py check --json %s/src/init.cpp',
     'test': test_single_check_passes_json},

    {'cmd':  'bin/copyright_header.py report -j8 %s',
     'test': test_single_report},
    {'cmd':  'bin/copyright_header.py report --json %s',
     'test': test_single_report_json},
    {'cmd':  'bin/copyright_header.py check -j8 %s',
     'test': test_single_check_fails},
    {'cmd':  'bin/copyright_header.py check --json %s',
     'test': test_single_check_fails_json},

    {'cmd':  'bin/copyright_header.py check -j8 %s/src/init.cpp',
     'test': test_single_check_passes},
    {'cmd':  'bin/copyright_header.py check --json %s/src/init.cpp',
     'test': test_single_check_passes_json},

    {'cmd':  'bin/clang_format.py report --jobs 8 %s',
     'test': test_single_report},
    {'cmd':  'bin/clang_format.py report --json %s',
     'test': test_single_report_json},
    {'cmd':  'bin/clang_format.py check --force -j8 %s',
     'test': test_single_check_fails},
    {'cmd':  'bin/clang_format.py check --force --json %s',
     'test': test_single_check_fails_json},

    {'cmd':  'bin/clang_format.py check --force -j8 %s/src/bench/bench_bitcoin.cpp',
     'test': test_single_check_passes},
    {'cmd':  'bin/clang_format.py check --force --json %s/src/bench/bench_bitcoin.cpp',
     'test': test_single_check_passes_json},

    {'cmd':  'bin/clang_static_analysis.py report -j8 %s',
     'test': test_single_report},
    {'cmd':  'bin/clang_static_analysis.py report --json %s',
     'test': test_single_report_json},
    {'cmd':  'bin/clang_static_analysis.py check -j8 %s',
     'test': test_single_check_fails},
    {'cmd':  'bin/clang_static_analysis.py check --json %s',
     'test': test_single_check_fails_json},

    {'cmd':  'bin/reports.py --json %s',
     'test': test_single_report_json},
    {'cmd':  'bin/reports.py -j8 %s',
     'test': test_single_report},
    {'cmd':  'bin/checks.py --force --json %s',
     'test': test_single_check_fails_json},
    {'cmd':  'bin/checks.py -j8 %s',
     'test': test_single_check_fails},
]


def test_single(repo, silent):
    for cmd in test_single_cmds:
        cmd_string = cmd['cmd'] % repo
        if not silent:
            print("testing '%s'" % cmd_string)
        cmd['test'](cmd_string)


###############################################################################
# test commands that modify the repo
###############################################################################

def test_modify_fixes_check(repo, check_cmd, modify_cmd):
    test_single_check_fails(check_cmd)
    _ = subprocess.check_output(modify_cmd.split(' ')).decode('utf-8')
    repo.assert_dirty()
    test_single_check_passes(check_cmd)

def test_modify_doesnt_fix_check(repo, check_cmd, modify_cmd):
    test_single_check_fails(check_cmd)
    _ = subprocess.check_output(modify_cmd.split(' ')).decode('utf-8')
    repo.assert_dirty()
    test_single_check_fails(check_cmd)


test_modify_cmds = [
    {'check_cmd':  'bin/basic_style.py check %s',
     'modify_cmd': 'bin/basic_style.py fix %s',
     'test':       test_modify_fixes_check},
    {'check_cmd':  'bin/copyright_header.py check %s',
     'modify_cmd': 'bin/copyright_header.py insert %s',
     'test':       test_modify_doesnt_fix_check},
    # copyright_header.py update skips bad headers and the dates aren't part
    # of the validation, so it doesn't fix anything.
    {'check_cmd':  'bin/copyright_header.py check %s',
     'modify_cmd': 'bin/copyright_header.py update %s',
     'test':       test_modify_doesnt_fix_check},
    # clang-format needs multiple applications to fix src/validation.cpp
    {'check_cmd':  'bin/clang_format.py check --force %s',
     'modify_cmd': 'bin/clang_format.py format --force %s',
     'test':       test_modify_doesnt_fix_check},

    {'check_cmd':  'bin/clang_format.py check --force %s/src/init.cpp',
     'modify_cmd': 'bin/clang_format.py format --force %s/src/init.cpp',
     'test':       test_modify_fixes_check},
]

def test_modify(repo, silent):
    for cmd in test_modify_cmds:
        repo.assert_not_dirty()
        check_cmd_string = cmd['check_cmd'] % repo
        modify_cmd_string = cmd['modify_cmd'] % repo
        if not silent:
            print("testing '%s' and then '%s'" % (check_cmd_string,
                                                  modify_cmd_string))
        cmd['test'](repo, check_cmd_string, modify_cmd_string)
        repo.reset_hard_head()


###############################################################################
# test
###############################################################################

class RegressionCmd(RepositoryCmd):
    def __init__(self, options):
        super().__init__(options)
        self.title = "Regression test command"

    def _exec(self):
        start_time = time.time()
        test_single(self.repository, self.silent)
        test_modify(self.repository, self.silent)
        return {'elapsed_time': time.time() - start_time}

    def _output(self, results):
        b = PrintBuffer()
        b.separator()
        b.add_green("Regression tests passed!\n")
        b.add("Elapsed time: %.2fs\n" % results['elapsed_time'])
        b.separator()
        return str(b)


###############################################################################
# UI
###############################################################################

description = """
Performs a basic smoke test of the tools with some variety of options.
This isn't intended to be comprehensive, but it is useful for not breaking
things while developing.

This script has hard-coded assumptions about the state of the bitcoin repository
for whether some commands are successful or not, so a failure might be due to
the target repo as opposed to the script.

It should fully pass agianst a target repo of release x.x.x checked out with a
normal ./configure already performed.
"""
# TODO test with well-known release

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=description)
    add_git_repository_parameter(parser)
    options = parser.parse_args()
    RegressionCmd(options).run()
