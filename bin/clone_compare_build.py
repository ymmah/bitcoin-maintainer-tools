#!/usr/bin/env python3
# Copyright (c) 2017 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import argparse

from framework.argparse.option import add_jobs_option
from framework.bitcoin.clone import DEFAULT_UPSTREAM_URL
from framework.bitcoin.setup import bitcoin_setup_build_ready_repo


def add_url_option(parser):
    u_help = "upstream url to clone from (default=%s)" % DEFAULT_UPSTREAM_URL
    parser.add_argument('-u', "--clone-url", type=str,
                        default=DEFAULT_UPSTREAM_URL, help=u_help)


def add_branch_option(parser):
    b_help = "branch to checkout before building (default=master)"
    parser.add_argument('-b', "--git-branch", type=str, default='master',
                        help=b_help)


def add_build_workspace_option(parser):
    w_help = "Directory to hold the repository and BerkeleyDb"
    parser.add_argument('workspace', type=str, help=w_help)


if __name__ == "__main__":
    description = ("Clones, downloads BerkeleyDB and builds a bitcoin "
                   "repository with stardard settings.")
    parser = argparse.ArgumentParser(description=description)
    add_jobs_option(parser)
    add_url_option(parser)
    add_branch_option(parser)
    add_build_workspace_option(parser)
    settings = parser.parse_args()
    repository = (
        bitcoin_setup_build_ready_repo(settings.workspace,
                                       upstream_url=settings.clone_url,
                                       branch=settings.git_branch))

