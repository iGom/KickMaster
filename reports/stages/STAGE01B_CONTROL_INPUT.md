# Stage 01B — control flow and input

Status: bounded static/CPU milestone complete; full game reconstruction remains open.

The session resumed the verified stage01A archive with SHA-256
`d4cf1e4e2e0f80f30e88545d574d5f57107498eb8654037f21e16e160a6d2c3a`.
Existing baseline, research, traces and 57 CPU cases were reused.

Read `../subsystems/MAIN_LOOP_INPUT_STATE.md` for findings, addresses, equations, test limits and diagram.

## Added artifacts

- `scripts/architecture_stage01b.py`: incremental reviewed regions, bank-aware call edges and tables.
- `scripts/cpu_stage01b.py`: serial input, NMI delivery, control-flow and boundary experiments.
- `scripts/audit_project.py`: address, instruction-byte, coverage and integration consistency.
- `analysis/service_jump_tables.csv`: 88 service entries in four banks.
- `analysis/scene_index_routes.csv`: all 32 rows of three routing tables.
- `analysis/main_loop_phases.csv`: 34 calls across four unrolled phases.
- `analysis/cpu_stage01B*.{json,csv}`: 18 passing groups / 2295 vectors / selected traces.
- Updated mixed sources, linker/debug symbols, 56 RAM entries and 135 total symbols.

## Reconstruction

3278 code bytes + 166 data bytes = 3444 reviewed PRG bytes / 131072 = 2.6275634765625%.
Explicit source including header: 3460 bytes. Remaining `.incbin`: 258700 bytes.
The full 262160-byte build matches the supplied image exactly. It still requires the original ROM.

## Boundaries

- No full NES run, rendered gameplay, scanline/APU timing or native Ghidra/MesenCE import.
- Acknowledged callee substitutions in control-flow tests; only initialized idle audio exercised in full D90C tests.
- Stage names and world geometry are not assigned to the 32 internal scene indices.
- `analysis/unresolved.csv` remains the historical stage01A candidate-walk stop list, not a global live count.
  New unresolved bank edges are recorded in `analysis/stage01B_static_summary.json`.
- Gameplay reference claims from stage00A retain their separate external-only status.
- Existing checkpoints are unchanged. New archive: `kickmaster-ntscu-checkpoint-stage01B.zip`.
  Its hash and upload/readback verification are recorded outside the archive after packaging.
