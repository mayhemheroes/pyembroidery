#! /usr/bin/env python3
import atheris
import sys
import fuzz_helpers

with atheris.instrument_imports(include=["pyembroidery"]):
    import pyembroidery

supported_file_suffxes = [
    '.pes', '.dst', '.exp',
    '.jef', '.vp3', '.10o',
    '.100', '.bro', '.dat',
    '.dsb', 'dsz', '.emd',
    '.exy', '.fxy', '.gt',
    '.hus', '.inb', '.jpx',
    '.ksm', '.max', '.mit',
    '.new', '.pcd', '.pcm',
    '.pcq', '.pcs', '.pec',
    '.phb', '.phc', '.sew',
    '.shv', '.stc', '.stx',
    '.tap', '.tbf', '.tbf',
    '.u01', '.xxx', '.zhs',
    '.xzy', '.gcode'
]

def TestOneInput(data):
    fdp = fuzz_helpers.EnhancedFuzzedDataProvider(data)
    try:
        with fdp.ConsumeTemporaryFile(suffix=fdp.PickValueInList(supported_file_suffxes), all_data=True) as file_path:
            # Uses the suffix to determine which reader to use
            pyembroidery.read(file_path)
    except (TypeError, AttributeError, ValueError):
        # Raised too often
        return -1


def main():
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
