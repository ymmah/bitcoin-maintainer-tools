#!/usr/bin/env python3
# Copyright (c) 2017 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import sys
import os
import time
import argparse
import json

from framework.report import Report
from framework.scan_build import ScanBuildResultDirectory
from framework.args import add_jobs_arg
from framework.args import add_json_arg
from framework.clang import add_clang_static_analysis_args
from framework.clang import scan_build_binaries_from_options
from framework.git import add_git_repository_arg
from framework.build_step import MakeClean
from framework.build_step import ScanBuild

###############################################################################
# cmd base class
###############################################################################

class ClangStaticAnalysisCmd(object):
    """
    Common base class for the commands in this script.
    """
    def __init__(self, repository, jobs, json, scan_build,
                 scan_build_report_path, scan_view):
        self.report = Report()
        self.repository = str(repository)
        self.jobs = jobs
        self.json = json
        self.scan_build = scan_build
        self.scan_build_result = ScanBuildResultDirectory(
            scan_build_report_path)
        self.scan_view = scan_view
        self.make_clean_output_file = os.path.join(scan_build_report_path,
                                                   'make_clean.log')
        self.make_clean_step = MakeClean(self.repository,
                                         self.make_clean_output_file)
        self.scan_build_output_file = os.path.join(scan_build_report_path,
                                                   'scan_build.log')
        self.scan_build_step = ScanBuild(
            self.scan_build, scan_build_report_path, self.repository,
            self.scan_build_output_file, self.jobs)

    def _analysis(self):
        start_time = time.time()
        r = self.report
        r.add("Running command:     %s" % str(self.make_clean_step))
        r.add("stderr/stdout to:    %s" % self.make_clean_output_file)
        if not self.json:
            r.flush()
        self.make_clean_step.run()
        r.add("Running command:     %s" % str(self.scan_build_step))
        r.add("stderr/stdout to:    %s" % self.scan_build_output_file)
        r.add("This might take a few minutes...")
        if not self.json:
            r.flush()
        self.scan_build_step.run()
        r.add("Done.")
        if not self.json:
            r.flush()
        elapsed_time = time.time() - start_time
        directory, issues = self.scan_build_result.most_recent_results()
        self.results = {'elapsed_time':      time.time() - start_time,
                        'results_directory': directory,
                        'issues':            issues}

    def _human_print(self):
        r = self.report
        a = self.results
        r.separator()
        r.add("Took %.2f seconds to analyze with scan-build\n" %
              a['elapsed_time'])
        r.add("Found %d issues:\n" % len(a['issues']))
        r.separator()

    def _json_print(self):
        print(json.dumps(self.results))

    def exec_report(self):
        self._analysis()
        self._json_print() if self.json else self._human_print()
        self._shell_exit()


###############################################################################
# report cmd
###############################################################################

class ReportCmd(ClangStaticAnalysisCmd):
    """
    'report' subcommand class.
    """
    def __init__(self, repository, jobs, json, scan_build,
                 scan_build_report_path, scan_view):
        super().__init__(repository, jobs, json, scan_build,
                         scan_build_report_path, scan_view)

    def _human_print(self):
        r = self.report
        a = self.results
        super()._human_print()
        issue_no = 0
        for issue in a['issues']:
            r.add("%d: %s:%d:%d - %s\n" % (issue_no, issue['file'],
                                           issue['line'], issue['col'],
                                           issue['description']))
            issue_no = issue_no + 1
        if len(a['issues']) > 0:
            r.separator()
            r.add("Full details can be seen in a browser by running:\n")
            r.add("    $ %s %s\n" % (self.scan_view, a['results_directory']))
            r.separator()
        r.flush()

    def _shell_exit(self):
        sys.exit(0)


def add_report_cmd(subparsers):
    def exec_report_cmd(options):
        ReportCmd(options.repository, options.jobs, options.json,
                  options.scan_build['path'], options.report_path,
                  options.scan_view['path']).exec_report()

    report_help = ("Runs clang static analysis and produces a summary report "
                   "of the findings.")
    parser = subparsers.add_parser('report', help=report_help)
    parser.set_defaults(func=exec_report_cmd)
    add_jobs_arg(parser)
    add_json_arg(parser)
    add_clang_static_analysis_args(parser)
    add_git_repository_arg(parser)


###############################################################################
# check cmd
###############################################################################

class CheckCmd(ClangStaticAnalysisCmd):
    """
    'check' subcommand class.
    """
    def __init__(self, repository, jobs, json, scan_build,
                 scan_build_report_path, scan_view):
        super().__init__(repository, jobs, json, scan_build,
                         scan_build_report_path, scan_view)

    def _human_print(self):
        r = self.report
        a = self.results
        super()._human_print()
        for issue in a['issues']:
            r.add("An issue has been found in ")
            r.add_red("%s:%d:%d\n" % (issue['file'], issue['line'],
                                      issue['col']))
            r.add("Type:         %s\n" % issue['type'])
            r.add("Description:  %s\n\n" % issue['description'])
            event_no = 0
            for event in issue['events']:
                r.add("%d: " % event_no)
                r.add("%s:%d:%d - " % (event['file'], event['line'],
                                       event['col']))
                r.add("%s\n" % event['message'])
                event_no = event_no + 1
            r.separator()
        if len(a['issues']) == 0:
            r.add_green("No static analysis issues found!\n")
            r.separator()
        else:
            r.add_red("Full details can be seen in a browser by running:\n")
            r.add("    $ %s %s\n" % (self.scan_view, a['results_directory']))
            r.separator()
        r.flush()

    def _shell_exit(self):
        return (sys.exit(0) if len(self.results['issues']) == 0 else
                sys.exit("*** static analysis issues found."))

def add_check_cmd(subparsers):
    def exec_check_cmd(options):
        CheckCmd(options.repository, options.jobs, options.json,
                 options.scan_build['path'], options.report_path,
                 options.scan_view['path']).exec_report()

    check_help = ("Runs clang static analysis and output details for each "
                  "discovered issue. Returns a non-zero shell status if any "
                  "issues are found.")
    parser = subparsers.add_parser('check', help=check_help)
    parser.set_defaults(func=exec_check_cmd)
    add_jobs_arg(parser)
    add_json_arg(parser)
    add_clang_static_analysis_args(parser)
    add_git_repository_arg(parser)


###############################################################################
# UI
###############################################################################

if __name__ == "__main__":
    description = ("A utility for running clang static analysis on a codebase "
                   "in a consistent way.")
    parser = argparse.ArgumentParser(description=description)
    subparsers = parser.add_subparsers()
    add_report_cmd(subparsers)
    add_check_cmd(subparsers)
    options = parser.parse_args()
    if not hasattr(options, "func"):
        parser.print_help()
        sys.exit("*** missing argument")
    options.scan_build, options.scan_view = (
        scan_build_binaries_from_options(options))
    options.func(options)
