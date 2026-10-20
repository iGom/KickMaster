# Boot, MMC3, PPU transfers and interrupt architecture

Evidence: `analysis/reviewed_ranges.csv` (A01-A27), annotated assembly, `analysis/cpu_experiments.json`,
and the exact input fingerprint. All names here describe newly reviewed local code behavior.

## Address convention and mapping

PRG banks are 8 KiB, numbered 00-0F. For bank b, in-bank offset o and active CPU window W:
`PRG_offset=b*0x2000+o`, `file_offset=0x10+PRG_offset`, `CPU=W+o`.
In mode 0, windows 8000/A000 use R6/R7; C000 uses 0E and E000 uses 0F.
Mode 1 exchanges the R6 and fixed-0E windows; E000 stays fixed. This general hardware rule is from NESdev.
Do not assume mode 0 without the documented path conditions.

RESET sets mode 0 and writes R6=04, R7=05. Thus the first established map is:

| CPU window | Physical PRG bank | File interval |
|---|---|---|
| 8000-9FFF | 04 | 008010-00A00F |
| A000-BFFF | 05 | 00A010-00C00F |
| C000-DFFF | 0E | 01C010-01E00F |
| E000-FFFF | 0F | 01E010-02000F |

These intervals alone are inclusive; CSV ranges otherwise use end-exclusive bounds.
RESET writes 00 to A000: CIRAM A10, conventionally called vertical mirroring. The file header's horizontal
mirroring bit is therefore not an invariant runtime setting. Physical MMC3C is reference cartridge data,
not identified from a special submapper flag.

## Reset and retained RAM

PRG0F:F010 begins with SEI, IRQ disable/acknowledgment, CLD, mapper/PPU initialization and SP=FF.
It waits for four observed PPU vblank assertion/clear pairs, then establishes the above PRG map.
The RAM loop clears all internal RAM **except 0100 and 0300-0307**. This is deliberate in the instruction
addresses; it is not a conventional eight-page clear. CPU01 confirms the nine retained bytes.

PRG0E:D60C checks 0100 against 68. On mismatch it initializes 0300-0305 to
`20 20 20 20 21 20`, then writes marker 68. The purpose of the retained block is not yet assigned.
Both marker branches were tested up to the subsequent, unreviewed D2F7 call (CPU02).

RESET initializes palette buffer 0143-0162 with 0F, enables NMI through PPUCTRL, uploads the palette,
enables IRQ processing with CLI and jumps to PRG0E:CF50. This is a main-flow entry, not yet a fully
reconstructed game loop. Calls to switchable bank 09 occur shortly afterward; complete state propagation
through those callees remains future work.

## Interrupt-safe mapper transaction

PRG0E:D6C3 (`MapperWriteRetry`, 15 bytes) takes A=value, X=bank-select value and clobbers Y to zero.
It clears A6, writes X to 8000 and A to 8001, compares A6 with zero and repeats if changed.
NMI and reviewed IRQ return paths increment A6. Consequently A6 is an interrupt-activity marker, not
reliably a once-per-frame counter.

CPU03 tests both R6 and R7 without interference and with one synthetic interrupt-like write at each of
seven instruction boundaries. All reach the intended final bank. The harness models competing mapper
writes and A6 changes; it does **not** validate real interrupt timing, starvation or the full mapper circuit.

Three nearby tail-call stubs map PRG0C to 8000 and jump to 8000, 8003 or 8006. Their physical targets are
recorded in `cross_bank_confirmed.json`. They do not themselves restore the old R6 bank.

## Far-call wrapper

PRG0F:F4CA reads the current window-end bytes at 9FFF/BFFF into 04EE/04ED, maps 04EC into the A000
window, then JSRs to F50A. F50A JMPs indirectly through 04EA/04EB, so a destination RTS returns to
the wrapper. The wrapper restores both R7 and R6 while preserving the callee's A/X/Y/status results.

Physical banks 01-0D have their own bank number in their last byte. Bank 00 ends in C1; fixed banks
0E/0F end in 99/F7. Therefore the tag mechanism must not be generalized to every bank without checking
the caller's mapping. CPU07 verifies the wrapper with initial R6=04/R7=05, target R7=09 and a documented
RAM callee that changes R6. It restores both banks and returns the callee's outputs. Nested calls are not tested;
the save slots are shared RAM rather than per-call stack entries.

## NMI and PPU work

PRG0F:F0BB saves A/X/Y in E7/E8/E9, resets OAMADDR and requests DMA from page 02.
The PPU dispatcher at F156 consumes A0, masks it with 1E and jumps through a 16-word table at F16A.
The original table and target banks are preserved. CPU05 checks all 32 low command values; the low bit
does not affect this dispatch. Other command bits and their producers remain to be reconstructed.

The dispatcher uses E5/E6 as scratch. If IRQ setup is enabled, NMI then restores that pointer from DC/DD,
programs the latch/reload/enable registers and establishes scroll/control state.
With 96 equal to 0 or 1, X is zero at F116, and six writes load CHR registers R0-R5 from 44-49.
These two states were tested in CPU06 with the no-work PPU command and D9=0. Other PPU tasks and IRQ
flag values were not exhaustively validated. CHR inversion is zero in these tested paths.

The 27-byte uploader at F18A temporarily uses SP=00 to read 0101-011B with PLA. The 32-byte palette
uploader at F24B uses SP=42 to read 0143-0162. Each restores the real SP from 0170 before returning.
CPU04 checks the palette byte stream, SP restoration and the 06EE post-upload flag. This does not test
PPU palette aliasing or visual output.

## IRQ splitting

PRG0F:F7B1 saves A/X/Y in E2/E3/E4, writes E000 then E001 and dispatches via E5/E6.
Reviewed handlers program PPUCTRL, scroll and/or PPUADDR after a short software delay and schedule further
IRQ counts. F0 sentinel values select terminal handlers. F83D also selects CHR R0=00 and R1=02.
Some transitions replace only the low pointer byte, so the F8 high byte is a required state precondition.

This establishes software support for multiple raster splits. Exact scanlines, HUD association, MMC3C
A12-edge behavior and visual effects are **not** measured. CPU08 checks dispatcher/return mechanics only.

## Remaining work

Trace CF50 and bank 09 entry points with explicit bank state; identify controller polling and game modes;
resolve remaining IRQ targets; collect actual MesenCE traces; map RAM producers and lifetimes; then move
into gameplay progression. Do not promote the 6,248 automatically decoded candidate bytes into reviewed code.

Technical sources: https://www.nesdev.org/wiki/MMC3 and https://www.nesdev.org/wiki/Programming_MMC3.
Implementation findings above come from the supplied ROM, not the hardware reference pages.
