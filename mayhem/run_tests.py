#!/usr/bin/python3
"""run_tests.py — RUN pyembroidery's own unittest suite and print a parseable summary.

Invoked via the `/mayhem/pyembroidery-tests` ELF launcher (NOT directly), so the verify-repo
sabotage oracle can neuter the launcher and prove the test oracle is behavioral.

pyembroidery ships its tests as `test/test_*.py` unittest cases (upstream CI runs
`python -m unittest discover test`). They are known-answer / round-trip cases asserting EXACT
behaviour: format read/write round-trips (DST/EXP/PEC/JEF/VP3/U01/XXX/TBF/CSV/JSON/GCODE),
matrix math, color/palette decoding, encoder output, catalog and IO error semantics. A no-op /
"exit(0)" / behaviour-altering patch to pyembroidery cannot pass it.

It runs the real suite, collects the unittest result counts, and prints one line:

    RUNTESTS tests=<n> passed=<p> failed=<f> skipped=<s>

Exit 0 iff failed == 0. mayhem/test.sh parses that line into a CTRF report.
"""
from __future__ import annotations

import os
import sys
import unittest

SRC = os.environ.get("SRC", "/mayhem")
TESTS_DIR = "test"


def main() -> int:
    os.chdir(SRC)
    # Put the repo root on sys.path so the test modules can import the `test` package
    # (they do "from test.pattern_for_tests import *"). The launcher exec()s us as
    # "python3 mayhem/run_tests.py", so sys.path[0] is mayhem/, not the repo root.
    if SRC not in sys.path:
        sys.path.insert(0, SRC)
    loader = unittest.TestLoader()
    suite = loader.discover(TESTS_DIR, top_level_dir=SRC)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    tests = result.testsRun
    failed = len(result.failures) + len(result.errors)
    skipped = len(result.skipped)
    passed = tests - failed - skipped

    print(f"RUNTESTS tests={tests} passed={passed} failed={failed} skipped={skipped}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
