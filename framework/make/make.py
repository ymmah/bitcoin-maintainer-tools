#!/usr/bin/env python3
# Copyright (c) 2017 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from framework.make.step import BuildStep


class MakeClean(BuildStep):
    """
    Executes 'make clean' on the respository.
    """
    def _cmd(self):
        return "make clean"


class Make(BuildStep):
    """
    Executes 'make' on the respository.
    """
    def __init__(self, repository, output_file, jobs, options=None):
        super().__init__(repository, output_file)
        self.jobs = jobs
        self.options = options

    def _cmd(self):
        cmd = "make -j%d" % self.jobs
        return cmd + ' ' + self.options if self.options else cmd
