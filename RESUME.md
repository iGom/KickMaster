# Resume: KickMaster NTSC-U — Stage 02G

Current milestone: **Stage02G kind00 AI, death/drop generation and special-death lifecycles**.
Analysis and CPU tests: 2026-10-22; documentation/checkpoint closure: 2026-10-29.
This bounded milestone is complete locally. Archive SHA and later clean-build/save/readback
results live separately in stage02G.verification/reproducibility/persistence/readback.json and
KickMaster_STAGE02G_REPORT.md. This internal snapshot cannot attest to its own future upload.
Comprehensive reconstruction is still in progress. Continue in Polish.

Work independently from the original ROM. Do not use separate user RE notes or repository claims.
Governing documents: project_specification.md and PROJECT_UPDATES.md. Preserve the supplied Wyrenth
guide, original maps.zip and eight sprays PNGs byte-for-byte in every checkpoint, at native dimensions.
Future crops must retain scale 1:1 and parent coordinates. Do not repeat Stage00A for source availability.

## Input, workspace and tools

- Original: KickMaster (USA)(1).nes, 262160 bytes.
- SHA-256: `00ad4a0c6612319bb9f918ca36d6e93b4e5d996716c0570a3ec92bd60533881b`.
- SHA-1: e329254370f4a66b110fee46988da585989a586e; CRC32: EABD6104.
- Original Library identity: libfile_2cc3d8953cd4819194df7416ad5fa8bd.
- Original specification identity: libfile_ba372c00278c81918250e7f66698913c.
- Current project: /workspace/scratch/073d0612ec00/continuation-02G/kickmaster-ntscu-re.
- Current input: inputs/original.nes. Original/rebuilt ROMs are excluded from checkpoints.
  Recover the exact separate original; ask again only if unavailable. Never replace/normalize dump/header.
- NES2 mapper4/submapper0, NTSC, 128KiB PRG+128KiB CHR; 16×8KiB PRG. MMC3 mode0:
  R6 at8000, R7 atA000, fixed0E atC000, fixed0F atE000. Qualify switched addresses by bank.
- Python3; vendored py65 1.2.0 under tools/vendor. Linux x86_64 ca65/ld65 under tools/bin,
  recorded cc65 commit8d86ca7e7ed15300cc4bfaba61a40a3d00f3114d, V2.19-Git8d86ca7.

## Checkpoint chain and resume proof

Current snapshot name: kickmaster-ntscu-checkpoint-stage02G.zip. Read its separate receipts before
assuming any durability step remains. Do not overwrite or reupload a valid earlier checkpoint.
The last checkpoint fully verified before this internal snapshot was02F:

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
|02F|618f67d900fddd41b1d4dc4166a9f67ae24b6637db3dc631ecd26efb61909ca2|libfile_bf686b66ed9c8191bd03c7887310493e|

02B's missing sidecars were repaired in02C (manifests/stage02B_sidecars_readback.json).
02C persistence/report were completed before02D (manifests/stage02C_closure_readback.json).
02D,02E,02F were saved with all six sidecars and final receipt readback.
At02G resume the02F ZIP and six separate files were freshly materialized and hash-compared.
ZIP CRC, complete278-file manifest and full extraction passed; ZIP size4846323 bytes.
No old CPU/build rerun and no earlier archive reupload. Proof: manifests/stage02F_resume_verification.json.
All02F JSON sidecars are now included, with final report SESSION_REPORT_stage02F.md and full
historical RESUME_stage02F.md under reports/stages/. Earlier detailed findings remain there.

## Read first and current evidence

- reports/stages/SESSION_REPORT.md: internal02G pre-packaging report.
- reports/subsystems/ENEMY_AI_DEATH_AND_REWARDS.md: new detailed contracts, addresses and boundaries.
- Prior subsystem reports remain authoritative for their bounded scopes: MELEE_CONTACT_AND_ENEMY_DISPATCH,
  PLAYER_CONTROL_JUMP_AND_TERRAIN, PROJECTILE_COLLISION_AND_ENEMY_HITS, MAGIC_ACQUISITION_AND_EFFECTS,
  PROGRESSION_PICKUPS_MAGIC, PLAYER_SCENE_FOUNDATIONS, MAIN_LOOP_INPUT_STATE, BOOT_MMC3_INTERRUPTS.
  Do not rerun their suites automatically.
- analysis/reviewed_ranges.csv:274code+130data=404ranges;6790instructions;
  14318code+5520data=19838 reviewedPRGbytes,15.135192871% of128KiB. Local semantic coverage only.
- I01..I46 adds31code+15data ranges,769instructions,2164bytes and34indirectedges.
- RAM139roles,543symbols,480complete file-classification ranges;
  383indirect table edges,717deduplicated call/table graph edges.
- Full262160-byte local rebuild matches.19854 explicit source bytes include16-byte header;
  242306bytes remain input-dependent incbin slices. Exact rebuild is not complete reverse engineering.
- cpu_stage02G.json:15groups/4050savedobservations/11437trace rows,allPASS.
  No ROM patches or callee stubs. .partial.json retains each group; _vectors.csv and _trace.csv are included.
- CPU group counts:2560,224,90,72,64,3,105,357,96,63,4,120,24,12,256.
  Multicall lifecycle fixtures contribute several saved observations, not one case per individual AI call.
- New CSVs: enemy_state_and_drop_dispatch34; enemy_drop_choices64; enemy_drop_triplets64;
  collectible_spawn_profiles24; special_death_rewards12; special_death_scatter_pairs32;
  kind00_collision_frames45; enemy_distance_band_tables5; cross_bank_instructions1.
- Preserved older CPU results:01A57cases;01B18groups/2295vectors;02A18/10137;02B16/52382;
  02C18/16460;02D16/26832;02E14/11868;02F12/27126. None rerun for02G.
- dataset_audit.json validates current bytes/addresses/source coverage/tables and reads saved CPU results;
  it does not execute old suites. Historical unresolved/traversal scans are not whole-game unresolved counts.
- research/originals_manifest.csv covers guide,ZIP,8PNGs. Exact hashes/native dimensions preserved.
  Maps are available; PNG-to-ROM geometry and32scenes→8sectors comparison remains pending.
- Native MesenCE/Ghidra imports, full NES execution and NMI/IRQ timing remain NOT_TESTED.
  Portable exports and isolated CPU runs do not establish native imports or gameplay-frame timing.

## New contracts to preserve

1. Kind00 dispatcher0B:814C has normal0..5 and virtual6death/7hit/8quake.
   Collision06:8622 has only6state pointers,45frames total(8,1,9,9,9,9), ending90B4.
   Do not index collision records using virtual death/hit selectors.
2. Kind00 attack X window is signed enemy-minus-target **−32..−25 or24..31**, not abs24..31.
   Local attack selection has noYgate. Table81BE index(97+slot2C)&0F doesnot advance97.
   State0 movement every3calls; nonnegative36 selectsfallstate1. With terrain disabled,36=0.
   States2..4 take27calls, state5 takes18; these are selectedAIcalls, not video frames.
3. D4..D7 is target snapshot. 08:ABA8 skips copying C9..CC only if06BD=0B and0593nonzero.
   It doesnot test0596. Do not infer full decoy sprite-coordinate provenance.
   E393→EB63 uses selectors1(X)/3(Y); full thresholds/masks in subsystem report.
4. Ordinary80D5 suppresses bothdrop andscore if047Dbit10.0487bit40 independently suppresses sound51.
   Score once evenifdrop allocationfails; eight calls fromnormaldeath reset clearflags.
   Queued lethal hit uses virtualhit first; death starts followingcall.
5. OrdinaryDFCB 1UPgate:(DA&03)==0&&(D9&FC)==0 → single type6A.
   Otherwise seed(D8>>1)&31, indices seed,seed+10,seed+20mod32 (decimalincrements).
   DF37 specialtable has no1UPgate. No97advance. Correlated choices, notindependentdraws.
   D8 separatebytecounter;D9/DA separate16bitcounter, notone24bitcounter.
6. E01B drop: allocatorN−1..1; copyX,Y−16;vx0/vy−7,counter0,timer7.
   Firsttwo successes getvx−1/+1,vy−6. Stopfirstallocationfailure.
   E08D reward: pertypeprofilemayforceslot1evenactive;copyXY,vx/vy0,flagsFEDE|40.
   It leaves0593/05A7 unchanged andclobbersX; callerrestores2C.
7. One logicalSTA$0543,Y starts0E:DFFF (opcode99) andends0F:E001(operands4305).
   Source emitsphysical.byte fragments inbothfixedbanks. Indexcountsoneinstruction.
   prepare_sources/audit support exactlythis verifiedspan;E000/E001 arenotfunctionentries.
8. 0A8061 constructoruseslowestfreeenemyslotelsecurrent. subtype0437=kind−50,newkind5B,flags46990.
   ZfromD9D7 indicatesallocationoutcome. Clears473 butdoesnot initializecoordinatesor047D.
   Sharedanchor0189Y/018BX clampedcamera+30..B0(Y)/+30..D0(X),hex.
   Kind50death82C5creates5B; otheractivekind50 changesitto60 andsets047Dbit08.
   Alivekind50states0..3 unreviewed; no namedbossidentification.
9. 5B:8frames×16cycles=128calls,scoreonce,oddframescallscatter;firstcycle4triples(max12attempts).
   Final12-entryrewardtable8A91/8A9D,49=2,thenstate1wait100calls.
   CleanupsetsF8bit20onlyscene1B. 60callsscattereverycall:firstcycle8triples(max24attempts);
   128callssetsF8bit80unless047Dbit08,deactivates,zeros070A/B;nofinalrewardtable.
10. Scatter8AA9 uses32overlappingpairsfrom33bytes, not16words.
    Index((D8|024D)+97+carry)&31;carrynotcleared,dropcalleecanchangeit.
    Direction8B16[D8&3]=[2,0,3,1]. E44Emovement;E4ACterrainnotreviewed.
    Group15cycle1isolatesincomingcarry0/1. Constructorsleave473=0 inthese testedpaths.

Initial generator error and failedgroup7expectation are documented in analysis/stage02G_development_notes.json.
Only failedgroup7was retried;passedgroups1..6 retained,then new8..15executed.
The later attack-window annotation correction changed no observations or ROM bytes and didnotrerunCPU.

Prior02F essentials are retained in RESUME_stage02F.md: three separate collisionpaths,
101attackprofiles,99collisionkindpointers,64ordinary+29specialAIentries,HPaggregatealiasatslot9,
terrainprefix gatesonlytoC773/firstC776. Do not turn those boundedtestsinto fullterrain/AIclaims.
Prior02E cache05B8 address=((linearYmod240)&F0)|(Xlow>>4);DA3DreturnsROMattributeA/3Dbut3C03.
Scene00 has3840 actual samples over16pageentries,lastpage repeated; not4096pixeltraversablelength.

## Resume and selective reproduction

At a new resume read02Greceipts, freshlyread archive, compareSHA/CRC/fullmanifest/extraction,
verifyexactexternalROM, then reuse results. Do not rebuildold02G orrerunCPU merelybecauseofreset.
For a concrete new discrepancy only, examples:

```sh
python3 scripts/cpu_stage02g.py inputs/original.nes --groups 15
python3 scripts/audit_project.py inputs/original.nes
python3 scripts/build.py inputs/original.nes
```

Intentional source/index regeneration only (not routine resume):

```sh
python3 scripts/annotate_stage02g.py
python3 scripts/architecture_stage02g.py inputs/original.nes
python3 scripts/prepare_sources.py inputs/original.nes
python3 scripts/export_indexes.py
python3 scripts/build.py inputs/original.nes
```

02g replacesIseries only,preservesA..H. Oldgeneratorscanrewrite newtables; deliberate reconstruction
requires02b→02c→02d→02e→02f→02g after02a. Nevercasuallyrun oldarchitecture.py.
Builduses savedassembly, doesnotregenerateit, anddoesnotexecuteCPUgroups.
For each newcheckpoint run checkpoint.py NEW_STAGE,then checkpoint_reproducibility.py with a fresh
extractiondirectory,exactexternalROM,--stage NEW_STAGE. SaveZIP/verif/repro/RESUME andreadbackallhashes;
thencreatepersistence/reportfromperformedchecks,save/readback;finallysave/readbackreceiptitself.
No futurePASS orselfreferentialZIPhash. Inputs/builds/olderZIPsexcluded;originalreferencesincluded.

## Next concrete work — Stage02H

1. Finish C773→DBB7 and C776 effects, cache05B8 producers/mutation/refill. Start atactualROMcallers
   alreadyindexed; do not repeat02F prefix or02E scene00 lookup tests. Also resolveE4AC enemyterrain
   where useful to explain kind00 movement. Keep disabledterrainfixtures distinct from realgrounding.
2. Integrate camera/scenebounds and terrainstructures for all32configurations. Reconstruct native-scale
   geometry andcompare suppliedsprays originals. Establish transitions and32→8sector mappingfromROM
   evidence. Preserveparentcoordinates andoriginalPNGs;do not restart00A.
3. Continue alivekind50 andotherAI/resistances/companions, completeTwinPowertargetprovenance,
   actual0440/06BCdisplayconsumer, remainingD3/HPwriters,01A5producer,
   password07:B645/B693 andending09:A6E8..A6EE. Do notclaimglobalwriterinventory.
4. Finish08:ABC5split-scroll/A1/NMI/bankpreservation, alternateflightfamily, remainingmagic,
   graphics/audio andnativeNESvalidationwhenavailable. These remainopen.
5. Preserve nextsubstantialmilestone underdistinctname withalloriginalsources and02Gexternalreceipts.
   Verifycleanarchivedsourcebuild andfreshreadbackwithoutoverwritinganyoldcheckpoint.

02suffixes are bounded architecture/RAM continuations covering parts of logicalStages03–05.
They do not mean those comprehensive stages, or the full project, are finished.
