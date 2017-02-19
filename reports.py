#!/usr/bin/env python3
# Copyright (c) 2017 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import sys
import argparse
import json

from framework.report import Report
from repo_info import REPO_INFO
from clang_static_analysis import ReportCmd as ClangStaticAnalysisReport
from basic_style import ReportCmd as BasicStyleReport
from copyright_header import ReportCmd as CopyrightHeaderReport
from clang_format import ReportCmd as ClangFormatReport
from framework.args import add_jobs_arg
from framework.args import add_json_arg
from framework.clang import scan_build_binaries_from_options
from framework.clang import clang_format_from_options
from framework.clang import add_clang_args
from framework.git import add_git_repository_arg

class Reports(object):
    """
    Represents an aggregation of underlying run that can be run in one step.
    """
    def __init__(self, options):
        o = options
        self.json = o.json
        self.reports = [
            {'human_title': 'Copyright Header Report',
             'json_label':  'copyright_header',
             'report':      CopyrightHeaderReport(o.repository, o.jobs,
                                                  o.target_fnmatches)},
            {'human_title': 'Basic Style Report',
             'json_label':  'basic_style',
             'report':      BasicStyleReport(o.repository, o.jobs,
                                             o.target_fnmatches)},
            {'human_title': 'Clang Format Style Report',
             'json_label':  'clang_format',
             'report':      ClangFormatReport(o.repository, o.jobs,
                                              o.target_fnmatches,
                                              o.clang_format)},
            {'human_title': 'Clang Static Analysis Report',
             'json_label':  'clang_static_analysis',
             'report':      ClangStaticAnalysisReport(o.repository, o.jobs,
                                                      o.scan_build,
                                                      o.report_path,
                                                      o.scan_view)},
        ]

    def run(self):
        o = Report()
        for r in self.reports:
            if not options.json:
                o.add("Computing %s...\n" % r['human_title'])
            r['results'] = r['report'].analysis()
            r['output'] = (r['results'] if options.json else
                           r['report'].human_print(r['results']))
            exit = r['report'].shell_exit(r['results'])
            if exit != 0:
                sys.exit(exit)
            if not options.json:
                o.add("Done.\n")
                o.add("%s:\n" % r['human_title'])
                o.add("%s\n" % r['output'])
        if options.json:
            o.add(json.dumps({r['json_label']: r['output'] for r in
                              self.reports}))
        return str(o)


if __name__ == "__main__":
    description = ("Wrapper to invoke a collection of scripts that produce "
                   "data from analyzing a repository.")
    parser = argparse.ArgumentParser(description=description)
    add_jobs_arg(parser)
    add_json_arg(parser)
    add_clang_args(parser)
    add_git_repository_arg(parser)
    options = parser.parse_args()
    options.clang_format = (
        clang_format_from_options(options, REPO_INFO['clang_format_style']))
    options.scan_build, options.scan_view = (
        scan_build_binaries_from_options(options))
    reports = Reports(options)
    output = reports.run()
    print(output)
