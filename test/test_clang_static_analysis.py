#!/usr/bin/env python3
# Copyright (c) 2017 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import os
import argparse

from framework.argparse.option import add_tmp_directory_option
from framework.bitcoin.setup import setup_build_ready_bitcoin_repo
from framework.test.exec import exec_cmd_no_error
from framework.test.exec import exec_cmd_error
from framework.test.exec import exec_cmd_json_no_error
from framework.test.exec import exec_cmd_json_error
from framework.test.exec import exec_modify_fixes_check
from framework.test.exec import exec_modify_doesnt_fix_check
from framework.test.clang import setup_test_bin_dir
from framework.test.cmd import ScriptTestCmd

###############################################################################
# test
###############################################################################


def test_help(repository):
    cmd = 'bin/clang_static_analysis.py -h'
    print(exec_cmd_no_error(cmd))


def test_report(repository, test_bin_dir):
    #cmd = 'bin/clang_static_analysis.py report -h'
    #print(exec_cmd_no_error(cmd))
    #cmd = 'bin/clang_static_analysis.py report %s' % repository
    #print(exec_cmd_no_error(cmd))
    #cmd = ("bin/clang_static_analysis.py report -j8 %s/src/init.cpp "
    #       "%s/src/qt/" % (repository, repository))
    #print(exec_cmd_error(cmd))
    cmd = 'bin/clang_static_analysis.py report -j8 --json %s' % repository
    print(exec_cmd_json_no_error(cmd))
    cmd = 'bin/clang_static_analysis.py report -j8 -b %s %s' % (test_bin_dir,
                                                                repository)
    print(exec_cmd_no_error(cmd))
    # no speecified targets runs it on the path/repository it is invoked from:
    cmd = 'bin/clang_static_analysis.py report'
    original = os.getcwd()
    os.chdir(str(repository))
    print(exec_cmd_no_error(cmd))
    os.chdir(original)


def test_check(repository, test_bin_dir):
    cmd = 'bin/clang_static_analysis.py check -h'
    print(exec_cmd_no_error(cmd))
    cmd = 'bin/clang_static_analysis.py check -j8 %s' % repository
    e, out = exec_cmd_error(cmd)
    print("%d\n%s" % (e, out))
    cmd = 'bin/clang_static_analysis.py check --json %s' % repository
    e, out = exec_cmd_json_error(cmd)
    cmd = 'bin/clang_static_analysis.py check -j8 -b %s %s' % (test_bin_dir,
                                                               repository)
    e, out = exec_cmd_error(cmd)
    print("%d\n%s" % (e, out))


def tests(settings):
    test_help(settings.repository)
    test_report(settings.repository, settings.test_bin_dir)
    test_check(settings.repository, settings.test_bin_dir)


class TestClangStaticAnalysisCmd(ScriptTestCmd):
    def __init__(self, settings):
        super().__init__(settings)
        self.title = __file__

    def _exec(self):
        return super()._exec(tests)

###############################################################################
# UI
###############################################################################

if __name__ == "__main__":
    description = ("Tests clang_static_analysis.py through its range of "
                   "subcommands and options.")
    parser = argparse.ArgumentParser(description=description)
    add_tmp_directory_option(parser)
    settings = parser.parse_args()
    settings.repository = (
        setup_build_ready_bitcoin_repo(settings.tmp_directory,
                                       branch="v0.13.2"))
    settings.test_bin_dir = setup_test_bin_dir(settings.tmp_directory)
    TestClangStaticAnalysisCmd(settings).run()
