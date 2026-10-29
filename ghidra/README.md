# Ghidra handoff

No Ghidra installation was available; no `.gpr` project or successful GUI/headless import is claimed.
`symbols.csv` and `prg_memory_blocks.csv` are portable bank-aware inputs, not a tested native import format.

The official GhidraNes README lists mapper 4 but notes that bank-switch control flow is not automatically
resolved. Use a GhidraNes build matching your Ghidra version and configure 8 KiB PRG blocks.
Set PRG0E to C000 for the verified mode-0 paths and PRG0F to E000. The reviewed R7 contexts for PRG07/08/09 use A000; their block CSV bases now reflect that context.
Other block bases remain context-dependent, and other aliases are not excluded.
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

Stage01B handoff: review FourPhaseMainLoop, WaitNmiAndServiceAudio, ReadControllerSerial and the
three scene route tables. service_jump_tables.csv distinguishes the physically different bank07/08/09
entries at shared CPU addresses. cross_references.csv deliberately leaves target-bank gaps after unknown
callees; inspect stage01B_static_summary.json, stage02A_static_summary.json, stage02B_static_summary.json
stage02C_static_summary.json and stage02D_static_summary.json for those gaps. Resolved target banks do not imply reviewed target bodies.
Scene pointer exports preserve both R6 and R7 targets. A CPU pointer in the A000 window must not
be assigned to the R6 data bank merely because it was read from that scene's configuration.

Stage02D collision tables in PRG06 use R6=06 at8000.32 projectile handler pairs resolve in PRG09
atA000. Review PROJECTILE_COLLISION_AND_ENEMY_HITS.md and preserve the0440 RAM alias.
There are456 portable symbols; successful native Ghidra import remains NOT_TESTED.

Stage02E adds normalplayer/terrain entries and32 splitdirection pointers; tables/labels remain portable exports.
CPU02E:14groups/11868cases/34866tracerows; nativeimport/gameplay still NOT_TESTED.
