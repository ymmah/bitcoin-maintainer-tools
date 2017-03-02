#!/usr/bin/env python3
# Copyright (c) 2017 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import os

from framework.bitcoin.clone import DEFAULT_UPSTREAM_URL
from framework.bitcoin.repository import BitcoinRepository

CLONE_DIR = "bitcoin-test-repo"
BDB_DIR = "berkeley-db"
AUTOGEN_LOG = "autogen.log"
CONFIGURE_LOG = "configure.log"
TEST_BRANCH = "v0.13.2"


def setup_build_ready_bitcoin_repo(directory,
                                   upstream_url=DEFAULT_UPSTREAM_URL,
                                   branch=TEST_BRANCH, silent=False):
    bdb_dir = os.path.join(directory, BDB_DIR)
    clone_dir = os.path.join(directory, CLONE_DIR)
    autogen_log = os.path.join(directory, AUTOGEN_LOG)
    configure_log = os.path.join(directory, CONFIGURE_LOG)
    repository = BitcoinRepository(clone_dir, clone=True,
                                   upstream_url=upstream_url, silent=silent)
    repository.reset_hard(TEST_BRANCH)
    repository.build_prepare(bdb_dir, autogen_log, configure_log)
    return repository
