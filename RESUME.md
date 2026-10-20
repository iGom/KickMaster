# Resume: KickMaster NTSC-U

Current milestone: Stage 00A research baseline established; external map-image review incomplete. Stage 01 next.

Input SHA-256: `00ad4a0c6612319bb9f918ca36d6e93b4e5d996716c0570a3ec92bd60533881b`.
Original filename: `KickMaster (USA)(1).nes`; 262160 bytes. The original is excluded from checkpoints.
Do not normalize the NES 2.0 header or substitute another dump.

This snapshot is `kickmaster-ntscu-checkpoint-stage00A.zip`.
Previous verified checkpoint: stage00; persisted and read back successfully (see manifests/stage00_persistence.json).
Its integrity and persistence are recorded by the external verification/readback receipts because the ZIP
cannot contain its own final hash or the result of a future upload.

Completed: exact identity; NES 2.0 parsing; PRG/CHR bank checksums; vectors; tool inventory;
published PRG/CHR/payload CRC32 comparison; reproducible baseline script; checkpoint verifier.
Confirmed: mapper 4, 128 KiB PRG, 128 KiB CHR, no trainer, no battery, no declared PRG/CHR RAM,
NTSC timing. NMI=PRG0F:F0BB; RESET=PRG0F:F010; IRQ/BRK=PRG0F:F7B1.
No gameplay execution or RAM-variable interpretation yet.

Tooling: Python 3.12, Java and Poppler available. Ghidra, ca65/ld65 and NES emulators were not on PATH.
See `manifests/toolchain.json` for precise versions. Optional py65 installation is being prepared for Stage 01.

Next:
1. Verify and extract the latest ZIP; read the current RESUME before running analysis.
2. Reuse `manifests`, `maps/rom` and reports. Do not repeat baseline unless validating a newly supplied file.
3. Read the Taito manual; catalog Wyrenth guide, cheats and eight sprays maps.
4. Start fixed-bank vector-led disassembly and manually confirm MMC3 initialization.
5. Preserve another verified checkpoint and read back its uploaded bytes.

Commands from extracted project root:

```sh
python3 scripts/checkpoint.py --verify /path/to/kickmaster-ntscu-checkpoint-stage00.zip
python3 scripts/baseline.py "/path/to/KickMaster (USA)(1).nes"
python3 -m unittest discover -s tests -v
```

Directories: `manifests` for identities; `analysis` for structured evidence; `maps` for memory/ROM maps;
`research` for cited gameplay baseline; `reports` for milestone/subsystem reports; `disassembly` for source;
`ghidra` and `MesenCE` for integration; `scripts`/`tests` for reproducibility; `checkpoints` for archives.

Stage 00A additions: 51 source-indexed claims, 8 map links and stage stubs, 29 experiment plans, 5 password vectors, 8 discrepancy records. No map-image inspection or gameplay validation.
