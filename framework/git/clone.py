#!/usr/bin/env python3
# Copyright (c) 2017 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import subprocess
import sys

from framework.git.repository import GitRepository
from framework.path.path import Path

class GitClone(object):
    def __init__(self, upstream_url):
        self.upstream_url = upstream_url

    def _clone(self, repository_base):
        cmd = "git clone %s %s" % (self.upstream_url, repository_base)
        rc = subprocess.call(cmd.split(" "))
        if rc != 0:
            sys.exit("*** clone command '%s' failed" % cmd)
        return GitRepository(repository_base)

    def _fetch(self, repository_base):
        r = GitRepository(repository_base)
        r.fetch()
        return r

    def clone_or_fetch(self, repository_base):
        """
        Clones a fresh repository at the given base, unless it exists, in
        which case it will fetch the latest upstream state. The result will
        be returned as a GitRepository instance.
        """
        p = Path(repository_base)
        return (self._fetch(repository_base) if p.exists() else
                self._clone(repository_base))
