; PRG bank 0B; CPU base used here is $8000.
; For unreviewed banks, the base is a scaffold convention, not a recovered mapping.
.segment "PRG0B"
.org $8000
    .incbin "inputs/original.nes", $016010, $2000 ; UNINTERPRETED preserved bytes
