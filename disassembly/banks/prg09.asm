; PRG bank 09; CPU base used here is $A000.
; For unreviewed banks, the base is a scaffold convention, not a recovered mapping.
.segment "PRG09"
.org $A000

; B45: Seven absolute JMP entry points in R7 bank 09; A009 reaches front-end sequence A499.
Bank09ServiceJumpTable:
    JMP a:$be90              ; A000 
    JMP a:$bf0b              ; A003 
    JMP a:$a12a              ; A006 
    JMP a:$a499              ; A009 
    JMP a:$a884              ; A00C 
    JMP a:$a015              ; A00F 
    JMP a:$a6a8              ; A012 
    .incbin "inputs/original.nes", $012025, $0484 ; UNINTERPRETED preserved bytes

; B46: Initialize display and animation, wait on split index 67, then poll two-choice input; preserve outcome carry across cleanup.
FrontEndSequence:
    JSR a:$c74c              ; A499 
    JSR a:$a557              ; A49C 
    LDX #$01                 ; A49F 
    LDA #$dc                 ; A4A1 
    STA a:$056b,X            ; A4A3 
    LDA #$c0                 ; A4A6 
    STA a:$057f,X            ; A4A8 
    LDA #$00                 ; A4AB 
    STA a:$0543,X            ; A4AD 
    STA a:$0557,X            ; A4B0 
    STA a:$052f,X            ; A4B3 
    STA a:$0507,X            ; A4B6 
    LDA a:$a555,X            ; A4B9 
    STA a:$051b,X            ; A4BC 
    LDA #$32                 ; A4BF 
    STA a:$04f3,X            ; A4C1 
    DEX                      ; A4C4 
    BPL $a4a1                ; A4C5 
    JSR a:$bf0b              ; A4C7 
    JSR a:$c782              ; A4CA 
    LDA #$06                 ; A4CD 
    STA $00                  ; A4CF 
    LDX #$3c                 ; A4D1 
    BNE $a4d7                ; A4D3 
    LDX #$03                 ; A4D5 
    JSR a:$c74c              ; A4D7 
    DEX                      ; A4DA 
    BNE $a4d7                ; A4DB 
    LDA $67                  ; A4DD Busy wait on IRQ-owned index; exact scanline and screen effect remain unobserved.
    CMP #$12                 ; A4DF 
    BNE $a4dd                ; A4E1 
    LDA $67                  ; A4E3 
    CMP #$03                 ; A4E5 
    BNE $a4e3                ; A4E7 
    LDX #$01                 ; A4E9 
    LDA $80,X                ; A4EB 
    SEC                      ; A4ED 
    SBC #$09                 ; A4EE 
    STA $80,X                ; A4F0 
    LDA a:$04f3,X            ; A4F2 
    SEC                      ; A4F5 
    SBC #$09                 ; A4F6 
    STA a:$04f3,X            ; A4F8 
    DEX                      ; A4FB 
    BPL $a4eb                ; A4FC 
    INC $7f                  ; A4FE 
    JSR a:$bf0b              ; A500 
    LDA $7f                  ; A503 
    CMP #$07                 ; A505 
    BNE $a4d5                ; A507 
    LDA #$00                 ; A509 
    STA $2c                  ; A50B 
    LDA #$80                 ; A50D 
    STA $2e                  ; A50F 
    LDA #$02                 ; A511 
    STA $2f                  ; A513 
    LDX #$3c                 ; A515 
    JSR a:$f6cc              ; A517 
    LDA #$00                 ; A51A 
    STA $38                  ; A51C 
    LDA #$97                 ; A51E 
    STA $3a                  ; A520 
    LDA #$a6                 ; A522 
    STA $3b                  ; A524 
    LDX #$05                 ; A526 
    JSR a:$f6cc              ; A528 
    JSR a:$f60b              ; A52B 
    LDA #$39                 ; A52E 
    STA $01                  ; A530 
    LDA $38                  ; A532 
    CMP #$ff                 ; A534 
    BNE $a526                ; A536 
    JSR a:$a630              ; A538 
    BCS $a548                ; A53B 
    DEC $2e                  ; A53D 
    BNE $a538                ; A53F 
    DEC $2f                  ; A541 
    BNE $a538                ; A543 
    CLC                      ; A545 
    BCC $a54c                ; A546 
    LDA #$37                 ; A548 
    STA $01                  ; A54A 
    PHP                      ; A54C Save outcome flags across cleanup calls and restore before RTS.
    JSR a:$c788              ; A54D 
    JSR a:$c749              ; A550 
    PLP                      ; A553 
    RTS                      ; A554 

; B47: Two X bytes 1C/E4 copied to 051B/051C by A4B9.
FrontEndObjectXPair:
    .byte $1C,$E4

; B48: Map R6=05, far-call bank07 A0BD, set tile transfer arguments, PPU split fields and IRQ source FA59.
InitializeFrontEndLayout:
    JSR a:$c74c              ; A557 
    JSR a:$c749              ; A55A 
    LDX #$06                 ; A55D 
    LDA #$05                 ; A55F 
    JSR a:$c76a              ; A561 
    LDA #$bd                 ; A564 
    STA a:$04ea              ; A566 
    LDA #$a0                 ; A569 
    STA a:$04eb              ; A56B 
    LDA #$07                 ; A56E 
    STA a:$04ec              ; A570 
    LDA #$01                 ; A573 
    STA a:$04e2              ; A575 
    JSR a:$f4ca              ; A578 
    LDA #$00                 ; A57B 
    STA a:$0046              ; A57D 
    LDA #$04                 ; A580 
    STA a:$0047              ; A582 
    LDA #$cf                 ; A585 
    STA $22                  ; A587 
    LDA #$26                 ; A589 
    STA $23                  ; A58B 
    LDA #$2e                 ; A58D 
    STA $24                  ; A58F 
    LDA #$a6                 ; A591 
    STA $25                  ; A593 
    LDA #$01                 ; A595 
    STA $3c                  ; A597 
    JSR a:$f400              ; A599 
    LDA #$ec                 ; A59C 
    STA $22                  ; A59E 
    LDA #$7f                 ; A5A0 
    STA $24                  ; A5A2 
    LDA #$81                 ; A5A4 
    STA $25                  ; A5A6 
    LDA #$07                 ; A5A8 
    STA $3c                  ; A5AA 
    JSR a:$f400              ; A5AC 
    LDA #$0c                 ; A5AF 
    STA $22                  ; A5B1 
    LDA #$27                 ; A5B3 
    STA $23                  ; A5B5 
    LDA #$86                 ; A5B7 
    STA $24                  ; A5B9 
    LDA #$81                 ; A5BB 
    STA $25                  ; A5BD 
    JSR a:$f400              ; A5BF 
    LDA #$4a                 ; A5C2 
    STA $22                  ; A5C4 
    LDA #$9e                 ; A5C6 
    STA $24                  ; A5C8 
    LDA #$81                 ; A5CA 
    STA $25                  ; A5CC 
    LDA #$0b                 ; A5CE 
    STA $3c                  ; A5D0 
    JSR a:$f400              ; A5D2 
    LDA #$8a                 ; A5D5 
    STA $22                  ; A5D7 
    LDA #$bd                 ; A5D9 
    STA $24                  ; A5DB 
    LDA #$81                 ; A5DD 
    STA $25                  ; A5DF 
    LDA #$0b                 ; A5E1 
    STA $3c                  ; A5E3 
    JSR a:$f400              ; A5E5 
    LDA #$a5                 ; A5E8 
    STA $22                  ; A5EA 
    LDA #$c8                 ; A5EC 
    STA $24                  ; A5EE 
    LDA #$81                 ; A5F0 
    STA $25                  ; A5F2 
    LDA #$18                 ; A5F4 
    STA $3c                  ; A5F6 
    JSR a:$f400              ; A5F8 
    LDA #$01                 ; A5FB 
    STA $68                  ; A5FD 
    STA $6a                  ; A5FF 
    STA $96                  ; A601 
    STA $7f                  ; A603 
    LDA #$37                 ; A605 
    STA $80                  ; A607 
    STA $81                  ; A609 
    LDA #$1e                 ; A60B 
    STA $60                  ; A60D 
    STA $61                  ; A60F 
    STA $62                  ; A611 
    LDA #$89                 ; A613 
    STA $4b                  ; A615 
    STA $4d                  ; A617 
    LDA #$88                 ; A619 
    STA $4c                  ; A61B 
    LDA #$80                 ; A61D 
    STA $e0                  ; A61F 
    LDA #$26                 ; A621 
    STA $e1                  ; A623 
    LDA #$59                 ; A625 
    STA $dc                  ; A627 
    LDA #$fa                 ; A629 
    STA $dd                  ; A62B 
    RTS                      ; A62D 

; B49: Two bytes 21/00 used as a PPU transfer source at A585..A599.
FrontEndTilePair:
    .byte $31,$00

; B50: A/Start return carry set; otherwise Select/Left/Right toggle 2C, draw cursor and return carry clear.
PollFrontEndChoice:
    JSR a:$c74c              ; A630 
    LDA $1f                  ; A633 Mask 90 confirms A or Start. B does not confirm this front-end choice.
    AND #$90                 ; A635 
    BNE $a655                ; A637 
    LDA $1f                  ; A639 
    AND #$23                 ; A63B Mask 23 combines Select, Left and Right; multiple set bits still toggle only once.
    BEQ $a649                ; A63D 
    LDA $2c                  ; A63F 
    EOR #$01                 ; A641 
    STA $2c                  ; A643 
    LDA #$39                 ; A645 
    STA $01                  ; A647 
    LDA #$20                 ; A649 
    STA $99                  ; A64B 
    JSR a:$a672              ; A64D 
    JSR a:$c74f              ; A650 
    CLC                      ; A653 
    RTS                      ; A654 
    SEC                      ; A655 
    RTS                      ; A656 
    .incbin "inputs/original.nes", $012667, $001B ; UNINTERPRETED preserved bytes

; B51: Write one four-byte OAM sprite at index 99; choose X through 2C; increment 99.
DrawFrontEndCursor:
    LDA $99                  ; A672 
    ASL A                    ; A674 
    ASL A                    ; A675 
    TAX                      ; A676 
    LDA #$98                 ; A677 
    STA a:$0200,X            ; A679 
    INX                      ; A67C 
    LDA #$2d                 ; A67D 
    STA a:$0200,X            ; A67F 
    INX                      ; A682 
    LDA #$01                 ; A683 
    STA a:$0200,X            ; A685 
    INX                      ; A688 
    LDY $2c                  ; A689 
    LDA a:$a695,Y            ; A68B 
    STA a:$0200,X            ; A68E 
    INX                      ; A691 
    INC $99                  ; A692 
    RTS                      ; A694 

; B52: Two cursor X bytes 38/88 for selections 00/01.
FrontEndCursorXPair:
    .byte $38,$88
    .incbin "inputs/original.nes", $0126A7, $047E ; UNINTERPRETED preserved bytes

; D25: Twelve sprite pointers from generic object table, corresponding to even object types70..86.
SelectedSpellSpritePointers:
    .byte $71,$AC,$71,$AC,$71,$AC,$71,$AC,$71,$AC,$5B,$AE,$5B,$AE,$71,$AC
    .byte $71,$AC,$71,$AC,$71,$AC,$71,$AC
    .incbin "inputs/original.nes", $012B3D, $00CA ; UNINTERPRETED preserved bytes

; D26: Twelve handler pointers; types70/72 target B6BA/B6CD. Remaining target behavior not inferred.
SelectedSpellHandlerPointers:
    .byte $BA,$B6,$CD,$B6,$3B,$BA,$69,$B8,$75,$BA,$DF,$B6,$D4,$B7,$8E,$B8
    .byte $B7,$B8,$30,$B8,$F0,$B8,$0C,$B9
    .incbin "inputs/original.nes", $012C1F, $0AAB ; UNINTERPRETED preserved bytes

; D27: New Select bit20 triggers cost60 decimal MP; on success add20 hex raw HP through BD98.
HealSpellTwoCells:
    LDA $1f                  ; B6BA 
    AND #$20                 ; B6BC 
    BEQ $b6cc                ; B6BE 
    LDA #$60                 ; B6C0 
    JSR a:$bd46              ; B6C2 
    BCS $b6cc                ; B6C5 
    LDA #$20                 ; B6C7 
    JMP a:$bd98              ; B6C9 
    RTS                      ; B6CC 

; D28: New Select bit20 triggers cost90 decimal MP; on success add40 hex raw HP through BD98.
HealSpellFourCells:
    LDA $1f                  ; B6CD 
    AND #$20                 ; B6CF 
    BEQ $b6cc                ; B6D1 
    LDA #$90                 ; B6D3 
    JSR a:$bd46              ; B6D5 
    BCS $b6cc                ; B6D8 
    LDA #$40                 ; B6DA 
    JMP a:$bd98              ; B6DC 
    .incbin "inputs/original.nes", $0136EF, $0667 ; UNINTERPRETED preserved bytes

; D29: A packed decimal cost;01A5 nonzero bypasses cost before D3 bit80 gate. Subtract base60 digits with borrow; insufficient MP rolls back all three digits and returns carry set.
SpendMagicPoints:
    LDX a:$01a5              ; BD46 Cost-bypass flag is checked before the D3 negative-state guard; its activation path is not established.
    BNE $bd88                ; BD49 
    STA $34                  ; BD4B 
    LSR A                    ; BD4D 
    LSR A                    ; BD4E 
    LSR A                    ; BD4F 
    LSR A                    ; BD50 
    STA $35                  ; BD51 
    LDA $34                  ; BD53 
    AND #$0f                 ; BD55 
    STA $34                  ; BD57 
    LDA #$00                 ; BD59 
    STA $36                  ; BD5B 
    LDA $d3                  ; BD5D 
    BMI $bd96                ; BD5F 
    LDA $ea                  ; BD61 
    STA $38                  ; BD63 
    LDA $eb                  ; BD65 
    STA $39                  ; BD67 
    LDA $ec                  ; BD69 
    STA $3a                  ; BD6B 
    LDX #$00                 ; BD6D 
    LDA $ea,X                ; BD6F 
    SEC                      ; BD71 
    SBC $34,X                ; BD72 
    CMP #$60                 ; BD74 
    BCS $bd81                ; BD76 
    CPX #$02                 ; BD78 
    BEQ $bd8a                ; BD7A 
    INC $35,X                ; BD7C 
    CLC                      ; BD7E 
    ADC #$0a                 ; BD7F 
    STA $ea,X                ; BD81 
    INX                      ; BD83 
    CPX #$03                 ; BD84 
    BNE $bd6f                ; BD86 
    CLC                      ; BD88 
    RTS                      ; BD89 
    LDA $38                  ; BD8A Rollback preserves current MP on insufficient funds, but scratch bytes can change.
    STA $ea                  ; BD8C 
    LDA $39                  ; BD8E 
    STA $eb                  ; BD90 
    LDA $3a                  ; BD92 
    STA $ec                  ; BD94 
    SEC                      ; BD96 
    RTS                      ; BD97 

; D30: Add raw A to06B9 and cap to06BB; valid normal HP plus supported heal does not overflow the eight-bit ADC.
AddHpClamped:
    CLC                      ; BD98 No carry-overflow handling; assertions about min(HP+heal,max) require valid HP/cost domain.
    ADC a:$06b9              ; BD99 
    CMP a:$06bb              ; BD9C 
    BCC $bda4                ; BD9F 
    LDA a:$06bb              ; BDA1 
    STA a:$06b9              ; BDA4 
    RTS                      ; BDA7 
    .incbin "inputs/original.nes", $013DB8, $00E8 ; UNINTERPRETED preserved bytes

; D31: Increment object clocks, scan04EF+4 global slots, apply flags/parity gates, dispatch handlers, integrate/cull, preserve reserved slot3 offscreen, draw visible sprites.
UpdateAndDrawObjects:
    INC $d8                  ; BE90 
    INC $d9                  ; BE92 
    BNE $be98                ; BE94 
    INC $da                  ; BE96 
    LDA $d9                  ; BE98 
    AND #$01                 ; BE9A 
    CLC                      ; BE9C 
    ADC #$04                 ; BE9D 
    STA $47                  ; BE9F 
    LDA $99                  ; BEA1 
    ASL A                    ; BEA3 
    ASL A                    ; BEA4 
    STA $b0                  ; BEA5 
    LDX #$02                 ; BEA7 
    STX $b1                  ; BEA9 
    LDA a:$04ef              ; BEAB 
    SEC                      ; BEAE 
    ADC #$03                 ; BEAF 
    STA $2e                  ; BEB1 
    LDX #$00                 ; BEB3 
    LDA a:$057c,X            ; BEB5 
    BPL $befa                ; BEB8 
    AND #$08                 ; BEBA 
    BNE $beca                ; BEBC 
    LDA a:$057c,X            ; BEBE 
    LSR A                    ; BEC1 
    LSR A                    ; BEC2 
    BCS $beca                ; BEC3 
    EOR $d9                  ; BEC5 
    LSR A                    ; BEC7 
    BCS $befa                ; BEC8 
    STX $2f                  ; BECA 
    JSR a:$bf3e              ; BECC 
    LDX $2f                  ; BECF 
    JSR a:$bf68              ; BED1 
    BNE $bf00                ; BED4 
    LDA a:$057c,X            ; BED6 
    LSR A                    ; BED9 
    LSR A                    ; BEDA 
    BCS $bee2                ; BEDB 
    EOR $d9                  ; BEDD 
    LSR A                    ; BEDF 
    BCS $befa                ; BEE0 
    LDA a:$057c,X            ; BEE2 
    AND #$20                 ; BEE5 
    AND $b8                  ; BEE7 
    STA $2c                  ; BEE9 
    LDA a:$0568,X            ; BEEB 
    LSR A                    ; BEEE 
    BCS $bef7                ; BEEF 
    JSR a:$f6ed              ; BEF1 
    JMP a:$befa              ; BEF4 
    JSR a:$f737              ; BEF7 
    INX                      ; BEFA 
    CPX $2e                  ; BEFB 
    BNE $beb5                ; BEFD 
    RTS                      ; BEFF 
    CPX #$03                 ; BF00 
    BEQ $befa                ; BF02 
    LDA #$00                 ; BF04 
    STA a:$057c,X            ; BF06 
    BEQ $befa                ; BF09 
    .incbin "inputs/original.nes", $013F1B, $0033 ; UNINTERPRETED preserved bytes

; D32: Even0568,X indexes sprite tableAAA5 and handler tableAB87; load B6/B7 and tail JMP(2C).
DispatchObjectHandler:
    LDA #$a5                 ; BF3E 
    STA $c7                  ; BF40 
    LDA #$aa                 ; BF42 
    STA $c8                  ; BF44 
    LDA #$87                 ; BF46 
    STA $c5                  ; BF48 
    LDA #$ab                 ; BF4A 
    STA $c6                  ; BF4C 
    LDA a:$0568,X            ; BF4E 
    AND #$fe                 ; BF51 
    TAY                      ; BF53 
    LDA ($c7),Y              ; BF54 
    STA $b6                  ; BF56 
    LDA ($c5),Y              ; BF58 
    STA $2c                  ; BF5A 
    INY                      ; BF5C 
    LDA ($c7),Y              ; BF5D 
    STA $b7                  ; BF5F 
    LDA ($c5),Y              ; BF61 
    STA $2d                  ; BF63 
    JMP ($002c)              ; BF65 

; D33: Flag40 skips velocity integration; signed X/Y velocities update coordinates. Low Y>=D8 or nonzero relative X high culls. Y high scratch subtract uses carry from CMP D8.
MoveAndCullObject:
    LDA a:$057c,X            ; BF68 
    ASL A                    ; BF6B 
    PHP                      ; BF6C 
    BMI $bf8b                ; BF6D 
    LDA #$00                 ; BF6F 
    STA $2d                  ; BF71 
    LDA a:$0554,X            ; BF73 
    BEQ $bf8b                ; BF76 
    BPL $bf7c                ; BF78 
    DEC $2d                  ; BF7A 
    CLC                      ; BF7C 
    ADC a:$04f0,X            ; BF7D 
    STA a:$04f0,X            ; BF80 
    LDA a:$0504,X            ; BF83 
    ADC $2d                  ; BF86 
    STA a:$0504,X            ; BF88 
    LDA a:$04f0,X            ; BF8B 
    SEC                      ; BF8E 
    SBC $a9                  ; BF8F 
    CMP #$d8                 ; BF91 
    BCS $bfcf                ; BF93 
    STA $22                  ; BF95 
    LDA a:$0504,X            ; BF97 
    SBC $aa                  ; BF9A 
    STA $23                  ; BF9C 
    PLP                      ; BF9E 
    BMI $bfbd                ; BF9F 
    LDA #$00                 ; BFA1 
    STA $2d                  ; BFA3 
    LDA a:$0540,X            ; BFA5 
    BEQ $bfbd                ; BFA8 
    BPL $bfae                ; BFAA 
    DEC $2d                  ; BFAC 
    CLC                      ; BFAE 
    ADC a:$0518,X            ; BFAF 
    STA a:$0518,X            ; BFB2 
    LDA a:$052c,X            ; BFB5 
    ADC $2d                  ; BFB8 
    STA a:$052c,X            ; BFBA 
    LDA a:$0518,X            ; BFBD 
    SEC                      ; BFC0 
    SBC $a7                  ; BFC1 
    STA $24                  ; BFC3 
    LDA a:$052c,X            ; BFC5 
    SBC $a8                  ; BFC8 
    BNE $bfd0                ; BFCA 
    STA $25                  ; BFCC 
    RTS                      ; BFCE 
    PLP                      ; BFCF 
    LDA #$01                 ; BFD0 
    RTS                      ; BFD2 
    .incbin "inputs/original.nes", $013FE3, $002D ; UNINTERPRETED preserved bytes
