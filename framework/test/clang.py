#!/usr/bin/env python3
# Copyright (c) 2017 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import os
import subprocess

from framework.clang.find import ClangFind, CLANG_BINARIES
from framework.file.io import write_file
from framework.path.path import Path

CLANG_DIR = "clang-test-files"
TEST_STYLE_FILE_NAME = ".alternate-clang-format"
TEST_STYLE_FILE_CONTENT = """
Language:        Cpp
AccessModifierOffset: -4
AlignEscapedNewlinesLeft: true
AlignTrailingComments: true
AllowAllParametersOfDeclarationOnNextLine: false
AllowShortBlocksOnASingleLine: false
AllowShortFunctionsOnASingleLine: All
AllowShortIfStatementsOnASingleLine: false
AllowShortLoopsOnASingleLine: false
AlwaysBreakBeforeMultilineStrings: false
AlwaysBreakTemplateDeclarations: true
BinPackParameters: false
BreakBeforeBinaryOperators: false
BreakBeforeBraces: Linux
BreakBeforeTernaryOperators: false
BreakConstructorInitializersBeforeComma: false
ColumnLimit:     0
CommentPragmas:  '^ IWYU pragma:'
ConstructorInitializerAllOnOneLineOrOnePerLine: false
ConstructorInitializerIndentWidth: 4
ContinuationIndentWidth: 4
Cpp11BracedListStyle: true
DerivePointerAlignment: false
DisableFormat:   false
ForEachMacros:   [ foreach, Q_FOREACH, BOOST_FOREACH, BOOST_REVERSE_FOREACH ]
IndentCaseLabels: false
IndentFunctionDeclarationAfterType: false
IndentWidth:     4
KeepEmptyLinesAtTheStartOfBlocks: false
NamespaceIndentation: None
ObjCSpaceAfterProperty: false
ObjCSpaceBeforeProtocolList: false
PenaltyBreakBeforeFirstCallParameter: 1
PenaltyBreakComment: 300
PenaltyBreakFirstLessLess: 120
PenaltyBreakString: 1000
PenaltyExcessCharacter: 1000000
PenaltyReturnTypeOnItsOwnLine: 200
PointerAlignment: Left
SpaceBeforeAssignmentOperators: true
SpaceBeforeParens: ControlStatements
SpaceInEmptyParentheses: false
SpacesBeforeTrailingComments: 1
SpacesInAngles:  false
SpacesInContainerLiterals: true
SpacesInCStyleCastParentheses: false
SpacesInParentheses: false
Standard:        Cpp03
TabWidth:        8
UseTab:          Never
"""


def setup_test_style_file(directory):
    clang_dir = os.path.join(directory, CLANG_DIR)
    style_file = os.path.join(clang_dir, TEST_STYLE_FILE_NAME)
    write_file(style_file, TEST_STYLE_FILE_CONTENT)
    return style_file


def setup_test_bin_dir(directory):
    """
    Copies installed clang binaries into a directory for test purposes
    """
    clang_dir = os.path.join(directory, CLANG_DIR)
    if not os.path.exists(str(clang_dir)):
        os.makedirs(str(clang_dir))
    finder = ClangFind()
    src_path = Path(finder.best('scan-build')['path']).containing_directory()
    for binary in CLANG_BINARIES:
        bin_path = os.path.join(src_path, binary)
        if Path(bin_path).exists():
            subprocess.call(['cp', bin_path, clang_dir])
    return clang_dir
