; PRG bank 01; CPU base used here is $8000.
; For unreviewed banks, the base is a scaffold convention, not a recovered mapping.
.segment "PRG01"
.org $8000
    .incbin "inputs/original.nes", $002010, $2000 ; UNINTERPRETED preserved bytes
