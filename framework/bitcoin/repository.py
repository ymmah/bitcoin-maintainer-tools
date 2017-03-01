#!/usr/bin/env python3
# Copyright (c) 2017 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import os

from framework.git.clone import GitClone
from framework.git.repository import GitRepository
from framework.berkeleydb.berkeleydb import BerkeleyDb
from framework.build.autogen import Autogen
from framework.build.configure import Configure


DEFAULT_UPSTREAM_URL = "https://github.com/bitcoin/bitcoin/"

class BitcoinClone(object):
    """
    Clones a bitcoin repository to a directory. If the directory already
    exists, just fetch changes from upstream to avoid re-downloading.
    """
    def __init__(self, directory, upstream_url=None, silent=False):
        self.directory = directory
        self.upstream_url = (upstream_url if upstream_url else
                             DEFAULT_UPSTREAM_URL)
        self.cloner = GitClone(self.upstream_url, silent=silent)

    def clone(self):
        self.cloner.clone_or_fetch(self.directory)


class BitcoinRepository(GitRepository):
    """
    A git repository that is specifically a bitcoin repository.
    """
    def __init__(self, directory, clone=False,
                 upstream_url=DEFAULT_UPSTREAM_URL, silent=False):
        self.directory = directory
        self.silent = silent
        if clone:
            BitcoinClone(self.directory, upstream_url=upstream_url,
                         silent=self.silent).clone()
        super().__init__(self.directory)

    def build_prepare(self, bdb_directory, autogen_log, configure_log):
        bdb = BerkeleyDb(bdb_directory, silent=self.silent)
        bdb.build()
        prefix = bdb.prefix()
        Autogen(self.directory, autogen_log).run()
        options = "LDFLAGS=-L%s/lib/ CPPFLAGS=-I%s/include/" % (prefix, prefix)
        Configure(self.directory, configure_log, options=options).run()
