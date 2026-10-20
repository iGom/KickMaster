# KickMaster NTSC-U: independent reverse engineering

This project analyzes only the supplied ROM identified in `manifests/rom_identity.json`.
The original ROM is not included in checkpoints. Keep the attached original and supply it again after a reset.
The project specification is preserved in `project_specification.md`.

Start with `RESUME.md`, then `reports/stages/STAGE00_BASELINE.md`.

Evidence classes: **FILE** (direct bytes/hashes), **STATIC** (decoded instructions and checked control flow),
**DOCUMENTED** (external source only), **CPU_TEST** (isolated execution with stated stubs),
**EMULATOR** (full NES runtime observation), **HYPOTHESIS**, **UNRESOLVED**.
CPU tests are not NES emulator validation. Automated reachability is not semantic understanding.
No prior user reverse-engineering notes were consulted or imported.

All offsets and CPU addresses in datasets use explicit `0x` hexadecimal notation. Bank IDs are hexadecimal.
Human-readable bank-qualified notation is `PRG0F:$F010`. Values in prose are identified as hex or decimal.
Address intervals are half-open unless a table explicitly states inclusive limits.

```sh
python3 scripts/baseline.py "/path/to/KickMaster (USA)(1).nes"
python3 -m unittest discover -s tests -v
python3 scripts/checkpoint.py --verify /path/to/checkpoint.zip
```

The checkpoint excludes input ROMs, local rebuilds and previous checkpoint ZIPs. All included files are
covered by `manifests/SHA256SUMS`, except that manifest itself (to avoid self-reference).
Archive hashes and post-upload readback receipts live alongside the ZIP, not inside the file being hashed.
