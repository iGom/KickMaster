# Reproducible toolchain

Bundled: py65 1.2.0 (Python package and distribution/license metadata; unused tests excluded), and
Linux x86_64 ca65/ld65/da65 binaries built from cc65 commit
`8d86ca7e7ed15300cc4bfaba61a40a3d00f3114d` using `make -j2 ca65 ld65 da65`.
The cc65 license is included. Runtime/system versions are in `manifests/analysis_toolchain.json`.

On Windows, put ca65 and ld65 on PATH; `scripts/build.py` selects those ahead of bundled Linux binaries.
The analysis and CPU experiment scripts use the bundled pure-Python py65 package.
No Ghidra or full-system NES emulator is bundled or required for the completed local checks.

To rebuild cc65 from the pinned source:

```sh
git clone https://github.com/cc65/cc65.git cc65
git -C cc65 checkout 8d86ca7e7ed15300cc4bfaba61a40a3d00f3114d
make -C cc65 -j2 ca65 ld65 da65
```

Do not use the presence of these tools as evidence of a gameplay experiment. Read each verification receipt.
