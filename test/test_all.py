#!/usr/bin/env python3
# Copyright (c) 2017 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import argparse

from framework.argparse.option import add_tmp_directory_option
from framework.bitcoin.setup import setup_build_ready_bitcoin_repo
from framework.cmd.repository import RepositoryCmds
from test_basic_style import TestBasicStyleCmd

class TestAll(RepositoryCmds):
    """
    Invokes several underlying RepositoryCmd check command instances and and
    aggregates the results.
    """
    def __init__(self, settings):
        repository_cmds = {
            'basic_style':           TestBasicStyleCmd(settings),
        }
        super().__init__(settings, repository_cmds)

    def _output(self, results):
        reports = [(self.repository_cmds[l].title + ":\n" +
                    self.repository_cmds[l]._output(r)) for l, r in
                   sorted(results.items())]
        return '\n'.join(reports)


if __name__ == "__main__":
    description = ("Runs all test scripts in serial to make sure they all "
                   "pass. This might take a while to finish.")
    parser = argparse.ArgumentParser(description=description)
    add_tmp_directory_option(parser)
    settings = parser.parse_args()
    settings.repository = (
        setup_build_ready_bitcoin_repo(settings.tmp_directory))
    TestAll(settings).run()
