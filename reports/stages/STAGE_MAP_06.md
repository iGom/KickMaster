# Stage 6: Across the Swamps

Status: research baseline only; ROM extraction not started.

- Reference guide: [Wyrenth, Sector 6](https://gamefaqs.gamespot.com/nes/563430-kickmaster/faqs/19876).
- Published map: [sprays, Stage 6](https://gamefaqs.gamespot.com/nes/563430-kickmaster/map/3652-stage-6-map).
- Availability updated in02C: original PNG supplied by user, 3840 × 240 pixels, preserved without resampling.
- Local reference: `research/originals/sprays/KickMaster-Sector6-AcrossTheSwamps.png`; SHA-256 `89b5042ad2aa3598d5c300a5121631abf1b5d5c4b33fc35d804fe50a73c3268f`.
- PNG integrity/dimensions checked; detailed visual and ROM-coordinate comparison remains pending.
- Priority investigation from the supplied specification: slow terrain; hidden shield; paired bosses.

Required outputs remain unknown: ROM tables, dimensions, metatiles, collision, spawn coordinates,
subarea links, hidden reward coordinates, boss IDs, camera limits, restart state and transitions.
Do not use an image pixel location as a ROM world coordinate without establishing the transform.

The Stage00A web-retrieval failure is historical. Current original bytes and fingerprints are recorded
in `research/originals_manifest.csv`. Original map pixels must remain unchanged; any future analysis
tiles must record source image, crop rectangle (x,y,width,height), and scale1:1.
