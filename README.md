# KickMaster NTSC-U: independent reverse engineering

This project analyzes only the supplied ROM identified in `manifests/rom_identity.json`.
The original ROM is not included in checkpoints. Its separate attachment identity is in RESUME.md;
recover that exact file after a reset, or supply it again if the attachment is unavailable.
The project specification is preserved in `project_specification.md`.

Start with `RESUME.md`, then `reports/stages/SESSION_REPORT.md` and
`reports/subsystems/PLAYER_CONTROL_JUMP_AND_TERRAIN.md`.

Current snapshot: Stage02E normal player control, jump phases and terrain lookup.
Stages00/00A/01A/01B/02A/02B/02C/02D remain preserved;02D was freshly verified at resume.
Comprehensive reverse engineering is **not** complete.231 code ranges,92 data ranges,133 RAM entries.
Stage02E adds14 CPU groups/11868 cases, no ROM patches or callee stubs. Old suites were not rerun.
The input-dependent ca65 scaffold matches all262160 original bytes;15194 PRG bytes have reviewed local semantics.
Current portable exports contain456 symbols and256 indirect dispatch edges.

New results include normal-state input/attack selectors, jump phases, animation call counts,
cache/ROM terrain contracts and3840 actual scene00 terrain samples. This is not complete level geometry,
full combat or a32-scene to8-sector mapping. Native NES execution and Ghidra/MesenCE imports remain NOT_TESTED.
Original guide/maps are unchanged in `research/originals/`; earlier map-access blocks are historical.
`PROJECT_UPDATES.md` records later source-preservation/checkpoint instructions. Historical reports are retained.

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
