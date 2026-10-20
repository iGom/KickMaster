; PRG bank 08; CPU base used here is $A000.
; For unreviewed banks, the base is a scaffold convention, not a recovered mapping.
.segment "PRG08"
.org $A000

; B44: Six absolute JMP entry points in R7 bank 08.
Bank08ServiceJumpTable:
    JMP a:$ab19              ; A000 
    JMP a:$b02a              ; A003 
    JMP a:$abc5              ; A006 
    JMP a:$b04c              ; A009 
    JMP a:$a012              ; A00C 
    JMP a:$a960              ; A00F 
    .incbin "inputs/original.nes", $010022, $1FEE ; UNINTERPRETED preserved bytes
