# Stage 8: Belzed's Haunted Tower

Status: research baseline only; ROM extraction not started.

- Reference guide: [Wyrenth, Sector 8](https://gamefaqs.gamespot.com/nes/563430-kickmaster/faqs/19876).
- Published map: [sprays, Stage 8](https://gamefaqs.gamespot.com/nes/563430-kickmaster/map/3654-stage-8-map).
- Availability updated in02C: original PNG supplied by user, 768 × 3600 pixels, preserved without resampling.
- Local reference: `research/originals/sprays/KickMaster-Sector8-Belzed'sHauntedTower.png`; SHA-256 `e6f0cf8ebbe8607b447d7e368117ce55b2111be81bef3aff717dd370a3faf522`.
- PNG integrity/dimensions checked; detailed visual and ROM-coordinate comparison remains pending.
- Priority investigation from the supplied specification: vertical camera kill boundary; guardian sequence; final transition.

Required outputs remain unknown: ROM tables, dimensions, metatiles, collision, spawn coordinates,
subarea links, hidden reward coordinates, boss IDs, camera limits, restart state and transitions.
Do not use an image pixel location as a ROM world coordinate without establishing the transform.

The Stage00A web-retrieval failure is historical. Current original bytes and fingerprints are recorded
in `research/originals_manifest.csv`. Original map pixels must remain unchanged; any future analysis
tiles must record source image, crop rectangle (x,y,width,height), and scale1:1.
