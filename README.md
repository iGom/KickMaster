# KickMaster NTSC-U: independent reverse engineering

This project analyzes only the supplied ROM identified in `manifests/rom_identity.json`.
The original ROM is not included in checkpoints. Its separate attachment identity is in RESUME.md;
recover that exact file after a reset, or supply it again if the attachment is unavailable.
The project specification is preserved in `project_specification.md`.

Start with `RESUME.md`, then `reports/stages/SESSION_REPORT.md` and `reports/subsystems/PROJECTILE_COLLISION_AND_ENEMY_HITS.md`.

Current snapshot: Stage 02D projectile/collision and enemy-hit consumers complete as a bounded milestone.
Stages 00/00A/01A/01B/02A/02B/02C remain preserved;02C durability is now closed. The original guide and eight maps supplied by the user
are now available unchanged in `research/originals/`; the earlier map-access block is historical.
Comprehensive reverse engineering is **not** complete. 190 reviewed code ranges, 84 data ranges, 131 RAM entries.
Stage02D adds 16 CPU groups/26832 vectors with no callee stubs; earlier-stage CPU results remain preserved without rerun.
The input-dependent ca65 scaffold matches every original byte; 12945 PRG bytes have reviewed local semantics.
Tables cover 32 scene configurations, 192 scene pointers, 116 player-state pairs, eight progression levels,
24 collectible pairs, 13 selected effects, 12 unlock/menu mappings, 32 acquisition routes, six score thresholds,32 projectile collision profiles
and101 player collision profiles.
Unknown downstream handlers remain explicitly unreviewed. Map geometry has not yet been compared to ROM data.
`PROJECT_UPDATES.md` records the user's later source-preservation and checkpoint instructions.

Evidence classes: **FILE** (direct bytes/hashes), **STATIC** (decoded instructions and checked control flow),
**DOCUMENTED** (external source only), **CPU_TEST** (isolated execution with stated stubs),
**EMULATOR** (full NES runtime observation), **HYPOTHESIS**, **UNRESOLVED**.
CPU tests are not NES emulator validation. Automated reachability is not semantic understanding.
No prior user reverse-engineering notes were consulted or imported.

All offsets and CPU addresses in datasets use explicit `0x` hexadecimal notation. Bank IDs are hexadecimal.
Human-readable bank-qualified notation is `PRG0F:$F010`. Values in prose are identified as hex or decimal.
Address intervals are half-open unless a table explicitly states inclusive limits.

```sh
python3 scripts/build.py "/path/to/KickMaster (USA)(1).nes"
python3 scripts/checkpoint.py --verify /path/to/checkpoint.zip
```

The checkpoint excludes input ROMs, local rebuilds and previous checkpoint ZIPs. All included files are
covered by `manifests/SHA256SUMS`, except that manifest itself (to avoid self-reference).
Archive hashes and post-upload readback receipts live alongside the ZIP, not inside the file being hashed.

Reuse saved CSV/JSON reports instead of rerunning completed analysis. Run `cpu_stage02d.py` only for a
concrete validation need; its recorded results are already included. `prepare_sources.py` intentionally
regenerates the assembly scaffold; do not use it as a build command after edits.
MLB syntax was checked against source, but actual MesenCE/Ghidra imports are untested.
In banks.csv, `payload_offset` is relative to `type` (PRG or CHR), not the combined file.
