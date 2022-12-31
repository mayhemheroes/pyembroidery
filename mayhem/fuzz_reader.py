#! /usr/bin/env python3
import atheris
import sys
import fuzz_helpers

with atheris.instrument_imports(include=["pyembroidery"]):
    import pyembroidery

supported_file_format_readers = [
    pyembroidery.read_pec, pyembroidery.read_dst, pyembroidery.read_exp,
    pyembroidery.read_jef, pyembroidery.read_vp3, pyembroidery.read_u01,
    pyembroidery.read_pec, pyembroidery.read_xxx, pyembroidery.read_gcode
]

def TestOneInput(data):
    fdp = fuzz_helpers.EnhancedFuzzedDataProvider(data)
    try:
        # Pick a file-format reader
        reader = fdp.PickValueInList(supported_file_format_readers)
        with fdp.ConsumeMemoryFile(all_data=True) as f:
            reader(f)
    except (TypeError, AttributeError, ValueError):
        # Raised too often
        return -1
    except Exception:
        return -1


def main():
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
