# KickMaster NTSC-U: independent reverse engineering

This project analyzes only the supplied ROM identified in `manifests/rom_identity.json`.
The original ROM is not included in checkpoints. Its separate attachment identity is in RESUME.md;
recover that exact file after a reset, or supply it again if the attachment is unavailable.
The project specification is preserved in `project_specification.md`.

Start with `RESUME.md`, then `reports/stages/SESSION_REPORT.md` and `reports/subsystems/PLAYER_SCENE_FOUNDATIONS.md`.

Current snapshot: Stage 00 complete; Stage 00A reference baseline established (map images blocked);
Stages 01A/01B architecture and 02A player/scene foundation complete as bounded milestones.
Comprehensive reverse engineering is **not** complete. 101 reviewed code ranges, 45 data ranges, 80 RAM entries.
Stage02A adds 18 CPU groups/10137 vectors; earlier 57 cases and 18 groups/2295 vectors remain preserved.
The input-dependent ca65 scaffold matches every original byte; 6829 PRG bytes have reviewed local semantics.
New tables cover 32 scene configurations, 192 bank-qualified pointers and 111 normal plus 5 alternate state pairs.

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
python3 scripts/cpu_stage02a.py "/path/to/KickMaster (USA)(1).nes"
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
