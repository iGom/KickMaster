# Stage 7: A Long Way From Home

Status: research baseline only; ROM extraction not started.

- Reference guide: [Wyrenth, Sector 7](https://gamefaqs.gamespot.com/nes/563430-kickmaster/faqs/19876).
- Published map: [sprays, Stage 7](https://gamefaqs.gamespot.com/nes/563430-kickmaster/map/3653-stage-7-map).
- Availability updated in02C: original PNG supplied by user, 3072 × 240 pixels, preserved without resampling.
- Local reference: `research/originals/sprays/KickMaster-Sector7-LongWayFromHome.png`; SHA-256 `f627f431df1d683017e43b0b0434cc446397feb3da0406368b8190e74b7362cd`.
- PNG integrity/dimensions checked; detailed visual and ROM-coordinate comparison remains pending.
- Priority investigation from the supplied specification: spawn triggers and multiple boss encounters.

Required outputs remain unknown: ROM tables, dimensions, metatiles, collision, spawn coordinates,
subarea links, hidden reward coordinates, boss IDs, camera limits, restart state and transitions.
Do not use an image pixel location as a ROM world coordinate without establishing the transform.

The Stage00A web-retrieval failure is historical. Current original bytes and fingerprints are recorded
in `research/originals_manifest.csv`. Original map pixels must remain unchanged; any future analysis
tiles must record source image, crop rectangle (x,y,width,height), and scale1:1.
