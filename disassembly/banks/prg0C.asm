; PRG bank 0C; CPU base used here is $8000.
; For unreviewed banks, the base is a scaffold convention, not a recovered mapping.
.segment "PRG0C"
.org $8000
    .incbin "inputs/original.nes", $018010, $2000 ; UNINTERPRETED preserved bytes
