; PRG bank 08; CPU base used here is $8000.
; For unreviewed banks, the base is a scaffold convention, not a recovered mapping.
.segment "PRG08"
.org $8000
    .incbin "inputs/original.nes", $010010, $2000 ; UNINTERPRETED preserved bytes
