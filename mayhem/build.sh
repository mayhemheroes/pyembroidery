#!/usr/bin/env bash
#
# pyembroidery/mayhem/build.sh — compile the ELF launcher shims for the Atheris fuzz harness and
# the unittest test runner. pyembroidery (EmbroidePy/pyembroidery) is a PURE-PYTHON package with
# NO runtime deps; Atheris and pyembroidery itself are installed into the image system Python by
# the Dockerfile (needs network + root). Mayhem requires each target `cmd:` to be an ELF, not a
# `.py`, so we compile a tiny C shim per Python entry point that exec()s `python3 <script>` (see
# mayhem/launcher.c). This script only compiles the shims — it needs neither network nor root, so
# its offline PATCH-tier re-run (as the non-root `mayhem` user) stays idempotent and air-gapped
# (clang only).
set -euo pipefail

# clang rejects SOURCE_DATE_EPOCH= (empty) — must be unset or a valid integer.
[ -n "${SOURCE_DATE_EPOCH:-}" ] || unset SOURCE_DATE_EPOCH

SRC="${SRC:-/mayhem}"
cd "$SRC"

: "${CC:=clang}"

# $DEBUG_FLAGS threads DWARF < 4 debug info onto the shims (SPEC §6.2 item 10): clang-19 plain `-g`
# emits DWARF-5, which Mayhem triage can not read, so force DWARF-3 explicitly.
: "${DEBUG_FLAGS:=-gdwarf-3}"

# The base exports $SANITIZER_FLAGS (ASan+UBSan, halting) for projects with compiled code;
# pyembroidery has none, and the shims are pure exec() wrappers (instrumenting them would only add
# ASan noise on the wrapper, never on the fuzzed Python). The real fuzzed code runs under
# Atheris/libFuzzer at runtime. Referenced here for parity / so an override is visible.
echo "SANITIZER_FLAGS=${SANITIZER_FLAGS:-<unset>} (pure-Python project; not applied to the exec shims)"
echo "DEBUG_FLAGS=$DEBUG_FLAGS"

build_launcher() {
  local out="$1" script="$2"
  echo "--- compiling launcher /mayhem/$out -> $script ---"
  # Dynamically linked (default) so the verify-repo sabotage oracle LD_PRELOAD can reach it.
  "$CC" $DEBUG_FLAGS -O1 -DPY_SCRIPT="\"$script\"" -o "/mayhem/$out" mayhem/launcher.c
  chmod +x "/mayhem/$out"
}

# Fuzz target: the preserved+repaired Atheris harness (pyembroidery binary-format stream readers).
build_launcher fuzz-reader /mayhem/mayhem/fuzz_reader.py
# Test oracle runner: runs the real unittest suite (driven by mayhem/test.sh through this ELF so
# the sabotage check can neuter it).
build_launcher pyembroidery-tests /mayhem/mayhem/run_tests.py

echo "build.sh complete:"
ls -la /mayhem/fuzz-reader /mayhem/pyembroidery-tests
