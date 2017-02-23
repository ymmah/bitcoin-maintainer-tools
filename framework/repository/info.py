#!/usr/bin/env python3
# Copyright (c) 2017 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import json
import os

from framework.path.path import Path
from framework.file.io import read_file

REPO_INFO_FILENAME = ".bitcoin-maintainer-tools.json"

FAILBACK_REPO_INFO_FILENAME = ".failback-bitcoin-maintainer-tools.json"

class RepositoryInfo(dict):
    """
    Dictionary that is sourced from a json file in the targeet repsitory.
    If the file doesn't exist, a failback file is used for the settings.
    """
    def __init__(self, repository_base):
        super().__init__()
        json_file = os.path.join(repository_base, REPO_INFO_FILENAME)
        path = Path(json_file)
        if not path.exists():
            # If there is no .json file in the repo, it might be an old version
            # checked out. We can still do best-effort with a default file.
            json_file = os.path.abspath(FAILBACK_REPO_INFO_FILENAME)
            path = Path(json_file)
            if not path.exists():
                sys.exit("Could not find a .json repository info file to use.")
        path.assert_is_file()
        path.assert_mode(os.R_OK)
        content = read_file(json_file)
        self.update(json.loads(content))
