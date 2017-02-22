#!/usr/bin/env python3
# Copyright (c) 2017 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from framework.make.make import Make


class ScanBuild(Make):
    """
    Executes 'make' wrapped in scan-build to get static analysis results.
    """
    def __init__(self, scan_build_path, report_dir, repository, output_file,
                 jobs, make_options=None):
        super().__init__(repository, output_file, jobs, options=make_options)
        self.scan_build_path = scan_build_path
        self.scan_build_options = ('-k -plist-html --keep-empty -o %s' %
                                   report_dir)

    def _cmd(self):
        make_cmd = super()._cmd()
        return "%s %s %s" % (self.scan_build_path, self.scan_build_options,
                             super()._cmd())
