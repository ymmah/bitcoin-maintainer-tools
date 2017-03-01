#!/usr/bin/env python3
# Copyright (c) 2017 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import os

from framework.berkeleydb.berkeleydb import BerkeleyDb
from framework.git.clone import GitClone
from framework.build.autogen import Autogen
from framework.build.configure import Configure
from framework.build.make import Make

UPSTREAM_URL = "https://github.com/bitcoin/bitcoin/"
CLONE_DIR = "bitcoin-test-repo"
BDB_DIR = "berkeley-db"
TEST_BRANCH = "v0.13.2"

tmp = "/tmp/1234/"
bdb = BerkeleyDb("/tmp/1234/")
bdb.build()
prefix = bdb.prefix()

cloner = GitClone(UPSTREAM_URL)
clone_dir = os.path.join(tmp, CLONE_DIR)
repository = cloner.clone_or_fetch(clone_dir)
repository.reset_hard(TEST_BRANCH)

autogener = Autogen(str(repository), "autogen.log")
autogener.run()

options = "LDFLAGS=-L%s/lib/ CPPFLAGS=-I%s/include/" % (prefix, prefix)

configurator = Configure(str(repository), "configure.log", options=options)
configurator.run()

maker = Make(str(repository), "make.log", jobs=8)
maker.run()
