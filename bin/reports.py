#!/usr/bin/env python3
# Copyright (c) 2017 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import argparse

from framework.cmd.repository import RepositoryCmds
from clang_static_analysis import ReportCmd as ClangStaticAnalysisReport
from basic_style import ReportCmd as BasicStyleReport
from copyright_header import ReportCmd as CopyrightHeaderReport
from clang_format import ReportCmd as ClangFormatReport
from framework.argparse.args import add_jobs_arg
from framework.argparse.args import add_json_arg
from framework.clang.args import add_clang_options
from framework.clang.args import finish_clang_settings
from framework.git.parameter import add_git_tracked_targets_parameter


class Reports(RepositoryCmds):
    """
    Invokes several underlying RepositoryCmd report command instances and and
    aggregates them into a single report.
    """
    def __init__(self, options):
        repository_cmds = {
            'copyright_header':      CopyrightHeaderReport(options),
            'basic_style':           BasicStyleReport(options),
            'clang_format':          ClangFormatReport(options),
            'clang_static_analysis': ClangStaticAnalysisReport(options),
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
    description = ("Wrapper to invoke a collection of scripts that produce "
                   "data from analyzing a repository.")
    parser = argparse.ArgumentParser(description=description)
    add_jobs_arg(parser)
    add_json_arg(parser)
    add_clang_options(parser, report_path=True, style_file=True)
    add_git_tracked_targets_parameter(parser)
    options = parser.parse_args()
    finish_clang_settings(options)
    reports = Reports(options)
    output = reports.run()
