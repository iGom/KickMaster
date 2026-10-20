; PRG bank 02; CPU base used here is $8000.
; For unreviewed banks, the base is a scaffold convention, not a recovered mapping.
.segment "PRG02"
.org $8000
    .incbin "inputs/original.nes", $004010, $2000 ; UNINTERPRETED preserved bytes
