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

from framework.build.make import Make
from framework.build.configure import Configure
from framework.file.hash import FileHash

SRC_SUBDIR = "db-4.8.30.NC"
BUILD_TARGET_SUBDIR = "berkeleydb-install"
TARBALL = SRC_SUBDIR + ".tar.gz"
DOWNLOAD_URL = "http://download.oracle.com/berkeley-db/" + TARBALL
CHECKSUM = "12edc0df75bf9abd7f82f821795bcee50f42cb2e5f76a6a281b85732798364ef"
UNTAR = "tar -xzf " + TARBALL
BUILD_FROM_SUBDIR = "build_unix"
CONFIGURE_SCRIPT = "../dist/configure"
CONFIGURE_OUTFILE = "bdb-configure.log"
CONFIGURE_OPTIONS ="--enable-cxx --disable-shared --with-pic --prefix=%s"
MAKE_OUTFILE = "bdb-make-install.log"


class BerkeleyDbDownload(object):
    """
    Downloads, verifies and unpacks the BerkeleyDB tarball from Oracle.
    """
    def __init__(self, directory, silent=False):
        self.directory = directory
        self.silent = silent
        self.tarball = os.path.join(self.directory, TARBALL)

    def download(self):
        if os.path.exists(self.tarball):
            # To avoid abusing Oracle's server, don't re-download if we
            # already have the tarball.
            if not self.silent:
                print("Found %s" % (self.tarball))
            return
        if not self.silent:
            print("Downloading %s..." % DOWNLOAD_URL)
        Download.urlretrieve(DOWNLOAD_URL, self.tarball)
        if not self.silent:
            print("Done.")

    def verify(self):
        if not str(FileHash(self.tarball)) == CHECKSUM:
            sys.exit("*** %s does not have expected hash %s" % (self.tarball,
                                                                CHECKSUM))

    def unpack(self):
        original_dir = os.getcwd()
        os.chdir(self.directory)
        rc = subprocess.call(UNTAR.split(" "))
        os.chdir(original_dir)
        if rc != 0:
            sys.exit("*** could not unpack %s" % self.tarball)


class BerkeleyDb(object):
    """
    Produces a build and installed subdirectory for Bitoin's build process to
    use. The instructions from build-unix.md are automated and the prefix to
    use for Bitcoin's ./configure step is made available.
    """
    def __init__(self, directory, silent=False):
        self.directory = directory
        self.silent = silent
        self.build_target_dir = os.path.join(self.directory,
                                             BUILD_TARGET_SUBDIR)
        self.src_dir = os.path.join(self.directory, SRC_SUBDIR)
        self.build_from_dir = os.path.join(self.src_dir, BUILD_FROM_SUBDIR)
        self.configure_outfile = os.path.join(self.directory, CONFIGURE_OUTFILE)
        self.make_outfile = os.path.join(self.directory, MAKE_OUTFILE)

    def _prep_directory(self):
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        if os.path.exists(self.build_target_dir):
            shutil.rmtree(self.build_target_dir)
        os.makedirs(self.build_target_dir)
        if os.path.exists(self.src_dir):
            shutil.rmtree(self.src_dir)

    def prefix(self):
        return self.build_target_dir

    def build(self):
        self._prep_directory()
        self.downloader = BerkeleyDbDownload(self.directory,
                                             silent=self.silent)
        self.downloader.download()
        self.downloader.verify()
        self.downloader.unpack()
        options = CONFIGURE_OPTIONS % self.prefix()
        self.configurator = Configure(self.build_from_dir,
                                      self.configure_outfile,
                                      script=CONFIGURE_SCRIPT, options=options)
        self.configurator.run(silent=self.silent)
        self.maker = Make(self.build_from_dir, self.make_outfile,
                          target="install")
        self.maker.run(silent=self.silent)
