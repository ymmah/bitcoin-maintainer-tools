#!/usr/bin/env python3
# Copyright (c) 2017 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import argparse

from framework.cmd.repository import RepositoryCmds
from clang_static_analysis import CheckCmd as ClangStaticAnalysisCheck
from basic_style import CheckCmd as BasicStyleCheck
from copyright_header import CheckCmd as CopyrightHeaderCheck
from clang_format import CheckCmd as ClangFormatCheck
from framework.argparse.args import add_jobs_arg
from framework.argparse.args import add_json_arg
from framework.clang import add_force_arg
from framework.clang import scan_build_binaries_from_options
from framework.clang import clang_format_from_options
from framework.clang import add_clang_args
from framework.git import add_git_repository_arg


class Checks(RepositoryCmds):
    """
    Invokes several underlying RepositoryCmd check command instances and and
    aggregates the results.
    """
    def __init__(self, options):
        repository_cmds = {
            'copyright_header':      CopyrightHeaderCheck(options),
            'basic_style':           BasicStyleCheck(options),
            'clang_format':          ClangFormatCheck(options),
            'clang_static_analysis': ClangStaticAnalysisCheck(options),
        }
        self.json = options.json
        super().__init__(options, repository_cmds, silent=options.json)

    def _output(self, results):
        if self.json:
            return super()._output(results)
        reports = [(self.repository_cmds[l].title + ":\n" +
                    self.repository_cmds[l]._output(r)) for l, r in
                   sorted(results.items())]
        return '\n'.join(reports)


if __name__ == "__main__":
    description = ("Wrapper to invoke a collection of scripts that check on "
                   "the state of the repository.")
    parser = argparse.ArgumentParser(description=description)
    add_jobs_arg(parser)
    add_json_arg(parser)
    add_force_arg(parser)
    add_clang_args(parser)
    add_git_repository_arg(parser)
    options = parser.parse_args()
    options.clang_format = clang_format_from_options(options)
    options.scan_build, options.scan_view = (
        scan_build_binaries_from_options(options))
    checks = Checks(options)
    output = checks.run()
