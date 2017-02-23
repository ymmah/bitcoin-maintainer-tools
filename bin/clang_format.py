#!/usr/bin/env python3
# Copyright (c) 2017 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import sys
import argparse
import hashlib
import json

from framework.utl.report import Report
from framework.argparse.args import add_jobs_arg
from framework.argparse.args import add_json_arg
from framework.clang.args import add_clang_format_args
from framework.clang.args import clang_format_from_options
from framework.clang.args import add_force_arg
from framework.file.info import FileInfo
from framework.file.style import StyleDiff, StyleScore
from framework.cmd.file_content import FileContentCmd
from framework.git.targets import add_git_tracked_targets_arg


APPLIES_TO = ['*.cpp', '*.h']

###############################################################################
# gather file and diff info
###############################################################################

class ClangFormatFileInfo(FileInfo):
    """
    Obtains and represents the information regarding a single file obtained
    from clang-format.
    """
    def __init__(self, repository, file_path, clang_format, force):
        super().__init__(repository, file_path)
        self.clang_format = clang_format
        self.force = force

    def read(self):
        super().read()
        self['formatted'] = (
            self.clang_format.read_formatted_file(self['file_path']))
        self._exit_if_parameters_unsupported()
        self.set_write_content(self['formatted'])

    def _exit_if_parameters_unsupported(self):
        if self.force:
            return
        rejected_parameters = self.clang_format.style.rejected_parameters
        if len(rejected_parameters) > 0:
            r = Report()
            r.add_red("\nERROR: ")
            r.add("clang-format version %s does not support all parameters "
                  "given in\n%s\n\n" % (self.clang_format.binary_version,
                                        self.clang_format.style))
            r.add("Unsupported parameters:\n")
            for parameter in rejected_parameters:
                r.add("\t%s\n" % parameter)
            # The applied formating has subtle differences that vary between
            # major releases of clang-format. The recommendation should
            # probably follow the latest widely-available stable release.
            repo_info = self['repository'].repo_info
            r.add("\nUsing clang-format version %s or higher is recommended\n"
                  % repo_info['clang_format_recommended']['min_version'])
            r.add("Use the --force option to override and proceed anyway.\n\n")
            r.flush()
            sys.exit("*** missing clang-format support.")

    def compute(self):
        self['matching'] = self['content'] == self['formatted']
        self['formatted_md5'] = (
            hashlib.md5(self['formatted'].encode('utf-8')).hexdigest())
        self.update(StyleDiff(self['content'], self['formatted']))


###############################################################################
# cmd base class
###############################################################################

class ClangFormatCmd(FileContentCmd):
    """
    Common base class for the commands in this script.
    """
    def __init__(self, options):
        assert hasattr(options, 'force')
        assert hasattr(options, 'clang_format')
        options.include_fnmatches = APPLIES_TO
        super().__init__(options)
        self.force = options.force
        self.clang_format = options.clang_format

    def _file_info_list(self):
        return [ClangFormatFileInfo(self.repository, f, self.clang_format,
                                    self.force)
                for f in self.files_targeted]


###############################################################################
# report cmd
###############################################################################

class ReportCmd(ClangFormatCmd):
    """
    'report' subcommand class.
    """
    def __init__(self, options):
        options.force = True
        super().__init__(options)
        self.title = "Clang Format Report"

    def _cumulative_md5(self):
        # nothing fancy, just hash all the hashes
        h = hashlib.md5()
        for f in self.file_infos:
            h.update(f['formatted_md5'].encode('utf-8'))
        return h.hexdigest()

    def _files_in_ranges(self):
        files_in_ranges = {}
        ranges = [(90, 99), (80, 89), (70, 79), (60, 69), (50, 59), (40, 49),
                  (30, 39), (20, 29), (10, 19), (0, 9)]
        for lower, upper in ranges:
            files_in_ranges['%2d%%-%2d%%' % (lower, upper)] = (
                sum(1 for f in self.file_infos if
                    f['score'].in_range(lower, upper)))
        return files_in_ranges

    def _exec(self):
        a = super()._exec()
        file_infos = self.file_infos
        a['clang_format_path'] = self.clang_format.binary_path
        a['clang_format_version'] = str(self.clang_format.binary_version)
        a['clang_style_path'] = str(self.clang_format.style_path)
        a['rejected_parameters'] = self.clang_format.style.rejected_parameters
        a['elapsed_time'] = self.elapsed_time
        a['lines_before'] = sum(f['lines_before'] for f in file_infos)
        a['lines_added'] = sum(f['lines_added'] for f in file_infos)
        a['lines_removed'] = sum(f['lines_removed'] for f in file_infos)
        a['lines_unchanged'] = sum(f['lines_unchanged'] for f in file_infos)
        a['lines_after'] = sum(f['lines_after'] for f in file_infos)
        score = StyleScore(a['lines_before'], a['lines_added'],
                           a['lines_removed'], a['lines_unchanged'],
                           a['lines_after'])
        a['style_score'] = float(score)
        a['slow_diffs'] = [{'file_path': f['file_path'],
                            'diff_time': f['diff_time']} for f in
                            file_infos if f['diff_time'] > 1.0]
        a['matching'] = sum(1 for f in file_infos if f['matching'])
        a['not_matching'] = sum(1 for f in file_infos if not f['matching'])
        a['formatted_md5'] = self._cumulative_md5()
        a['files_in_ranges'] = self._files_in_ranges()
        return a

    def _output(self, results):
        if self.json:
            return super()._output(results)
        r = Report()
        r.add(super()._output(results))
        a = results
        r.add("%-30s %s\n" % ("clang-format bin:", a['clang_format_path']))
        r.add("%-30s %s\n" % ("clang-format version:",
                              a['clang_format_version']))
        r.add("%-30s %s\n" % ("Using style in:", a['clang_style_path']))
        r.separator()
        if len(a['rejected_parameters']) > 0:
            r.add_red("WARNING")
            r.add(" - This version of clang-format does not support the "
                  "following style\nparameters, so they were not used:\n\n")
            for param in a['rejected_parameters']:
                r.add("%s\n" % param)
            r.separator()
        r.add("%-30s %.02fs\n" % ("Elapsed time:", a['elapsed_time']))
        if len(a['slow_diffs']) > 0:
            r.add("Slowest diffs:\n")
            for slow in a['slow_diffs']:
                r.add("%6.02fs for %s\n" % (slow['diff_time'],
                                            slow['file_path']))
        r.separator()
        r.add("%-30s %4d\n" % ("Files scoreing 100%:", a['matching']))
        r.add("%-30s %4d\n" % ("Files scoring <100%:", a['not_matching']))
        r.add("%-30s %s\n" % ("Formatted Content MD5:", a['formatted_md5']))
        r.separator()
        for score_range in reversed(sorted(a['files_in_ranges'].keys())):
            r.add("%-30s %4d\n" % ("Files scoring %s:" % score_range,
                                   a['files_in_ranges'][score_range]))
        r.separator()
        r.add("Overall scoring:\n\n")
        score = StyleScore(a['lines_before'], a['lines_added'],
                           a['lines_removed'], a['lines_unchanged'],
                           a['lines_after'])
        r.add(str(score))
        r.separator()
        return str(r)


def add_report_cmd(subparsers):
    report_help = ("Produces a report with the analysis of the code format "
                   "adherence of the selected targets taken as a group.")
    parser = subparsers.add_parser('report', help=report_help)
    parser.set_defaults(cmd=lambda o: ReportCmd(o))
    add_jobs_arg(parser)
    add_json_arg(parser)
    add_clang_format_args(parser)
    add_git_tracked_targets_arg(parser)


###############################################################################
# check cmd
###############################################################################

class CheckCmd(ClangFormatCmd):
    """
    'check' subcommand class.
    """
    def __init__(self, options):
        super().__init__(options)
        self.title = "Clang Format Check"

    def _exec(self):
        a = super()._exec()
        a['failures'] = [{'file_path':       f['file_path'],
                          'style_score':     float(f['score']),
                          'lines_before':    f['lines_before'],
                          'lines_added':     f['lines_added'],
                          'lines_removed':   f['lines_removed'],
                          'lines_unchanged': f['lines_unchanged'],
                          'lines_after':     f['lines_after']}
                         for f in self.file_infos if not f['matching']]
        return a

    def _output(self, results):
        if self.json:
            return super()._output(results)
        r = Report()
        r.add(super()._output(results))
        a = results
        for f in a['failures']:
            r.add("A code format issue was detected in ")
            r.add_red("%s\n\n" % f['file_path'])
            score = StyleScore(f['lines_before'], f['lines_added'],
                               f['lines_removed'], f['lines_unchanged'],
                               f['lines_after'])
            r.add(str(score))
            r.separator()
        if len(a['failures']) == 0:
            r.add_green("No format issues found!\n")
        else:
            r.add_red("These files can be formatted by running:\n")
            r.add("$ clang_format.py format [option [option ...]] "
                  "[target [target ...]]\n")
        r.separator()
        return str(r)

    def _shell_exit(self, results):
        return (0 if len(results) == 0 else "*** code format issue found")


def add_check_cmd(subparsers):
    check_help = ("Validates that the selected targets match the style, gives "
                  "a per-file report and returns a non-zero shell status if "
                  "there are any format issues discovered.")
    parser = subparsers.add_parser('check', help=check_help)
    parser.set_defaults(cmd=lambda o: CheckCmd(o))
    add_jobs_arg(parser)
    add_json_arg(parser)
    add_force_arg(parser)
    add_clang_format_args(parser)
    add_git_tracked_targets_arg(parser)


###############################################################################
# format cmd
###############################################################################

class FormatCmd(ClangFormatCmd):
    """
    'format' subcommand class.
    """
    def __init__(self, options):
        options.json = False
        options.jobs = 1
        super().__init__(options)
        self.title = "Clang Format"

    def _exec(self):
        super()._exec()
        self.file_infos.write_all()

    def _output(self, results):
        return None


def add_format_cmd(subparsers):
    format_help = ("Applies the style formatting to the target files.")
    parser = subparsers.add_parser('format', help=format_help)
    parser.set_defaults(cmd=lambda o: FormatCmd(o))
    add_force_arg(parser)
    add_clang_format_args(parser)
    add_git_tracked_targets_arg(parser)


###############################################################################
# UI
###############################################################################


if __name__ == "__main__":
    description = ("A utility for invoking clang-format to look at the C++ "
                   "code formatting in the repository. It produces "
                   "reports of style metrics and also can apply formatting.")
    parser = argparse.ArgumentParser(description=description)
    subparsers = parser.add_subparsers()
    add_report_cmd(subparsers)
    add_check_cmd(subparsers)
    add_format_cmd(subparsers)
    options = parser.parse_args()
    if not hasattr(options, "cmd"):
        parser.print_help()
        sys.exit("*** missing argument")
    options.clang_format = clang_format_from_options(options)
    options.cmd(options).run()
