#!/usr/bin/env python3
# Copyright (c) 2017 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import sys
import json

class RepositoryCmd(object):
    """
    Superclass for a command or subcommand that is targeted at a git repository.
    'silent=True' instructs to only print what is produced by the _output()
    function.
    """
    def __init__(self, options, silent=False):
        assert hasattr(options, 'repository')
        self.options = options
        self.repository = options.repository
        self.silent = silent
        self.title = "RepositoryCmd superclass"

    def _analysis(self):
        return {}

    def _output(self, results):
        return json.dumps(results)

    def _shell_exit(self, results):
        return 0

    def _print(self, output, exit):
        print(output)
        if self.silent and type(exit) is str:
            sys.exit(1)
        sys.exit(exit)

    def run(self):
        results = self._analysis()
        self._print(self._output(results), self._shell_exit(results))
