#!/usr/bin/env python3
# Copyright (c) 2017 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import sys
import argparse
import json

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



if __name__ == "__main__":
    description = ("Wrapper to invoke a collection of scripts that produce "
                   "data from analizing a repository.")
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

    copyright_header = CopyrightHeaderReport(options.repository, options.jobs,
                                             options.target_fnmatches,
                                             options.json)

    clang_format = ClangFormatReport(options.repository, options.jobs,
                                     options.target_fnmatches, options.json,
                                     options.clang_format)
    basic_style = BasicStyleReport(options.repository, options.jobs,
                                   options.target_fnmatches, options.json)
    static_analysis = ClangStaticAnalysisReport(options.repository,
                                                options.jobs, options.json,
                                                options.scan_build,
                                                options.report_path,
                                                options.scan_view)

    exit, copyright_header_out = copyright_header.run()
    if exit != 0:
        sys.exit(exit)
    exit, clang_format_out = clang_format.run()
    if exit != 0:
        sys.exit(exit)
    exit, basic_style_out = basic_style.run()
    if exit != 0:
        sys.exit(exit)
    exit, static_analysis_out = static_analysis.run()
    if exit != 0:
        sys.exit(exit)

    outputs = {'Copyright Header Report:':       copyright_header_out,
               'Basic Style Report':             basic_style_out,
               'Clang Format Report:':           clang_format_out,
               'Clang Static Analysis Report:':  static_analysis_out}
    if json:
        print(json.dumps({k: json.loads(v) for k, v in outputs.items()}))
