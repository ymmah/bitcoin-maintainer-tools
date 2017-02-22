#!/usr/bin/env python3
# Copyright (c) 2017 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import argparse
import subprocess
import sys
import os
import json

from framework.cmd.repository import RepositoryCmd
from framework.git.repository import add_git_repository_arg

###############################################################################
# cmd test functions
###############################################################################

def test_report(cmd):
    output = subprocess.check_output(cmd.split(' ')).decode('utf-8')
    print(output)


def test_report_json(cmd):
    output = subprocess.check_output(cmd.split(' ')).decode('utf-8')
    output_loaded = json.loads(output)
    print(json.dumps(output_loaded))


def test_check(cmd):
    try:
        exit = subprocess.call(cmd.split(' '))
    except subprocess.CalledProcessError as e:
        print("exit: %d" % e.returncode)
        assert e.returncode == 1
        output = e.output.decode('utf-8')
        assert "Traceback" not in output


def test_check_json(cmd):
    try:
        exit = subprocess.call(cmd.split(' '))
    except subprocess.CalledProcessError as e:
        print("exit: %d" % e.returncode)
        assert e.returncode == cmd
        output = e.output.decode('utf-8')
        assert "Traceback" not in output
        output_loaded = json.loads(output)
        print(json.dumps(output_loaded))


###############################################################################
# test single commands
###############################################################################

test_single_cmds = [
    {'cmd':  'bin/basic_style.py report -j8 %s',
     'test': test_report},
    {'cmd':  'bin/copyright_header.py report -j8 %s',
     'test': test_report},
    {'cmd':  'bin/clang_format.py report -j8 %s',
     'test': test_report},
    {'cmd':  'bin/clang_static_analysis.py report -j8 %s',
     'test': test_report},
    {'cmd':  'bin/reports.py -j8 %s',
     'test': test_report},
    {'cmd':  'bin/basic_style.py report --json %s',
     'test': test_report_json},
    {'cmd':  'bin/copyright_header.py report --json %s',
     'test': test_report_json},
    {'cmd':  'bin/clang_format.py report --json %s',
     'test': test_report_json},
    {'cmd':  'bin/clang_static_analysis.py report --json %s',
     'test': test_report_json},
    {'cmd':  'bin/reports.py --json %s',
     'test': test_report_json},
    {'cmd':  'bin/basic_style.py check -j8 %s',
     'test': test_check},
    {'cmd':  'bin/copyright_header.py check -j8 %s',
     'test': test_check},
    {'cmd':  'bin/clang_format.py check --force -j8 %s',
     'test': test_check},
    {'cmd':  'bin/clang_static_analysis.py check -j8 %s',
     'test': test_check},
    {'cmd':  'bin/checks.py -j8 %s',
     'test': test_check},
    {'cmd':  'bin/basic_style.py check --json %s',
     'test': test_check_json},
    {'cmd':  'bin/copyright_header.py check --json %s',
     'test': test_check_json},
    {'cmd':  'bin/clang_format.py check --force --json %s',
     'test': test_check_json},
    {'cmd':  'bin/clang_static_analysis.py check --json %s',
     'test': test_check_json},
    {'cmd':  'bin/checks.py --force --json %s',
     'test': test_check_json},
]

###############################################################################
# test
###############################################################################

class RegressionCmd(RepositoryCmd):
    def __init__(self, options):
        super().__init__(options)
        self.title = "Regression test command"

    def _exec(self):
        for cmd in test_single_cmds:
            if not self.silent:
                cmd_string = cmd['cmd'] % self.repository
                print("testing '%s'" % cmd_string)
            cmd['test'](cmd_string)


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
    add_git_repository_arg(parser)
    options = parser.parse_args()
    RegressionCmd(options).run()
