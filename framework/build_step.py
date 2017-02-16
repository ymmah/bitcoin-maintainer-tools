#!/usr/bin/env python3
# Copyright (c) 2017 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import os
import sys
import subprocess

from framework.path import Path

###############################################################################
# base class
###############################################################################

class BuildStep(object):
    def __init__(self, repository, output_file):
        path = Path(output_file)
        containing_directory = Path(path.containing_directory())
        containing_directory.assert_exists()
        containing_directory.assert_mode(os.R_OK | os.W_OK)
        self.repository = repository
        self.output_file = str(path)

    def __str__(self):
        return self._cmd()

    def run(self):
        cmd = self._cmd()
        original_dir = os.getcwd()
        os.chdir(self.repository)
        f = open(os.path.abspath(self.output_file), 'w')
        if subprocess.call(cmd.split(' '), stdout=f, stderr=f) != 0:
            sys.exit("*** '%s' returned a non-zero status. log in %s" %
                     (cmd, self.output_file))
        f.close()
        os.chdir(original_dir)


###############################################################################
# make
###############################################################################

class MakeClean(BuildStep):
    def _cmd(self):
        return "make clean"


class Make(BuildStep):
    def __init__(self, repository, output_file, jobs, options=None):
        super().__init__(repository, output_file)
        self.jobs = jobs
        self.options = options

    def _cmd(self):
        cmd = "make -j%d" % self.jobs
        return cmd + ' ' + self.options if self.options else cmd


###############################################################################
# clang static analysis
###############################################################################

class ScanBuild(Make):
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
