# Stage 02A — player and scene foundation

Completed bounded milestone, 2026-10-20. Start checkpoint01B was verified; workspace was intact.
Detailed Polish report: `reports/subsystems/PLAYER_SCENE_FOUNDATIONS.md`.

New static evidence C01..C67 covers 33 code ranges,34 data ranges,892 instructions,3385 PRG bytes.
Current union: 5020 code +1809 data =6829 PRG bytes (5.210113525390625%).
Exact rebuild: PASS for262160 bytes. Input-dependent mixed assembly/incbin remains explicit.

Deliverables added:

- 32 scene configurations and192 bank-qualified source/target pointer records.
- 111 normal +5 alternate player code pairs; normal table has22 unique handler targets.
- 138 rows of indirect dispatch tables; targets retain their reviewed/unreviewed distinction.
- Damage-to-death-to-restart trace; exact-zero and unsigned-borrow outcomes separated.
- HP bar buffering,16 raw units per full cell, eight capacity-table values.
- 18 CPU groups/10137 vectors/5921 trace rows, with explicit boundary stubs.
- 80 RAM entries,226 unified symbols,198 exhaustive file ranges,325 graph edges.

Retained without rerun: stage01A57 cases, stage01B18 groups/2295 vectors. Previous archives unchanged.
The source generator and audit now include the new C-series while preserving A/B evidence.
The first development runs exposed a test-result metadata key error and an integer/string formatting
error in indirect-table export. Both were corrected; final outputs and gates pass.

Unresolved: whole game timing and native emulator imports; remaining movement/attack handlers;
complete HP healing/level clamps; MP/EXP and pickups; scene geometry/names and non-chain routes;
PRG08:ABC5 split-scroll behavior and PRG09:BE90 object rendering beyond the inspected entry code.
