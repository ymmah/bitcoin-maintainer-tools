#!/usr/bin/env python3
# Copyright (c) 2017 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import sys
import os
import time
import argparse
import json

from framework.utl.report import Report
from framework.scan_build import ScanBuildResultDirectory
from framework.argparse.args import add_jobs_arg
from framework.argparse.args import add_json_arg
from framework.clang import add_clang_static_analysis_args
from framework.clang import scan_build_binaries_from_options
from framework.git import add_git_repository_arg
from framework.build_step import MakeClean
from framework.build_step import ScanBuild
from framework.cmd.repository import RepositoryCmd

###############################################################################
# cmd base class
###############################################################################

class ClangStaticAnalysisCmd(RepositoryCmd):
    """
    Superclass for a command that runs clang static analysis.
    """
    def __init__(self, options):
        assert hasattr(options, 'scan_build')
        assert hasattr(options, 'report_path')
        assert hasattr(options, 'scan_view')
        super().__init__(options)
        self.jobs = options.jobs
        self.json = options.json
        self.scan_build = options.scan_build['path']
        self.scan_build_report_path = options.report_path
        self.scan_build_result = ScanBuildResultDirectory(
            self.scan_build_report_path)
        self.scan_view = options.scan_view['path']
        self.make_clean_output_file = (
            os.path.join(self.scan_build_report_path, 'make_clean.log'))
        self.make_clean_step = MakeClean(str(self.repository),
                                         self.make_clean_output_file)
        self.scan_build_output_file = (
            os.path.join(self.scan_build_report_path, 'scan_build.log'))
        self.scan_build_step = ScanBuild(
            self.scan_build, self.scan_build_report_path,
            str(self.repository), self.scan_build_output_file, self.jobs)

    def _analysis(self):
        start_time = time.time()
        r = Report()
        r.add("Running command:     %s\n" % str(self.make_clean_step))
        r.add("stderr/stdout to:    %s\n" % self.make_clean_output_file)
        if not self.json:
            r.flush()
        self.make_clean_step.run()
        r.add("Running command:     %s\n" % str(self.scan_build_step))
        r.add("stderr/stdout to:    %s\n" % self.scan_build_output_file)
        r.add("This might take a few minutes...")
        if not self.json:
            r.flush()
        self.scan_build_step.run()
        r.add("Done.\n")
        if not self.json:
            r.flush()
        elapsed_time = time.time() - start_time
        directory, issues = self.scan_build_result.most_recent_results()
        return {'elapsed_time':      time.time() - start_time,
                'results_directory': directory,
                'issues':            issues}

    def _output(self, results):
        if self.json:
            return super()._output(results)
        r = Report()
        a = results
        r.separator()
        r.add("Took %.2f seconds to analyze with scan-build\n" %
              a['elapsed_time'])
        r.add("Found %d issues:\n" % len(a['issues']))
        r.separator()
        return str(r)

    def _shell_exit(self, results):
        return 0


###############################################################################
# report cmd
###############################################################################

class ReportCmd(ClangStaticAnalysisCmd):
    """
    'report' subcommand class.
    """
    def __init__(self, options):
        super().__init__(options)
        self.title = "Clang Static Analysis Report"

    def _output(self, results):
        if self.json:
            return super()._output(results)
        r = Report()
        r.add(super()._output(results))
        a = results
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
        return str(r)


def add_report_cmd(subparsers):
    def report_cmd(options):
        return ReportCmd(options)

    report_help = ("Runs clang static analysis and produces a summary report "
                   "of the findings.")
    parser = subparsers.add_parser('report', help=report_help)
    parser.set_defaults(get_cmd=report_cmd)
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
    def __init__(self, repository, jobs, scan_build, scan_build_report_path,
                 scan_view):
        super().__init__(repository, jobs, scan_build, scan_build_report_path,
                         scan_view)

    def human_print(self, results):
        r = Report()
        r.add(super().human_print(results))
        a = results
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
        return str(r)

    def shell_exit(self, results):
        return (0 if len(results['issues']) == 0 else
                "*** static analysis issues found.")

def add_check_cmd(subparsers):
    def check_cmd(options):
        return CheckCmd(options.repository, options.jobs, options.scan_build,
                        options.report_path, options.scan_view)

    check_help = ("Runs clang static analysis and output details for each "
                  "discovered issue. Returns a non-zero shell status if any "
                  "issues are found.")
    parser = subparsers.add_parser('check', help=check_help)
    parser.set_defaults(get_cmd=check_cmd)
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
    if not hasattr(options, "get_cmd"):
        parser.print_help()
        sys.exit("*** missing argument")
    options.scan_build, options.scan_view = (
        scan_build_binaries_from_options(options))
    cmd = options.get_cmd(options)
    results = cmd.analysis()
    print(json.dumps(results) if options.json else cmd.human_print(results),
          end='')
    sys.exit(cmd.shell_exit(results))
