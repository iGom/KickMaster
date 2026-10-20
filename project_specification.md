# KickMaster (NES, NTSC-U) — Comprehensive Reverse Engineering Project

## 1. Main objective

Perform an extensive, evidence-driven reverse engineering analysis of the original North American NTSC-U release of **KickMaster (NES, 1992)**, developed by KID and published by Taito.

The primary goal is to reconstruct and document as much of the original game's executable code, data structures, memory organization, gameplay logic, hardware interactions and internal architecture as reasonably possible.

The intended end product is a readable, extensively annotated, preferably byte-matching 6502 assembly reconstruction, supported by technical documentation and independently verifiable evidence.

The user intends to perform their own reverse engineering of the same game using tools such as MesenCE and Ghidra. Your work must therefore produce reference material that can be independently inspected, reproduced and compared with the user's own findings.

**This is a reverse engineering and documentation project, not yet a ROM-hacking or randomizer development project.**

Do not implement gameplay modifications, randomizers, balancing patches or unrelated enhancements.

### Fundamental requirements

- Prioritize correctness, reproducibility and evidence.
- Distinguish verified findings from hypotheses.
- Preserve raw analysis results and intermediate artifacts.
- Do not fabricate addresses, code, test results or undocumented mechanics.
- Do not describe guessed behavior as established fact.
- Preserve progress across sessions and environment resets.
- Produce downloadable reports, data files and verified checkpoints.
- Treat incomplete but properly documented work as more valuable than an unsupported claim of complete reconstruction.

---

## 2. Target ROM and cartridge hardware

Analyze only the original NTSC-U commercial release.

Known reference cartridge characteristics:

| Property | Reference value |
|---|---|
| Platform | Nintendo Entertainment System |
| Game | KickMaster / Kick Master |
| Region | North America, NTSC-U |
| Developer | KID |
| Publisher | Taito |
| Original release | January 1992 |
| Mapper | MMC3, iNES mapper 4 |
| PRG ROM | 128 KiB |
| CHR ROM | 128 KiB |
| PCB | NES-TLROM-03 |
| Mapper chip | MMC3C |
| Cartridge battery | None |

Source: https://nescartdb.com/profile/view/2564/kick-master

Treat these values as documented reference data, not a substitute for examining the supplied ROM.

### Initial verification

1. Identify and inspect the provided `.nes` file.
2. Calculate SHA-256, SHA-1, CRC32 and file size.
3. Parse the iNES/NES 2.0 header.
4. Confirm the mapper, mirroring, PRG/CHR layout and any trainer.
5. Compare the cartridge characteristics against published reference data.
6. Identify any inconsistencies, corruption or unexpected changes.
7. Establish an unambiguous ROM identity for all subsequent reports.

Never substitute an alternative dump without explicitly documenting the change.

Do not download or substitute an unauthorized ROM if the required input file is unavailable.

### Bank mapping

The MMC3 hardware is particularly important.

Reconstruct:

- PRG and CHR banking modes.
- Fixed and switchable PRG ROM windows.
- Bank selection routines.
- Mapper register writes.
- Mirroring configuration.
- IRQ initialization, enable/disable and acknowledgment.
- Scanline IRQ behavior where used.
- Interactions between NMI/IRQ handlers and bank switching.
- Any bank-switching trampolines or far-call mechanisms.

Every identified ROM address must be expressible as:

- PRG bank identifier.
- CPU-visible address.
- Offset within the PRG bank.
- Absolute PRG ROM offset.
- Absolute offset within the `.nes` file.
- Relevant bank-mapping conditions.

Do not use an unqualified CPU address to identify code that can exist in several banks.

---

## 3. External research and source hierarchy

Before relying on gameplay assumptions, research available documentation of the original game.

Use the following source hierarchy.

### 3.1 Primary gameplay documentation

**Original Taito instruction manual**

https://www.digitpress.com/library/manuals/nes/Kickmaster.pdf

This should be the main reference for official descriptions of:

- Controls and menu behavior.
- HP, MP, experience and leveling.
- Fighting moves.
- Spell names and MP costs.
- Pickups and their effects.
- Passwords.
- Stage organization.

### 3.2 Detailed walkthrough

**KickMaster Guide and Walkthrough — Wyrenth, GameFAQs**

https://gamefaqs.gamespot.com/nes/563430-kickmaster/faqs/19876

Use it to research:

- Stage progression and layouts.
- Hidden spells and pickup locations.
- Enemies and bosses.
- Attack patterns.
- Secret routes and breakable terrain.
- Expected gameplay behavior.
- Password and progression behavior.

Treat observations and interpretations from the walkthrough as secondary evidence requiring verification.

### 3.3 Stage maps

GameFAQs provides eight individual stage maps by sprays:

https://gamefaqs.gamespot.com/nes/563430-kickmaster/faqs

Compare these maps against the ROM's actual stage data, transitions, collision geometry, scrolling behavior and enemy placement.

### 3.4 Additional gameplay references

- GameFAQs cheats/passwords:
  https://gamefaqs.gamespot.com/nes/563430-kickmaster/cheats
- MobyGames:
  https://www.mobygames.com/game/18675/kick-master/
- NesCartDB:
  https://nescartdb.com/profile/view/2564/kick-master

### 3.5 Technical documentation

- NESdev MMC3:
  https://www.nesdev.org/wiki/MMC3
- NESdev MMC3 programming:
  https://www.nesdev.org/wiki/Programming_MMC3
- GhidraNes:
  https://github.com/kylewlacy/GhidraNes
- MesenCE:
  https://github.com/nesdev-org/MesenCE

Research additional reliable technical sources when necessary.

### Research methodology

Create `RESEARCH_SOURCES.md` and a structured source index.

For every externally documented mechanic, record:

- Source URL.
- Relevant manual page or guide section.
- Concise paraphrase of the described behavior.
- Source reliability.
- Whether the behavior has been verified against the actual ROM.
- Any disagreement between sources.

Avoid copying entire copyrighted guides into the checkpoint. Preserve citations, technical summaries and references instead.

**External documentation defines a research baseline. The ROM and observable game behavior are the final authorities on implementation.**

---

# PART A — KNOWN GAMEPLAY REFERENCE

This section documents mechanics that should guide the investigation.

These are reference observations, not claims that their underlying assembly implementation has already been identified.

## 4. Player and progression systems

The protagonist is Thonolan, a martial artist who primarily fights through kicking techniques and collectible magic spells.

The game contains eight main stages and incorporates RPG-like progression through experience levels.

### 4.1 Experience and level progression

According to the original manual:

| Level | Cumulative EXP required | Maximum HP | Maximum MP |
|---|---:|---:|---:|
| 0 | 0 | 4 | 100 |
| 1 | 1,000 | 5 | 200 |
| 2 | 2,000 | 6 | 300 |
| 3 | 3,000 | 7 | 400 |
| 4 | 4,000 | 8 | 500 |
| 5 | 5,000 | 9 | 600 |
| 6 | 6,000 | 10 | 700 |
| 7 | 7,000 | 11 | 999 |

These are cumulative experience thresholds.

Further investigate the actual storage limits, display limits and behavior beyond level 7.

### Required research

Identify and document:

1. Current experience variables and their numerical encoding.
2. Experience thresholds and lookup tables.
3. Experience accumulation.
4. Level-up detection and processing.
5. Maximum-level handling.
6. Maximum HP and MP progression.
7. Current HP/MP modification during leveling.
8. Saturation, overflow and clamping behavior.
9. Maximum displayed versus internally stored experience.
10. Interaction with death, continues and passwords.

Determine whether the game uses ordinary binary values, decimal digit encoding, BCD or other representations for each relevant quantity.

Do not assume that EXP, MP, HP and score all use the same storage format.

### 4.2 Player state

Map and document:

- Current HP and maximum HP.
- Current MP and maximum MP.
- Current EXP and level.
- Score.
- Remaining lives.
- Current stage and gameplay mode.
- Player world and screen coordinates.
- Velocity, gravity and movement state.
- Facing direction.
- Animation state.
- Current attack and attack phase.
- Invulnerability and damage reactions.
- Current selected spell.
- Learned/available spells.
- Active spell effects.
- Any relevant timers and temporary flags.

The game has no conventional persistent inventory system. Do not invent one.

---

## 5. Fighting techniques

The original manual describes ten kicking techniques.

Three are available at the beginning, with additional techniques obtained through leveling.

| Level | Technique |
|---|---|
| 0 | High Kick |
| 0 | Sweep Kick |
| 0 | Vertical Press Kick |
| 1 | Knee Drop |
| 2 | Sliding Kick |
| 3 | Double Front Kick |
| 4 | Roundhouse Kick |
| 5 | Flying Kick |
| 6 | Double Butterfly Kick |
| 7 | Blazing Flip Kick |

Some advanced techniques replace earlier attacks rather than simply adding another independent action.

### Required analysis

For every fighting technique, determine:

- Input sequence and activation conditions.
- Required experience level.
- Player-state prerequisites.
- Animation sequence and duration.
- Attack hitboxes.
- Collision detection.
- Damage amount and calculation.
- Single-hit versus multi-hit behavior.
- Knockback and enemy reactions.
- Temporary invulnerability, if any.
- Player movement during attacks.
- Cooldowns and cancellation behavior.
- Replacements of earlier techniques.
- Relevant assembly routines and data tables.

Investigate which techniques share implementation code and which use independent routines.

Distinguish observed attack behavior from assumptions based on animation appearance.

---

## 6. Pickup generation and collection

**This game does not use a conventional RPG inventory.**

Defeated ordinary enemies generally release three airborne pickups that the player can attempt to collect.

Bosses can release larger sets of rewards.

Pickups include positive and negative effects.

### Known pickup types

| Pickup | Documented effect |
|---|---|
| Small EXP Coin | +10 EXP |
| Medium EXP Coin | +30 EXP |
| Large EXP Coin | +50 EXP |
| Heart | +1 HP |
| Small Magic Bottle | +5 MP |
| Large Magic Bottle | +10 MP |
| Jewel / Crystal | +100 score |
| 1-UP | +1 life |
| Poison / Skull | Damages the player |

The original manual documents these nine categories.

The walkthrough suggests that rare 1-UP pickups may behave differently from normal three-pickup drops. Investigate rather than assuming identical behavior.

### 6.1 Drop generation

Identify the procedures responsible for:

- Enemy death detection.
- Reward eligibility.
- RNG calls.
- Pickup type selection.
- Drop probability or weighting tables.
- Standard drop counts.
- Boss and miniboss reward generation.
- Pickup spawning coordinates.
- Initial velocity and spread patterns.
- Active-object slot allocation.
- Object-pool limits.
- Exceptional and suppressed drops.

Determine whether the generated pickups are truly selected independently or whether the game applies additional restrictions.

Investigate whether enemy type, stage, difficulty, player level or other state variables affect the results.

### 6.2 Pickup physics

Reverse engineer:

- Initial trajectories.
- Horizontal and vertical velocities.
- Gravity or other movement rules.
- Collision with terrain.
- Screen boundaries.
- Lifetime and despawn conditions.
- Offscreen behavior.
- Interaction with scrolling.
- Collection hitboxes.
- The relationship between pickup objects and the general entity system.

### 6.3 Pickup effects

Locate and document the code responsible for:

- EXP increases.
- HP restoration.
- MP restoration.
- Score increases.
- Extra lives.
- Poison damage.
- Knockback and temporary invulnerability.
- Value clamping and capacity limits.

Investigate score-based extra lives. The GameFAQs walkthrough reports awards at 10,000 and 50,000 points; verify the actual logic and any additional thresholds.

### 6.4 Important architectural distinction

Defeating an enemy does not automatically provide the corresponding EXP.

The player must successfully collect the relevant experience pickup.

Treat enemy death, reward spawning, pickup collection and progression updates as separate mechanisms until their actual code relationships have been established.

---

## 7. Magic system

The game contains twelve magic powers.

Spells must be acquired during progression and can be selected using the game's spell selection menu.

Only one spell is selected for activation at a time. Some effects can remain active temporarily.

### 7.1 Documented spells

| Spell | MP cost | Reference behavior |
|---|---|---|
| Bouncing Bulb | 3 | Bouncing magical projectile |
| Life Up 1 | 60 | Restores up to 2 HP |
| Magic Boots | 20 | Temporary protection against hazardous terrain |
| Twin Power | 20 | Creates a decoy that distracts enemies |
| ?? Magic | 1 | Deliberately undocumented/mysterious effect |
| Lightning | 20 | Electrical attack effect |
| Life Up 2 | 90 | Restores up to 4 HP |
| Pulse Wave | 5 | Expanding energy-wave attack |
| Whip Lightning | 30 | Multi-directional lightning attack |
| Force Shield | 30 | Defensive barrier |
| Harpy Flying | 10 per second, nominal | Temporary flight |
| Earthquake | 20 | Temporarily stops enemies |

Some guides use longer names such as Bouncing Bulb Spirit, Lightning Spirit, Pulse Wave Spirit and Harpy Wings.

Maintain a list of canonical names and aliases.

The actual duration and frame-based MP consumption of Harpy Flying must be established from code.

The functionality of `?? Magic` is unresolved in the walkthrough and must not be presented as confirmed.

### 7.2 Preliminary spell acquisition map

The following locations are based on the walkthrough and require verification.

| Stage | Spell | Acquisition |
|---|---|---|
| 1 | Bouncing Bulb | Chest in stage |
| 1 | Life Up 1 | Boss reward |
| 2 | Magic Boots | Hidden area |
| 2 | Twin Power | Boss reward |
| 3 | ?? Magic | Hidden area |
| 3 | Lightning | Boss reward |
| 4 | Life Up 2 | Found within stage |
| 4 | Pulse Wave | Boss reward |
| 5 | Whip Lightning | Boss reward |
| 6 | Force Shield | Hidden area |
| 6 | Harpy Flying | Boss reward |
| 7 | Earthquake | Boss reward |

The walkthrough indicates that Stage 5 contains only one new spell and Stage 8 does not introduce another.

Do not assume a uniform two-spells-per-stage system.

### 7.3 Required reverse engineering

For each spell:

1. Identify its internal ID.
2. Identify its acquisition flag.
3. Locate acquisition and unlock procedures.
4. Identify the spell-selection menu logic.
5. Locate the MP-cost table or corresponding code.
6. Reconstruct execution and cancellation conditions.
7. Locate effects on the player, enemies and environment.
8. Map timers and lifetime behavior.
9. Investigate interaction with player attacks.
10. Identify object creation and effect animation.
11. Establish whether selection of another spell cancels existing effects.
12. Test behavior with insufficient MP and boundary values.

Create a detailed spell reference containing addresses, bank identifiers, documented effects and evidence.

### 7.4 Spell acquisition mechanisms

Distinguish at least:

- Hidden magic objects.
- Chests and breakable environmental objects.
- Enemy- or boss-triggered spell rewards.
- Stage progression and mandatory rewards.
- Spell-selection state and persistent availability.

Determine whether these all eventually call a shared spell-unlock routine or use different implementations.

---

## 8. Stage structure and world progression

The game contains eight main stages.

### Known stage names

1. The Witches' Forest
2. The Caverns of No Return
3. Belzed's First Stronghold
4. Bottomless Crevasse
5. Aboard the Ship of Strife
6. Across the Swamps
7. A Long Way From Home
8. Belzed's Haunted Tower

Names may vary slightly between the official manual and community guides.

### Stage-by-stage investigation

For every stage, reconstruct:

- Stage entry and initialization.
- Complete stage data organization.
- Level geometry.
- Tile and metatile representations.
- Collision information.
- Horizontal and vertical scrolling.
- Camera behavior and scrolling boundaries.
- Enemy spawning positions.
- Enemy activation and despawn triggers.
- Boss and miniboss encounters.
- Hidden areas.
- Breakable blocks and environmental interactions.
- Pickup and reward placements.
- Secret paths.
- Stage transitions.
- Death and restart locations.
- Any stage-specific routines.

### Known behaviors requiring attention

The game generally restricts backward traversal through completed portions of a stage, but several areas use vertical scrolling.

Some areas contain destructible blocks, hidden routes, collapsing platforms, spikes, hazardous ground and terrain that slows player movement.

Stage 7 is described in the walkthrough as a relatively straightforward horizontal route with numerous enemy encounters and multiple bosses.

Stage 8 contains vertical platforming and the final sequence involving Belzed and multiple guardians.

Reconstruct these features from the actual stage data rather than treating guide descriptions as authoritative implementation details.

### Deliverables

Produce individual stage reports and structured datasets for:

- Map dimensions and coordinates.
- Enemy spawn tables.
- Environmental objects.
- Hidden rewards.
- Boss encounters.
- Transitions.
- Relevant ROM offsets.

Where possible, correlate extracted ROM maps with the published eight GameFAQs maps.

---

## 9. Enemies, minibosses and bosses

Perform a systematic reconstruction of the game's entity and enemy systems.

### 9.1 Entity architecture

Identify:

- Entity types and internal IDs.
- Active-entity arrays.
- Object slots.
- Position and velocity fields.
- HP and damage fields.
- Animation state.
- AI state.
- Collision flags.
- Despawn conditions.
- Timers and counters.
- Shared update and rendering routines.

Determine which entities share underlying structures.

### 9.2 Enemy behavior

Investigate representative documented enemies, including skeletons, harpies, axe-wielding lizards, reapers, bats, frogs, armadillos, mages, ninjas, golems and other encountered types.

Build a complete enemy catalog from actual gameplay and code.

For each identified enemy, document:

- Spawn conditions.
- Movement and AI states.
- Attack routines.
- HP and damage.
- Collision behavior.
- Special resistances or vulnerabilities.
- Reward generation.
- Variants.
- Stage appearances.
- Associated ROM structures and routines.

Do not invent formal enemy names when community descriptions are uncertain. Use provisional identifiers and describe the observed appearance.

### 9.3 Boss systems

Investigate all major bosses and minibosses, including the forest witch, the second-stage Wolf Rider encounter, gargoyle, chimera, ship octopus, Great Harpies, later-stage bosses and final Belzed sequence.

Examples of documented boss mechanics worth investigating include:

- Summoned helper enemies.
- Vulnerability dependent on subordinate enemies.
- Multi-phase behaviors.
- Destructible limbs or parts.
- Transformation between forms.
- Multiple attack patterns.
- Shared AI between boss variants.
- Special boss HP displays.
- Larger reward generation.
- Spell rewards and stage transitions.

Identify whether bosses use shared or unique routines, tables and object layouts.

---

## 10. RNG and gameplay determinism

Reconstruct the random number generation system in detail.

Determine:

- Algorithm and state size.
- Initialization and seeding.
- RNG update routines.
- All call sites.
- Use in reward generation.
- Use in enemy behavior.
- Use in projectile movement or attack variation.
- Dependence on frames, input, timers or other runtime values.
- Any alternate or independent generators.

Test whether identical savestates and input sequences reproduce the same results.

Document how gameplay randomness affects the program's execution and progression.

---

## 11. Password and continuation system

The game uses passwords to restore progression.

According to the community walkthrough, passwords preserve at least:

- Stage.
- Experience level.
- Acquired spells.
- MP.
- Remaining lives.

The same guide reports that exact accumulated EXP, current HP and score are not preserved.

These claims require verification.

### Required investigation

1. Identify the password character set.
2. Recover encoding and decoding routines.
3. Determine how game state is packed.
4. Identify the underlying bit fields.
5. Reconstruct any checksum or validation logic.
6. Determine default values for data omitted from passwords.
7. Analyze invalid passwords.
8. Investigate level selection and stage selection behavior.
9. Analyze difficulty and subsequent-quest flags.
10. Implement a separate reference encoder/decoder if the algorithm is understood.

Test round-trip consistency:

`Game state → Password → Decoding → Restored game state`

### Additional reference data

The GameFAQs cheats page documents various passwords, including:

- Debug menu access.
- Player-level selection.
- Specific stage starts.
- Subsequent quests.
- High-level configurations with spells and extra lives.

Treat these as community-supplied test vectors, not automatically verified features.

Test them when practical and document any discrepancies.

Do not confuse special debug passwords with the normal password-generation algorithm unless the code demonstrates a relationship.

---

## 12. Death, lives, difficulty and endings

Analyze:

- Player death.
- Lives decrement.
- Restart locations.
- Game-over state.
- Continues.
- State retained or reset after death.
- Stage-entry state.
- Password restoration.
- Score-based lives.
- Difficulty changes.
- Final completion state.
- Ending sequences.

Community sources describe additional, more difficult quests after completing the game.

Investigate:

- How difficulty levels are represented.
- How subsequent quests are entered.
- Enemy HP or AI changes.
- Changes in spawns or attack patterns.
- Which player properties are reset or carried over.
- How difficulty is encoded in passwords.
- Whether endings vary by quest or difficulty.

Do not assume that increased difficulty consists only of modifying enemy HP.

---

# PART B — COMPLETE TECHNICAL RECONSTRUCTION

## 13. Program architecture and execution flow

Reconstruct the program's execution architecture, including:

- RESET, NMI and IRQ vectors.
- Startup and initialization.
- Title screen and menus.
- Main game loop.
- VBlank synchronization.
- Controller polling.
- State machines.
- Subroutine organization.
- Shared utility routines.
- Indirect calls and jump tables.
- Bank switching and cross-bank calls.
- Interrupt interactions.
- Memory copy and decompression routines.
- Transition between gameplay modes.
- Error or debug routines if present.

Produce a cross-referenced function index and call graph.

Document any code that appears unreachable, unused or only accessible under special conditions.

Use consistent symbolic names and explicitly label provisional identifications.

## 14. RAM and hardware memory mapping

Create a comprehensive map of:

- Zero page.
- Stack.
- Internal CPU RAM.
- CPU/PPU/APU register usage.
- Mapper registers.
- Sprite/OAM buffers.
- Background rendering buffers.
- Controller state.
- Gameplay variables.
- Entity arrays.
- Temporary working memory.
- Persistent stage and progression state.

For each RAM variable, record:

- Address and size.
- Accessing procedures.
- Read/write behavior.
- Suspected and verified purposes.
- Data encoding.
- Relevant game states.
- Evidence.

Document reused RAM addresses whose meaning changes between game states.

## 15. Graphics and PPU

Reconstruct the graphics pipeline where feasible:

- CHR bank organization.
- Background tiles.
- Sprite graphics.
- Metatiles and tile maps.
- Palette tables.
- Sprite/OAM updates.
- Animation frames and frame selection.
- Scrolling and camera effects.
- PPU register writes.
- DMA.
- Any compression or graphics streaming.
- HUD and menu rendering.

Export graphical assets in useful, reproducible formats when possible.

Preserve palette information, tile indices and ROM provenance.

## 16. Audio and APU

Identify the game's audio engine, including:

- Music playback routines.
- Sound-effect dispatch.
- Music and sound IDs.
- Track and pattern data.
- Instrument definitions where applicable.
- APU register usage.
- Channel allocation.
- Timing and sequencing.
- Interrupt or frame synchronization.

Create an indexed map of audio data and control routines.

An NSF/NSFe extraction may be investigated if useful, but it must not replace documentation of the original audio implementation.

## 17. Data structures and binary formats

Reconstruct all identifiable structures, including:

- Tables of pointers.
- Entity and enemy definitions.
- Collision data.
- Stage data.
- Spawn data.
- Animation data.
- Spell tables.
- Attack data.
- Drop probabilities.
- EXP thresholds.
- Password lookup tables.
- Graphics metadata.
- Audio metadata.
- Compression formats.

For each structure, provide byte-level layouts and examples tied to real ROM addresses.

---

# PART C — DISASSEMBLY AND VALIDATION

## 18. Assembly reconstruction

Create a structured and readable assembly project targeting the NES CPU.

Prefer meaningful symbolic names, explicit comments, reusable definitions and logical organization by bank and subsystem.

Use a suitable 6502 assembler, for example ca65/ld65 if appropriate.

Select tools based on actual compatibility, not familiarity.

### Matching disassembly

Aim to rebuild a ROM that matches the original input byte-for-byte.

Verify through:

- Binary comparison.
- File sizes.
- SHA-256.
- Bank-level checksums.
- Automated build scripts.

Preserve original instructions, data, bank layout and bytes wherever required for an exact match.

Raw byte directives or included binary blocks are acceptable as intermediate measures, but must be clearly identified.

### Two independent progress metrics

**Binary reconstruction coverage:** How much of the original ROM can be reproduced exactly.

**Semantic understanding coverage:** How much executable code and data has actually been identified, interpreted and documented.

Do not claim that a byte-matching ROM proves full understanding of its internals.

Do not assign arbitrary progress percentages. Derive coverage values from documented byte ranges and classification rules.

## 19. Ghidra and MesenCE integration

Produce findings that can be imported into and explored within external reverse engineering tools.

Where supported:

- Export Ghidra projects or reproducible project-creation scripts.
- Preserve memory blocks, labels, comments and references.
- Use bank-aware memory spaces or overlays.
- Export structured procedure and symbol indexes.
- Produce MesenCE-compatible `.mlb` labels.
- Produce Code/Data Logger information (`.cdl`) where available.
- Preserve trace logs and relevant debugger configuration.
- Generate assembler-compatible symbol information.
- Produce `.dbg` information when supported by the selected assembler.

Test the actual import/export formats before claiming compatibility.

Document tool versions and any required extensions.

### Naming conventions

Maintain consistent symbols across assembly, Ghidra, MesenCE and CSV/JSON files.

Use descriptive names and clearly distinguish:

- Confirmed functions.
- Probable functions.
- Unresolved routines.
- RAM variables.
- Constants.
- ROM tables.
- Jump tables.
- Hardware registers.

Keep an index mapping each symbol to its bank and source address.

## 20. Validation methodology

Use both static analysis and dynamic verification where technically possible.

Examples include:

- Breakpoints on RAM reads/writes.
- Execution breakpoints at identified routines.
- Trace logging.
- Code/Data Logger coverage.
- Controlled emulator savestates.
- Input recordings or reproducible input sequences.
- Memory inspections.
- Comparison against documented gameplay values.
- Rebuilding and executing reconstructed ROMs.
- Comparing game behavior before and after reconstruction.

Create small automated experiments for identified mechanics.

For example:

**EXP test:** Collect a known +30 EXP pickup and observe the corresponding memory changes and execution path.

**Spell test:** Cast Life Up 1 and verify MP reduction, healing, clipping and boundary behavior.

**Drop test:** Repeatedly defeat a known enemy from controlled states and analyze reward selection.

**Password test:** Encode and decode several known progression configurations.

**Bank test:** Track mapper register writes and establish which PRG bank executes the subsequent instructions.

Each completed experiment must include observations and sufficient information to reproduce the test.

Do not claim dynamic verification when only static analysis has been performed.

---

# PART D — WORK SESSIONS AND DELIVERABLES

## 21. Session plan

Organize the project into the following logical stages.

These are milestones, not strict limits on the number or duration of working sessions.

### Stage 00 — Baseline and toolchain

- Verify ROM identity.
- Establish hardware characteristics.
- Verify tool availability.
- Prepare project directory.
- Configure the initial analysis environment.
- Generate baseline manifest and report.

### Stage 00A — External gameplay research

- Examine the manual.
- Study the walkthrough.
- Review the eight published stage maps.
- Construct a detailed gameplay reference.
- Identify documented contradictions and unresolved questions.
- Prepare a research checklist for ROM validation.

### Stage 01 — ROM architecture

- Parse ROM layout.
- Map PRG and CHR banks.
- Initialize disassembly.
- Recover vectors.
- Identify initial execution flow.
- Study MMC3 usage.

### Stage 02 — Program structure and RAM

- Reconstruct main execution flow.
- Map interrupts.
- Identify main systems and subroutines.
- Build the RAM map.
- Establish initial function cross-references.

### Stage 03 — Player and progression

- Player state and movement.
- Input and fighting techniques.
- HP/MP/EXP.
- Leveling.
- Damage and collision.

### Stage 04 — Pickups, RNG and magic

- Reward generation.
- RNG.
- Pickup object behavior.
- Spell acquisition.
- Spell effects and selection.

### Stage 05 — Stages and enemies

- Stage layouts and collision.
- Spawn systems.
- Entity structures.
- Enemy AI.
- Boss logic.
- Secrets and stage transitions.

### Stage 06 — Passwords and remaining gameplay

- Password system.
- Difficulty/quest variations.
- Death and continues.
- Menus, scoring and endings.
- Remaining gameplay subsystems.

### Stage 07 — Graphics and audio

- CHR data.
- Rendering.
- Animations.
- Sound and music engine.
- Relevant data formats.

### Stage 08 — Source reconstruction

- Organize assembly sources.
- Complete symbol mapping.
- Attempt exact ROM rebuilding.
- Record unresolved code and data.

### Stage 09 — Final verification

- Confirm binary equivalence where achieved.
- Audit documentation.
- Re-run selected experiments.
- Verify reproducibility.
- Produce final reports and checkpoint.

Subdivide stages where necessary.

Do not artificially terminate a stage before preserving useful findings.

## 22. Required project structure

Use an organized directory resembling:

    kickmaster-ntscu-re/
    ├── README.md
    ├── RESUME.md
    ├── manifests/
    ├── research/
    │   ├── RESEARCH_SOURCES.md
    │   ├── GAMEPLAY_REFERENCE.md
    │   └── SOURCE_DISCREPANCIES.md
    ├── reports/
    │   ├── stages/
    │   └── subsystems/
    ├── disassembly/
    │   ├── banks/
    │   ├── symbols/
    │   └── data/
    ├── maps/
    │   ├── ram/
    │   ├── rom/
    │   └── stages/
    ├── analysis/
    │   ├── functions.csv
    │   ├── symbols.csv
    │   ├── cross_references.csv
    │   ├── data_structures.csv
    │   ├── unresolved.csv
    │   └── evidence.csv
    ├── ghidra/
    ├── MesenCE/
    ├── assets/
    │   ├── graphics/
    │   └── audio/
    ├── scripts/
    ├── tests/
    ├── builds/
    └── checkpoints/

Adapt the structure as the investigation develops.

## 23. Evidence and report quality

Each identified routine or structure must have a traceable record.

Recommended fields include:

- Unique identifier.
- Human-readable name.
- Classification.
- PRG bank.
- CPU address.
- ROM offset.
- Size.
- Function or data description.
- Referenced RAM locations.
- Callers and callees where identified.
- Evidence.
- Verification status.
- Confidence.
- Remaining questions.

Provide reports in Markdown and machine-readable datasets in CSV or JSON.

Technical findings must remain understandable without access to the original chat conversation.

---

# PART E — CHECKPOINTS AND PERSISTENCE

## 24. Mandatory checkpoint system

**Checkpoint durability is a critical requirement.**

The user has previously experienced the loss of a substantial reverse engineering workspace after an environment reset.

Do not assume that the execution environment persists between Work sessions.

After each major stage and before any planned termination or transition, create a verified checkpoint.

Naming convention:

`kickmaster-ntscu-checkpoint-stageXX.zip`

Use distinct suffixes for sub-stages if required.

### Each checkpoint must contain

- Completed reports.
- Current project documentation.
- Source reconstruction progress.
- Symbol and function indexes.
- Memory maps.
- Relevant CSV and JSON files.
- Analysis scripts.
- Reproducible test cases.
- Ghidra projects or portable exports.
- MesenCE data and labels.
- Important intermediate results.
- Build scripts and configurations.
- Tool/version information.
- SHA-256 manifest.
- `RESUME.md`.

Do not require the user to re-run completed disassembly or tracing steps to reconstruct information already present in the checkpoint.

### ROM handling

Preserve the input ROM's hash and identification details.

Document whether the original ROM is included in the checkpoint or must be supplied again.

Do not silently replace, modify or redistribute the original ROM.

### Integrity verification

After creating each checkpoint:

1. Verify that the ZIP exists.
2. Verify that it is readable.
3. Test archive integrity.
4. Calculate the ZIP SHA-256.
5. Verify the included file manifest.
6. Perform a sample extraction of important files.
7. Confirm that the latest `RESUME.md` is present.
8. Record the result in the session report.

### ChatGPT Library persistence

When available, upload the checkpoint to ChatGPT Library.

After uploading, verify that the uploaded artifact is accessible and can be read back.

Do not report a successful Library checkpoint unless that operation actually succeeded.

If Library persistence is unavailable, provide the verified archive as a downloadable artifact and explicitly report the limitation.

Do not delete previous checkpoints without explicit user authorization.

### Preservation priority

If the session is running out of time, resources or execution budget:

**Preserve the current work before attempting additional analysis.**

An incomplete analysis with a valid checkpoint is preferable to additional findings that are lost when the environment resets.

## 25. RESUME.md

Maintain an up-to-date resume document containing:

- ROM identity and hash.
- Current milestone.
- Completed milestones.
- Last verified checkpoint.
- Workspace directory structure.
- Tool versions and setup instructions.
- Confirmed findings.
- Open hypotheses.
- Unresolved technical problems.
- Next concrete steps.
- Exact commands or procedures needed to resume.
- Artifact and manifest locations.

At the beginning of every resumed session:

1. Read `RESUME.md`.
2. Locate the latest checkpoint.
3. Verify its integrity.
4. Restore the required project files.
5. Check whether previous results can be reused.
6. Continue from the last verified state.

Avoid repeating completed work unless a specific discrepancy requires revalidation.

## 26. Session completion report

At the end of each milestone, report:

- Completed tasks.
- Newly documented routines and data.
- Important discoveries.
- Tests performed.
- What was not completed.
- Problems and uncertainty.
- Current reconstruction status.
- Checkpoint filename and SHA-256.
- Checkpoint verification result.
- Library persistence status.
- Downloadable artifact location.
- Recommended next milestone.

Do not claim that a checkpoint exists unless the file was created successfully.

---

# PART F — INDEPENDENCE AND COMPLETION

## 27. Independent research

The user maintains separate research notes about KickMaster.

Do not request those notes for the initial analysis unless essential to accessing the target ROM or validating its identity.

First produce independent findings.

This allows the user to compare the analysis with their own discoveries without introducing avoidable confirmation bias.

A later comparison stage may reconcile both analyses and document discrepancies.

## 28. Completion criteria

Aim for:

- Complete mapping of the ROM's known program and data regions.
- High-confidence identification of gameplay subsystems.
- Documented RAM and ROM maps.
- Extensive procedural labeling.
- Reproducible technical findings.
- Readable and annotated 6502 assembly.
- Importable symbols and useful debugger artifacts.
- A byte-matching ROM rebuild if technically achieved.
- Explicit documentation of all unresolved areas.
- Final reports and a verified downloadable checkpoint.

Do not claim complete reverse engineering solely because a ROM can be rebuilt.

Do not conceal uncertainty, unidentified code, unused regions or unsuccessful tests.

---

## 29. Immediate execution instructions

**Begin with Stage 00, followed by Stage 00A.**

First identify the supplied ROM and verify the available toolchain.

Then research and organize the known gameplay mechanics using the specified sources.

Create a technical baseline and research reference that clearly distinguish:

1. Published game behavior.
2. Behavior observed in an emulator.
3. Implementation confirmed in assembly.
4. Hypotheses still requiring investigation.

Prepare the project for subsequent comprehensive static and dynamic reverse engineering.

Create, test and expose the first downloadable checkpoint.

Continue into later milestones when resources and tool availability permit, but never prioritize additional analysis over preserving a valid, resumable working state.
