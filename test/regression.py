#!/usr/bin/env python3
# Copyright (c) 2017 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import subprocess
import sys
import os
import json

h = """
Performs a basic smoke test of the tools with some variety of options.
This isn't intended to be comprehensive, but it is useful for not breaking
things while developing.

Invoke as:

$ test/regression.py <bitcoin repo>

from the base repo of bitcoin-maintainer-tools

This script makes assumptions about the state of the bitcoin repository for
whether some commands are successful or not, so a failure might be due to
the target repo as opposed to the script.

It should fully pass agianst a target repo of release x.x.x checked out with a
normal ./configure already performed.
"""
# TODO test with well-known release

if not len(sys.argv) == 2:
    sys.exit(h)
if not os.path.isdir(sys.argv[1]):
    sys.exit(h)


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
# report cmd
###############################################################################

test_cmds = [
    {'cmd':  'bin/basic_style.py report -j8 %s' % sys.argv[1],
     'test': test_report},
    {'cmd':  'bin/copyright_header.py report -j8 %s' % sys.argv[1],
     'test': test_report},
    {'cmd':  'bin/clang_format.py report -j8 %s' % sys.argv[1],
     'test': test_report},
    {'cmd':  'bin/clang_static_analysis.py report -j8 %s' % sys.argv[1],
     'test': test_report},
    {'cmd':  'bin/reports.py -j8 %s' % sys.argv[1],
     'test': test_report},
    {'cmd': 'bin/basic_style.py report --json %s' % sys.argv[1],
     'test': test_report_json},
    {'cmd': 'bin/copyright_header.py report --json %s' % sys.argv[1],
     'test': test_report_json},
    {'cmd': 'bin/clang_format.py report --json %s' % sys.argv[1],
     'test': test_report_json},
    {'cmd': 'bin/clang_static_analysis.py report --json %s' % sys.argv[1],
     'test': test_report_json},
    {'cmd':  'bin/reports.py --json %s' % sys.argv[1],
     'test': test_report_json},
    {'cmd': 'bin/basic_style.py check -j8 %s' % sys.argv[1],
     'test': test_check},
    {'cmd': 'bin/copyright_header.py check -j8 %s' % sys.argv[1],
     'test': test_check},
    {'cmd': 'bin/clang_format.py check --force -j8 %s' % sys.argv[1],
     'test': test_check},
    {'cmd': 'bin/clang_static_analysis.py check -j8 %s' % sys.argv[1],
     'test': test_check},
    {'cmd':  'bin/checks.py -j8 %s' % sys.argv[1],
     'test': test_check},
    {'cmd': 'bin/basic_style.py check --json %s' % sys.argv[1],
     'test': test_check_json},
    {'cmd': 'bin/copyright_header.py check --json %s' % sys.argv[1],
     'test': test_check_json},
    {'cmd': 'bin/clang_format.py check --force --json %s' % sys.argv[1],
     'test': test_check_json},
    {'cmd': 'bin/clang_static_analysis.py check --json %s' % sys.argv[1],
     'test': test_check_json},
    {'cmd':  'bin/checks.py --force --json %s' % sys.argv[1],
     'test': test_check_json},
]


###############################################################################
# run tests
###############################################################################

for cmd in test_cmds:
    print("testing '%s'" % cmd['cmd'])
    cmd['test'](cmd['cmd'])
