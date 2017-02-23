#!/usr/bin/env python3
# Copyright (c) 2017 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import re
import os
import sys
import subprocess
import argparse

from framework.clang.find import ClangFind
from framework.utl.path import Path
from framework.argparse.action import ExecutableBinaryAction
from framework.argparse.action import ReadableFileAction
from framework.utl.io import read_file, write_file

###############################################################################
# argparse utilities
###############################################################################


class ClangDirectoryAction(argparse.Action):
    """
    Validate that 'values' is a path that points to a directory that has
    clang executables in it. The set of clang binaries contained is returned
    along with their detected version. Tolerates either a directory, a
    directory with a 'bin/' subdirectory or a path to an executable file.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        if not isinstance(values, str):
            sys.exit("*** %s is not a string" % values)
        clang_find = ClangFind(values)
        executables = clang_find.best_binaries()
        for clang_binary in CLANG_BINARIES:
            if clang_binary not in executables:
                sys.exit("*** %s does not contain a %s binary" %
                         (values, clang_binary))
        namespace.clang_executables = executables


###############################################################################
# style
###############################################################################

class ClangFormatStyle(object):
    """
    Reads and parses a .clang-format style file to represent it. The style can
    have keys removed and it can be translated into a '--style' argument for
    invoking clang-format.
    """
    def __init__(self, file_path):
        p = Path(file_path)
        p.assert_exists()
        p.assert_is_file()
        p.assert_mode(os.R_OK)
        self.file_path = file_path
        self.raw_contents = read_file(file_path)
        self.parameters = self._parse_parameters()
        self.rejected_parameters = {}

    def __str__(self):
        return self.file_path

    def _parse_parameters(self):
        # Python does not have a built-in yaml parser, so here is a
        # hand-written one that *seems* to minimally work for this purpose.
        many_spaces = re.compile(': +')
        spaces_removed = many_spaces.sub(':', self.raw_contents)
        # split into a list of lines
        lines = [l for l in spaces_removed.split('\n') if l != '']
        # split by the colon separator
        split = [l.split(':') for l in lines]
        # present as a dictionary
        return {item[0]: ''.join(item[1:]) for item in split}

    def reject_parameter(self, key):
        if key not in self.rejected_parameters:
            self.rejected_parameters[key] = self.parameters.pop(key)

    def style_arg(self):
        return '-style={%s}' % ', '.join(["%s: %s" % (k, v) for k, v in
                                          self.parameters.items()])


###############################################################################
# clang format class
###############################################################################

class ClangFormat(object):
    """
    Facility to read in the formatted content of a file using a particular
    clang-format binary and style file.
    """
    def __init__(self, binary, style_path):
        self.binary_path = binary['path']
        self.binary_version = binary['version']
        self.style_path = style_path
        self.style = ClangFormatStyle(self.style_path)
        self.UNKNOWN_KEY_REGEX = re.compile("unknown key '(?P<key_name>\w+)'")

    def _parse_unknown_key(self, err):
        if len(err) == 0:
            return 0, None
        match = self.UNKNOWN_KEY_REGEX.search(err)
        if not match:
            return len(err), None
        return len(err), match.group('key_name')

    def _try_format_file(self, file_path):
        cmd = [self.binary_path, self.style.style_arg(), file_path]
        return subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)

    def read_formatted_file(self, file_path):
        while True:
            p = self._try_format_file(file_path)
            out = p.stdout.read().decode('utf-8')
            err = p.stderr.read().decode('utf-8')
            p.communicate()
            if p.returncode != 0:
                sys.exit("*** clang-format could not execute")
            # Older versions of clang don't support some style parameter keys,
            # so we work around by redacting any key that gets rejected until
            # we find a subset of parameters that can apply the format without
            # producing any stderr output.
            err_len, unknown_key = self._parse_unknown_key(err)
            if not unknown_key and err_len > 0:
                sys.exit("*** clang-format produced unknown output to stderr")
            if unknown_key:
                self.style.reject_parameter(unknown_key)
                continue
            return out

    def rejected_parameters(self):
        return self.style.rejected_parameters


###############################################################################
# getting a clang format class from args
###############################################################################

def add_bin_path_arg(parser):
    b_help = ("path to the clang directory or binary to be used "
              "(default=The required clang binary installed in PATH with the "
              "highest version number)")
    parser.add_argument("-b", "--bin-path", type=str,
                        action=ClangDirectoryAction, help=b_help)

def add_style_file_arg(parser):
    sf_help = ("path to the clang style file to be used (default=The "
               "src/.clang_format file of the repository which holds the "
               "targets)")
    parser.add_argument("-s", "--style-file", type=str,
                        action=ReadableFileAction, help=sf_help)


def add_clang_format_args(parser):
    add_bin_path_arg(parser)
    add_style_file_arg(parser)


def clang_format_from_options(options):
    binary = (options.clang_executables['clang-format'] if
              hasattr(options, 'clang_executables') else
              ClangFind().best('clang-format'))
    style_path = (options.style_file if options.style_file else
                  os.path.join(str(options.repository),
                  options.repository.repo_info['clang_format_style']['value']))
    return ClangFormat(binary, style_path)


###############################################################################
# TODO
###############################################################################

class ReportPathAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if not isinstance(values, str):
            sys.exit("*** %s is not a single string" % values)
        p = Path(values)
        p.assert_exists()
        p.assert_is_file()
        p.assert_mode(os.R_OK | os.W_OK)


DEFAULT_REPORT_PATH = "/tmp/bitcoin-scan-build/"

def add_report_path_arg(parser):
    r_help = ("The path for scan-build to write its report files. "
              "(default=%s)" % DEFAULT_REPORT_PATH)
    parser.add_argument("-r", "--report-path", default=DEFAULT_REPORT_PATH,
                        type=str, action=ReportPathAction, help=r_help)


def add_clang_static_analysis_args(parser):
    add_bin_path_arg(parser)
    add_report_path_arg(parser)


def scan_build_binaries_from_options(options):
    if hasattr(options, 'clang_executables'):
        scan_build = options.clang_executables['scan-build']
        scan_view = options.clang_executables['scan-view']
    else:
        finder = ClangFind()
        scan_build = finder.best('scan-build')
        scan_view = finder.best('scan-view')
    return scan_build, scan_view

###############################################################################
# TODO
###############################################################################


def add_clang_args(parser):
    add_bin_path_arg(parser)
    add_report_path_arg(parser)
    add_style_file_arg(parser)


def add_force_arg(parser):
    f_help = ("force proceeding with if clang-format doesn't support all "
              "parameters in the style file (default=False)")
    parser.add_argument("-f", "--force", action='store_true', help=f_help)
