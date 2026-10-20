; PRG bank 09; CPU base used here is $8000.
; For unreviewed banks, the base is a scaffold convention, not a recovered mapping.
.segment "PRG09"
.org $8000
    .incbin "inputs/original.nes", $012010, $2000 ; UNINTERPRETED preserved bytes
