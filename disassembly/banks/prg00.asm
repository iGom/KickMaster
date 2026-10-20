; PRG bank 00; CPU base used here is $8000.
; For unreviewed banks, the base is a scaffold convention, not a recovered mapping.
.segment "PRG00"
.org $8000
    .incbin "inputs/original.nes", $000010, $2000 ; UNINTERPRETED preserved bytes
