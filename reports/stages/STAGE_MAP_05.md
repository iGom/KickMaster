# Stage 5: Aboard the Ship of Strife

Status: research baseline only; ROM extraction not started.

- Reference guide: [Wyrenth, Sector 5](https://gamefaqs.gamespot.com/nes/563430-kickmaster/faqs/19876).
- Published map: [sprays, Stage 5](https://gamefaqs.gamespot.com/nes/563430-kickmaster/map/3651-stage-5-map).
- Availability updated in02C: original PNG supplied by user, 2560 × 240 pixels, preserved without resampling.
- Local reference: `research/originals/sprays/KickMaster-Sector5-AboardTheShipOfStrife.png`; SHA-256 `8494dff9d91395d654d29317b32c85f8688b54f3e1fbaa18d6f2370cd933c1c2`.
- PNG integrity/dimensions checked; detailed visual and ROM-coordinate comparison remains pending.
- Priority investigation from the supplied specification: ship movement and octopus body-part gating.

Required outputs remain unknown: ROM tables, dimensions, metatiles, collision, spawn coordinates,
subarea links, hidden reward coordinates, boss IDs, camera limits, restart state and transitions.
Do not use an image pixel location as a ROM world coordinate without establishing the transform.

The Stage00A web-retrieval failure is historical. Current original bytes and fingerprints are recorded
in `research/originals_manifest.csv`. Original map pixels must remain unchanged; any future analysis
tiles must record source image, crop rectangle (x,y,width,height), and scale1:1.
