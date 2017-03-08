Contents
========
This directory contains common infrastructure for bitcoin maintainer scripts.

File, Subdirectory and Namspace Convention
==========================================

The subdirectory, file and the class names are meant to follow a pattern that is relatively consistent. This is not a strict requirement in all cases, but consider it guidance for keeping the content layout reasonably modular, organized and intuitive.

To illustrate the convention, the class `GitRepository` is found in `git/repository.py`. The file and the class encapsulate the concept of a git repository and is placed in the `git` subdirectory with other git-related concepts. The `ClangTarball` class is therefore located in `clang/tarball.py` following the same convention.

Please attempt to follow this convention for new code.
