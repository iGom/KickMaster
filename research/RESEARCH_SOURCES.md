# Research sources

Access date: 2026-10-19. `source_index.csv` is the machine-readable access/status index.
`gameplay_claims.csv` separates source reading from ROM verification. The seed reference tables were
supplied by the user in `project_specification.md`; each cross-check records a source location.
Stage02C preserves the full guide and all eight original PNGs explicitly supplied by the user,
plus maps.zip, unchanged, as requested for this private project checkpoint. The manual is not bundled.
Integrity and dimensions are recorded in originals_manifest.csv; reference bytes are not ROM evidence.

## Source hierarchy and access

1. **Taito manual**: https://www.digitpress.com/library/manuals/nes/Kickmaster.pdf
   Primary published gameplay reference. Downloaded successfully; 12 scanned PDF spreads. Read relevant
   printed pages 5-22 visually (PDF pages 3-12); text extraction produced no usable text. Printed page 8
   is PDF page 5, not PDF page 8. The PDF fingerprint is in `manual_metadata.json`.
2. **Wyrenth guide**: https://gamefaqs.gamespot.com/nes/563430-kickmaster/faqs/19876
   Secondary observations. Direct HTTP returned 403; search-index-backed reading succeeded for controls,
   screen, progression/passwords, items, kicks, spells and stage sections. Site wrapper says v1.1/2003;
   document body/history says v1.1b/2017. Preserve both in citations rather than silently choosing a date.
3. **sprays maps**: https://gamefaqs.gamespot.com/nes/563430-kickmaster/faqs
   All eight entries independently verified in the listing. Stage 3 and 5 landing pages also retrieved.
   Stage00A image access was blocked. Since02C all eight user-supplied original PNGs are available
   with checked integrity/dimensions. Detailed visual/ROM comparison remains pending; exact paths,
   dimensions and hashes are in `stage_map_index.csv`. Use them during geometry/scroll/spawn work.
4. **GameFAQs cheats**: https://gamefaqs.gamespot.com/nes/563430-kickmaster/cheats
   Community test vectors. Search-backed reading succeeded after direct HTTP 403.
   Password acceptance, advertised state and quest counts are not ROM-verified.
5. **NesCartDB**: https://nescartdb.com/profile/view/2564/kick-master
   Primary cartridge inspection record: PRG/CHR CRCs match this input; PCB and mapper revision remain
   reference hardware properties. See Stage 00 for the comparison.
6. **MobyGames**: https://www.mobygames.com/game/18675/kick-master/
   HTTP 403. No new claims adopted from this inaccessible page.
7. **NESdev**: https://www.nesdev.org/wiki/NES_2.0 ; https://www.nesdev.org/wiki/MMC3 ;
   https://www.nesdev.org/wiki/Programming_MMC3
   Technical format/hardware documentation. Search-backed content retrieved; direct page access 403.
8. **GhidraNes**: https://github.com/kylewlacy/GhidraNes
   Official extension documentation. MMC3 is listed; bank-switch control flow still requires manual
   work. README advertises iNES 1.0, so acceptance of this NES 2.0 header must be tested rather than assumed.
9. **MesenCE**: https://github.com/nesdev-org/MesenCE
   Official emulator repository. It is the preferred full-system validation target; currently unavailable
   locally. Do not label custom CPU harness results as Mesen validation.

## Interpretation rules

- Numeric facts, canonical names and acquisition expectations are organized from the user-supplied scope.
- An external description does not establish a RAM encoding, internal ID, routine address or timing.
- The manual outranks the guide for official descriptions; actual executable behavior resolves conflicts.
- A boss's estimated number of kicks is not a measured HP value or single-hit damage value.
- Map names, guide names, manual names and future ROM IDs need separate columns.
- Unavailable source material is an explicit gap, not a license to fill in details from memory.

## User-supplied originals — update 2026-10-20

The full Wyrenth text and maps.zip arrived during02C. This is an availability update, not a rerun
of Stage00A. Original TXT, ZIP and eight PNG payloads are preserved byte-for-byte. Full reading of
the new text is not implied by header/integrity checks. Use targeted sections when investigating
spells, enemies, objects and routes. Map geometry, pixel/world transforms and the32-scene/eight-sector
mapping must be derived from ROM evidence before assigning coordinates or scene identities.
Future crops, if needed, use original scale and explicit source rectangles; originals stay untouched.
