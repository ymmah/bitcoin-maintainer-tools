#!/usr/bin/env python3
# Copyright (c) 2017 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import os
import argparse

from framework.argparse.option import add_tmp_directory_option
from framework.berkeleydb.setup import berkeleydb_setup_dir
from framework.bitcoin.setup import bitcoin_setup_repo
from framework.clang.setup import clang_setup_bin_dir

if __name__ == "__main__":
    description = ("Downloads and unpacks the dependencies for TravisCI runs "
                   "before it forks out to the parallel build matrix.")
    parser = argparse.ArgumentParser(description=description)
    add_tmp_directory_option(parser)
    settings = parser.parse_args()
    _ = berkeleydb_setup_dir(settings.tmp_directory)
    _ = clang_setup_bin_dir(settings.tmp_directory)
    _ = bitcoin_setup_repo(settings.tmp_directory, branch="v0.14.0")
