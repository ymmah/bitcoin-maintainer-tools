#!/usr/bin/env python3
# Copyright (c) 2017 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import sys
import time
import json
import subprocess
import argparse

from framework.argparse.option import add_tmp_directory_option
from framework.bitcoin.setup import setup_bitcoin_repo
from framework.print.buffer import PrintBuffer
from framework.cmd.repository import RepositoryCmd
from framework.test.cmd import test_cmd_no_error
from framework.test.cmd import test_cmd_error
from framework.test.cmd import test_cmd_json_no_error
from framework.test.cmd import test_cmd_json_error
from framework.test.cmd import test_modify_fixes_check
from framework.test.cmd import test_modify_doesnt_fix_check

###############################################################################
# test
###############################################################################


def test_help(repository):
    cmd = 'bin/basic_style.py -h'
    print(test_cmd_no_error(cmd))
    cmd = 'bin/basic_style.py report -h'
    print(test_cmd_no_error(cmd))
    cmd = 'bin/basic_style.py check -h'
    print(test_cmd_no_error(cmd))
    cmd = 'bin/basic_style.py fix -h'
    print(test_cmd_no_error(cmd))


def test_report(repository):
    cmd = 'bin/basic_style.py report %s' % repository
    print(test_cmd_no_error(cmd))
    cmd = 'bin/basic_style.py report -j8 %s' % repository
    print(test_cmd_no_error(cmd))
    cmd = ('bin/basic_style.py report -j8 %s/src/init.cpp %s/src/qt/' %
           (repository, repository))
    print(test_cmd_no_error(cmd))
    cmd = 'bin/basic_style.py report --json %s' % repository
    print(test_cmd_json_no_error(cmd))
    cmd = ('bin/basic_style.py report --json %s/src/init.cpp %s/src/qt/' %
           (repository, repository))
    print(test_cmd_json_no_error(cmd))
    # No specified targets means it runs on its own repo - in this case, the
    # maintainer tools repo.
    cmd = 'bin/basic_style.py report --json'
    print(test_cmd_no_error(cmd))


def test_check(repository):
    cmd = 'bin/basic_style.py check -j3 %s' % repository
    e, out = test_cmd_error(cmd)
    print("%d\n%s" % (e, out))
    cmd = 'bin/basic_style.py check --json %s' % repository
    e, out = test_cmd_json_error(cmd)
    print("%d\n%s" % (e, out))
    cmd = 'bin/basic_style.py check %s/src/init.cpp' % repository
    print(test_cmd_no_error(cmd))


def test_fix(repository):
    check_cmd = "bin/basic_style.py check %s" % repository
    modify_cmd = "bin/basic_style.py fix %s" % repository
    test_modify_fixes_check(repository, check_cmd, modify_cmd)
    repository.reset_hard_head()


class TestBasicStyleCmd(RepositoryCmd):
    def __init__(self, settings):
        super().__init__(settings)
        self.title = "basic_style.py test"

    def _exec(self):
        start_time = time.time()
        test_help(self.repository)
        test_report(self.repository)
        test_check(self.repository)
        test_fix(self.repository)
        return {'elapsed_time': time.time() - start_time}

    def _output(self, results):
        b = PrintBuffer()
        b.separator()
        b.add_green("test_basic_style.py passed!\n")
        b.add("Elapsed time: %.2fs\n" % results['elapsed_time'])
        b.separator()
        return str(b)

###############################################################################
# UI
###############################################################################

if __name__ == "__main__":
    description = ("Tests basic_style.py through its range of subcommands and "
                   "options.")
    parser = argparse.ArgumentParser(description=description)
    add_tmp_directory_option(parser)
    settings = parser.parse_args()
    settings.repository = setup_bitcoin_repo(settings.tmp_directory)
    TestBasicStyleCmd(settings).run()
