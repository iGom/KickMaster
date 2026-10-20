# Ghidra handoff

No Ghidra installation was available; no `.gpr` project or successful GUI/headless import is claimed.
`symbols.csv` and `prg_memory_blocks.csv` are portable bank-aware inputs, not a tested native import format.

The official GhidraNes README lists mapper 4 but notes that bank-switch control flow is not automatically
resolved. Use a GhidraNes build matching your Ghidra version and configure 8 KiB PRG blocks.
Set PRG0E to C000 for the verified mode-0 paths and PRG0F to E000. Other block bases remain context-dependent.
Treat per-bank memory blocks as separate spaces; never merge every 8000 target into one function.

Header caveat was checked in `NesRomHeader.java` at commit
`4c419644c51c650d2507920e2f083d288056c6f0`: the NES 2.0 branch contains an empty TODO rather than rejection.
For this particular image the older size/mapper fields still describe mapper 4 and 128 KiB PRG/CHR.
This is **source-level inspection**, not proof of end-to-end import. Do not rewrite the input header merely
because the README advertises iNES 1.0. Verify the actual import result first.

Suggested review order: ResetEntry, MapperWriteRetry, NmiEntry, DispatchPpuTask, IrqEntry, FarCallViaA000.
Apply names and comments from symbols.csv. Use cross_bank_confirmed.json for the three confirmed PRG0C
tail-jumps; unresolved fixed-window references are deliberately not promoted to verified banked calls.
Mark PpuTaskPointers and ResetRetainedDefaults as data, not instructions.

Sources:
- https://github.com/kylewlacy/GhidraNes
- https://github.com/kylewlacy/GhidraNes/blob/4c419644c51c650d2507920e2f083d288056c6f0/GhidraNes/src/main/java/ghidranes/NesRomHeader.java
