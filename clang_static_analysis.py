#!/usr/bin/env python3
# Copyright (c) 2017 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import sys
import os
import subprocess
import time
import argparse

from framework.scan_build import ScanBuildResultDirectory
from framework.args import add_jobs_arg
from framework.args import add_json_arg
from framework.clang import add_clang_static_analysis_args
from framework.clang import scan_build_binaries_from_options
from framework.git import add_git_repository_arg

###############################################################################
# do analysis
###############################################################################


def call_cmd(cmd, outfile):
    file = open(os.path.abspath(outfile), 'w')
    if subprocess.call(cmd.split(' '), stdout=file, stderr=file) != 0:
        sys.exit("*** '%s' returned a non-zero status" % cmd)
    file.close()

def run_scan_build(opts):
    print("Running command:     %s" % opts.make_clean_cmd)
    call_cmd(opts.make_clean_cmd, opts.make_clean_log)
    print("Running command:     %s" % opts.scan_build_cmd)
    print("stderr/stdout to:    %s" % opts.scan_build_log)
    print("This might take a few minutes...")
    call_cmd(opts.scan_build_cmd, opts.scan_build_log)
    print("Done.")


def do_analysis(opts):
    run_scan_build(opts)
    report_path = ScanBuildResultDirectory(opts.report_path)
    return report_path.most_recent_results()


###############################################################################
# issue reporting
###############################################################################


def report_issues_compact(issues):
    issue_no = 0
    for issue in issues:
        R.add("%d: %s:%d:%d - %s\n" % (issue_no, issue['file'], issue['line'],
                                       issue['col'], issue['description']))
        issue_no = issue_no + 1


def report_issue(issue):
    R.add("An issue has been found in ")
    R.add_red("%s:%d:%d\n" % (issue['file'], issue['line'], issue['col']))
    R.add("Type:         %s\n" % issue['type'])
    R.add("Description:  %s\n\n" % issue['description'])
    event_no = 0
    for event in issue['events']:
        R.add("%d: " % event_no)
        R.add("%s:%d:%d - " % (event['file'], event['line'], event['col']))
        R.add("%s\n" % event['message'])
        event_no = event_no + 1


def report_issues(issues):
    for issue in issues:
        report_issue(issue)
        R.separator()


###############################################################################
# 'report' subcommand execution
###############################################################################


def report_output(opts, result_subdir, issues, elapsed_time):
    R.separator()
    R.add("Took %.2f seconds to analyze with scan-build\n" % elapsed_time)
    R.add("Found %d issues:\n" % len(issues))
    R.separator()
    if len(issues) > 0:
        report_issues_compact(issues)
        R.separator()
        R.add("Full details can be seen in a browser by running:\n")
        R.add("    $ %s %s\n" % (opts.scan_view, result_subdir))
        R.separator()
    R.flush()


def exec_report(opts):
    start_time = time.time()
    result_subdir, issues = do_analysis(opts)
    elapsed_time = time.time() - start_time
    report_output(opts, result_subdir, issues, elapsed_time)


###############################################################################
# 'check' subcommand execution
###############################################################################


def check_output(opts, result_subdir, issues):
    R.separator()
    report_issues(issues)
    if len(issues) == 0:
        R.add_green("No static analysis issues found!\n")
    else:
        R.add_red("Full details can be seen in a browser by running:\n")
        R.add("    $ %s %s\n" % (opts.scan_view, result_subdir))
    R.separator()
    R.flush()


def exec_check(opts):
    result_subdir, issues = do_analysis(opts)
    check_output(opts, result_subdir, issues)
    if len(issues) > 0:
        sys.exit("*** Static analysis issues found!")


###############################################################################
# validate inputs
###############################################################################


class PathAction(argparse.Action):
    def _path_exists(self, path):
        return os.path.exists(path)

    def _assert_exists(self, path):
        if not self._path_exists(path):
            sys.exit("*** does not exist: %s" % path)

    def _assert_mode(self, path, flags):
        if not os.access(path, flags):
            sys.exit("*** %s does not have correct mode: %x" % (path, flags))


class RepositoryPathAction(PathAction):
    def _assert_has_makefile(self, path):
        if not self._path_exists(os.path.join(path, "Makefile")):
            sys.exit("*** no Makefile found in %s. You must ./autogen.sh "
                     "and/or ./configure first" % path)

    def _assert_git_repository(self, path):
        cmd = 'git -C %s status' % path
        dn = open(os.devnull, 'w')
        if (subprocess.call(cmd.split(' '), stderr=dn, stdout=dn) != 0):
            sys.exit("*** %s is not a git repository" % path)

    def __call__(self, parser, namespace, values, option_string=None):
        path = os.path.abspath(values)
        self._assert_exists(path)
        self._assert_git_repository(path)
        self._assert_has_makefile(path)
        namespace.repository = path


###############################################################################
# helpers for defaults
###############################################################################


DEFAULT_REPORT_PATH = "/tmp/bitcoin-scan-build/"


###############################################################################
# cmd base class
###############################################################################

class ClangStaticAnalysisCmd(object):
    """
    Common base class for the commands in this script.
    """
    def __init__(self, repository, jobs, json, scan_build, scan_view):
        self.repository = repository
        self.jobs = jobs
        self.json = json
        self.scan_build = scan_build
        self.scan_view = scan_view

###############################################################################
# report cmd
###############################################################################

class ReportCmd(ClangStaticAnalysisCmd):
    """
    'report' subcommand class.
    """
    def __init__(self, repository, jobs, json, scan_build, scan_view):
        super().__init__(repository, jobs, json, scan_build, scan_view)

    def exec_analysis(self):
        print("analysis")
        pass


def add_report_cmd(subparsers):
    def exec_report_cmd(options):
        ReportCmd(options.repository, options.jobs, options.json,
                  options.scan_build, options.scan_view).exec_analysis()

    report_help = ("Runs clang static analysis and produces a summary report "
                   "of the findings.")
    parser = subparsers.add_parser('report', help=report_help)
    parser.set_defaults(func=exec_report_cmd)
    add_jobs_arg(parser)
    add_json_arg(parser)
    add_clang_static_analysis_args(parser)
    add_git_repository_arg(parser)


###############################################################################
# UI
###############################################################################


    # additional setup for default opts
#    if not (hasattr(opts, 'scan_build') and hasattr(opts, 'scan_view')):
#        opts.scan_build, opts.scan_view = locate_installed_binaries()
#    if opts.report_path == DEFAULT_REPORT_PATH:
#        make_report_path_if_missing()

    # non-configurable defaults
#    opts.make_clean_cmd = 'make clean'
#    opts.make_clean_log = 'make_clean.log'
#    opts.scan_build_log = 'scan_build.log'
#    opts.scan_build_cmd = ('%s -k -plist-html --keep-empty -o %s make -j%d' %
#                           (opts.scan_build, opts.report_path, opts.jobs))


if __name__ == "__main__":
    description = ("A utility for running clang static analysis on a codebase "
                   "in a consistent way.")
    parser = argparse.ArgumentParser(description=description)
    subparsers = parser.add_subparsers()
    add_report_cmd(subparsers)
    options = parser.parse_args()
    if not hasattr(options, "func"):
        parser.print_help()
        sys.exit("*** missing argument")
    options.scan_build, options.scan_view = (
        scan_build_binaries_from_options(options))
    options.func(options)
