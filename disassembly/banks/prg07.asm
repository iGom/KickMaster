; PRG bank 07; CPU base used here is $A000.
; For unreviewed banks, the base is a scaffold convention, not a recovered mapping.
.segment "PRG07"
.org $A000
    .incbin "inputs/original.nes", $00E010, $0078 ; UNINTERPRETED preserved bytes

; B43: 33 absolute JMP entry points in R7 bank 07; callee gameplay semantics mostly unresolved.
Bank07ServiceJumpTable:
    JMP a:$a0db              ; A078 
    JMP a:$a0fa              ; A07B 
    JMP a:$a119              ; A07E 
    JMP a:$a4e9              ; A081 
    JMP a:$a537              ; A084 
    JMP a:$a63e              ; A087 
    JMP a:$a6fe              ; A08A 
    JMP a:$a33e              ; A08D 
    JMP a:$a3bc              ; A090 
    JMP a:$a315              ; A093 
    JMP a:$a37f              ; A096 
    JMP a:$a139              ; A099 
    JMP a:$a15c              ; A09C 
    JMP a:$a190              ; A09F 
    JMP a:$a1bc              ; A0A2 
    JMP a:$a374              ; A0A5 
    JMP a:$a362              ; A0A8 
    JMP a:$a182              ; A0AB 
    JMP a:$a1ed              ; A0AE 
    JMP a:$b022              ; A0B1 
    JMP a:$ac42              ; A0B4 
    JMP a:$aaff              ; A0B7 
    JMP a:$ae3a              ; A0BA 
    JMP a:$a5ab              ; A0BD 
    JMP a:$a935              ; A0C0 
    JMP a:$a9b3              ; A0C3 
    JMP a:$aec6              ; A0C6 
    JMP a:$aef7              ; A0C9 
    JMP a:$b5d4              ; A0CC 
    JMP a:$b645              ; A0CF 
    JMP a:$af28              ; A0D2 
    JMP a:$b991              ; A0D5 
    JMP a:$b83c              ; A0D8 
    .incbin "inputs/original.nes", $00E0EB, $1F25 ; UNINTERPRETED preserved bytes
