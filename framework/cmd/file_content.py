#!/usr/bin/env python3
# Copyright (c) 2017 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import time
import json
import sys
from framework.utl.report import Report
from framework.file_filter import FileFilter
from framework.file_info import FileInfos
from framework.cmd.repository import RepositoryCmd


class FileContentCmd(RepositoryCmd):
    """
    Base class for commands that compute info on a set of files based on
    the content inside of the files. Provides a common way for indicating
    a subset of files that the operation is to apply to via lists of
    fnmatch expressions.
    """
    def __init__(self, options):
        assert hasattr(options, 'json')
        super().__init__(options, silent=options.json)
        assert hasattr(options, 'jobs')
        assert hasattr(options, 'include_fnmatches')
        assert hasattr(options, 'target_fnmatches')
        self.title = "FileContentCmd superclass"
        self.json = options.json
        self.jobs = options.jobs
        self.tracked_files = self.repository.tracked_files()
        exclude_fnmatches = self.repository.repo_info['subtrees']['fnmatches']
        self.files_in_scope = list(
            self._files_in_scope(self.repository, self.tracked_files,
                                 options.include_fnmatches, exclude_fnmatches))
        self.files_targeted = list(
            self._files_targeted(self.repository, self.files_in_scope,
                                 options.include_fnmatches, exclude_fnmatches,
                                 options.target_fnmatches))

    def _scope_filter(self, repository, include_fnmatches, exclude_fnmatches):
        file_filter = FileFilter()
        file_filter.append_include(include_fnmatches,
                                   base_path=str(repository))
        file_filter.append_exclude(exclude_fnmatches,
                                   base_path=str(repository))
        return file_filter

    def _files_in_scope(self, repository, tracked_files, include_fnmatches,
                        exclude_fnmatches):
        file_filter = self._scope_filter(repository, include_fnmatches,
                                         exclude_fnmatches)
        return (f for f in tracked_files if file_filter.evaluate(f))

    def _target_filter(self, repository, include_fnmatches, exclude_fnmatches,
                       target_fnmatches):
        file_filter = self._scope_filter(repository, include_fnmatches,
                                         exclude_fnmatches)
        file_filter.append_include(target_fnmatches, base_path=repository)
        return file_filter

    def _files_targeted(self, repository, tracked_files, include_fnmatches,
                        exclude_fnmatches, target_fnmatches):
        file_filter = self._target_filter(repository, include_fnmatches,
                                          exclude_fnmatches, target_fnmatches)
        return (f for f in tracked_files if file_filter.evaluate(f))

    def _read_file_infos(self):
        self.file_infos.read_all()

    def _compute_file_infos(self):
        self.file_infos.compute_all()

    def _read_and_compute_file_infos(self):
        start_time = time.time()
        self.file_infos = FileInfos(self.jobs, self._file_info_list())
        self._read_file_infos()
        self._compute_file_infos()
        self.elapsed_time = time.time() - start_time

    def _exec(self):
        self._read_and_compute_file_infos()
        a = super()._exec()
        a['tracked_files'] = len(self.tracked_files)
        a['files_in_scope'] = len(self.files_in_scope)
        a['files_targeted'] = len(self.files_targeted)
        a['jobs'] = self.jobs
        return a

    def _output(self, results):
        if self.json:
            return super()._output(results)
        r = Report()
        a = results
        r.separator()
        r.add("%4d files tracked in repo\n" % a['tracked_files'])
        r.add("%4d files in scope according to script settings\n" %
              a['files_in_scope'])
        r.add("%4d files examined according to listed targets\n" %
              a['files_targeted'])
        r.add("%4d parallel jobs for computing analysis\n" % a['jobs'])
        r.separator()
        return str(r)

    def _shell_exit(self, results):
        return 0
