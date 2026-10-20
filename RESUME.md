# Resume: KickMaster NTSC-U

Current milestone: **Stage 01A bounded architecture foundation complete**.
Stage 00 is complete. Stage 00A has a sourced baseline; eight external map images remain unread.
Stages 01B/02 and gameplay reconstruction are next. This is not a finished game disassembly.

## Exact input

- Filename: `KickMaster (USA)(1).nes`; size 262160 bytes.
- SHA-256: `00ad4a0c6612319bb9f918ca36d6e93b4e5d996716c0570a3ec92bd60533881b`.
- Separate original attachment Library ID: `libfile_2cc3d8953cd4819194df7416ad5fa8bd`.
- Specification attachment ID: `libfile_ba372c00278c81918250e7f66698913c`; also preserved as project_specification.md.
- Original/rebuilt ROMs are excluded from checkpoints. Recover the original attachment after a reset;
  request it again only if that attachment cannot be accessed. Never fetch or substitute another dump.
- NES 2.0, mapper 4/submapper 0, 128 KiB PRG + 128 KiB CHR, no trainer/battery/declared cart RAM, NTSC.
- Published PRG/CHR/payload CRC32 match. Do not normalize the header.

## Checkpoints

This snapshot: `kickmaster-ntscu-checkpoint-stage01A.zip`.
Final ZIP hash and post-upload readback are recorded in adjacent external receipts and the separately
saved session report; the ZIP cannot contain its own hash or a future upload result.

Previous checkpoints successfully persisted and read back:

| Snapshot | SHA-256 | Library identity |
|---|---|---|
| stage00 | 6c3b48030b66ae25e6fad9b21ca7c42904b1448a4c70d50d077df2ff45678e9f | libfile_9936c2d5304c8191af74afd619d8ec84 |
| stage00A | 88779ce28f16092345a6d87a084855b6b96731d8f75471a2228cfc6e1a82debf | libfile_a4d0d65a40b08191a53925e0b1ae05f0 |

Never delete or overwrite those archives. Prior persistence receipts are in manifests/.

## Reuse these results

- manifests/rom_identity.json: input/component hashes and header fields.
- research/: 51 cited reference claims, 8 stage links, 29 experiment plans, 5 untested password vectors,
  source-access status and eight discrepancies. No full manual/guide/map images redistributed.
- reports/subsystems/BOOT_MMC3_INTERRUPTS.md: concrete findings and preconditions.
- analysis/reviewed_ranges.csv: 24 code entries and 3 data regions; 925 code + 44 data = 969 reviewed PRG bytes.
- analysis/reviewed_instructions.csv: 431 reviewed instructions. fixed_window_candidates.csv has 2924 candidate
  instructions / 6248 bytes, outside semantic coverage. unresolved.csv has 34 control-flow stop records.
- analysis/cpu_experiments.json and cpu_trace.csv: 57 passing isolated CPU cases / 3595 trace rows.
  They are not NES gameplay or cycle-accurate PPU/APU observations.
- analysis/rebuild_verification.json: complete input-dependent mixed assembly/incbin build match.
- analysis/symbols.csv and maps/ram/ram_map.csv: 62 symbols / 35 local RAM roles.
- maps/rom/classification.csv: exhaustive 52-range partition of the input.
- MesenCE/kickmaster.mlb: source-grammar-checked labels; actual emulator import untested.
- ghidra/: portable symbol/block CSVs and source-inspected header caveat; no native project/import claim.

## Confirmed architecture

NMI=PRG0F:F0BB; RESET=PRG0F:F010; IRQ=PRG0F:F7B1.
RESET establishes mode 0, R6=04/R7=05, fixed banks 0E:C000 and 0F:E000.
It clears RAM except 0100 and 0300-0307. D60C checks marker 68 and loads six defaults on mismatch.
D6C3 retries mapper writes when NMI/IRQ changes A6. A6 is not safely a pure frame counter.
F4CA saves live bank tags, calls through 04EA after mapping 04EC, then restores both PRG windows.
NMI uses page-02 OAM DMA, a 16-pointer PPU dispatcher and conditional IRQ setup. E5/E6 is shared scratch/IRQ state.
PPU transfers temporarily use the stack to stream 27 or 32 bytes. IRQ handlers support multiple PPU splits;
exact scanlines and visual roles have not been observed.

## Setup and commands

Python 3.12.14 was used. py65 1.2.0 is vendored. ca65/ld65 V2.19 Git 8d86ca7 are bundled for Linux x86_64.
On Windows, install cc65 on PATH; scripts select PATH tools first. Ghidra and MesenCE are not installed here.
See tools/README.md and manifests/analysis_toolchain.json for precise setup and provenance.

Verify and extract the latest checkpoint before continuing. Read this RESUME and reuse existing outputs.
Do not rerun finished tracing to recreate files already in the archive.

```sh
python3 scripts/checkpoint.py --verify /path/to/kickmaster-ntscu-checkpoint-stage01A.zip
python3 scripts/build.py /path/to/original.nes
```

When a concrete change requires validation:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/cpu_experiments.py /path/to/original.nes
```

Intentional regeneration only:

```sh
python3 scripts/architecture.py /path/to/original.nes
python3 scripts/export_indexes.py
python3 scripts/prepare_sources.py /path/to/original.nes
```

prepare_sources.py can overwrite manual assembly edits; build.py never regenerates source.
Baseline/research scripts are preserved for reproducibility, not mandatory reexecution.

## Next concrete work

1. Continue PRG0E:CF50 and bank-09 entry points with propagated R6/R7 state; identify game states and main loop.
2. Resolve remaining PPU/IRQ targets and E5/E6 versus DC/DD producers and lifetimes.
3. Identify controller polling and RAM reuse; obtain actual MesenCE traces before gameplay timing claims.
4. Begin independent HP/MP/EXP analysis. Do not import the user's separate notes as discoveries.
5. Test native debugger imports and review blocked sprays map images when accessible.
6. Preserve the next distinct checkpoint; verify ZIP, manifest, extraction, upload and readback.

Unknowns: gameplay encodings/IDs, RNG, drops, spell effects, maps/collision/spawns, passwords, difficulty,
complete audio engine, graphics metadata, and dynamic interrupt timing.
