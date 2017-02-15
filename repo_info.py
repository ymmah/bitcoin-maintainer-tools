#!/usr/bin/env python3
# Copyright (c) 2017 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

# TODO move this into bitcoin repo.
REPO_INFO = {
    'subtrees': [
        'src/secp256k1/*',
        'src/leveldb/*',
        'src/univalue/*',
        'src/crypto/ctaes/*',
    ],
    'clang_format_style':       'src/.clang-format',
    'clang_format_recommended': '3.9.0',
    'no_copyright_header': [
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
    'other_copyright_occurrences': [
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
