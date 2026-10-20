# Stage 3: Belzed's First Stronghold

Status: research baseline only; ROM extraction not started.

- Reference guide: [Wyrenth, Sector 3](https://gamefaqs.gamespot.com/nes/563430-kickmaster/faqs/19876).
- Published map: [sprays, Stage 3](https://gamefaqs.gamespot.com/nes/563430-kickmaster/map/3649-stage-3-map).
- Availability updated in02C: original PNG supplied by user, 2560 × 720 pixels, preserved without resampling.
- Local reference: `research/originals/sprays/KickMaster-Sector3-Belzed'sFirstStronghold.png`; SHA-256 `2e7cb2076b17c6cbedb942367202f9a23ea1313dce449aa49137dc21dd2e7271`.
- PNG integrity/dimensions checked; detailed visual and ROM-coordinate comparison remains pending.
- Priority investigation from the supplied specification: branching hidden path; chests versus mimics; transforming entities.

Required outputs remain unknown: ROM tables, dimensions, metatiles, collision, spawn coordinates,
subarea links, hidden reward coordinates, boss IDs, camera limits, restart state and transitions.
Do not use an image pixel location as a ROM world coordinate without establishing the transform.

The Stage00A web-retrieval failure is historical. Current original bytes and fingerprints are recorded
in `research/originals_manifest.csv`. Original map pixels must remain unchanged; any future analysis
tiles must record source image, crop rectangle (x,y,width,height), and scale1:1.
