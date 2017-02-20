#!/usr/bin/env python3
# Copyright (c) 2017 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import sys
import argparse
import json

from framework.utl.report import Report
from clang_static_analysis import CheckCmd as ClangStaticAnalysisCheck
from basic_style import CheckCmd as BasicStyleCheck
from copyright_header import CheckCmd as CopyrightHeaderCheck
from clang_format import CheckCmd as ClangFormatCheck
from framework.utl.parser import add_jobs_arg
from framework.utl.parser import add_json_arg
from framework.clang import add_force_arg
from framework.clang import scan_build_binaries_from_options
from framework.clang import clang_format_from_options
from framework.clang import add_clang_args
from framework.git import add_git_repository_arg

class Checks(object):
    """
    Represents an aggregation of underlying checks that can be run in one step.
    """
    def __init__(self, options):
        o = options
        self.json = o.json
        self.checks = [
            {'human_title': 'Copyright Header Check',
             'json_label':  'copyright_header',
             'check':       CopyrightHeaderCheck(o.repository, o.jobs,
                                                 o.target_fnmatches)},
            {'human_title': 'Basic Style Check',
             'json_label':  'basic_style',
             'check':       BasicStyleCheck(o.repository, o.jobs,
                                            o.target_fnmatches)},
            {'human_title': 'Clang Format Style Check',
             'json_label':  'clang_format',
             'check':       ClangFormatCheck(o.repository, o.jobs,
                                             o.target_fnmatches,
                                             o.clang_format, o.force)},
            {'human_title': 'Clang Static Analysis Check',
             'json_label':  'clang_static_analysis',
             'check':       ClangStaticAnalysisCheck(o.repository, o.jobs,
                                                     o.scan_build,
                                                     o.report_path,
                                                     o.scan_view)},
        ]

    def __iter__(self):
        return iter(self.checks)

    def run(self):
        r = Report()
        for c in self.checks:
            if not options.json:
                r.add("Computing %s...\n" % c['human_title'])
            c['results'] = c['check'].analysis()
            c['output'] = (c['results'] if options.json else
                           c['check'].human_print(c['results']))
            c['exit'] = c['check'].shell_exit(c['results'])
            if not options.json:
                r.add("Done.\n")
                r.add("%s:\n" % c['human_title'])
                r.add("%s\n" % c['output'])
        if options.json:
            r.add(json.dumps({c['json_label']: c['output'] for c in
                              self.checks}))
        return str(r)


if __name__ == "__main__":
    description = ("Wrapper to invoke a collection of scripts that produce "
                   "data from analysing a repository.")
    parser = argparse.ArgumentParser(description=description)
    add_jobs_arg(parser)
    add_json_arg(parser)
    add_clang_args(parser)
    add_force_arg(parser)
    add_git_repository_arg(parser)
    options = parser.parse_args()
    options.clang_format = clang_format_from_options(options)
    options.scan_build, options.scan_view = (
        scan_build_binaries_from_options(options))
    checks = Checks(options)
    output = checks.run()
    print(output)
    errors = [c['exit'] for c in checks if c['exit'] != 0]
    if not options.json:
        print('\n'.join(e))
    sys.exit(len(errors) > 1)
