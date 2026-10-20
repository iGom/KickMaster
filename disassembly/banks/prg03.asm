; PRG bank 03; CPU base used here is $8000.
; For unreviewed banks, the base is a scaffold convention, not a recovered mapping.
.segment "PRG03"
.org $8000
    .incbin "inputs/original.nes", $006010, $2000 ; UNINTERPRETED preserved bytes
