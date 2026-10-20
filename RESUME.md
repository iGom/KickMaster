# Resume: KickMaster NTSC-U

Current milestone: **Stage 01B control-flow/input foundation complete**.
Stage 00 complete; stage00A reference baseline established (eight external map images still unread).
Stage01A and 01B are bounded architecture milestones. Comprehensive game reconstruction is not complete.

## Exact input

- Original: `KickMaster (USA)(1).nes`, 262160 bytes.
- SHA-256: `00ad4a0c6612319bb9f918ca36d6e93b4e5d996716c0570a3ec92bd60533881b`.
- Original attachment Library identity: `libfile_2cc3d8953cd4819194df7416ad5fa8bd`.
- Specification attachment identity: `libfile_ba372c00278c81918250e7f66698913c`; preserved as project_specification.md.
- ROMs are excluded from every checkpoint. Recover the same original attachment after reset;
  request it again only if unavailable. Never fetch another dump or normalize the header.
- NES 2.0, mapper4/submapper0, NTSC, 128 KiB PRG + 128 KiB CHR; no trainer/battery/declared cart RAM.

## Checkpoints and persistence

This snapshot: `kickmaster-ntscu-checkpoint-stage01B.zip`.
Its final SHA-256 and post-upload readback result are in the external stage01B report and receipts.
A ZIP cannot contain its own final hash or a future upload result.

Previous checkpoints were saved, read back and verified:

| Stage | SHA-256 | Library identity |
|---|---|---|
| 00 | 6c3b48030b66ae25e6fad9b21ca7c42904b1448a4c70d50d077df2ff45678e9f | libfile_9936c2d5304c8191af74afd619d8ec84 |
| 00A | 88779ce28f16092345a6d87a084855b6b96731d8f75471a2228cfc6e1a82debf | libfile_a4d0d65a40b08191a53925e0b1ae05f0 |
| 01A | d4cf1e4e2e0f80f30e88545d574d5f57107498eb8654037f21e16e160a6d2c3a | libfile_cedece9827ac81919e818448c976beb2 |

Do not delete or overwrite these archives. Prior persistence receipts are in manifests/.
The stage01A archive was verified again when starting stage01B. The existing workspace remained available.

## Read first and reuse

- reports/subsystems/MAIN_LOOP_INPUT_STATE.md: current detailed findings and limits, Polish.
- reports/subsystems/BOOT_MMC3_INTERRUPTS.md: stage01A hardware foundation.
- reports/stages/SESSION_REPORT.md: current session summary; earlier report retained as SESSION_REPORT_stage01A.md.
- manifests/rom_identity.json: input/component hashes, header, published payload CRC match.
- analysis/reviewed_ranges.csv: 68 code ranges + 11 data ranges; 3278+166=3444 bytes.
- analysis/reviewed_instructions.csv: 1463 reviewed instructions with exact bytes and physical addresses.
- analysis/service_jump_tables.csv: 88 entries in PRG0E/07/08/09.
- analysis/main_loop_phases.csv: 34 calls in four unrolled phases.
- analysis/scene_index_routes.csv: 32 next/restart/continue rows; no stage-name assignments.
- analysis/cpu_experiments.json and cpu_trace.csv: preserved stage01A, 57 passing cases.
- analysis/cpu_stage01B.json, cpu_stage01B_vectors.csv and cpu_stage01B_trace.csv:
  18 passing groups, 2295 vectors, 14033 selected trace rows. Stubs are explicitly listed.
- analysis/rebuild_verification.json: complete byte-identical mixed assembly/incbin build.
- analysis/dataset_audit.json: range, address, source and integration consistency checks.
- maps/ram/ram_map.csv: 56 local roles. analysis/symbols.csv: 135 total symbols.
- maps/rom/classification.csv: 116 contiguous file ranges covering all 262160 bytes.
- research/: 51 external reference claims, 29 experiment plans, 5 untested passwords, source gaps/discrepancies.
- MesenCE/: 135 MLB rows, syntax checked; native import NOT TESTED.
- ghidra/: portable CSVs; bank07/08/09 bases now A000 for reviewed R7 contexts. No native project/import claim.
- disassembly/: mixed sources for all banks; full CHR and unknown PRG remain incbin.
- tools/: vendored py65 and Linux x86_64 ca65/ld65/da65 plus license/provenance.

Historical candidate data are separate from manual coverage. fixed_window_candidates.csv has 2924
stage01A candidates / 6248 bytes; some statuses were updated as ranges were reviewed.
unresolved.csv is that old traversal's 34 stop records, NOT a current global unresolved total.
New bank-context gaps are in stage01B_static_summary.json and cross_references.csv.

## Established local findings

- RESET/NMI/IRQ = PRG0F:F010/F0BB/F7B1; reset maps R6=04/R7=05, mode0.
- Mapper write D6C3 retries if interrupt epoch A6 changes; far-call F4CA saves/restores bank tags.
- D90C waits for 95=0, sets 95=1, temporarily maps audio banks 00/01, restores mappings and polls input.
  NMI F116 writes zero to 95 under documented 96=0/1 conditions. RAM symbol renamed FrameNmiHandshake.
- D977 strobes 4016 and reads eight bits; D0 OR D1 accepted. Masks A/B/Select/Start/U/D/L/R=80/40/20/10/08/04/02/01.
- Held 20 = sample1 AND sample2; pressed 1F = held AND NOT old held. 21 stores A history; 0713/0714 older held values.
- 97 is updated every wait-loop iteration and by D9CB using X. Full RNG roles remain unproved.
- D046 is a four-phase unrolled loop; D90C appears once per phase. Mixer calls occur in phases 1/3.
- 9A indexes three 32-byte route tables D23F/D25F/D27F, not the four loop phases.
- CE bit7 selects counter-decrement path; D3 bit7 gates Start. 030E=0 enters a two-choice menu.
  030E is a candidate attempts/lives counter, not gameplay-validated yet.
- Start flow D3C4 saves/restores palette/CHR and discards a return word before JMP D046.
- Counter-zero menu choice0 routes D19A; nonzero eventually JMP(FFFC), reaching F010.
- FF successor under index1B increments 030C unless already03; normal 0..3 saturates, arbitrary invalid values do not.
- E2A3 handles palette handshake 06EE=FF; E2E2 handles odd-phase scroll adjustment.

## Setup and commands

Python 3.12.14, vendored py65 1.2.0, ca65/ld65 V2.19 Git 8d86ca7.
Bundled binaries are Linux x86_64; install cc65 on PATH on Windows. build.py prefers PATH tools.
Original ROM path is the sole build input outside the checkpoint.

After verifying and unpacking the latest checkpoint, reuse saved analysis. A normal build does not regenerate sources:

```sh
python3 scripts/checkpoint.py --verify /path/to/kickmaster-ntscu-checkpoint-stage01B.zip
python3 scripts/build.py /path/to/original.nes
```

Only when a concrete change needs validation:

```sh
python3 scripts/cpu_stage01b.py /path/to/original.nes
python3 scripts/audit_project.py /path/to/original.nes
```

Intentional regeneration sequence:

```sh
python3 scripts/architecture_stage01b.py /path/to/original.nes
python3 scripts/export_indexes.py
python3 scripts/prepare_sources.py /path/to/original.nes
python3 scripts/build.py /path/to/original.nes
```

architecture_stage01b.py retains old A-series rows and replaces its B-series rows. The old architecture.py
recreates stage01A only; if deliberately used, apply stage01b afterward. prepare_sources.py regenerates
assembly from current reviewed CSVs and can overwrite manual assembly edits. Do not run it casually.

## Next concrete work

1. Follow producers/consumers of CE, D3 and 03B9; establish death/player state and bank contracts.
2. Analyze PRG07:A0DB/A0FA/A119/B022, PRG08:ABC5/AB19/B04C and PRG09:BE90 under propagated R6/R7.
3. Independently establish HP/MP/EXP roles. FDE0 copying was observed but HP meaning was not imported from notes.
4. Map 32 scene indices to headers, collision/spawns and stage names; resolve non-chain indices 02/03/0F.
5. Confirm native MesenCE/Ghidra imports and obtain actual gameplay/NMI/IRQ observations.
6. Preserve a distinct verified next checkpoint; test ZIP/manifest/extraction, upload and readback.

Still unresolved: full player/magic/pickup/RNG systems, map formats and geometry, enemies/bosses, passwords,
complete audio/graphics reconstruction, full-cycle bank preservation, exact timing and the blocked map images.
