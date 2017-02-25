#!/usr/bin/env python3
# Copyright (c) 2017 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.


def add_jobs_option(parser):
    j_help = "parallel jobs for computations (default=4)"
    parser.add_argument("-j", "--jobs", type=int, default=4, help=j_help)


def add_json_option(parser):
    j_help = "print output in json format (default=False)"
    parser.add_argument("--json", action='store_true', help=j_help)
