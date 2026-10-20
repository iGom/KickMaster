; PRG bank 0A; CPU base used here is $8000.
; For unreviewed banks, the base is a scaffold convention, not a recovered mapping.
.segment "PRG0A"
.org $8000
    .incbin "inputs/original.nes", $014010, $2000 ; UNINTERPRETED preserved bytes
