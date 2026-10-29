; PRG bank 0A; CPU base used here is $8000.
; For unreviewed banks, the base is a scaffold convention, not a recovered mapping.
.segment "PRG0A"
.org $8000

; H30: Reloadslot2C; kind-46 indexes29 stored return-address-minus-one pointers; pushhigh/low andRTS.8016 is sharedRTS. Valid tableindices0..28; nativekindreachability notclaimed.
DispatchSpecialEnemyAi:
    JMP a:$8003              ; 8000 
    LDX $2c                  ; 8003 
    LDA a:$03dd,X            ; 8005 
    SEC                      ; 8008 
    SBC #$46                 ; 8009 
    ASL A                    ; 800B 
    TAY                      ; 800C 
    LDA a:$8018,Y            ; 800D 
    PHA                      ; 8010 
    LDA a:$8017,Y            ; 8011 
    PHA                      ; 8014 
    RTS                      ; 8015 
    RTS                      ; 8016 

; H31: 29 stored addresses for kinds46..62; executabletarget=word+1. Next8051 isCMP0423,X code, not anotherpointer.
SpecialEnemyAiReturnPointers:
    .byte $15,$80,$15,$80,$15,$80,$15,$80,$15,$80,$15,$80,$15,$80,$15,$80
    .byte $15,$80,$1D,$9F,$6D,$81,$FB,$82,$85,$85,$74,$88,$79,$9A,$15,$80
    .byte $47,$98,$53,$8B,$7E,$8D,$A8,$91,$E9,$94,$F9,$89,$4B,$8F,$4F,$81
    .byte $5E,$85,$41,$88,$19,$8B,$1F,$9C,$F0,$9C
    .incbin "inputs/original.nes", $014061, $1FAF ; UNINTERPRETED preserved bytes
