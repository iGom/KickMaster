# KickMaster NTSC-U: independent reverse engineering

This project analyzes only the supplied ROM identified in `manifests/rom_identity.json`.
The original ROM is not included in checkpoints. Its separate attachment identity is in RESUME.md;
recover that exact file after a reset, or supply it again if the attachment is unavailable.
The project specification is preserved in `project_specification.md`.

Start with `RESUME.md`, `reports/stages/SESSION_REPORT.md` and
`reports/subsystems/ENEMY_AI_DEATH_AND_REWARDS.md`.

Current snapshot: Stage02G kind00 AI, ordinary drops and special-death object lifecycles.
Prior stages00..02F are retained;02F was freshly verified at resume without CPU/build reruns.
Comprehensive reverse engineering is **not** complete:274 code ranges,130 data ranges,139 RAM roles.
Stage02G adds15 CPU groups/4050 saved observations with11437 trace rows, no ROM patches or callee stubs.
Tests cover explicitly scoped AI/death paths, not full enemy terrain or all other AI bodies.
The input-dependent ca65 scaffold matches all262160 bytes;19838 PRG bytes have reviewed local semantics.
Portable exports contain543 symbols and383 indirect table edges. Native NES and Ghidra/MesenCE imports
remain NOT_TESTED. Full AI, geometry and32-scene to8-sector mapping remain open.
Original guide/maps are unchanged in `research/originals/`; earlier map-access failures are historical.
`PROJECT_UPDATES.md` records later source-preservation/checkpoint instructions. Historical reports remain.

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

Reuse saved CSV/JSON reports instead of rerunning completed analysis. Run `cpu_stage02g.py` only for a
concrete validation need; its recorded results are already included. `prepare_sources.py` intentionally
regenerates the assembly scaffold; do not use it as a build command after edits.
MLB syntax was checked against source, but actual MesenCE/Ghidra imports are untested.
In banks.csv, `payload_offset` is relative to `type` (PRG or CHR), not the combined file.
