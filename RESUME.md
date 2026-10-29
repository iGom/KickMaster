# Resume: KickMaster NTSC-U

Current milestone: **Stage 02D projectile/collision and enemy-hit consumers complete as a bounded milestone**, 2026-10-21.
Stages 00, 00A, 01A, 01B, 02A, 02B and 02C retained. Comprehensive reconstruction is incomplete.
Continue in Polish. In prose use `$` for addresses, not numeric values; CSV retains explicit 0x notation.
Do not use separate user reverse-engineering notes as discoveries. Work independently from this ROM. Read PROJECT_UPDATES.md for later user instructions.
Original guide/maps must remain byte-preserved in every subsequent checkpoint.

## Exact input

- Original: `KickMaster (USA)(1).nes`, 262160 bytes.
- SHA-256: `00ad4a0c6612319bb9f918ca36d6e93b4e5d996716c0570a3ec92bd60533881b`.
- Original attachment identity: `libfile_2cc3d8953cd4819194df7416ad5fa8bd`.
- Specification attachment: `libfile_ba372c00278c81918250e7f66698913c`; copy in project_specification.md.
- Verified current input: `/workspace/scratch/073d0612ec00/continuation-02D/kickmaster-ntscu-re/inputs/original.nes`.
- Project: `/workspace/scratch/073d0612ec00/continuation-02D/kickmaster-ntscu-re`. Older scratch root is preserved, but is not the current project.
- NES 2.0, mapper 4/submapper 0, NTSC, 128 KiB PRG +128 KiB CHR; no trainer/battery/declared cart RAM.
- Recover this exact attachment after reset; request again only if unavailable. Never fetch another dump
  or normalize the header. Original and rebuilt ROMs are excluded from checkpoints.

## Checkpoints

This snapshot: `kickmaster-ntscu-checkpoint-stage02D.zip`.
Its final hash and save/readback identifiers live in the external stage02D report and receipts;
an archive cannot contain its own final hash or future upload result.

| Stage | SHA-256 | Saved identity |
|---|---|---|
|00|6c3b48030b66ae25e6fad9b21ca7c42904b1448a4c70d50d077df2ff45678e9f|libfile_9936c2d5304c8191af74afd619d8ec84|
|00A|88779ce28f16092345a6d87a084855b6b96731d8f75471a2228cfc6e1a82debf|libfile_a4d0d65a40b08191a53925e0b1ae05f0|
|01A|d4cf1e4e2e0f80f30e88545d574d5f57107498eb8654037f21e16e160a6d2c3a|libfile_cedece9827ac81919e818448c976beb2|
|01B|a0c1d35ed1d82a0a12db9ff25d4f625ffad5382f535908b3fbfc56d03847992d|libfile_eab08812e5048191af0b39db86eb0810|
|02A|1dfbc341acfa500072f21a1533ba6108088976ea03b1dbbcb3cceb141c2ee4e4|libfile_1fb1ef5971b4819186b37e5bcc003b93|
|02B|397afcb28be6c26ce6fa471b5270531162a4a62b61f810cc02d14681fd5ce07b|libfile_2de6444368d08191ad09d2e9fde8dec5|
|02C|9abf1f5c0bdbba3f264bb34ffd9112a5e3bb3803fcd1ba87e84e493e26650a3d|libfile_b0d3c38af9cc8191a1fa9757fe6b850e|

Previous snapshots were saved/read back/verified. Never overwrite/delete them. Receipts are in manifests/.
Stage02A was materialized at the start of02B through alias libfile_66e039ad85b08191b3f07f153c6f0afa
(file_0000000081fc81f5b0a9ef7fe4e4c448,version0);159 manifest files and matching workspace passed.
Original02A persistence identity above is preserved, not replaced by the materialization alias.

02B repair during the preceding02C session: existing 1762502-byte ZIP was downloaded and verified against the exact
expected hash, ZIP CRC and all177 manifest files. No reupload. Three missing separate reports were
created and downloaded again with exact byte equality; their copies and readback proof are in
manifests/stage02B.*.json and stage02B_sidecars_readback.json. Historical persistence-pending notes
in earlier reports are superseded by this actual verification. No earlier checkpoint was overwritten.
The02B clean build was reused from its retained prior execution; only saved sources/output were
compared again. Neither02B compilation nor its52382 CPU vectors were rerun.


02C durability closed on2026-10-21 before new02D work: the existing2597797-byte ZIP was
freshly materialized, SHA256 compared, CRC checked and all206 manifest members extracted/hash-checked.
No ZIP reupload. Newly saved stage02C.persistence.json and KickMaster_STAGE02C_REPORT.md were both
freshly downloaded and compared byte-for-byte. Exact identities/hashes are in
manifests/stage02C_closure_readback.json; their verified copies are manifests/stage02C.persistence.json
and reports/stages/SESSION_REPORT_stage02C.md. Existing02C verification/reproducibility/RESUME sidecars
were also read. Reused the successful clean02C build of2026-10-20; no02C compilation or CPU rerun.
The last prior fully closed checkpoint is02C. Consult separate02D receipts for post-archive gates.

## Read first, then reuse

- reports/stages/SESSION_REPORT.md and reports/subsystems/PROJECTILE_COLLISION_AND_ENEMY_HITS.md: latest Polish reports.
- Prior magic: MAGIC_ACQUISITION_AND_EFFECTS.md. Prior progression: PROGRESSION_PICKUPS_MAGIC.md. Foundations: PLAYER_SCENE_FOUNDATIONS.md,
  MAIN_LOOP_INPUT_STATE.md, BOOT_MMC3_INTERRUPTS.md. Historical session reports retained through02C, including its final durability closure.
- analysis/reviewed_ranges.csv:190 code+84 data ranges;9818+3127=12945 PRG bytes,9.876251220703125%.
- analysis/reviewed_instructions.csv:4611 instructions. New F01..F35 adds681 instructions/2127 bytes.
- maps/ram/ram_map.csv:131 local roles; analysis/symbols.csv:405 symbols; file classification:353 ranges.
  EnemyHP indexed slot9 aliases0440 accumulator; do not assume ten independent live enemies.
- progression_levels.csv:8 rows; pickup_effects.csv:24 paired types; selected_spell_dispatch.csv:13 entries.
- magic_unlock_menu_map.csv:12 rows; magic_acquisition_scene_routes.csv:32; magic_description_pointers.csv:12;
  magic_aim_and_velocity.csv:16. Description pointers explicitly resolve to R6=03, not source bank08.
- score_thresholds.csv:6 rows; numeric_formats.csv:5 counters; progression_snapshot_layout.csv:5 fields/11 bytes.
- scene_configurations.csv:32 rows; scene_configuration_pointers.csv:192 source/target mappings retained.
- player_state_dispatch.csv:111 normal+5 alternate pairs;22/3 unique targets; many handlers remain open.
- indirect_dispatch_tables.csv:224 table edges; reviewed_call_graph.dot:465 deduplicated edges.
- New projectile_collision_profiles.csv:32; projectile_object_dispatch.csv:32;
  player_hurtbox_profiles.csv:101; magic_collision_slot_limits.csv:13.
- scene_index_routes.csv:32 next/restart/continue mappings; eight named sector associations remain unresolved.
- cpu_stage02D.json and *_vectors.csv,*_trace.csv:16 groups/26832 vectors/117943 trace rows,all PASS.
  No ROM patch or callee stub. F_CPU13 zero-limit routes stop before unreviewed body contact A2C3.
  stage02D_test_development.json records corrected oracles and the concrete missing-evidence reason
  for rerunning ONLY newF_CPU11..13; all other already-passed groups were reused.
- Preserved cpu_stage02C.json:18 groups/16460 vectors/5906 trace rows,all PASS.
  No callee stubs; selection-prefix and presentation probes explicitly stop before unexecuted paths.
  Actual unlock→selection-prefix→initialization→first full object-update integration is covered.
- Preserved without rerun:01A57 cases;01B18 groups/2295 vectors;02A18 groups/10137 vectors;
  02B16 groups/52382 vectors. These are isolated CPU experiments, not full NES emulation.
- rebuild_verification.json:entire262160-byte image matches;12961 explicit bytes incl.header,
  249199 input-incbin bytes. Matching scaffold does not establish full semantics.
- MesenCE:405 MLB rows,source-backed syntax validation; actual import NOT TESTED.
- ghidra:bank-aware CSVs;PRG06 at8000 in collision R6 context; PRG07/08/09 atA000 in reviewed R7 contexts; no native project/import claim.
- research:51 historical external claims,29 experiment plans,5 untested passwords. Original user guide
  and eight PNG maps now available; map visuals/ROM geometry correspondence have not been analyzed.
  Sources retain their authorship and external-reference status. Guide Spells section was read for02C.
- research/originals_manifest.csv verifies10 source files:guide,original maps.zip,eight original PNGs.
  Do not rescale/overwrite originals. If cropping later, retain scale1:1 and parent image coordinates.

Historical candidate decode remains2924 instructions/6248 bytes,not semantic coverage. Statuses update
only at reviewed instruction starts. analysis/unresolved.csv is the old01A traversal's34 stops,not a global
count. New direct target banks are resolved in02B/02C/02D, but several target bodies remain unreviewed.

## Established findings

Hardware/loop retained:

- RESET/NMI/IRQ=PRG0F:F010/F0BB/F7B1. Reset maps R6=04/R7=05, mode0.
- Mapper D6C3 retries when interrupt epoch A6 changes. Far-call F4CA saves/restores bank tags.
- D90C waits for 95=0, sets1, services audio in banks00/01 and polls controller twice.
- Held20=sample1 AND sample2; pressed1F=held AND NOT old-held. Masks80/40/20/10/08/04/02/01=A/B/Select/Start/U/D/L/R.
- 97 changes in the wait loop and via D9CB/X; complete RNG roles remain unresolved.
- D046 has four phases, one handshake each. 9A is a scene index, not a loop-phase counter.
- CE80 drives counter decrement; D3 bit80 blocks Start. Counter-zero choice0 continues via D19A,
  other choice eventually JMP(FFFC). FF route at index1B increments030C unless equal03.

Retained 02A foundations:

- PRG07:A4E9 initializes camera/player; A537 loads 32 scene configurations. 03B9=B262[9A].
- A5AB uses 17 special-layout rows indexed04E2. Encoded bank bit7 increments camera X page,
  then R6 receives low 7 bits. Later A990/A6FE semantics remain unreviewed.
- Pointers in8000..9FFF use R6; A000..BFFF use R7=07. Scene 17 has R6=03 but
  B9/BA=07:B59A and palette=07:B563. Never assign all scene pointers to R6.
- CameraX=A7/A8, CameraY=A9/AA; PlayerY=C9/CA, PlayerX=CB/CC, all little-endian pixel values.
- F78B normalizes linearY into 240-line pages for high byte 00..0F (4096 tested inputs).
  AAB6 multiplies by F0 only in domain 00..80; 81..FF yield 0.
- DB direction bits2..1: down/up/right/left; bit01 dispatch enable, bit08 autostep, bit80 scroll-work gate.
- PRG08:AB19 clears transient D3 bit80; F8 bit20 branches to scene advance. Otherwise retains only CE bit01.
- ACF7 uses CE bit01 to choose table family. CD>>1 chooses CHR; CD&FE chooses metasprite/handler;
  CD bit0 is facing. Right wins over Left in three-sample input history.
- CurrentHP=06B9, display copy=06BA, bar capacity=06BB. 16 raw units/full cell, 2 raw units/partial step.
  Copy decreases immediately or rises 1 per B04B call. FDE0=40..B0 by10; D3&07 used on restore.
  Stage02B now traces pickup/healing clamps and the EXP level-up producer; other writers remain open.
- DDD9 ignores damage if D2 or 01A4 nonzero. Damage>HP starts death; equality yields 0 and hurt.
  Hurt sets D2=3C, D3bit20, CF0 and direction bit10 from incoming carry. Zero damage also triggers hurt locally.
- Fatal damage selects BA/BB. Five 15-update animation states lead CA/CB, then 15 more updates set CE80.
  Both facings tested through 90 complete player/draw updates, then actual D39F decrements 030E from 03 to 02
  and reaches D17A with A=01. Only final E154 fade is stubbed, not death or sprite code.
- Fall state C4/C5 adds 4 to Y; low-byte relative Y>=F0 sets CE80, not a full 16-bit distance test.
- DB02 terrain bit40/80 priority returns 3/0. Otherwise bit10 requests damage 9A+04 except 06BD=08/0593 nonzero.
  Sample helpers were stubbed in classification tests; complete terrain decoding remains open.
- B022 normal HUD phases 1..5 target B165,F681,B04B,B104,B0B0; negative A1 skips. NMI/transfer contract open.

## New 02B findings

- CurrentMP=EA..EC,EXP=ED..F0,nextEXP=F1..F4,maxMP=F5..F7. Each byte is60 hex+decimal digit,
  least significant first. ROM tables are most significant first. Score0306..030B uses bias20 hex.
- PRG08:A6AB/A6B4/A6BD add10/30/50 decimal EXP. A6C4 handles digit carry; overflow clamps9999
  and returns before level/sound. At threshold advance at most one level,maximum7.
- D3low3 is now confirmed level. PRG0F:FDA8 thresholds1000..7000,9999; FDC8 MPmax100..700,999;
  FDE0 HPmax40..B0 by10hex. Level-up changes maxima and next threshold,not current HP/MP/displayHP.
- A6FD uses unmaskedD3 for HP lookup after INC; later MP/EXP use D3&7. High-flag direct-entry probes
  read beyond eight HP entries; normal-gameplay reachability NOT ESTABLISHED. Collection gate blocksD3&A0.
- PRG08:A73D/A744 add5/10 decimal MP,cap to maximum.09:BD46 takes packed decimal cost inA;
  insufficient funds restores all3 MP bytes,carry1; successcarry0.01A5nonzero bypasses cost before D3bit80.
  Producer/activation of01A5 unresolved; do not call it a verified cheat/debug mode.
- PRG08:A78A heart adds10hex rawHP.09:BD98 clamps supported healing to06BB in valid domain;
  invalid rawHP can wrap8-bit ADC.06BA is not directly increased by these heals.
- 06BD selects13 effects through07:AE93:00 type70->09:B6BA costs60MP/heals20hexHP;
  01 type72->B6CD costs90MP/heals40hexHP;0C disables slot3. NewSelect1Fbit20 triggers both.
  Costs charged even at fullHP. Do not infer all spell names/acquisition order from selector IDs.
- 07:AE3A creates selected effect global slot3;09:BE90 runs objects;BF3E dispatches viaAAA5 sprites,
  AB87 handlers. Full first-two-heal integration executes actual frame,MP,HP,physics and sprite code.
- 08:A64D types40..6F ->24pairs.40HP,42/44MP,46/48/4AEXP,4Cscore100,4Escenetransition,
  50..67->A7DB (reviewed in02C),68/6E deactivate+damage4,6Aextraattempt,6Cdamage4withoutdeactivate.
- 08:A14F scans04EF..1 excluding0. Needsactive80,type40..6F,low-coordinate rectangle overlap,
  Yvelocity00..7F orFB..FF. Player-object difference: X[-13,12],Y[-20,26],modulo256;nohighbytes.
- 08:A05B gate may PLA/PLA/RTS to discard caller continuation.03D8/03D9 bothnonzero block;
  03D8nonzero/03D9zero mapsCHR R1=2 before D3&A0 gate. SP and unchangedPRG banks tested.
- Global object arrays have20byte stride. Pickup-relativeY =globalY+3. BE90 scans04EF+4 entries;
  E0ED allocator scans04EF-1..1. Producer/full range of04EF unresolved; tests useconfigured16.
- Level effect08:A878 type96,flags80,playerposition,velocityX0,YFD. Full pool does not cancellevelup.
- 0E:C746->D8B5 score: Ahighnibble increment,low3digitposition (11hex->10decimal,12hex->100).
  Thresholds0F:FDE8:10000,50000,100000,200000,500000,999999; offset030F+=6 on success even
  at attempts cap030E=0A. At mostoneaward percall. Scoreoverflow clamps999999 and skips award.
  Sentinel exactmatch beyond table tested as synthetic boundary,not claimed reachable exploit.
- Extraattempt guard is exact equality0A,not >=.0F:F681 stages level(D3&7)+60 and attempts030E+5F;
  HUD digit thereforeinternalattempts-1. Internal03 displays2,cap0A displays9; no new PPUvisualclaim.
- 07:AEC6 saves11bytes:06C2level,06C3HP,06C4..C6MP,06C7..CAEXP,06CB..CCflags from06BE/BF.
  AEF7 restores then tailsB7F4,which overwrites current/displayHP with fulllevelcapacity,leaves06BB,
  setsmaxMP,nextEXP and does not clampcurrentMP. B7F4 masksD3&0F;validdomain0..7.
  Full continue/password semantics await other callers. B829 returnscarry1iffcurrentMP>maxMP.

## New 02C findings and limits

- PRG08:$A831 maps types50..67 to ID=((type-50)&FE)/2 and sets bitID in $06BE/$06BF.
  $04E3 receives ID; pending $06C0 is filled if0C, otherwise $06C1 is overwritten.
  Acquisition does not change selected $06BD and does not immediately deactivate the pickup.
- Menu table07:$AC35 has cell→ID permutation [5,0,8,11,9,3,1,6,4,10,2,7].
  $AEA0 returns ownership in carry; $AEB6 reverse-searches cells11..1 then falls back to0.
  $ACBD uses Right/Left/Down/Up priority, no wrap and no fallback after blocked first direction.
- $AD03 requires new B and nonzero $01A5 to set $D3=(old&F0)|((old+1)&7).
  This local branch does not update HP/MP maxima. Producer of $01A5 remains unresolved.
- $AD65 rejects unowned IDs; owned selection writes $06BD then performs16 icon-tween updates
  before $AE3A. Tests stop at07:$AD81; complete tween/render synchronization remains unexecuted.
- 08:$BBAD acquisition animation starting $CF=0 reaches presentation on handler call96.
  $BD56 sets up presentation and uses12 text pointers in PRG03;32 post-presentation scene routes
  are exported. Full presentation rendering not executed. Routes are not yet eight-sector mappings.
- IDs02..0B activation/first update executed with original bytes, boundary MP/input cases and no
  callee stubs. Names are source correlations, not a claim to validate every external spell description.
- ID02 flight:10MP activation and each30 active handler calls; Select toggles off free. Negative
  $D3 exits before payment even with $01A5 bypass. Full player flight movement remains open.
- IDs05/06 projectile allocator scans global slots2..0 before charging3/5MP. Full pool costs nothing.
  Aim moves one step toward old target before computing new target from held-direction nibble.
- ID09 mask effect starts240-call counter and toggles $B8 bit20 on multiples4, then restoresFF.
  No hidden-object reveal has been demonstrated. ID08 boots starts high/low4/F0 and decrements
  on activation:1008 total handler invocations including activation; zero-low phases240/496/752/1008.
  Terrain guard checks selected08 AND nonzero lowcounter $0593. Reachable gameplay gaps not tested.
- ID07 quake controller cycles60 calls, sets $03D6 and requests via0E:$D7E7: first8 enemy-secondary
  flags skip bit20, others become(v&AF)|10; $03DC=1. This is not measured enemy stun duration.
- ID0A shield initializes $05A7=0A, follows player while counter nonnegative, then returns to ready.
  Counter consumers/hit budget remain unknown. ID0B decoy starts201 calls and clears on expiry/offscreen;
  enemy AI targeting it remains unreviewed.
- ID03 lightning phases8C→8E→90/92→94→76; spawns three bolt objects; actual bolt handlers open.
  ID04 columns occupy slots0..2 at cameraX+20/80/E0 (hex), expire at call30; slot0 calls09:$BD1B
  with A=6 at counters8/16/24. It queues $0441 only for eligible enemy flags, not immediate HP damage.
- All durations above are handler calls. The original02C scope excluded downstream damage/collision,
  shield budget and quake lifetime. New02D findings below supersede those specific open items;
  full game scheduling, PPU/NMI/IRQ timing, enemy AI and rendering remain open.


## Stage02D confirmed local findings

- PRG0F:E32A consumes0441 into0437 HP with unsigned saturation atzero when0469bit40 is set.
  It clears40, preserves pending20 and queued value, sets047Dbit80 and resets0455. E2F9 supplies
  pending gating and death/hit/quake/normal priority. Tested selector bases0/2/5, not every wrap case.
- E35B re-arms acceptance at0455=0A. Starting phase/recovery0 needs10 handler calls, with9 knockback
  steps;0423 resets after each active phase. Clear terrain-adjust path uses deltaX0/+2/-2, deltaY0.
- PRG08:A230 scans eligible enemies descending and one magic-projectile hit per enemy. Type<40
  indexes32 R6=06 profiles. Bit10 of057C preserves the projectile; otherwise collision consumes it.
  Selected03/0C scan slots1..0;05/06 scan2..0; other indices tail bodycontact A2C3. Lightning slot2 is
  absent from THIS path, despite three spawned segments. Do not generalize to all collision paths.
- R6=06 player collision has101 paired profiles; helpers use strict8-bit modular interval tests.
  Full collision→queue→HP tests use actual enemykind0/frame0; all profile bytes exported without
  claiming every profile/state reachable during gameplay. Projectile X endpoints clip to camera page.
- PRG08:A305 removes colliding enemy projectile before shield or HP handling. Selected0A decrements
  05A7; initial0A absorbs10 qualifying intersections, thenFF passes damage. Invulnerability can suppress
  HP loss after consuming the budget. No active-object-type check here, no blanket body/terrain protection.
- PRG0E:D7AD expires03DC from seed1 after240 calls; call210 adds secondary40 toentries flagged10,
  call240 clears10/40 fromfirst8. D6F0 invokes it onlyon oddD8. E2F9 uses10 as alternate state route;
  full stun behavior of every enemy/boss and real-time duration still unresolved.
- Pulse09:B55C grows everythird actual handler call to type0A/0B after15. FullBE90 loop withflags90
  andinitialD9=1 invokes it on alternating loops; tested48loops per facing, movement8 units per active call.
- Bounce09:B571 toggles type10/12 and rawdamage3/2; original terrain samplers independently reverse
  vx/vy. Tests use scene0 interior RAMcache cells00..03/08; full terrain/destruction decoding remainsopen.
- Lightning09:B5EF..B65D follows selectedslot3. Defaultcentral counter21 expires after92 dispatch calls;
  sidecounter8 after91. Synthetic sidecounter1 wraps and expires after3069 calls, not a reachable exploit claim.
- 35 new reviewed ranges:22code+13data;681 instructions/2127 bytes. Original-byte CPU execution plus
  new source build and dataset audit pass. Native MesenCE/Ghidra and fullNES timing remain NOT_TESTED.
- Original guide/maps unchanged. No map-to-ROM geometry comparison or sector assignment was claimed.

## Reproduce only when needed

Python3.12.14,vendored py65 1.2.0,Linux x86_64 ca65/ld65 V2.19 Git8d86ca7. Build prefers PATH,
then bundled executables. Original ROM is the only external input. Keep project basename.

```sh
python3 scripts/checkpoint.py --verify /path/to/kickmaster-ntscu-checkpoint-stage02D.zip
python3 scripts/build.py /path/to/original.nes
```

For a new checkpoint clean-extraction gate (use a fresh destination):

```sh
python3 scripts/checkpoint_reproducibility.py /path/to/new.zip /path/to/original.nes /fresh/parent /path/to/new.reproducibility.json --stage NEW_STAGE
```

For a concrete validation need:

```sh
python3 scripts/cpu_stage02d.py /path/to/original.nes
python3 scripts/audit_project.py /path/to/original.nes
```

Intentional regeneration only (can overwrite manual source edits):

```sh
python3 scripts/annotate_stage02d.py
python3 scripts/architecture_stage02d.py /path/to/original.nes
python3 scripts/prepare_sources.py /path/to/original.nes
python3 scripts/export_indexes.py
python3 scripts/build.py /path/to/original.nes
```

02d replaces F-series and retains A/B/C/D/E.02c replaces E-series; rerun02d after intentional02c regeneration.
02b replaces D-series; rerun02c and02d after deliberate02b regeneration.
02a replaces C and rewrites indirect tables: rerun02b then02c then02d after02a.
01b summaries/table exports are historical. architecture.py recreates01A only:do not casually run it.
Do not rerun all old CPU experiments without a concrete remaining risk. Build does not regenerate assembly.

## Next concrete work

1. Player movement/attack handlers PRG08:$B81D/$B8B5 and physics $BCEF; follow the collision/terrain
   services behind $C75B/$C773 using actual scene data. This continues main-plan player/physics work.
2. Body-contact path PRG08:$A2C3, full enemy/projectile kind/state/frame definitions, enemy scheduler
   D759 and actual enemy/boss state routines. Resolve0440 aggregate alias, resistances, drops and decoy AI.
   Do not repeat the now-complete local queued-hit/shield/quake consumers without a concrete new need.
3. Other $D3/HP writers and $01A5 producer; password path07:$B645/$B693 and ending HP writes
   09:$A6E8..$A6EE remain candidates. Menu07:$AD03 is reviewed; no complete writer inventory claimed.
4. Decode geometry, scroll transitions and spawn data; compare ROM outputs against original sprays PNGs.
   Establish coordinate transforms and32 scene→eight sector mapping from evidence. If crops are needed,
   retain original scale1:1 and parent coordinates. Do not restart Stage00A just because sources are available.
5. Finish08:$ABC5 split-scroll,$A1/NMI contract and bank preservation; native MesenCE/Ghidra imports,
   actual gameplay and fullNMI/IRQ timing remain untested, not PASS.
6. Preserve a distinct next checkpoint with reports, original sources, new02D external receipts and
   exact ROM identity; verify archive/manifest/extraction, clean build, durable save and fresh readback.

Still open: comprehensive combat,enemy/boss AI,drops/RNG,passwords,geometry and complete graphics/audio.
No full reverse-engineering completion is claimed. Do not equate CPU calls with measured seconds.
