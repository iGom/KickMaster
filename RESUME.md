# Resume: KickMaster NTSC-U — Stage 02E

Current milestone: **Stage02E normal player control, jump phases and terrain lookup**, 2026-10-21.
This bounded milestone is complete locally. The archive's final SHA and post-save/readback
results are recorded in separate02E verification/reproducibility/persistence/readback files and
KickMaster_STAGE02E_REPORT.md. Do not infer future persistence from this internal snapshot.
Comprehensive reconstruction is not complete. Continue in Polish.

Work independently from the supplied ROM; do not import separate user RE notes/repository claims
as discoveries. Read `project_specification.md` and `PROJECT_UPDATES.md` for governing instructions.
The original Wyrenth guide, maps.zip and eight sprays PNGs must remain byte-preserved in every checkpoint.
Do not rescale/overwrite originals. Any later crop must keep scale1:1 and parent coordinates.

## Exact input and working directory

- Original: KickMaster (USA)(1).nes;262160 bytes.
- SHA-256: `00ad4a0c6612319bb9f918ca36d6e93b4e5d996716c0570a3ec92bd60533881b`.
- SHA-1: `e329254370f4a66b110fee46988da585989a586e`; CRC32:EABD6104.
- Original Library identity: `libfile_2cc3d8953cd4819194df7416ad5fa8bd`.
- Specification identity: `libfile_ba372c00278c81918250e7f66698913c`; local unchanged copy project_specification.md.
- Current project: `/workspace/scratch/073d0612ec00/continuation-02E/kickmaster-ntscu-re`.
- Current input: current project + `/inputs/original.nes`.
- Older scratch roots are historical, not this snapshot. After reset restore a fresh directory from02E.
- NES2.0 mapper4/submapper0,NTSC,128KiB PRG+128KiB CHR. MMC3mode0,16×8KiB PRG.
  R6 is8000,R7 isA000,fixed0E isC000,fixed0F isE000. Keep explicit bank contexts in all references.
- The original and rebuilt ROMs are excluded from archives. Recover this exact separate attachment;
  ask for it again only if unavailable. Never substitute a different dump or normalize the header.

## Checkpoint chain and resume verification

This snapshot: `kickmaster-ntscu-checkpoint-stage02E.zip`.
Read its separate receipts before deciding whether any durability step remains unfinished.
The archive cannot contain its own final hash or later upload outcome. Never overwrite earlier checkpoints.

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

02B's three separate files were repaired and read back in02C; proof:
`manifests/stage02B_sidecars_readback.json`. No valid02B ZIP reupload.
02C persistence/report were completed and read back before02D; proof:
`manifests/stage02C_closure_readback.json`. No valid02C ZIP reupload.
02D was fully closed, including all six sidecars. At the start of02E the original02D ZIP and
six sidecars were freshly materialized and compared to their recorded hashes. ZIP CRC, complete
228-file manifest and full extraction all passed. No02D CPU or build rerun, no archive reupload.
Proof:`manifests/stage02D_resume_verification.json`; prior receipts `stage02D.*.json` are now included.
The separately completed02D report is `reports/stages/SESSION_REPORT_stage02D.md`.
Historical full02D resume is `reports/stages/RESUME_stage02D.md`; use for detailed prior findings.

## Read first and reuse

- `reports/stages/SESSION_REPORT.md`: current02E internal session report.
- `reports/subsystems/PLAYER_CONTROL_JUMP_AND_TERRAIN.md`: new findings, caveats, tables and tests.
- Previous subsystem reports: PROJECTILE_COLLISION_AND_ENEMY_HITS.md, MAGIC_ACQUISITION_AND_EFFECTS.md,
  PROGRESSION_PICKUPS_MAGIC.md, PLAYER_SCENE_FOUNDATIONS.md, MAIN_LOOP_INPUT_STATE.md, BOOT_MMC3_INTERRUPTS.md.
- `analysis/reviewed_ranges.csv`:231 code+92 data ranges;11855 code+3339 data=15194 PRG bytes,
  11.592102051% of128KiB PRG. This is bounded local semantic coverage, not whole-game completion.
- `analysis/reviewed_instructions.csv`:5624 instructions. G01..G49 adds1013 instructions/2249bytes.
- RAM map:133 local entries;symbols:456;exhaustive file classification:401 ranges;
  indirect dispatch table edges:256;deduplicated call/table graph:563 edges.
- Current rebuild matches all262160bytes.15210 explicitsource bytes include16-byte header;
  246950bytes are input-dependent incbin slices. Matching scaffold does not imply allcodeunderstood.
- `player_direction_dispatch.csv`:32 split pointers. `player_air_attack_selection.csv`:256 cases.
- `player_jump_step_table.csv`:13 entries. `player_attack42_sequence.csv`:33 entries.
- `scene_terrain_cache_flags.csv`:32 flags. `scene00_terrain_samples.csv`:3840 actualROM samples,
  16 pageorder entries (last repeats0E), not evidence of4096-pixel traversable length.
- `player_state_dispatch.csv`:111 normal+5 alternate state pairs;normal00..B8 handlers now reviewed.
  Alternate-family flight and caller-dependent reachability remain incomplete.
- Retained scene_configurations.csv:32;scene_configuration_pointers.csv:192 mappings.
- Retained progression8,collectible24,selectedeffects13,unlock/menu12,acquisitionroutes32,scorethresholds6,
  projectileprofiles32,playercollisionprofiles101,projectilehandlerpairs32,slotlimits13.
- `analysis/cpu_stage02E.json`:14groups/11868vectors/34866tracerows,allPASS,nocalleestubs,nopatches.
  `cpu_stage02E.partial.json` preserves each group immediately for selective continuation.
  `stage02E_development_notes.json` records initialfixturefailure and duplicate-range assertion.
- Saved earlier CPU results remain untouched:01A57cases;01B18groups/2295vectors;
  02A18/10137;02B16/52382;02C18/16460;02D16/26832. No old suite rerun.
- `analysis/dataset_audit.json`: byte-address/table/source/coverage checks; reads old result files,
  does not execute old tests. `analysis/unresolved.csv` remains historical01A traversal stops,
  not a global unresolved-function count. Fixed-window candidate traversal is also historical.
- `research/originals_manifest.csv`:10 files (guide,originalZIP,8PNGs) with hashes/dimensions.
  Stage00A map-access failure is historical; files now available. PNG-to-ROM comparison remains pending.
- Native MesenCE/Ghidra import and full NES execution are NOT_TESTED. Portable labels/maps are available;
  syntax checks are not successful native imports. Tool details in manifests/analysis_toolchain.json.

## Important new contracts

- ACF7 takes family selector in A; normal family=0. Reinitialise A on each isolated dispatch call.
- New A wins B on the ground. Standingdirection masks1/2/4 startwalkright/left/crouch;
  other masks use sharedRTS. Walk andhorizontalmotion use current|history1|history2;rightwinsconflict.
- Walking advances every8calls for low normalstates; SBC07inheritscarryfromoldCDbit7.
- Attacktier selection:BC56 levels0..3=>1E,4..5=>2C,6..7=>7E. BCBE level7=>42,
  elselevel>=3withhorizontal=>5C,elseAC. BC34 level>=5withmatchingfacing=>A0,D1=80.
  DownairBC81 level>=1=>1C;grounddownBC99 level>=2=>A0. DirectBCAE bypassesslidingreplacement.
- Do not yet equate these IDs to manualtechnique names. Fullhitboxes/damage/cancellation remainopen.
- Attackcalls:12..1A15;1E..2A28;2C..4044;42sequence32;5C..7C51;7E..9E51;AC..B618;
  A0..AA36 inclearfixture,96pixelhorizontaltravel. B8tableentrydoesnotaddanormalACphase.
- D1 isphase+flags, notsignedvelocity. JumpseedE7 thenimmediateup3. Ascentbit40;
  heldnegativephase usesup3 whileA/historylow2. Releaseseeds40withoutYstep.
  Taper table B80A=3×4,2×4,1×4,0. Upincrementsbeforelookup;downusesoldindexbeforedecrement.
  Ceilingbit02;floorbit01. Normalphaseindices0..12 only. No conversiontocycle/secondtiming.
- CE40 ismotionmarker, notproof ofdisplacement: slowterrainCE04 onoddD8 skipsXtranslationbutsets40.
- Cache05B8 index=((linearY mod240)&F0)|((X&FF)>>4);16columns×15validrows.
  Classifier/refill determineworldpage. Refill andmutableterrainproducersstillopen.
- ROMlookup DA3D: B9bytepageorder,BB64-bytepages,C1fourattributes/metatile. Save/restoreR6andX.
  F50D adds64*pageID using32-entrytables. Allscene bounds/verticalconfigurationsnotyetvalidated.
- Crucialreturncontract: DA3D returnsactualattributeA/3D but3C=03. C75BpreservesA;
  C767/DB02classifies3C andreturns03onthatROMpath. CachepathA/3Careequal.
- DD5Fflagsbypasscoordinatechecks forsceneindices7,11,14,18,19,22,23,24,25decimal.
  DD92fragmenthasnopathfromreviewedDD5Fentry; do notclaimitschecksareactive.

## Commands and tool setup

Python3; vendoredpy651.2.0 under tools/vendor; ca65/ld65 binaries under tools/bin (Linuxx86_64).
Recordedcc65commit8d86ca7e7ed15300cc4bfaba61a40a3d00f3114d,versionV2.19-Git8d86ca7.
No runtimeinstall is needed for savedsourcebuild on this environment.

At resume, verify newZIP hash/CRC/fullmanifest/extraction and exactROM, reuse saved evidence.
For an actual new validation need:

```sh
python3 scripts/audit_project.py inputs/original.nes
python3 scripts/build.py inputs/original.nes
```

Do not automatically rerun CPU. Only if required:

```sh
python3 scripts/cpu_stage02e.py inputs/original.nes --groups 14
```

Intentional regeneration of current02E products, not routine resume:

```sh
python3 scripts/annotate_stage02e.py
python3 scripts/architecture_stage02e.py inputs/original.nes
python3 scripts/prepare_sources.py inputs/original.nes
python3 scripts/export_indexes.py
python3 scripts/build.py inputs/original.nes
```

02e replaces G-series and preservesA..F. Earliergenerators can rewrite laterindexedtables;
if deliberately regenerating earlier stages, apply02b→02c→02d→02e after02a and regenerateexports.
Do not useoldarchitecture.py casually; it creates01A-only products. Builddoesnotregeneratesources.
Newcheckpoint gate:

```sh
python3 scripts/checkpoint.py NEW_STAGE
python3 scripts/checkpoint_reproducibility.py /path/new.zip /path/exact-original.nes /fresh/parent /path/new.reproducibility.json --stage NEW_STAGE
```

Then save newZIP andseparateverification/reproducibility/RESUME;freshlyreadback/hashcompare.
Createpersistence/reportfromcompletedchecks;save/readbackthem;recordseparatereceiptandverifyitsownreadback.
Never markfuturechecksPASS. OriginalROM, rebuiltROM,inputs/builds/checkpoints excludedfromZIP.

## Next concrete work — Stage02F / continued player-combat work

1. Continue bodycontact/attack resolution atPRG08:A2C3 and its realcallee/datachain; distinguish
   playerattack hitboxes and damage from the alreadyreviewed playerhurtbox/profile tables.
   Follow actual callers before assigning manualtechnique names to newlyreviewedstateIDs.
   Do not repeat localmovement,attackselection,queuedhit/shield/quake tests withoutnewreason.
2. Resolve fullenemy/projectile kind/state/frame definitions and schedulerD759; examineactualAI,
   bosslogic,resistances,drops,decoytargeting.0440 aliasesHPindexedslot9 andpassaccumulator;
   thealias andglobalnumberofindependentliveenemies remainopen.
3. FollowC773→DBB7 andrelatedterrainmutation;producers/refillof05B8cache;integratecamera limits
   andscrolling withrealconfigurations. ExtendcurrentROMstructuretoall32scenes withbounds,
   thencompareoriginalspraysmaps atnativecoordinates;establish32scenes→8sectorsfromevidence.
   Scene00sampletableisnotyetacompletevisuallevelreconstruction. Do notrestartStage00A.
4. OtherD3/HPwriters,01A5producer;password07:B645/B693;endingHP09:A6E8..A6EE remaincandidates.
   Menu07:AD03andknownprogression/selectionpathsarealreadyreviewed;noglobalwriterinventoryclaim.
5. Finish08:ABC5split-scroll,A1/NMIcontract,bankpreservation;alternateflightfamily;remainingmagic.
   NativeMesenCE/Ghidraandrealgameplay,NMI/IRQtimingareNOT_TESTED.
6. Preserveeachsubstantialnextmilestone,includingalloriginalsourcesandthese02Eexternalreceipts,
   underadistinctname;verifyarchiveandcleanbuild,persistandfreshreadbackwithoutoverwritingolderZIPs.

Stillopen: comprehensivecombat,AI,bosses,drops/RNG,passwords,geometry,graphics/audio andfullsourceunderstanding.
Do not equate exactbinaryrebuild or CPUcalls withfullgameverification.
