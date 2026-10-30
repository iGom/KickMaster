# Resume: KickMaster NTSC-U — Stage 02F

Current milestone: **Stage02F melee, body/secondary contact, AI entry dispatch and HP aggregate**, 2026-10-22.
This bounded milestone is complete locally. Final archive SHA and later clean-build/save/readback
results are separate files: stage02F.verification/reproducibility/persistence/readback.json and
KickMaster_STAGE02F_REPORT.md. This internal snapshot cannot attest to its own future upload.
Comprehensive reconstruction is still in progress. Continue in Polish.

Work independently from the original ROM. Do not use separate user RE notes or repository claims.
Governing documents: project_specification.md and PROJECT_UPDATES.md. Keep the supplied Wyrenth guide,
original maps.zip and eight sprays PNGs byte-for-byte in every checkpoint. Preserve native dimensions;
future crops must retain scale1:1 and parent coordinates. No repeat of Stage00A for source availability.

## Input, workspace and tools

- Original: KickMaster (USA)(1).nes, 262160 bytes.
- SHA-256: `00ad4a0c6612319bb9f918ca36d6e93b4e5d996716c0570a3ec92bd60533881b`.
- SHA-1: e329254370f4a66b110fee46988da585989a586e; CRC32:EABD6104.
- Original Library identity: libfile_2cc3d8953cd4819194df7416ad5fa8bd.
- Original specification identity: libfile_ba372c00278c81918250e7f66698913c.
- Current project: `/workspace/scratch/073d0612ec00/continuation-02F/kickmaster-ntscu-re`.
- Current input: inputs/original.nes. Original/rebuilt ROMs are excluded from checkpoints.
  Recover the exact separate original; ask again only if unavailable. Never replace/normalize dump/header.
- NES2 mapper4/submapper0,NTSC,128KiB PRG+128KiB CHR;16×8KiB PRG. MMC3mode0:
  R6 at8000,R7 atA000,fixed0E atC000,fixed0F atE000. Always qualify switched addresses by bank.
- Python3; vendoredpy651.2.0 under tools/vendor. Linuxx86_64 ca65/ld65 under tools/bin,
  recordedcc65commit8d86ca7e7ed15300cc4bfaba61a40a3d00f3114d, V2.19-Git8d86ca7.

## Checkpoint chain and resume proof

Latest snapshot: kickmaster-ntscu-checkpoint-stage02F.zip. Read its separate receipts before
assuming any durability step remains. Do not overwrite or reupload a valid earlier checkpoint.

| Stage | SHA-256 | Library identity |
|---|---|---|
|00|6c3b48030b66ae25e6fad9b21ca7c42904b1448a4c70d50d077df2ff45678e9f|libfile_9936c2d5304c8191af74afd619d8ec84|
|00A|88779ce28f16092345a6d87a084855b6b96731d8f75471a2228cfc6e1a82debf|libfile_a4d0d65a40b08191a53925e0b1ae05f0|
|01A|d4cf1e4e2e0f80f30e88545d574d5f57107498eb8654037f21e16e160a6d2c3a|libfile_cedece9827ac81919e818448c976beb2|
|01B|a0c1d35ed1d82a0a12db9ff25d4f625ffad5382f535908b3fbfc56d03847992d|libfile_eab08812e5048191af0b39db86eb0810|
|02A|1dfbc341acfa500072f21a1533ba6108088976ea03b1dbbcb3cceb141c2ee4e4|libfile_1fb1ef5971b4819186b37e5bcc003b93|
|02B|397afcb28be6c26ce6fa471b5270531162a4a62b61f810cc02d14681fd5ce07b|libfile_2de6444368d08191ad09d2e9fde8dec5|
|02C|9abf1f5c0bdbba3f264bb34ffd9112a5e3bb3803fcd1ba87e84e493e26650a3d|libfile_b0d3c38af9cc8191a1fa9757fe6b850e|
|02D|dbc9cf8ab43668c8042ed80dc25aeb966579968d7e7b8c39628d62b8af30609a|libfile_bcb9e2525a84819192dd9ba369387309|

|02E|1ae70fe401ac890e7e083e1c2ec4d5763e3ac314bf4b4ae698ccb1107f55759c|libfile_de8838c573c48191882debd818871feb|

02B's three missing sidecars were repaired in02C (manifests/stage02B_sidecars_readback.json).
02C persistence/report were completed before02D (manifests/stage02C_closure_readback.json).
02D and02E were fully saved, including all six separate sidecars and receipt readback.
Before this02F milestone,02E ZIP and six sidecars were freshly materialized and hash-compared;
ZIP CRC, complete251-file manifest and full extraction passed. No02E CPU/build rerun or reupload.
Proof: manifests/stage02E_resume_verification.json; all02E separate JSON files now included.
Final02E report and full historical resume: reports/stages/SESSION_REPORT_stage02E.md and
reports/stages/RESUME_stage02E.md. Earlier resumes retain detailed prior findings.

## Read first and current evidence

- reports/stages/SESSION_REPORT.md: internal02F session report.
- reports/subsystems/MELEE_CONTACT_AND_ENEMY_DISPATCH.md: new contracts and test boundaries.
- Prior subsystem reports: PLAYER_CONTROL_JUMP_AND_TERRAIN.md,
  PROJECTILE_COLLISION_AND_ENEMY_HITS.md, MAGIC_ACQUISITION_AND_EFFECTS.md,
  PROGRESSION_PICKUPS_MAGIC.md, PLAYER_SCENE_FOUNDATIONS.md, MAIN_LOOP_INPUT_STATE.md,
  BOOT_MMC3_INTERRUPTS.md. Reuse their evidence; do not rerun their suites automatically.
- analysis/reviewed_ranges.csv:243code+115data=358ranges,6021instructions;
  12651code+5023data=17674 reviewedPRGbytes,13.484191895% of128KiB. Local semantic coverage only.
- H01..H35 adds12code+23data ranges,397instructions,2480bytes.
- RAM133entries (nine roles refined),491symbols,429complete file-classification ranges;
  349indirect table edges,653deduplicated call/table edges.
- Complete262160-byte rebuild matches.17690 explicit source bytes include16-byte header;
  244470bytes remain input-dependent incbin slices. Exact rebuild is not complete RE.
- cpu_stage02F.json:12groups/27126vectors/5223trace rows,allPASS,no callee stubs or ROM patches.
  .partial.json saves each group; _vectors.csv and _trace.csv preserve observations.
- New CSVs: player_attack_profiles101, enemy_body_collision_shapes30,
  enemy_attack_collision_shapes48, enemy_kind_collision_pointers99,
  enemy_state0_collision_records99, player_hit_direction_table16,
  player_terrain_probe_flags32, player_foot_terrain_state_flags101, enemy_ai_dispatch93.
- Historical CPU evidence retained:01A57cases;01B18groups/2295vectors;02A18/10137;
  02B16/52382;02C18/16460;02D16/26832;02E14/11868. None rerun for02F.
- dataset_audit.json validates current byte/address/source/table consistency and reads saved old results.
  It does not execute old tests. unresolved.csv and fixed traversal summaries are historical bounded scans,
  not whole-game unresolved counts.
- Original-source manifest: research/originals_manifest.csv (guide,ZIP,8PNGs). Hashes and dimensions
  retained. Maps available; PNG-to-ROM geometry and32scenes→8sectors still pending.
- Native MesenCE/Ghidra imports and full NES execution remain NOT_TESTED. Portable exports are not
  evidence of successful native import. No gameplay-frame/NMI/IRQ timing claim from isolated CPU tests.

## New contracts to preserve

1. A197 melee, A2C3 body contact and A075 secondary enemy attack are separate paths.
   Flags469 requireC0;473low2 mustzero; descending scan. A075/A197 guard count0;A2C3 doesnot.
   A197 skips CE01 family. First overlapping target ends scan even with zero damage.
   Positive06:8328[CD>>1] queues0441,sets469bit20,updates047Dlow3. No local D3level multiplier.
2. A452 uses101physical attack profiles (not proof allstates reachable). Signed16-bit endpoints:
   any endpoint outside camera page0 maps to cameraorigin, including one beyond right edge.
   Final comparisons use strict modular8-bit sums. Profiles34..3A have zero geometry but damage1;
   enemy extent can still permit overlap. See independent oracle in cpu_stage02f.py.
3. Enemy kind→state pointer→four-byte frame: primarydamage,bodyshape,secondarydamage,attackshape.
   Kindtable06:855C has99entries00..62; bodyshapes30;secondaryshapes48. State/frame counts remainopen.
   A354 rejects X endpoints outside camera page; A0B0 only uses lowcoords and doesnot reject Xhigh.
   Kind0/state0/frame0 =00 00 06 00 at06:9000;state1/frame0 =06 00 00 00.
4. A5EC hitdirection uses signed low-byte deltas and ratio buckets; highcoords ignored.
   A075/A2C3 damage-direction carry is high-byte-less then low-byte compare, not ordinary16-bit compare.
5. D759 matches slotparity to06F9: matching skipsAI thenaggregates/render; opposite chooses
   R6=0B forkind<46,else0A. Caller requiresR7=0D. Tests stop beforeAI8000/renderA000.
6. Ordinary0B:8011..8091 table64entries00..3F;special0A:8017..8051 table29entries46..62.
   Storedpointer+1 is executed viaPHA/PHA/RTS;2C reloadsslot. All93dispatches CPU-checked onlytoentry.
   Following bytes arecode. Schedulerthreshold46 doesNOTvalidate kinds40..45. Bodiesnotreviewed.
7. D78B sums0437,X into0440 forkind>=50 except5B/60;capAFhex inclcarry. Slot9aliases0440anddoublesit.
   D6F0copiesaggregate to06BC. Do notlabel unconditionallybossHP orclaim10independentHPslots.
8. A1E8 sceneA8A6/strength8457 gates C773;838D givesY,83F2 givesX negatedforoddCD,2Cstrength.
   A120 sceneA8C6/stateA8F2 gates feet at-6/+6,Y+2. CPUtests stopatfirstC776 only;
   secondcallstatic. A8F2sharedwithlastF16entry;only100newbytespromoted;physicalfullarrayendnotproven.

Prior02E essentials: CDpairs/facing, CE01family, D1jump phase notvelocity; E7launch; B80A13steps;
Ainput80/B40; groundinputpriority and attacktiers alreadytested. No manualtechniquenamesassigned.
Cache05B8 uses((linearY mod240)&F0)|(Xlow>>4). DA3DreturnsactualROMattributeA/3D but3C03;
C75BpreservesA;C767/DB02classifies3C onROMpath. Scene00 table has3840actualsamples over16pageentries,
lastpage repeated; not proof4096pixeltraversablelength. Full prior details in02Eresume/report.

## Resume and selective reproduction

At resume: read02Freceipts, freshlyread archive,comparehash/CRC/fullmanifest/extraction,verifyexactROM,
then reuse evidence. Do not rebuildold02F orrerunCPU merely because an environment was reset.
To verify a concrete new issue, commands are:

```sh
python3 scripts/cpu_stage02f.py inputs/original.nes --groups 10
python3 scripts/audit_project.py inputs/original.nes
python3 scripts/build.py inputs/original.nes
```

Only for intentional regeneration of02Fproducts (not routine resume):

```sh
python3 scripts/annotate_stage02f.py
python3 scripts/architecture_stage02f.py inputs/original.nes
python3 scripts/prepare_sources.py inputs/original.nes
python3 scripts/export_indexes.py
python3 scripts/build.py inputs/original.nes
```

02f replacesHseries only, preservesA..G. Earliergenerators can rewrite later tables: if deliberately
reconstructing old indexes, apply02b→02c→02d→02e→02f after02a. Do not casually run oldarchitecture.py.
Builduses savedassembly anddoesnot regenerateit. CPUgroups are notpartofbuild.
For each newcheckpoint, run checkpoint.py NEW_STAGE then checkpoint_reproducibility.py with fresh
extractiondirectory,exactexternalROM,--stage NEW_STAGE. SaveZIP/verif/repro/RESUME,readbackhashall;
thencreatepersistence/reportfromperformedchecks,save/readback;finallysave/readbackreceiptitself.
No futurePASS, no self-referentialarchivehash. Original/builds/inputs/olderZIPs excluded.

## Next concrete work — Stage02G

1. Follow actual AI targets nowindexed in enemy_ai_dispatch.csv. Start ordinary0B:814C (kind00)
   and a concrete special-kind path chosen from ROM callers. Resolve kind/state/frame validity,
   entry/animation synchronization, E2F9 hit/death continuation, reward generation and slot lifetimes.
   Maintain independence; no imported userRE conclusions. Do not repeat dispatch-only tests.
2. FollowC773→DBB7 and C776 completely, cache05B8 mutation/producers/refill. Current02F tests only
   establish arguments and gates. Trace callers to avoid assigning intended terrain behavior prematurely.
3. Integrate camera/scenebounds and terrain structures for all32 configurations; reconstruct native-scale
   geometry and compare sprays originals. Establish transitions and32→8sector mapping from evidence.
   Preserve coordinates and PNG originals; don'trepeatStage00A or scene00completedlookup tests.
4. Continue bossAI/resistances/drops/decoytargeting, actual0440/06BCdisplayconsumer, remainingD3/HPwriters,
   01A5producer,password07:B645/B693,ending09:A6E8..A6EE. Do notclaim globalwriterinventory.
5. Complete08:ABC5split-scroll/A1/NMI andbankpreservation, alternateflightfamily, remainingmagic,
   graphics/audio andnativeNESvalidation whenavailable. These remainopen.
6. Preserve next substantial milestone underdistinctcheckpointname withalloriginalsources and02Fexternal
   receipts. Verifycleanarchivedsourcebuildandfreshreadbackwithoutoverwritinganyoldcheckpoint.

The02suffixes are bounded continuations of architecture/RAM analysis, covering parts of logicalStages03–05;
none constitutes completion of those comprehensive stages or the full project.
