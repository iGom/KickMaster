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
    .incbin "inputs/original.nes", $0126A7, $1969 ; UNINTERPRETED preserved bytes
