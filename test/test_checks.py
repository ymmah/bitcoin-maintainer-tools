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
from framework.test.clang import setup_test_style_file
from framework.test.cmd import ScriptTestCmd

###############################################################################
# test
###############################################################################


def tests(settings):
    cmd = 'bin/checks.py -h'
    print(exec_cmd_no_error(cmd))
    cmd = 'bin/checks.py -j8 --force %s' % settings.repository
    print("%d\n%s" % exec_cmd_error(cmd))
    cmd = 'bin/checks.py --force --json -j8 %s' % settings.repository
    print(exec_cmd_json_error(cmd))
    cmd = ('bin/checks.py --force -b %s -s %s -j8 %s' %
           (settings.test_bin_dir, settings.test_style_file,
            settings.repository))
    print("%d\n%s" % exec_cmd_error(cmd))
    # put the results in a different directory:
    test_tmp_dir = os.path.join(settings.tmp_directory,
                                "another-tmp-directory")
    cmd = 'bin/checks.py --force -j8 -t %s %s' % (test_tmp_dir,
                                                  settings.repository)
    print("%d\n%s" % exec_cmd_error(cmd))
    # no speecified targets runs it on the path/repository it is invoked from:
    cmd = 'bin/checks.py --force'
    original = os.getcwd()
    os.chdir(str(settings.repository))
    print("%d\n%s" % exec_cmd_error(cmd))
    os.chdir(original)


class TestChecksCmd(ScriptTestCmd):
    def __init__(self, settings):
        super().__init__(settings)
        self.title = __file__

    def _exec(self):
        return super()._exec(tests)


###############################################################################
# UI
###############################################################################

if __name__ == "__main__":
    description = ("Tests checks.py through its range of subcommands and"
                   "options.")
    parser = argparse.ArgumentParser(description=description)
    add_tmp_directory_option(parser)
    settings = parser.parse_args()
    settings.repository = (
        setup_build_ready_bitcoin_repo(settings.tmp_directory,
                                       branch="v0.13.2"))
    settings.test_bin_dir = setup_test_bin_dir(settings.tmp_directory)
    settings.test_style_file = setup_test_style_file(settings.tmp_directory)
    TestChecksCmd(settings).run()
