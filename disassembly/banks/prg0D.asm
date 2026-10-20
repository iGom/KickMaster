; PRG bank 0D; CPU base used here is $8000.
; For unreviewed banks, the base is a scaffold convention, not a recovered mapping.
.segment "PRG0D"
.org $8000
    .incbin "inputs/original.nes", $01A010, $2000 ; UNINTERPRETED preserved bytes
