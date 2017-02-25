#!/usr/bin/env python3
# Copyright (c) 2017 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import re
import os
import sys
import subprocess
import argparse

from framework.clang.find import ClangFind, CLANG_BINARIES
from framework.clang.format import ClangFormat
from framework.clang.scan_build import ScanBuild
from framework.clang.scan_view import ScanView
from framework.make.make import MakeClean
from framework.path.path import Path
from framework.argparse.action import ReadableFileAction
from framework.file.io import read_file, write_file

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
# defaults
###############################################################################

DEFAULT_REPORT_DIR = "/tmp/bitcoin-scan-build/"

SCAN_BUILD_OUTPUT = "scan_build.log"
MAKE_CLEAN_OUTPUT = "make_clean.log"

###############################################################################
# add options
###############################################################################

def add_clang_bin_path_option(parser):
    b_help = ("path to the clang directory or binary to be used "
              "(default=The required clang binary installed in PATH with the "
              "highest version number)")
    parser.add_argument("-b", "--bin-path", type=str,
                        action=ClangDirectoryAction, help=b_help)


def add_scan_build_report_path_option(parser):
    r_help = ("path for scan-build to write its report files. "
              "(default=%s)" % DEFAULT_REPORT_DIR)
    parser.add_argument("-r", "--report-path", default=DEFAULT_REPORT_DIR,
                        type=str, action=ReportPathAction, help=r_help)


def add_clang_format_style_file_option(parser):
    sf_help = ("path to the clang style file to be used (default=The "
               "src/.clang_format file specified in the repo info)")
    parser.add_argument("-s", "--style-file", type=str,
                        action=ReadableFileAction, help=sf_help)


def add_clang_format_force_option(parser):
    f_help = ("force proceeding with if clang-format doesn't support all "
              "parameters in the style file (default=False)")
    parser.add_argument("-f", "--force", action='store_true', help=f_help)


def add_clang_options(parser, report_path=False, style_file=False,
                      force=False):
    """
    Adds optional arguments to the parser for specifying options for
    clang binaries and their execution settings.
    """
    add_clang_bin_path_option(parser)
    if report_path:
        add_scan_build_report_path_option(parser)
    if style_file:
        add_clang_format_style_file_option(parser)
    if force:
        add_clang_format_force_option(parser)


###############################################################################
# finish settings
###############################################################################

def finish_clang_settings(options):
    """
    Makes the settings namepsce uniform by instantiating classes filled in with
    default behavior if options have not been specified by the user.
    """
    assert hasattr(options, 'repository')
    assert hasattr(options, 'jobs')
    # locate clang executables:
    if hasattr(options, 'clang_executables'):
        clang_format = options.clang_executables['clang-format']
        scan_build = options.clang_executables['scan-build']
        scan_view = options.clang_executables['scan-view']
    else:
        finder = ClangFind()
        clang_format = finder.best('clang-format')
        scan_build = finder.best('scan-build')
        scan_view = finder.best('scan-view')
    # clang-format settings:
    default_style = os.path.join(str(options.repository),
        options.repository.repo_info['clang_format_style']['value'])
    clang_format_style_path = (options.style_file if
                               (hasattr(options, 'style_file') and
                                options.style_file) else default_style)
    options.clang_format = ClangFormat(clang_format,
                                       clang_format_style_path)
    # scan-build settings:
    viewer = ScanView(scan_view)
    scan_build_report_dir = (options.report_path if
                             hasattr(options, "report_path") else
                             DEFAULT_REPORT_DIR)
    make_clean_output_file = os.path.join(scan_build_report_dir,
                                          MAKE_CLEAN_OUTPUT)
    cleaner = MakeClean(str(options.repository), make_clean_output_file)
    scan_build_output_file = os.path.join(scan_build_report_dir,
                                          SCAN_BUILD_OUTPUT)
    options.scan_build = ScanBuild(scan_build, scan_build_report_dir,
                                   cleaner, viewer, str(options.repository),
                                   scan_build_output_file, options.jobs)
