#!/usr/bin/env python3
# Copyright (c) 2017 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import sys
import argparse
import json


from framework.cmd import RepositoryCmd
from framework.utl.report import Report
from clang_static_analysis import ReportCmd as ClangStaticAnalysisReport
from basic_style import ReportCmd as BasicStyleReport
from copyright_header import ReportCmd as CopyrightHeaderReport
from clang_format import ReportCmd as ClangFormatReport
from framework.argparse.args import add_jobs_arg
from framework.argparse.args import add_json_arg
from framework.clang import scan_build_binaries_from_options
from framework.clang import clang_format_from_options
from framework.clang import add_clang_args
from framework.git import add_git_repository_arg

class Reports(RepositoryCmd):
    """
    A RepositoryCmd that collects options and invokes several underlying
    RepositoryCmds and and aggregates the report that result.
    """
    def __init__(self, options):
        super().__init__(options, silent=options.json)
        self.json = options.json
        self.reports = {
            'copyright_header':      CopyrightHeaderReport(options)},
#            'basic_style':           BasicStyleReport(options)},
#            'clang_format':          ClangFormatReport(options)},
#            'clang_static_analysis': ClangStaticAnalysisReport(options)},
        }

    def _analysis(self):
        results = super()._analysis()
        for l, r in self.reports.items():
            if not self.silent:
                print("Computing %s..." % r.title)
            results[l] = r._analysis()
            if not self.silent:
                print("Done." % r.title)
        return results

    def _output(self, results)
        if self.json:
            return super()._output(results)
        return [self.reports[l]._output(r)
                for l, r in results.items()].join('\n')

    def _shell_exit(self, results):
        exits = [l: r._shell_exit(results[l]) for l, r in
                 self.reports.items()]
        if all(e == 0 for e in exits):
            return 0
        non_zero_ints = [e for e in exit if type(e) is int and not e == 0]
        strings = [e for e in exits if type(e) is str]
        if len(strings) == 0:
            return max(non_zero_ints)
        return strings.join('\n')


if __name__ == "__main__":
    description = ("Wrapper to invoke a collection of scripts that produce "
                   "data from analyzing a repository.")
    parser = argparse.ArgumentParser(description=description)
    add_jobs_arg(parser)
    add_json_arg(parser)
    add_clang_args(parser)
    add_git_repository_arg(parser)
    options = parser.parse_args()
    options.clang_format = clang_format_from_options(options)
    options.scan_build, options.scan_view = (
        scan_build_binaries_from_options(options))

    reports = Reports(options)
    output = reports.run()
