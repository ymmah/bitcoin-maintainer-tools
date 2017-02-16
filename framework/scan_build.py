#!/usr/bin/env python3
# Copyright (c) 2017 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import os
import subprocess
import plistlib
import itertools

from framework.path import Path


class ScanBuildPlistDirectory(Path):
    def __init__(self, directory):
        path = Path(directory)
        path.assert_exists()
        path.assert_is_directory()
        path.assert_mode(os.R_OK)
        self.directory = directory

    def _find_events(self, paths, files):
        for p in paths:
            if p['kind'] == 'event':
                yield {'message': p['extended_message'],
                       'line':    p['location']['line'],
                       'col':     p['location']['col'],
                       'file':    files[p['location']['file']]}

    def _plist_to_issue(self, plist):
        files = plist['files']
        for d in plist['diagnostics']:
            yield {'type':        d['type'],
                   'description': d['description'],
                   'line':        d['location']['line'],
                   'col':         d['location']['col'],
                   'file':        files[d['location']['file']],
                   'events':      list(self._find_events(d['path'], files))}

    def issues(self):
        plist_files = (os.path.join(self.directory, f) for f in
                       os.listdir(self.directory) if f.endswith('.plist'))
        read_plists = (plistlib.readPlist(plist_file) for plist_file in
                       plist_files)
        relevant_plists = (plist for plist in read_plists if
                           len(plist['diagnostics']) > 0)
        return list(itertools.chain(*[self._plist_to_issue(plist) for plist in
                                     relevant_plists]))


class ScanBuildResultDirectory(Path):
    def __init__(self, directory):
        self._create_if_missing(directory)
        path = Path(directory)
        path.assert_exists()
        path.assert_is_directory()
        path.assert_mode(os.R_OK | os.W_OK)
        self.directory = directory

    def _create_if_missing(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    def most_recent_results(self):
        # scan-build puts results in a subdirectory where the directory name is
        # a timestamp. e.g. /tmp/bitcoin-scan-build/2017-01-23-115243-901-1 We
        # want the most recent directory, so we sort and return the path name
        # sorted highest.
        subdirs = sorted([d for d in os.listdir(self.directory) if
                          os.path.isdir(os.path.join(self.directory, d))])
        directory = ScanBuildPlistDirectory(os.path.join(self.directory,
                                                         subdirs[-1]))
        return directory.directory, directory.issues()
