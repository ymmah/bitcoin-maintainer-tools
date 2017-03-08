Contents
========
This directory contains regression test scripts for the scripts under `bin`.

Tests
============
There should be a `test_<script>.py` file corresponding for every script in the `bin` directory. Each should cover the basic invocation options of the script to protect against breakage. They should also all be called from TravisCI.


test\_all.py
============

This script is the exception, since it should include an invocation of every other test script. It runs in serial, which means it takes a very long time to finish, but it is useful for running the full set of tests on a local workstation before pushing to TravisCI.
