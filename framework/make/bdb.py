#!/usr/bin/env python3
# Copyright (c) 2017 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import os
import sys
import subprocess
import urllib.request as Download
import hashlib
import shutil

from framework.make.make import Make
from framework.make.configure import Configure
from framework.file.hash import FileHash

BDB_SRC_DIR = "db-4.8.30.NC"
BDB_FILE = "%s.tar.gz" % BDB_SRC_DIR
BDB_URL = "http://download.oracle.com/berkeley-db/" + BDB_FILE
BDB_SHA256 = "12edc0df75bf9abd7f82f821795bcee50f42cb2e5f76a6a281b85732798364ef"
BDB_BUILD = "berkeleydb-build"
CONFIGURE_SCRIPT = "../dist/configure"
CONFIGURE_OUTFILE = "configure.log"
CONFIGURE_OPTIONS ="--enable-cxx --disable-shared --with-pic --prefix=%s"
MAKE_OUTFILE = "make.log"

UNTAR = "tar -xzf %s" % BDB_FILE


class BerkeleyDb(object):
    """
    Downloads and builds the correct version of BerkeleyDB following along
    the steps in build-unix.md.
    """
    def __init__(self, bdb_dir, silent=False):
        self.bdb_dir = bdb_dir
        self.silent = silent
        self.prefix = os.path.join(self.bdb_dir, BDB_BUILD)
        self.destination = os.path.join(self.bdb_dir, BDB_SRC_DIR)
        self.bdb_tar = os.path.join(self.bdb_dir, BDB_FILE)
        self._prep_bdb_dir()
        self._download()
        self._verify()
        self._unpack()

        build_dir = os.path.join(self.destination, 'build_unix/')
        configure_outfile = os.path.join(self.bdb_dir, CONFIGURE_OUTFILE)
        self.configurator = Configure(build_dir, configure_outfile,
                                      script=CONFIGURE_SCRIPT,
                                      options=CONFIGURE_OPTIONS % self.prefix)
        make_outfile = os.path.join(self.bdb_dir, MAKE_OUTFILE)
        self.maker = Make(build_dir, make_outfile, target="install")

    def _prep_bdb_dir(self):
        if not os.path.exists(self.bdb_dir):
            os.makedirs(self.bdb_dir)
        if os.path.exists(self.prefix):
            shutil.rmtree(self.prefix)
        os.makedirs(self.prefix)
        if os.path.exists(self.destination):
            shutil.rmtree(self.destination)

    def _download(self):
        if os.path.exists(self.bdb_tar):
            # To avoid abusing Oracle's server, don't re-download if we
            # already have the tarball.
            if not self.silent:
                print("Found %s" % (self.bdb_tar))
            return
        if not self.silent:
            print("Downloading %s..." % BDB_URL)
        Download.urlretrieve(BDB_URL, self.bdb_tar)
        if not self.silent:
            print("Done.")

    def _verify(self):
        if not str(FileHash(self.bdb_tar)) == BDB_SHA256:
            sys.exit("*** %s does not have expected hash %s" % (self.bdb_tar,
                                                                BDB_SHA256))

    def _unpack(self):
        original_dir = os.getcwd()
        os.chdir(self.bdb_dir)
        rc = subprocess.call(UNTAR.split(" "))
        os.chdir(original_dir)
        if rc != 0:
            sys.exit("*** could not unpack %s" % BDB_FILE)

    def build(self):
        self.configurator.run(silent=self.silent)
        self.maker.run(silent=self.silent)
