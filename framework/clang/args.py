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
from framework.clang.format import ClangFormat
from framework.utl.path import Path
from framework.argparse.action import ReadableFileAction
from framework.utl.io import read_file, write_file

###############################################################################
# actions
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


class ReportPathAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if not isinstance(values, str):
            sys.exit("*** %s is not a single string" % values)
        p = Path(values)
        p.assert_exists()
        p.assert_is_file()
        p.assert_mode(os.R_OK | os.W_OK)



###############################################################################
# arg management
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


def add_clang_args(parser):
    add_bin_path_arg(parser)
    add_report_path_arg(parser)
    add_style_file_arg(parser)


def add_force_arg(parser):
    f_help = ("force proceeding with if clang-format doesn't support all "
              "parameters in the style file (default=False)")
    parser.add_argument("-f", "--force", action='store_true', help=f_help)
