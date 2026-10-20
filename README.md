# KickMaster NTSC-U: independent reverse engineering

This project analyzes only the supplied ROM identified in `manifests/rom_identity.json`.
The original ROM is not included in checkpoints. Its separate attachment identity is in RESUME.md;
recover that exact file after a reset, or supply it again if the attachment is unavailable.
The project specification is preserved in `project_specification.md`.

Start with `RESUME.md`, then `reports/stages/SESSION_REPORT.md` and `reports/subsystems/PROGRESSION_PICKUPS_MAGIC.md`.

Current snapshot: Stage 00 complete; Stage 00A reference baseline established (map images blocked);
Stages 01A/01B architecture, 02A player/scene foundation and 02B progression/pickups/healing complete as bounded milestones.
Comprehensive reverse engineering is **not** complete. 134 reviewed code ranges, 54 data ranges, 101 RAM entries.
Stage02B adds 16 CPU groups/52382 vectors with no callee stubs; prior 01A/01B/02A results remain preserved.
The input-dependent ca65 scaffold matches every original byte; 8558 PRG bytes have reviewed local semantics.
Tables cover 32 scene configurations, 192 scene pointers, 116 player-state pairs, eight progression levels,
24 collectible pairs, 13 selected effects and six score thresholds. Unknown handlers remain explicitly unreviewed.

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
python3 scripts/cpu_stage02b.py "/path/to/KickMaster (USA)(1).nes"
python3 scripts/build.py "/path/to/KickMaster (USA)(1).nes"
python3 scripts/checkpoint.py --verify /path/to/checkpoint.zip
```

The checkpoint excludes input ROMs, local rebuilds and previous checkpoint ZIPs. All included files are
covered by `manifests/SHA256SUMS`, except that manifest itself (to avoid self-reference).
Archive hashes and post-upload readback receipts live alongside the ZIP, not inside the file being hashed.

Reuse saved CSV/JSON reports instead of rerunning completed analysis. `prepare_sources.py` intentionally
regenerates the assembly scaffold; do not use it as a build command after edits.
MLB syntax was checked against source, but actual MesenCE/Ghidra imports are untested.
In banks.csv, `payload_offset` is relative to `type` (PRG or CHR), not the combined file.
