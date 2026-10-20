# Stage 01A: bounded architecture reconstruction

This milestone establishes an initial static/dynamic foundation. Stage 01 as a whole remains incomplete.

Completed:

- 24 reviewed code entries and 3 reviewed data regions, with full bank/CPU/PRG/file coordinates.
- 35 local RAM roles, separate from unresolved gameplay variables; 62 consistent symbols overall.
- RESET, NMI, IRQ entry/return, mapper retry, three cross-bank stubs, far-call wrapper and PPU stack transfers.
- 16-entry PPU task table, retained defaults, hardware-access index and physical bank tags.
- 2,924 candidate instructions / 6,248 bytes reached by a deliberately limited fixed-window traversal.
  These are candidates; indirect calls, inline data and switchable-bank propagation remain incomplete.
- 57 passing isolated CPU cases and 3,595 instruction trace rows, with hardware stubs explicitly documented.
- ca65/ld65 mixed-source build producing an exact 262,160-byte match and identical per-PRG-bank hashes.
- MLB labels checked against the inspected source grammar; portable Ghidra CSVs; assembler debug symbols.

## Coverage

| Metric | Result | Meaning |
|---|---:|---|
| Full binary output match | 262160 / 262160 bytes | Requires the original ROM for unreviewed incbin slices |
| Reviewed executable ranges | 925 bytes | Local instruction semantics documented |
| Reviewed PRG data ranges | 44 bytes | Defaults, PPU pointer table and interrupt vectors |
| Reviewed PRG total | 969 / 131072 bytes (0.7393%) | Derived from union of reviewed_ranges.csv |
| Automatically decoded candidates | 6248 bytes | Not a semantic understanding percentage |
| Full NES gameplay experiments | 0 | No MesenCE session or PPU/APU timing validation |

The header adds 16 explicitly emitted metadata bytes to the assembly scaffold. The remaining 261175 bytes
come from unreviewed input slices. The original and rebuilt ROM files are excluded from checkpoints.
The scaffold is therefore reproducible with the original input, not a self-contained source reconstruction.

`maps/rom/classification.csv` accounts for the complete file without gaps or overlap.
`analysis/rebuild_verification.json` records the actual byte comparison, not merely matching file lengths.
Native Ghidra and MesenCE imports have **not** been tested. No fake Ghidra project, CDL or savestate is included.

## Reproduction

```sh
python3 -m unittest discover -s tests -v
python3 scripts/cpu_experiments.py /path/to/original.nes
python3 scripts/build.py /path/to/original.nes
```

Do not run `prepare_sources.py` just to build: it intentionally regenerates the scaffold and can overwrite
manual source changes. `build.py` assembles the existing files. To continue static analysis, edit the reviewed
range definitions, review evidence, and regenerate indexes deliberately.

Read `reports/subsystems/BOOT_MMC3_INTERRUPTS.md` for concrete findings and preconditions.
The next milestone is bank-aware main-flow/RAM reconstruction, followed by controlled gameplay validation.
