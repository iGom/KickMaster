# Stage 1: The Witches' Forest

Status: research baseline only; ROM extraction not started.

- Reference guide: [Wyrenth, Sector 1](https://gamefaqs.gamespot.com/nes/563430-kickmaster/faqs/19876).
- Published map: [sprays, Stage 1](https://gamefaqs.gamespot.com/nes/563430-kickmaster/map/3647-stage-1-map).
- Availability updated in02C: original PNG supplied by user, 3840 × 240 pixels, preserved without resampling.
- Local reference: `research/originals/sprays/KickMaster-Sector1-Witches'Forest.png`; SHA-256 `c336e76549d2adea9b934c5f2395a1853176b532ed1de56eee14554de1219bfc`.
- PNG integrity/dimensions checked; detailed visual and ROM-coordinate comparison remains pending.
- Priority investigation from the supplied specification: chest, boss reward and three-item drops.

Required outputs remain unknown: ROM tables, dimensions, metatiles, collision, spawn coordinates,
subarea links, hidden reward coordinates, boss IDs, camera limits, restart state and transitions.
Do not use an image pixel location as a ROM world coordinate without establishing the transform.

The Stage00A web-retrieval failure is historical. Current original bytes and fingerprints are recorded
in `research/originals_manifest.csv`. Original map pixels must remain unchanged; any future analysis
tiles must record source image, crop rectangle (x,y,width,height), and scale1:1.
