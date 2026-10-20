; Reviewed local routines. Gaps are intentionally absent; not a standalone whole-bank file.
.setcpu "6502"

; A01: Initialize APU registers and call two five-entry index initializers.
; {'bank': '0E', 'cpu': '0xCC84', 'bank_offset': '0x0C84', 'prg_offset': '0x01CC84', 'file_offset': '0x01CC94', 'mapping_condition': 'MMC3 PRG mode 0'}
.org $CC84
ApuInitialize:
    LDA #$00                 ; CC84 A9 00    
    STA a:$4010              ; CC86 8D 10 40 
    LDA #$40                 ; CC89 A9 40    
    STA a:$4017              ; CC8B 8D 17 40 
    LDA #$0f                 ; CC8E A9 0F    
    STA a:$4015              ; CC90 8D 15 40 
    LDY #$00                 ; CC93 A0 00    
    STY a:$4001              ; CC95 8C 01 40 
    STY a:$4005              ; CC98 8C 05 40 
    STY $03                  ; CC9B 84 03    
    STY $04                  ; CC9D 84 04    
    DEY                      ; CC9F 88       
    STY $00                  ; CCA0 84 00    
    STY $01                  ; CCA2 84 01    
    JSR a:$ccab              ; CCA4 20 AB CC 
    JSR a:$ccba              ; CCA7 20 BA CC 
    RTS                      ; CCAA 60       

; A02: Fill 0015..0019 with 05,0B,11,17,1D; audio role from A01 caller.
; {'bank': '0E', 'cpu': '0xCCAB', 'bank_offset': '0x0CAB', 'prg_offset': '0x01CCAB', 'file_offset': '0x01CCBB', 'mapping_condition': 'MMC3 PRG mode 0'}
.org $CCAB
InitializeAudioIndicesA:
    LDA #$05                 ; CCAB A9 05    
    LDX #$00                 ; CCAD A2 00    
    STA $15,X                ; CCAF 95 15    
    CLC                      ; CCB1 18       
    ADC #$06                 ; CCB2 69 06    
    INX                      ; CCB4 E8       
    CPX #$05                 ; CCB5 E0 05    
    BCC $ccaf                ; CCB7 90 F6    
    RTS                      ; CCB9 60       

; A03: Fill 001A..001E with 23,29,2F,35,3B.
; {'bank': '0E', 'cpu': '0xCCBA', 'bank_offset': '0x0CBA', 'prg_offset': '0x01CCBA', 'file_offset': '0x01CCCA', 'mapping_condition': 'MMC3 PRG mode 0'}
.org $CCBA
InitializeAudioIndicesB:
    LDA #$23                 ; CCBA A9 23    
    LDX #$00                 ; CCBC A2 00    
    STA $1a,X                ; CCBE 95 1A    
    CLC                      ; CCC0 18       
    ADC #$06                 ; CCC1 69 06    
    INX                      ; CCC3 E8       
    CPX #$05                 ; CCC4 E0 05    
    BCC $ccbe                ; CCC6 90 F6    
    RTS                      ; CCC8 60       

; A04: Check retained 0100 marker 68; otherwise load six bytes at 0300; call D2F7.
; {'bank': '0E', 'cpu': '0xD60C', 'bank_offset': '0x160C', 'prg_offset': '0x01D60C', 'file_offset': '0x01D61C', 'mapping_condition': 'MMC3 PRG mode 0'}
.org $D60C
ResetRetentionCheck:
    LDA a:$0100              ; D60C AD 00 01 0100 was deliberately excluded from the reset clear loop.
    CMP #$68                 ; D60F C9 68    
    BEQ $d623                ; D611 F0 10    
    LDX #$05                 ; D613 A2 05    
    LDA a:$d627,X            ; D615 BD 27 D6 Copy table backwards to retained 0300..0305.
    STA a:$0300,X            ; D618 9D 00 03 
    DEX                      ; D61B CA       
    BPL $d615                ; D61C 10 F7    
    LDA #$68                 ; D61E A9 68    
    STA a:$0100              ; D620 8D 00 01 
    JSR a:$d2f7              ; D623 20 F7 D2 
    RTS                      ; D626 60       

; A05: Six default bytes copied to 0300..0305; purpose unresolved.
; {'bank': '0E', 'cpu': '0xD627', 'bank_offset': '0x1627', 'prg_offset': '0x01D627', 'file_offset': '0x01D637', 'mapping_condition': 'MMC3 PRG mode 0'}
.org $D627
ResetRetainedDefaults:
    .byte $20,$20,$20,$20,$21,$20

; A06: Write F1 to every OAM Y byte in page 02.
; {'bank': '0E', 'cpu': '0xD62D', 'bank_offset': '0x162D', 'prg_offset': '0x01D62D', 'file_offset': '0x01D63D', 'mapping_condition': 'MMC3 PRG mode 0'}
.org $D62D
HideAllSprites:
    LDX #$00                 ; D62D A2 00    
    LDA #$f1                 ; D62F A9 F1    
    STA a:$0200,X            ; D631 9D 00 02 
    INX                      ; D634 E8       
    INX                      ; D635 E8       
    INX                      ; D636 E8       
    INX                      ; D637 E8       
    BNE $d631                ; D638 D0 F7    
    RTS                      ; D63A 60       

; A07: For index 99 below 64, fill remaining OAM Y bytes with F3.
; {'bank': '0E', 'cpu': '0xD63B', 'bank_offset': '0x163B', 'prg_offset': '0x01D63B', 'file_offset': '0x01D64B', 'mapping_condition': 'MMC3 PRG mode 0'}
.org $D63B
HideSpritesFromIndex:
    LDA $99                  ; D63B A5 99    
    ASL A                    ; D63D 0A       
    ASL A                    ; D63E 0A       
    BCS $d64d                ; D63F B0 0C    
    TAX                      ; D641 AA       
    LDA #$f3                 ; D642 A9 F3    
    STA a:$0200,X            ; D644 9D 00 02 
    INX                      ; D647 E8       
    INX                      ; D648 E8       
    INX                      ; D649 E8       
    INX                      ; D64A E8       
    BNE $d644                ; D64B D0 F7    
    RTS                      ; D64D 60       

; A08: Write X to 8000 and A to 8001; retry if interrupt activity changes A6.
; {'bank': '0E', 'cpu': '0xD6C3', 'bank_offset': '0x16C3', 'prg_offset': '0x01D6C3', 'file_offset': '0x01D6D3', 'mapping_condition': 'MMC3 PRG mode 0'}
.org $D6C3
MapperWriteRetry:
    LDY #$00                 ; D6C3 A0 00    Contract: A=bank value, X=MMC3 selector. Y clobbered to zero.
    STY $a6                  ; D6C5 84 A6    Clear epoch before each attempt, including a retry.
    STX a:$8000              ; D6C7 8E 00 80 
    STA a:$8001              ; D6CA 8D 01 80 
    CPY $a6                  ; D6CD C4 A6    NMI/IRQ increments A6; a changed epoch repeats the two-write transaction.
    BNE $d6c5                ; D6CF D0 F4    
    RTS                      ; D6D1 60       

; A09: Map PRG0C at 8000, then tail-jump to 8000.
; {'bank': '0E', 'cpu': '0xD6D2', 'bank_offset': '0x16D2', 'prg_offset': '0x01D6D2', 'file_offset': '0x01D6E2', 'mapping_condition': 'MMC3 PRG mode 0'}
.org $D6D2
Bank0CEntry0:
    LDX #$06                 ; D6D2 A2 06    
    LDA #$0c                 ; D6D4 A9 0C    
    JSR a:$d6c3              ; D6D6 20 C3 D6 
    JMP a:$8000              ; D6D9 4C 00 80 

; A10: Map PRG0C at 8000, then tail-jump to 8003.
; {'bank': '0E', 'cpu': '0xD6DC', 'bank_offset': '0x16DC', 'prg_offset': '0x01D6DC', 'file_offset': '0x01D6EC', 'mapping_condition': 'MMC3 PRG mode 0'}
.org $D6DC
Bank0CEntry3:
    LDX #$06                 ; D6DC A2 06    
    LDA #$0c                 ; D6DE A9 0C    
    JSR a:$d6c3              ; D6E0 20 C3 D6 
    JMP a:$8003              ; D6E3 4C 03 80 

; A11: Map PRG0C at 8000, then tail-jump to 8006.
; {'bank': '0E', 'cpu': '0xD6E6', 'bank_offset': '0x16E6', 'prg_offset': '0x01D6E6', 'file_offset': '0x01D6F6', 'mapping_condition': 'MMC3 PRG mode 0'}
.org $D6E6
Bank0CEntry6:
    LDX #$06                 ; D6E6 A2 06    
    LDA #$0c                 ; D6E8 A9 0C    
    JSR a:$d6c3              ; D6EA 20 C3 D6 
    JMP a:$8006              ; D6ED 4C 06 80 

