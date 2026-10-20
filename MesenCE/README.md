# MesenCE integration status

`kickmaster.mlb` contains 62 labels derived only from reviewed ROM ranges and documented local RAM roles.
ROM labels use **PRG-relative offsets excluding the 16-byte NES header**, rather than CPU addresses.
This preserves physical-bank identity even for switchable regions. RAM labels use physical internal RAM.

The generated rows use the current explicit types `NesPrgRom` and `NesInternalRam`.
The grammar was checked against `UI/Debugger/Labels/CodeLabel.cs` at MesenCE commit
`4b8a196e299b3de297b204fd1208d2981562c89b`. Our emitted subset passes local syntax checks.
**Actual MesenCE import is NOT TESTED** because the emulator is not installed here.

Open the original ROM, import the MLB through the debugger's label integration, then confirm:

1. ResetEntry resolves to PRG offset 1F010 / CPU F010 / file offset 1F020.
2. MapperWriteRetry resolves to PRG offset 1D6C3 / CPU D6C3 under PRG mode 0.
3. OamDmaBuffer resolves to internal RAM 0200.

Use the research experiment checklist for future savestate/input-based tests. No CDL, gameplay trace,
movie or savestate is fabricated. `analysis/cpu_trace.csv` is from a bounded CPU harness, not MesenCE.
The generated ca65 `.dbg` is preserved separately; importing that format into MesenCE is also untested.

Source: https://github.com/nesdev-org/MesenCE/blob/4b8a196e299b3de297b204fd1208d2981562c89b/UI/Debugger/Labels/CodeLabel.cs
