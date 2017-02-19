#!/usr/bin/env python3
# Copyright (c) 2017 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import subprocess
import sys
import os
import json

h = """
Invoke as $ ./regression.py <repo>

The expectations of results from command make assumptions about the state of
the bitcoin repository for whether some commands are successful or not.

Tested with release x.x.x checked out with a normal ./configure
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
    {'cmd':  './basic_style.py report -j8 %s' % sys.argv[1],
     'test': test_report},
    {'cmd':  './copyright_header.py report -j8 %s' % sys.argv[1],
     'test': test_report},
    {'cmd':  './clang_format.py report -j8 %s' % sys.argv[1],
     'test': test_report},
    {'cmd':  './clang_static_analysis.py report -j8 %s' % sys.argv[1],
     'test': test_report},
    {'cmd':  './reports.py -j8 %s' % sys.argv[1],
     'test': test_report},
    {'cmd': './basic_style.py report --json %s' % sys.argv[1],
     'test': test_report_json},
    {'cmd': './copyright_header.py report --json %s' % sys.argv[1],
     'test': test_report_json},
    {'cmd': './clang_format.py report --json %s' % sys.argv[1],
     'test': test_report_json},
    {'cmd': './clang_static_analysis.py report --json %s' % sys.argv[1],
     'test': test_report_json},
    {'cmd':  './reports.py --json %s' % sys.argv[1],
     'test': test_report_json},
    {'cmd': './basic_style.py check -j8 %s' % sys.argv[1],
     'test': test_check},
    {'cmd': './copyright_header.py check -j8 %s' % sys.argv[1],
     'test': test_check},
    {'cmd': './clang_format.py check --force -j8 %s' % sys.argv[1],
     'test': test_check},
    {'cmd': './clang_static_analysis.py check -j8 %s' % sys.argv[1],
     'test': test_check},
    {'cmd':  './checks.py -j8 %s' % sys.argv[1],
     'test': test_check},
    {'cmd': './basic_style.py check --json %s' % sys.argv[1],
     'test': test_check_json},
    {'cmd': './copyright_header.py check --json %s' % sys.argv[1],
     'test': test_check_json},
    {'cmd': './clang_format.py check --force --json %s' % sys.argv[1],
     'test': test_check_json},
    {'cmd': './clang_static_analysis.py check --json %s' % sys.argv[1],
     'test': test_check_json},
    {'cmd':  './checks.py --force --json %s' % sys.argv[1],
     'test': test_check_json},
]


###############################################################################
# run tests
###############################################################################

for cmd in test_cmds:
    print("testing '%s'" % cmd['cmd'])
    cmd['test'](cmd['cmd'])
