; PRG bank 0E; CPU base used here is $C000.
; For unreviewed banks, the base is a scaffold convention, not a recovered mapping.
.segment "PRG0E"
.org $C000
    .incbin "inputs/original.nes", $01C010, $0C84 ; UNINTERPRETED preserved bytes

; A01: Initialize APU registers and call two five-entry index initializers.
ApuInitialize:
    LDA #$00                 ; CC84 
    STA a:$4010              ; CC86 
    LDA #$40                 ; CC89 
    STA a:$4017              ; CC8B 
    LDA #$0f                 ; CC8E 
    STA a:$4015              ; CC90 
    LDY #$00                 ; CC93 
    STY a:$4001              ; CC95 
    STY a:$4005              ; CC98 
    STY $03                  ; CC9B 
    STY $04                  ; CC9D 
    DEY                      ; CC9F 
    STY $00                  ; CCA0 
    STY $01                  ; CCA2 
    JSR a:$ccab              ; CCA4 
    JSR a:$ccba              ; CCA7 
    RTS                      ; CCAA 

; A02: Fill 0015..0019 with 05,0B,11,17,1D; audio role from A01 caller.
InitializeAudioIndicesA:
    LDA #$05                 ; CCAB 
    LDX #$00                 ; CCAD 
    STA $15,X                ; CCAF 
    CLC                      ; CCB1 
    ADC #$06                 ; CCB2 
    INX                      ; CCB4 
    CPX #$05                 ; CCB5 
    BCC $ccaf                ; CCB7 
    RTS                      ; CCB9 

; A03: Fill 001A..001E with 23,29,2F,35,3B.
InitializeAudioIndicesB:
    LDA #$23                 ; CCBA 
    LDX #$00                 ; CCBC 
    STA $1a,X                ; CCBE 
    CLC                      ; CCC0 
    ADC #$06                 ; CCC1 
    INX                      ; CCC3 
    CPX #$05                 ; CCC4 
    BCC $ccbe                ; CCC6 
    RTS                      ; CCC8 
    .incbin "inputs/original.nes", $01CCD9, $0943 ; UNINTERPRETED preserved bytes

; A04: Check retained 0100 marker 68; otherwise load six bytes at 0300; call D2F7.
ResetRetentionCheck:
    LDA a:$0100              ; D60C 0100 was deliberately excluded from the reset clear loop.
    CMP #$68                 ; D60F 
    BEQ $d623                ; D611 
    LDX #$05                 ; D613 
    LDA a:$d627,X            ; D615 Copy table backwards to retained 0300..0305.
    STA a:$0300,X            ; D618 
    DEX                      ; D61B 
    BPL $d615                ; D61C 
    LDA #$68                 ; D61E 
    STA a:$0100              ; D620 
    JSR a:$d2f7              ; D623 
    RTS                      ; D626 

; A05: Six default bytes copied to 0300..0305; purpose unresolved.
ResetRetainedDefaults:
    .byte $20,$20,$20,$20,$21,$20

; A06: Write F1 to every OAM Y byte in page 02.
HideAllSprites:
    LDX #$00                 ; D62D 
    LDA #$f1                 ; D62F 
    STA a:$0200,X            ; D631 
    INX                      ; D634 
    INX                      ; D635 
    INX                      ; D636 
    INX                      ; D637 
    BNE $d631                ; D638 
    RTS                      ; D63A 

; A07: For index 99 below 64, fill remaining OAM Y bytes with F3.
HideSpritesFromIndex:
    LDA $99                  ; D63B 
    ASL A                    ; D63D 
    ASL A                    ; D63E 
    BCS $d64d                ; D63F 
    TAX                      ; D641 
    LDA #$f3                 ; D642 
    STA a:$0200,X            ; D644 
    INX                      ; D647 
    INX                      ; D648 
    INX                      ; D649 
    INX                      ; D64A 
    BNE $d644                ; D64B 
    RTS                      ; D64D 
    .incbin "inputs/original.nes", $01D65E, $0075 ; UNINTERPRETED preserved bytes

; A08: Write X to 8000 and A to 8001; retry if interrupt activity changes A6.
MapperWriteRetry:
    LDY #$00                 ; D6C3 Contract: A=bank value, X=MMC3 selector. Y clobbered to zero.
    STY $a6                  ; D6C5 Clear epoch before each attempt, including a retry.
    STX a:$8000              ; D6C7 
    STA a:$8001              ; D6CA 
    CPY $a6                  ; D6CD NMI/IRQ increments A6; a changed epoch repeats the two-write transaction.
    BNE $d6c5                ; D6CF 
    RTS                      ; D6D1 

; A09: Map PRG0C at 8000, then tail-jump to 8000.
Bank0CEntry0:
    LDX #$06                 ; D6D2 
    LDA #$0c                 ; D6D4 
    JSR a:$d6c3              ; D6D6 
    JMP a:$8000              ; D6D9 

; A10: Map PRG0C at 8000, then tail-jump to 8003.
Bank0CEntry3:
    LDX #$06                 ; D6DC 
    LDA #$0c                 ; D6DE 
    JSR a:$d6c3              ; D6E0 
    JMP a:$8003              ; D6E3 

; A11: Map PRG0C at 8000, then tail-jump to 8006.
Bank0CEntry6:
    LDX #$06                 ; D6E6 
    LDA #$0c                 ; D6E8 
    JSR a:$d6c3              ; D6EA 
    JMP a:$8006              ; D6ED 
    .incbin "inputs/original.nes", $01D700, $0910 ; UNINTERPRETED preserved bytes
