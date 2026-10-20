# Resume: KickMaster NTSC-U

Current milestone: **Stage 02A player/scene foundation complete**, 2026-10-20.
Stages 00, 00A, 01A, 01B retained. Comprehensive reconstruction is incomplete.
Continue in Polish. In prose use `$` for addresses, not numeric values; CSV retains explicit 0x notation.
Do not use separate user reverse-engineering notes as discoveries. Work independently from this ROM.

## Exact input

- Original: `KickMaster (USA)(1).nes`, 262160 bytes.
- SHA-256: `00ad4a0c6612319bb9f918ca36d6e93b4e5d996716c0570a3ec92bd60533881b`.
- Original attachment identity: `libfile_2cc3d8953cd4819194df7416ad5fa8bd`.
- Specification attachment: `libfile_ba372c00278c81918250e7f66698913c`; copy in project_specification.md.
- Original local path: `/workspace/scratch/073d0612ec00/upload/KickMaster (USA)(1).nes`.
- Project: `/workspace/scratch/073d0612ec00/kickmaster-ntscu-re`.
- NES 2.0, mapper 4/submapper 0, NTSC, 128 KiB PRG +128 KiB CHR; no trainer/battery/declared cart RAM.
- Recover this exact attachment after reset; request again only if unavailable. Never fetch another dump
  or normalize the header. Original and rebuilt ROMs are excluded from checkpoints.

## Checkpoints

This snapshot: `kickmaster-ntscu-checkpoint-stage02A.zip`.
Its final hash and save/readback identifiers live in the external stage02A report and receipts;
an archive cannot contain its own final hash or future upload result.

| Stage | SHA-256 | Saved identity |
|---|---|---|
|00|6c3b48030b66ae25e6fad9b21ca7c42904b1448a4c70d50d077df2ff45678e9f|libfile_9936c2d5304c8191af74afd619d8ec84|
|00A|88779ce28f16092345a6d87a084855b6b96731d8f75471a2228cfc6e1a82debf|libfile_a4d0d65a40b08191a53925e0b1ae05f0|
|01A|d4cf1e4e2e0f80f30e88545d574d5f57107498eb8654037f21e16e160a6d2c3a|libfile_cedece9827ac81919e818448c976beb2|
|01B|a0c1d35ed1d82a0a12db9ff25d4f625ffad5382f535908b3fbfc56d03847992d|libfile_eab08812e5048191af0b39db86eb0810|

Previous snapshots were saved/read back/verified. Never overwrite/delete them. Receipts are in manifests/.
Stage01B was verified at the start of 02A; its 145-file manifest and extraction passed, workspace intact.

## Read first, then reuse

- reports/stages/SESSION_REPORT.md and reports/subsystems/PLAYER_SCENE_FOUNDATIONS.md: latest Polish reports.
- reports/subsystems/MAIN_LOOP_INPUT_STATE.md and BOOT_MMC3_INTERRUPTS.md: earlier foundations.
- Earlier session reports: SESSION_REPORT_stage01A.md and SESSION_REPORT_stage01B.md.
- analysis/reviewed_ranges.csv: 101 code +45 data ranges; 5020+1809=6829 PRG bytes, 5.210113525390625%.
- analysis/reviewed_instructions.csv: 2355 instructions. New C01..C67 adds 892 instructions/3385 bytes.
- maps/ram/ram_map.csv: 80 local roles; analysis/symbols.csv: 226 symbols; file classification: 198 ranges.
- analysis/scene_configurations.csv: 32 rows; scene_configuration_pointers.csv: 192 source/target mappings.
- analysis/player_state_dispatch.csv: 111 normal +5 alternate pairs; 22/3 unique targets respectively.
- analysis/indirect_dispatch_tables.csv: 138 table edges; reviewed_call_graph.dot: 325 deduplicated edges.
- analysis/scene_index_routes.csv: 32 next/restart/continue mappings; stage names still unresolved.
- analysis/cpu_stage02A.json and *_vectors.csv, *_trace.csv: 18 groups/10137 vectors/5921 trace rows, all PASS.
- Preserved stage01A: 57 cases; stage01B: 18 groups/2295 vectors/14033 trace rows; not rerun in 02A.
- analysis/rebuild_verification.json: entire 262160-byte image matches; 6845 explicit bytes including header,
  255315 input-incbin bytes. A matching input-dependent scaffold does not establish full semantics.
- MesenCE: 226 MLB rows, source-backed syntax validation; actual import NOT TESTED.
- ghidra: bank-aware CSVs; PRG07/08/09 at A000 for reviewed R7 contexts. No native project/import claim.
- research: 51 external claims, 29 experiment plans, 5 untested passwords; eight map images unread.

Historical candidate decode remains 2924 instructions/6248 bytes. Statuses update only at reviewed
instruction starts; candidates never count as semantic coverage. analysis/unresolved.csv is the old01A
traversal's 34 stops, not a global count. See stage01B/02A_static_summary and cross_references for new gaps.

## Established findings

Hardware/loop retained:

- RESET/NMI/IRQ=PRG0F:F010/F0BB/F7B1. Reset maps R6=04/R7=05, mode0.
- Mapper D6C3 retries when interrupt epoch A6 changes. Far-call F4CA saves/restores bank tags.
- D90C waits for 95=0, sets1, services audio in banks00/01 and polls controller twice.
- Held20=sample1 AND sample2; pressed1F=held AND NOT old-held. Masks80/40/20/10/08/04/02/01=A/B/Select/Start/U/D/L/R.
- 97 changes in the wait loop and via D9CB/X; complete RNG roles remain unresolved.
- D046 has four phases, one handshake each. 9A is a scene index, not a loop-phase counter.
- CE80 drives counter decrement; D3 bit80 blocks Start. Counter-zero choice0 continues via D19A,
  other choice eventually JMP(FFFC). FF route at index1B increments030C unless equal03.

New 02A:

- PRG07:A4E9 initializes camera/player; A537 loads 32 scene configurations. 03B9=B262[9A].
- A5AB uses 17 special-layout rows indexed04E2. Encoded bank bit7 increments camera X page,
  then R6 receives low 7 bits. Later A990/A6FE semantics remain unreviewed.
- Pointers in8000..9FFF use R6; A000..BFFF use R7=07. Scene 17 has R6=03 but
  B9/BA=07:B59A and palette=07:B563. Never assign all scene pointers to R6.
- CameraX=A7/A8, CameraY=A9/AA; PlayerY=C9/CA, PlayerX=CB/CC, all little-endian pixel values.
- F78B normalizes linearY into 240-line pages for high byte 00..0F (4096 tested inputs).
  AAB6 multiplies by F0 only in domain 00..80; 81..FF yield 0.
- DB direction bits2..1: down/up/right/left; bit01 dispatch enable, bit08 autostep, bit80 scroll-work gate.
- PRG08:AB19 clears transient D3 bit80; F8 bit20 branches to scene advance. Otherwise retains only CE bit01.
- ACF7 uses CE bit01 to choose table family. CD>>1 chooses CHR; CD&FE chooses metasprite/handler;
  CD bit0 is facing. Right wins over Left in three-sample input history.
- CurrentHP=06B9, display copy=06BA, bar capacity=06BB. 16 raw units/full cell, 2 raw units/partial step.
  Copy decreases immediately or rises 1 per B04B call. FDE0=40..B0 by10; D3&07 used on restore.
  Full healing caps and level-up/EXP producers remain unreviewed; do not import meanings from notes.
- DDD9 ignores damage if D2 or 01A4 nonzero. Damage>HP starts death; equality yields 0 and hurt.
  Hurt sets D2=3C, D3bit20, CF0 and direction bit10 from incoming carry. Zero damage also triggers hurt locally.
- Fatal damage selects BA/BB. Five 15-update animation states lead CA/CB, then 15 more updates set CE80.
  Both facings tested through 90 complete player/draw updates, then actual D39F decrements 030E from 03 to 02
  and reaches D17A with A=01. Only final E154 fade is stubbed, not death or sprite code.
- Fall state C4/C5 adds 4 to Y; low-byte relative Y>=F0 sets CE80, not a full 16-bit distance test.
- DB02 terrain bit40/80 priority returns 3/0. Otherwise bit10 requests damage 9A+04 except 06BD=08/0593 nonzero.
  Sample helpers were stubbed in classification tests; complete terrain decoding remains open.
- B022 normal HUD phases 1..5 target B165,F681,B04B,B104,B0B0; negative A1 skips. NMI/transfer contract open.

## Reproduce only when needed

Python3.12.14, vendored py65 1.2.0, Linux x86_64 ca65/ld65 V2.19 Git8d86ca7. Build prefers PATH tools,
then bundled executables. Original ROM is the only external input. Keep project basename.

```sh
python3 scripts/checkpoint.py --verify /path/to/kickmaster-ntscu-checkpoint-stage02A.zip
python3 scripts/build.py /path/to/original.nes
```

For a concrete validation need:

```sh
python3 scripts/cpu_stage02a.py /path/to/original.nes
python3 scripts/audit_project.py /path/to/original.nes
```

Intentional regeneration only (can overwrite manual source edits):

```sh
python3 scripts/architecture_stage02a.py /path/to/original.nes
python3 scripts/export_indexes.py
python3 scripts/prepare_sources.py /path/to/original.nes
python3 scripts/build.py /path/to/original.nes
```

architecture_stage02a replaces C-series and retains A/B. architecture_stage01b replaces B and keeps others,
but its summaries/table exports are historical; rerun 02a afterward if deliberately regenerating.
The original architecture.py recreates 01A only: do not casually run it on a later dataset.

## Next concrete work

1. Player movement/attack handlers at PRG08:B81D,B8B5 etc; BCEF physics and collision sample paths.
2. Derive all HP-healing/level writes and producers of D3low3, then MP/EXP and pickups independently.
3. Reconstruct scene geometry/collision; map 32 indices to eight named stages, including 02/03/0F.
4. Finish PRG08:ABC5 split-scroll, PRG09:BE90 objects, A1/NMI contract and bank preservation.
5. Native MesenCE/Ghidra import, actual gameplay, full NMI/IRQ timing and external map images.
6. Preserve a distinct next checkpoint; verify ZIP/manifest/extraction, clean rebuild, save and readback.

Still open: full magic/pickup/RNG systems, attacks, enemies/bosses, passwords, complete graphics/audio.
Do not report 90 CPU updates as measured wall-clock duration or 111 state pairs as 111 independent techniques.
