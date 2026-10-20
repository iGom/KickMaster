# Stage 4: Bottomless Crevasse

Status: research baseline only; ROM extraction not started.

- Reference guide: [Wyrenth, Sector 4](https://gamefaqs.gamespot.com/nes/563430-kickmaster/faqs/19876).
- Published map: [sprays, Stage 4](https://gamefaqs.gamespot.com/nes/563430-kickmaster/map/3650-stage-4-map).
- Availability updated in02C: original PNG supplied by user, 3216 × 240 pixels, preserved without resampling.
- Local reference: `research/originals/sprays/KickMaster-Sector4-BottomlessCrevasse.png`; SHA-256 `18aa5866facf500de65b0e5a0d2b56cb7ebd6b2be7db40a45b88d67969056241`.
- PNG integrity/dimensions checked; detailed visual and ROM-coordinate comparison remains pending.
- Priority investigation from the supplied specification: pit boundaries and spell object.

Required outputs remain unknown: ROM tables, dimensions, metatiles, collision, spawn coordinates,
subarea links, hidden reward coordinates, boss IDs, camera limits, restart state and transitions.
Do not use an image pixel location as a ROM world coordinate without establishing the transform.

The Stage00A web-retrieval failure is historical. Current original bytes and fingerprints are recorded
in `research/originals_manifest.csv`. Original map pixels must remain unchanged; any future analysis
tiles must record source image, crop rectangle (x,y,width,height), and scale1:1.
