#! /usr/bin/env python3
# Atheris harness for pyembroidery: fuzzes the binary embroidery-format stream readers
# (read_pec, read_dst, read_exp, read_jef, read_vp3, read_u01, read_xxx, read_gcode).
# Preserved + repaired from the original Mayhem Heroes integration (target reader-fuzz):
# the old harness called fdp.PickValueInList(...) but the shipped fuzz_helpers.py never
# defined that method, so every input raised AttributeError and no reader was ever run.
# fuzz_helpers.py now defines PickValueInList, so the readers are actually exercised.
#
# Runs under Atheris/libFuzzer; the /mayhem/fuzz-reader ELF launcher exec()s
# `python3 <this>` so Mayhem has an ELF entry point (see mayhem/launcher.c).
import os
import sys
from struct import error as struct_error

import atheris

# Make the sibling fuzz_helpers importable regardless of CWD (the launcher exec()s us with an
# absolute path; sys.path[0] is this dir, but be explicit for the fork-mode re-exec children too).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import fuzz_helpers

# Scope instrumentation to the pyembroidery package only (Atheris fork-mode: a bare
# instrument-all balloons startup per fork child; scoping keeps re-exec children fast and
# coverage on-target).
with atheris.instrument_imports(include=['pyembroidery']):
    import pyembroidery

# Binary-format stream readers that accept a file-like object.
supported_file_format_readers = [
    pyembroidery.read_pec, pyembroidery.read_dst, pyembroidery.read_exp,
    pyembroidery.read_jef, pyembroidery.read_vp3, pyembroidery.read_u01,
    pyembroidery.read_xxx, pyembroidery.read_gcode,
]


def TestOneInput(data):
    fdp = fuzz_helpers.EnhancedFuzzedDataProvider(data)
    try:
        reader = fdp.PickValueInList(supported_file_format_readers)
        with fdp.ConsumeMemoryFile(all_data=True) as f:
            reader(f)
    except (TypeError, AttributeError, ValueError, IndexError, KeyError,
            UnicodeDecodeError, struct_error):
        # Legitimate "reject this input" signals from the readers on malformed data, not defects.
        return -1


def main():
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
