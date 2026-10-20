# Gameplay research baseline

This is a structured research baseline, **not** a reverse-engineered gameplay specification.
The user's supplied reference tables are preserved and cross-referenced in these datasets:

| Dataset | Scope | Source location checked |
|---|---|---|
| progression_reference.csv | Eight levels; cumulative thresholds; displayed capacities | Manual p.8 |
| kicks_reference.csv | Ten moves; required levels; input expectations | Manual pp.10-11 |
| pickups_reference.csv | Nine item categories and nominal increments | Manual p.9 |
| spells_reference.csv | Twelve names/aliases; nominal MP costs | Manual pp.12-14 |
| acquisition_reference.csv | Twelve acquisition expectations across stages 1-7 | Guide, corresponding sector |
| stage_map_index.csv | Eight external map links and investigation scope | GameFAQs map listing |
| gameplay_claims.csv | Per-claim source, reliability and separate evidence flags | See each row |
| validation_checklist.csv | Concrete experiments for ROM implementation | Original project test design |

Controls baseline: A jumps; B attacks; Start opens pause/magic selection; Select casts.
The manual also documents a sound test and kick demonstration. [Manual pp.5,7](https://www.digitpress.com/library/manuals/nes/Kickmaster.pdf).

The following remain explicit unknowns: HP/MP/EXP encodings, exact capacity clamping, score carry rules,
internal move/spell/item IDs, hitbox geometry, spell durations, RNG algorithm, drop independence,
object pool size, collision/map formats, checkpoint state, password fields and quest transitions.

For progression, separate displayed units from raw RAM units. For rewards, keep enemy death, object
creation, collision/collection and stat update as separate candidate systems. For magic, the order in
the manual or CSV is not an internal ID assignment. No conventional inventory is introduced.

Enemy research uses descriptive provisional names until an internal ID and visual appearance are linked.
The eight stage report stubs state what has not been extracted. Published map images remain unread.

All current gameplay claims have `rom_verified=false`, `assembly_confirmed=false` and
`emulator_observed=false`. Hardware initialization findings in Stage 01 do not change those flags.
