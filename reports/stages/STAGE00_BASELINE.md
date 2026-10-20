# Stage 00: ROM identity and toolchain

## Findings

The supplied image is structurally consistent with the NTSC-U cartridge reference.
The PRG and CHR CRC32 values independently match NesCartDB; the concatenated payload CRC32 matches too.
This is strong identification evidence, not a cryptographic proof against deliberate CRC collisions.
The database does not provide a whole-file SHA-256 to compare. No alternate ROM was downloaded.

| Component | Bytes | CRC32 |
|---|---:|---|
| Complete uploaded file | 262160 | EABD6104 |
| PRG ROM | 131072 | D88D48D7 |
| CHR ROM | 131072 | 5B03178D |
| PRG + CHR, without header | 262144 | 5104833E |

Whole-file SHA-256: `00ad4a0c6612319bb9f918ca36d6e93b4e5d996716c0570a3ec92bd60533881b`.
Whole-file SHA-1: `e329254370f4a66b110fee46988da585989a586e`.
Hashes for all 16 PRG banks (8 KiB) and 128 CHR units (1 KiB) are in `maps/rom/banks.csv`.

## Header and layout

Header: `4E 45 53 1A 08 10 40 08 00 00 00 00 00 00 00 01`.
Byte 7 masked with 0C gives 08: **NES 2.0**, not legacy iNES 1.0.
Mapper=4, submapper=0 (unspecified variant); normal NES console; NTSC timing.
Expansion device=1 (standard NES/Famicom controllers).
Battery=false; trainer=false; four-screen=false; all RAM/NVRAM size fields zero.
The header mirroring bit is 0 (horizontal); MMC3 can subsequently change mirroring through A000.

| Region | File start | File end exclusive | Size |
|---|---|---|---:|
| Header | 0x000000 | 0x000010 | 16 |
| PRG | 0x000010 | 0x020010 | 131072 |
| CHR | 0x020010 | 0x040010 | 131072 |

No trailing bytes or length mismatch. NES 2.0 bytes are container metadata, not original cartridge ROM.
PCB NES-TLROM-03 and MMC3C are **published physical-cartridge properties**; they cannot be established
solely from these file bytes or submapper 0. The reference lists no battery, WRAM or VRAM.

## Vectors

| Vector location | Target | Target PRG offset | Target file offset |
|---|---|---|---|
| PRG0F:FFFA | PRG0F:F0BB | 0x01F0BB | 0x01F0CB |
| PRG0F:FFFC | PRG0F:F010 | 0x01F010 | 0x01F020 |
| PRG0F:FFFE | PRG0F:F7B1 | 0x01F7B1 | 0x01F7C1 |

All target addresses are in the last 8 KiB PRG bank fixed at E000-FFFF. These are byte-level vector
identifications; handler semantics require the following milestone.

## Toolchain and limits

Python, Java, GCC, Git, Poppler and Tesseract are available. Ghidra, NES emulators and cc65 executables
were not found on PATH. This is an availability check, not a claim that their import formats work.
See `manifests/toolchain.json`. No Ghidra project, Mesen label import, CDL, savestate or gameplay trace
has yet been generated or verified. Reconstruction and semantic coverage are not yet claimed.

## Sources and verification

- [NesCartDB, profile 2564](https://nescartdb.com/profile/view/2564/kick-master), ROM Details and PCB:
  independently inspected 2026-10-19; primary cartridge inspection/database evidence.
- [NESdev NES 2.0](https://www.nesdev.org/wiki/NES_2.0), Identification and Header:
  specification retrieved through search; direct HTTP access returned 403.
- `scripts/baseline.py`: reproducible hashes, parsed fields, bank boundaries and vector records.
- `tests/test_baseline.py`: meaningful checks for NES 2.0 fields, truncation, trainer offset and exponent size.

The checkpoint verifier checks ZIP CRC, every manifest member, member-set equality and sample extraction.
Its result and ZIP SHA-256 are in the adjacent `.verification.json` receipt. Library readback is a separate,
post-creation check; never infer persistence solely from a local ZIP.
