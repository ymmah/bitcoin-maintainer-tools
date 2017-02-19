#!/usr/bin/env python3
# Copyright (c) 2017 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import json

# TODO move this into bitcoin repo as a .json file? also to better enable tools
# in this repo to run against other repos...
REPO_INFO = {
    'subtrees': {
        'description': "Subtrees of the repository which should be ignored since they follow different rules. Expressed as a list of fmnmatch expressions.",
        'fnmatches': [
            'src/secp256k1/*',
            'src/leveldb/*',
            'src/univalue/*',
            'src/crypto/ctaes/*',
        ],
    },
    'clang_format_style': {
    'description': "File in the repository which contains the clang-format style definition.",
    'value': 'src/.clang-format',
    },
    'clang_format_recommended': {
        'description': "The recommendation for the minimum version of clang-format to be used for applying formatting. Different versions have small discrepancies for applied formatting and the tools will warn if an old version is being used.",
        'min_version': '3.9.0',
    },
    'no_copyright_header_expected': {
        'description' : "Source files where it is acceptable to not have a MIT Licence copyright header. Expressed as a list of fnmatch expressions.",
        'fnmatches': [
            '*__init__.py',
            'doc/man/Makefile.am',
            'build-aux/m4/ax_boost_base.m4',
            'build-aux/m4/ax_boost_chrono.m4',
            'build-aux/m4/ax_boost_filesystem.m4',
            'build-aux/m4/ax_boost_program_options.m4',
            'build-aux/m4/ax_boost_system.m4',
            'build-aux/m4/ax_boost_thread.m4',
            'build-aux/m4/ax_boost_unit_test_framework.m4',
            'build-aux/m4/ax_check_compile_flag.m4',
            'build-aux/m4/ax_check_link_flag.m4',
            'build-aux/m4/ax_check_preproc_flag.m4',
            'build-aux/m4/ax_cxx_compile_stdcxx.m4',
            'build-aux/m4/ax_gcc_func_attribute.m4',
            'build-aux/m4/ax_pthread.m4',
            'build-aux/m4/l_atomic.m4',
            'src/qt/bitcoinstrings.cpp',
            'src/chainparamsseeds.h',
            'src/tinyformat.h',
            'qa/rpc-tests/test_framework/bignum.py',
            'contrib/devtools/clang-format-diff.py',
            'qa/rpc-tests/test_framework/authproxy.py',
            'qa/rpc-tests/test_framework/key.py',
        ],
    },
    'other_copyright_occurrences_expected': {
    'description' : "Files where it is expected to have an occurence of the sequence of characters 'Copyright', 'COPRIGHT', or 'copyright' in the file outside of the MIT Licence copyright header. This list helps to ensures we are keeping close track where there may be external considerations for licence and copyright. Expressed as a list of fnmatch expressions.",
    'fnmatches': [
        'contrib/devtools/gen-manpages.sh',
        'share/qt/extract_strings_qt.py',
        'src/Makefile.qt.include',
        'src/clientversion.h',
        'src/init.cpp',
        'src/qt/bitcoinstrings.cpp',
        'src/qt/splashscreen.cpp',
        'src/util.cpp',
        'src/util.h',
        'src/tinyformat.h',
        'contrib/devtools/clang-format-diff.py',
        'qa/rpc-tests/test_framework/authproxy.py',
        'qa/rpc-tests/test_framework/key.py',
        'contrib/devtools/git-subtree-check.sh',
        'build-aux/m4/l_atomic.m4',
        'build-aux/m4/ax_boost_base.m4',
        'build-aux/m4/ax_boost_chrono.m4',
        'build-aux/m4/ax_boost_filesystem.m4',
        'build-aux/m4/ax_boost_program_options.m4',
        'build-aux/m4/ax_boost_system.m4',
        'build-aux/m4/ax_boost_thread.m4',
        'build-aux/m4/ax_boost_unit_test_framework.m4',
        'build-aux/m4/ax_check_compile_flag.m4',
        'build-aux/m4/ax_check_link_flag.m4',
        'build-aux/m4/ax_check_preproc_flag.m4',
        'build-aux/m4/ax_cxx_compile_stdcxx.m4',
        'build-aux/m4/ax_gcc_func_attribute.m4',
        'build-aux/m4/ax_pthread.m4',
    ],
    }
}

print(json.dumps(REPO_INFO))
