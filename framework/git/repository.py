#!/usr/bin/env python3
# Copyright (c) 2017 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import os
import sys
import subprocess
import argparse

from framework.utl.path import Path
from framework.repo_info import RepoInfo
from framework.git.path import GitPath


class GitRepository(object):
    """
    Represents and queries information from a git repository clone.
    """
    def __init__(self, repository_base):
        self.repository_base = str(Path(repository_base))
        git_path = GitPath(repository_base)
        git_path.assert_exists()
        git_path.assert_mode(os.R_OK)
        git_path.assert_in_git_repository()
        if str(self.repository_base) != str(git_path.repository_base()):
            sys.exit("*** %s is not the base of its repository" %
                     self.repository_base)
        self.repo_info = RepoInfo(self.repository_base)

    def __str__(self):
        return self.repository_base

    def tracked_files(self):
        orig = os.getcwd()
        os.chdir(self.repository_base)
        out = subprocess.check_output(['git', 'ls-files'])
        os.chdir(orig)
        return [os.path.join(self.repository_base, f) for f in
                out.decode("utf-8").split('\n') if f != '']

    def assert_has_makefile(self):
        makefile = Path(os.path.join(self.repository_base, "Makefile"))
        if not makefile.exists():
            sys.exit("*** no Makefile found in %s. You must ./autogen.sh "
                     "and/or ./configure first" % self.repository_base)


class GitRepositoryAction(argparse.Action):
    """
    Checks taht the string points to a valid git repository.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        if not isinstance(values, str):
            sys.exit("*** %s is not a string" % values)
        repository = GitRepository(values)
        repository.assert_has_makefile()
        namespace.repository = repository
        namespace.target_fnmatches = [os.path.join(str(repository), '*')]


def add_git_repository_arg(parser):
    repo_help = ("A source code repository for which the static analysis is "
                 "to be performed upon.")
    parser.add_argument("repository", type=str, action=GitRepositoryAction,
                        help=repo_help)
