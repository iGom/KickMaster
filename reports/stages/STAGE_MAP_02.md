# Stage 2: The Caverns of No Return

Status: research baseline only; ROM extraction not started.

- Reference guide: [Wyrenth, Sector 2](https://gamefaqs.gamespot.com/nes/563430-kickmaster/faqs/19876).
- Published map: [sprays, Stage 2](https://gamefaqs.gamespot.com/nes/563430-kickmaster/map/3648-stage-2-map).
- Availability updated in02C: original PNG supplied by user, 3840 × 720 pixels, preserved without resampling.
- Local reference: `research/originals/sprays/KickMaster-Sector2-CavernsOfNoReturn.png`; SHA-256 `5e2c6bd4be0bbfc463dffaeba4440ab70e99b42be7db08493f7c14003a9caae3`.
- PNG integrity/dimensions checked; detailed visual and ROM-coordinate comparison remains pending.
- Priority investigation from the supplied specification: horizontal/vertical transitions; hidden boots; breakable terrain.

Required outputs remain unknown: ROM tables, dimensions, metatiles, collision, spawn coordinates,
subarea links, hidden reward coordinates, boss IDs, camera limits, restart state and transitions.
Do not use an image pixel location as a ROM world coordinate without establishing the transform.

The Stage00A web-retrieval failure is historical. Current original bytes and fingerprints are recorded
in `research/originals_manifest.csv`. Original map pixels must remain unchanged; any future analysis
tiles must record source image, crop rectangle (x,y,width,height), and scale1:1.
