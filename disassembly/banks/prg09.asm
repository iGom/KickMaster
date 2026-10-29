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
    .incbin "inputs/original.nes", $012B3D, $005A ; UNINTERPRETED preserved bytes

; F17: 32 little-endian handler pointers for paired types00..3F; sprite table remains separately addressed.
ProjectileObjectHandlerPointers:
    .byte $5C,$B5,$5C,$B5,$5C,$B5,$5C,$B5,$5C,$B5,$70,$B5,$71,$B5,$71,$B5
    .byte $71,$B5,$71,$B5,$71,$B5,$71,$B5,$EF,$B5,$F4,$B5,$F4,$B5,$F4,$B5
    .byte $F4,$B5,$F4,$B5,$F4,$B5,$08,$B6,$EF,$B5,$F4,$B5,$F4,$B5,$20,$B6
    .byte $F4,$B5,$F4,$B5,$F4,$B5,$F4,$B5,$F4,$B5,$3A,$B6,$70,$B5,$70,$B5
    .incbin "inputs/original.nes", $012BD7, $0030 ; UNINTERPRETED preserved bytes

; D26: Twelve handler pointers; types70/72 target B6BA/B6CD. Remaining target behavior not inferred.
SelectedSpellHandlerPointers:
    .byte $BA,$B6,$CD,$B6,$3B,$BA,$69,$B8,$75,$BA,$DF,$B6,$D4,$B7,$8E,$B8
    .byte $B7,$B8,$30,$B8,$F0,$B8,$0C,$B9

; E20: Twelve handlers for even types88..9E;96 level-up visual remains unreviewed; others control decoy/shield/lightning continuations.
MagicContinuationHandlerPointers:
    .byte $30,$B9,$64,$B9,$72,$B9,$91,$B9,$E1,$B9,$E1,$B9,$19,$BA,$70,$B5
    .byte $C7,$BA,$C7,$BA,$C7,$BA,$C7,$BA
    .incbin "inputs/original.nes", $012C37, $0935 ; UNINTERPRETED preserved bytes

; F18: Increment counter; everythirdcall reset andadvance even typeby2. Type0A dispatches shared RTS B570 andholds finalshape.
GrowPulseProjectile:
    INC a:$0590,X            ; B55C 
    LDA a:$0590,X            ; B55F 
    SEC                      ; B562 
    SBC #$03                 ; B563 
    BNE $b570                ; B565 
    STA a:$0590,X            ; B567 
    INC a:$0568,X            ; B56A 
    INC a:$0568,X            ; B56D 
    RTS                      ; B570 

; F19: Toggle typebit1; sample separate futureY/futureX and negate corresponding velocity for result&3. Currentpoint result&3 deactivates, bit3setsattribute20; typebit4 determines persistencebit10. Terrain service callees remain partiallyreviewed.
UpdateBouncingProjectile:
    LDA a:$0568,X            ; B571 
    EOR #$02                 ; B574 Alternating type10/12 also selects damage3/2 in R6=06 collision table.
    STA a:$0568,X            ; B576 
    LDA #$00                 ; B579 
    STA a:$0590,X            ; B57B 
    LDA a:$0518,X            ; B57E 
    STA $26                  ; B581 
    LDA a:$052c,X            ; B583 
    STA $27                  ; B586 
    LDA a:$04f0,X            ; B588 
    SEC                      ; B58B 
    SBC #$08                 ; B58C 
    STA $28                  ; B58E 
    LDA a:$0504,X            ; B590 
    SBC #$00                 ; B593 
    STA $29                  ; B595 
    LDA #$00                 ; B597 
    LDY a:$0554,X            ; B599 
    JSR a:$c773              ; B59C 
    STA a:$0590,X            ; B59F 
    LDA a:$0540,X            ; B5A2 
    LDY #$00                 ; B5A5 
    JSR a:$c773              ; B5A7 
    AND #$03                 ; B5AA 
    BEQ $b5b9                ; B5AC 
    LDA a:$0540,X            ; B5AE 
    EOR #$ff                 ; B5B1 
    CLC                      ; B5B3 
    ADC #$01                 ; B5B4 
    STA a:$0540,X            ; B5B6 
    LDA a:$0590,X            ; B5B9 
    AND #$03                 ; B5BC 
    BEQ $b5cb                ; B5BE 
    LDA a:$0554,X            ; B5C0 
    EOR #$ff                 ; B5C3 
    CLC                      ; B5C5 
    ADC #$01                 ; B5C6 
    STA a:$0554,X            ; B5C8 
    JSR a:$c75b              ; B5CB 
    PHA                      ; B5CE 
    AND #$08                 ; B5CF 
    ASL A                    ; B5D1 
    ASL A                    ; B5D2 
    ORA #$80                 ; B5D3 
    STA a:$057c,X            ; B5D5 
    PLA                      ; B5D8 
    AND #$03                 ; B5D9 
    BEQ $b5e1                ; B5DB 
    STA a:$057c,X            ; B5DD 
    RTS                      ; B5E0 
    LDA a:$0568,X            ; B5E1 
    AND #$10                 ; B5E4 
    EOR #$10                 ; B5E6 
    ORA a:$057c,X            ; B5E8 
    STA a:$057c,X            ; B5EB 
    RTS                      ; B5EE 

; F20: EntryB5EF clears activeflags when counterzero; B5F4 advances type by signed05A4, sound93, then anchors toselected slot3; zeroresult clearsflags.
AdvanceLightningSegment:
    LDA a:$0590,X            ; B5EF 
    BEQ $b604                ; B5F2 
    LDA #$93                 ; B5F4 
    STA $01                  ; B5F6 
    LDA a:$0568,X            ; B5F8 
    CLC                      ; B5FB 
    ADC a:$05a4,X            ; B5FC 
    STA a:$0568,X            ; B5FF 
    BNE $b645                ; B602 
    STA a:$057c,X            ; B604 
    RTS                      ; B607 

; F21: Decrementcounter at type26; nonzero resets type20; zero sets deltaFE andtype1E for reversefinish.
CycleCentralLightningSegment:
    DEC a:$0590,X            ; B608 
    BEQ $b614                ; B60B 
    LDA #$20                 ; B60D 
    STA a:$0568,X            ; B60F 
    BNE $b645                ; B612 
    LDA #$fe                 ; B614 
    STA a:$05a4,X            ; B616 
    LDA #$1e                 ; B619 
    STA a:$0568,X            ; B61B 
    BNE $b645                ; B61E 

; F22: At type2E/2F decrement counter; nonzero sets step+2 and advances type by2; zero steps back by2 WITHOUT changing step. Synthetic seed1 therefore wraps counter before eventual expiry.
CycleSideLightningSegment:
    DEC a:$0590,X            ; B620 
    BEQ $b632                ; B623 
    LDA #$02                 ; B625 
    STA a:$05a4,X            ; B627 
    INC a:$0568,X            ; B62A 
    INC a:$0568,X            ; B62D 
    BNE $b645                ; B630 
    DEC a:$0568,X            ; B632 
    DEC a:$0568,X            ; B635 
    BNE $b645                ; B638 

; F23: At type3A setdeltaFE andstepbackto38.
ReverseSideLightningSegment:
    LDA #$fe                 ; B63A 
    STA a:$05a4,X            ; B63C 
    DEC a:$0568,X            ; B63F 
    DEC a:$0568,X            ; B642 

; F24: Copy selectedslot3 16-bitX/Y to currentprojectileslot; no independent velocity here.
AnchorLightningSegment:
    LDA a:$04f3              ; B645 
    STA a:$04f0,X            ; B648 
    LDA a:$0507              ; B64B 
    STA a:$0504,X            ; B64E 
    LDA a:$051b              ; B651 
    STA a:$0518,X            ; B654 
    LDA a:$052f              ; B657 
    STA a:$052c,X            ; B65A 
    RTS                      ; B65D 

; E21: Copy selected effect slot3 Y/X pairs to global objectY; preservesY.
CopySelectedEffectPositionToObject:
    LDA a:$04f3              ; B65E 
    STA a:$04f0,Y            ; B661 
    LDA a:$0507              ; B664 
    STA a:$0504,Y            ; B667 
    LDA a:$051b              ; B66A 
    STA a:$0518,Y            ; B66D 
    LDA a:$052f              ; B670 
    STA a:$052c,Y            ; B673 
    RTS                      ; B676 

; E22: Copy player worldY/X to reserved global slot3.
AnchorSelectedEffectToPlayer:
    LDA $cb                  ; B677 
    STA a:$051b              ; B679 
    LDA $cc                  ; B67C 
    STA a:$052f              ; B67E 
    LDA $c9                  ; B681 
    STA a:$04f3              ; B683 
    LDA $ca                  ; B686 
    STA a:$0507              ; B688 
    RTS                      ; B68B 
    .incbin "inputs/original.nes", $01369C, $002E ; UNINTERPRETED preserved bytes

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

; E23: Update aiming orb; newSelect, free reserved projectile slot and cost3MP required; spawn type10 flags80 with one of16 direction velocities; restoreX.
CastDirectionalMagicProjectile:
    JSR a:$b747              ; B6DF 
    LDA $1f                  ; B6E2 
    AND #$20                 ; B6E4 
    BEQ $b724                ; B6E6 
    JSR a:$bda8              ; B6E8 
    BMI $b724                ; B6EB 
    LDA #$03                 ; B6ED 
    JSR a:$bd46              ; B6EF 
    BCS $b724                ; B6F2 
    LDA #$59                 ; B6F4 
    STA $01                  ; B6F6 
    JSR a:$b65e              ; B6F8 
    LDA $20                  ; B6FB 
    AND #$0f                 ; B6FD 
    BNE $b708                ; B6FF 
    LDA $cd                  ; B701 
    AND #$01                 ; B703 
    CLC                      ; B705 
    ADC #$01                 ; B706 
    TAX                      ; B708 
    LDA a:$b727,X            ; B709 
    STA a:$0540,Y            ; B70C 
    LDA a:$b737,X            ; B70F 
    STA a:$0554,Y            ; B712 
    LDA #$10                 ; B715 
    STA a:$0568,Y            ; B717 
    LDA #$80                 ; B71A 
    STA a:$057c,Y            ; B71C 
    LDA #$00                 ; B71F 
    STA a:$0590,Y            ; B721 
    LDX $3e                  ; B724 
    RTS                      ; B726 

; E24: Sixteen signed X velocities indexed held direction nibble; no-direction uses player facing.
DirectionalProjectileVelocityX:
    .byte $08,$08,$F8,$08,$00,$06,$FA,$08,$00,$06,$FA,$08,$08,$08,$08,$08

; E25: Sixteen signed Y velocities paired with B727.
DirectionalProjectileVelocityY:
    .byte $00,$00,$00,$00,$08,$06,$06,$00,$F8,$FA,$FA,$00,$00,$00,$00,$00

; E26: SaveX, copy facing, move current aim index one step toward previous target, position at signed offset from player, then derive next target from held-direction nibble.
UpdateMagicAimingOrb:
    STX $3e                  ; B747 
    LSR a:$056b              ; B749 
    LDA $cd                  ; B74C 
    LSR A                    ; B74E 
    ROL a:$056b              ; B74F 
    LDA a:$0593              ; B752 
    CMP a:$05a7              ; B755 
    BEQ $b765                ; B758 
    BCC $b762                ; B75A 
    DEC a:$0593              ; B75C 
    JMP a:$b765              ; B75F 
    INC a:$0593              ; B762 
    LDA #$00                 ; B765 
    STA $3c                  ; B767 
    STA $3d                  ; B769 
    LDA a:$0593              ; B76B 
    ASL A                    ; B76E 
    TAY                      ; B76F 
    LDA a:$b7c2,Y            ; B770 
    BPL $b777                ; B773 
    DEC $3c                  ; B775 
    CLC                      ; B777 
    ADC $cb                  ; B778 
    STA a:$051b              ; B77A 
    LDA $cc                  ; B77D 
    ADC $3c                  ; B77F 
    STA a:$052f              ; B781 
    LDA a:$b7c3,Y            ; B784 
    BPL $b78b                ; B787 
    DEC $3d                  ; B789 
    CLC                      ; B78B 
    ADC $c9                  ; B78C 
    STA a:$04f3              ; B78E 
    LDA $ca                  ; B791 
    ADC $3d                  ; B793 
    STA a:$0507              ; B795 
    LDA $20                  ; B798 
    AND #$0f                 ; B79A 
    BNE $b7aa                ; B79C 
    LDA $cd                  ; B79E 
    LSR A                    ; B7A0 
    BCC $b7a8                ; B7A1 
    LDA #$02                 ; B7A3 
    JMP a:$b7aa              ; B7A5 
    LDA #$01                 ; B7A8 
    TAY                      ; B7AA 
    LDA a:$b7b2,Y            ; B7AB 
    STA a:$05a7              ; B7AE 
    RTS                      ; B7B1 

; E27: Sixteen direction-nibble target indices0..8; default facing suppliesLeft/Right.
MagicAimTargetIndices:
    .byte $04,$02,$06,$04,$04,$08,$00,$03,$04,$01,$07,$02,$04,$04,$04,$04

; E28: Nine signed X/Y offset pairs; original scale pixels, player-relative.
MagicAimOffsets:
    .byte $EC,$F0,$EC,$E8,$F0,$E0,$F8,$DC,$00,$D8,$08,$DC,$10,$E0,$14,$E8
    .byte $14,$F0

; E29: Update aiming orb; newSelect, free reserved projectile slot and cost5MP required; spawn type00/01,flags90,velocityX±8,Y0 at orbY-8.
CastHorizontalMagicWave:
    JSR a:$b747              ; B7D4 
    LDA $1f                  ; B7D7 
    AND #$20                 ; B7D9 
    BEQ $b82d                ; B7DB 
    JSR a:$bda8              ; B7DD Projectile allocation precedes MP charge: full reserved pool costs nothing.
    BMI $b82d                ; B7E0 
    LDA #$05                 ; B7E2 
    JSR a:$bd46              ; B7E4 
    BCS $b82d                ; B7E7 
    LDA #$66                 ; B7E9 
    STA $01                  ; B7EB 
    LDA a:$04f3              ; B7ED 
    SEC                      ; B7F0 
    SBC #$08                 ; B7F1 
    STA a:$04f0,Y            ; B7F3 
    LDA a:$0507              ; B7F6 
    SBC #$00                 ; B7F9 
    STA a:$0504,Y            ; B7FB 
    LDA a:$051b              ; B7FE 
    STA a:$0518,Y            ; B801 
    LDA a:$052f              ; B804 
    STA a:$052c,Y            ; B807 
    LDA #$00                 ; B80A 
    STA a:$0554,Y            ; B80C 
    STA a:$0568,Y            ; B80F 
    STA a:$0590,Y            ; B812 
    LDA #$90                 ; B815 
    STA a:$057c,Y            ; B817 
    LDA $cd                  ; B81A 
    LSR A                    ; B81C 
    BCC $b828                ; B81D 
    LDA #$01                 ; B81F 
    STA a:$0568,Y            ; B821 
    LDA #$f8                 ; B824 
    BMI $b82a                ; B826 
    LDA #$08                 ; B828 
    STA a:$0540,Y            ; B82A 
    LDX $3e                  ; B82D 
    RTS                      ; B82F 

; E30: Cost1MP starts240-count effect and setsB8=DF; active calls decrement, toggleB8bit20 on multiples4, restoreFF at expiry. Hidden-object reveal semantics not established.
ToggleObjectAttributeEffect:
    LDA a:$0593              ; B830 
    BNE $b850                ; B833 
    LDA $1f                  ; B835 
    AND #$20                 ; B837 
    BEQ $b868                ; B839 
    LDA #$01                 ; B83B 
    JSR a:$bd46              ; B83D 
    BCS $b868                ; B840 
    LDA #$a9                 ; B842 
    STA $01                  ; B844 
    LDA #$f0                 ; B846 
    STA a:$0593              ; B848 
    LDA #$df                 ; B84B 
    STA $b8                  ; B84D 
    RTS                      ; B84F 
    DEC a:$0593              ; B850 
    LDA a:$0593              ; B853 
    BEQ $b863                ; B856 
    AND #$03                 ; B858 
    BNE $b868                ; B85A 
    LDA $b8                  ; B85C 
    EOR #$20                 ; B85E 
    STA $b8                  ; B860 
    RTS                      ; B862 
    LDA #$ff                 ; B863 
    STA a:$00b8              ; B865 
    RTS                      ; B868 

; E31: NewSelect and20MP reanchor slot3, set velocityY=F8,type8C,counter5,secondarycounter0.
StartOverheadLightning:
    LDA $1f                  ; B869 
    AND #$20                 ; B86B 
    BEQ $b88d                ; B86D 
    LDA #$20                 ; B86F 
    JSR a:$bd46              ; B871 
    BCS $b88d                ; B874 
    JSR a:$b677              ; B876 
    LDA #$f8                 ; B879 
    STA a:$0557              ; B87B 
    LDA #$8c                 ; B87E 
    STA a:$056b              ; B880 
    LDA #$05                 ; B883 
    STA a:$0593              ; B885 
    LDA #$00                 ; B888 
    STA a:$05a7              ; B88A 
    RTS                      ; B88D 

; E32: Cost20MP invokesC7BE once; cycle0593/03D6 from1 through59 then0. Active calls ignore newSelect; enemy duration beyond flag setter unresolved.
StartQuakeAndUpdateScrollPhase:
    LDY a:$0593              ; B88E 
    BNE $b8a9                ; B891 
    LDA $1f                  ; B893 
    AND #$20                 ; B895 
    BEQ $b8b6                ; B897 
    LDA #$20                 ; B899 
    JSR a:$bd46              ; B89B 
    BCS $b8b6                ; B89E 
    LDA #$b5                 ; B8A0 
    STA $01                  ; B8A2 
    JSR a:$c7be              ; B8A4 
    LDY #$00                 ; B8A7 
    INY                      ; B8A9 
    CPY #$3c                 ; B8AA 
    BNE $b8b0                ; B8AC 
    LDY #$00                 ; B8AE 
    STY a:$0593              ; B8B0 
    STY a:$03d6              ; B8B3 
    RTS                      ; B8B6 

; E33: Cost20MP sets palette0158=16,counters04:F0; same invocation decrements lowcounter. Expiry after1008 handler invocations restoresFFB5 palette byte.
StartTerrainProtectionTimer:
    LDA a:$0593              ; B8B7 
    ORA a:$05a7              ; B8BA 
    BNE $b8df                ; B8BD 
    LDA $1f                  ; B8BF 
    AND #$20                 ; B8C1 
    BEQ $b8ef                ; B8C3 
    LDA #$20                 ; B8C5 
    JSR a:$bd46              ; B8C7 
    BCS $b8ef                ; B8CA 
    LDA #$98                 ; B8CC 
    STA $01                  ; B8CE 
    LDA #$16                 ; B8D0 
    STA a:$0158              ; B8D2 
    LDA #$04                 ; B8D5 
    STA a:$05a7              ; B8D7 
    LDA #$f0                 ; B8DA 
    STA a:$0593              ; B8DC 
    DEC a:$0593              ; B8DF Activation falls through decrement; total is F0+3*100=3F0 hex handler calls.
    BNE $b8ef                ; B8E2 
    DEC a:$05a7              ; B8E4 
    BNE $b8ef                ; B8E7 
    LDA a:$ffb5              ; B8E9 
    STA a:$0158              ; B8EC 
    RTS                      ; B8EF 

; E34: Cost30MP sets sound9D,secondarycounter0A,type8A; actual hit consumption not reviewed.
StartShieldEffect:
    LDA $1f                  ; B8F0 
    AND #$20                 ; B8F2 
    BEQ $b90b                ; B8F4 
    LDA #$30                 ; B8F6 
    JSR a:$bd46              ; B8F8 
    BCS $b90b                ; B8FB 
    LDA #$9d                 ; B8FD 
    STA $01                  ; B8FF 
    LDA #$0a                 ; B901 
    STA a:$05a7              ; B903 
    LDA #$8a                 ; B906 
    STA a:$056b              ; B908 
    RTS                      ; B90B 

; E35: Cost20MP reanchors slot3,sets counterC9,type88,flags84.
StartDecoyEffect:
    LDA $1f                  ; B90C 
    AND #$20                 ; B90E 
    BEQ $b92f                ; B910 
    LDA #$20                 ; B912 
    JSR a:$bd46              ; B914 
    BCS $b92f                ; B917 
    LDA #$aa                 ; B919 
    STA $01                  ; B91B 
    JSR a:$b677              ; B91D 
    LDA #$c9                 ; B920 
    STA a:$0593              ; B922 
    LDA #$88                 ; B925 
    STA a:$056b              ; B927 
    LDA #$84                 ; B92A 
    STA a:$057f              ; B92C 
    RTS                      ; B92F 

; E36: Require same cameraX page and relativeY in0..EF; then decrementC9 lifetime. Offscreen or zero resets type86 and counter0.
UpdateDecoyLifetimeAndBounds:
    LDA a:$051b              ; B930 
    SEC                      ; B933 
    SBC $a7                  ; B934 
    LDA a:$052f              ; B936 
    SBC $a8                  ; B939 
    BNE $b959                ; B93B 
    LDA a:$04f3              ; B93D 
    SEC                      ; B940 
    SBC $a9                  ; B941 
    STA a:$05a7              ; B943 
    LDA a:$0507              ; B946 
    SBC $aa                  ; B949 
    BNE $b959                ; B94B 
    LDA a:$05a7              ; B94D 
    CMP #$f0                 ; B950 
    BCS $b959                ; B952 
    DEC a:$0593              ; B954 
    BNE $b963                ; B957 
    LDA #$00                 ; B959 
    STA a:$0593              ; B95B 
    LDA #$86                 ; B95E 
    STA a:$056b              ; B960 
    RTS                      ; B963 

; E37: While05A7 nonnegative anchor slot3 to player; negative returns type84. Consumer of shield budget outside this range.
UpdateShieldAnchorOrFinish:
    LDA a:$05a7              ; B964 
    BMI $b96c                ; B967 
    JMP a:$b677              ; B969 
    LDA #$84                 ; B96C 
    STA a:$056b              ; B96E 
    RTS                      ; B971 

; E38: Track playerX; low-byte effectY-cameraY<30 stops vertical velocity and changes type8E.
RaiseLightningToCameraTop:
    LDA $cb                  ; B972 
    STA a:$051b              ; B974 
    LDA $cc                  ; B977 
    STA a:$052f              ; B979 
    LDA a:$04f3              ; B97C 
    SEC                      ; B97F 
    SBC $a9                  ; B980 
    CMP #$30                 ; B982 
    BCS $b990                ; B984 
    LDA #$00                 ; B986 
    STA a:$0557              ; B988 
    LDA #$8e                 ; B98B 
    STA a:$056b              ; B98D 
    RTS                      ; B990 

; E39: Anchor selected effect at cameraY+30 and playerX; after5-count wait spawn3 slots with types28,18,29,flagsD4,zero velocities; selectedtype90.
SpawnOverheadLightningBolts:
    LDA $cb                  ; B991 
    STA a:$051b              ; B993 
    LDA $cc                  ; B996 
    STA a:$052f              ; B998 
    LDA $a9                  ; B99B 
    CLC                      ; B99D 
    ADC #$30                 ; B99E 
    STA a:$04f3              ; B9A0 
    LDA $aa                  ; B9A3 
    ADC #$00                 ; B9A5 
    STA a:$0507              ; B9A7 
    DEC a:$0593              ; B9AA 
    BNE $b9da                ; B9AD 
    LDY #$02                 ; B9AF 
    JSR a:$b65e              ; B9B1 
    LDA #$00                 ; B9B4 
    STA a:$0540,Y            ; B9B6 
    STA a:$0554,Y            ; B9B9 
    LDA a:$b9de,Y            ; B9BC 
    STA a:$0590,Y            ; B9BF 
    LDA #$02                 ; B9C2 
    STA a:$05a4,Y            ; B9C4 
    LDA a:$b9db,Y            ; B9C7 
    STA a:$0568,Y            ; B9CA 
    LDA #$d4                 ; B9CD 
    STA a:$057c,Y            ; B9CF 
    DEY                      ; B9D2 
    BPL $b9b1                ; B9D3 
    LDA #$90                 ; B9D5 
    STA a:$056b              ; B9D7 
    RTS                      ; B9DA 

; E40: Three types28,18,29 then three counters08,15,08; not three-byte CPU pointers.
LightningBoltTypesAndCounters:
    .byte $28,$18,$29,$08,$15,$08

; E41: Anchor at cameraY+30/playerX; decrement05A7 seeded0 (256 invocations), toggle90/92 on odd remaining count; zero selects94 and downwardvelocity8.
HoldAndLowerLightning:
    LDA $cb                  ; B9E1 
    STA a:$051b              ; B9E3 
    LDA $cc                  ; B9E6 
    STA a:$052f              ; B9E8 
    LDA $a9                  ; B9EB 
    CLC                      ; B9ED 
    ADC #$30                 ; B9EE 
    STA a:$04f3              ; B9F0 
    LDA $aa                  ; B9F3 
    ADC #$00                 ; B9F5 
    STA a:$0507              ; B9F7 
    DEC a:$05a7              ; B9FA 
    BEQ $ba0e                ; B9FD 
    LDA a:$05a7              ; B9FF 
    LSR A                    ; BA02 
    BCC $ba0d                ; BA03 
    LDA a:$056b              ; BA05 
    EOR #$02                 ; BA08 
    STA a:$056b              ; BA0A 
    RTS                      ; BA0D 
    LDA #$94                 ; BA0E 
    STA a:$056b              ; BA10 
    LDA #$08                 ; BA13 
    STA a:$0557              ; BA15 
    RTS                      ; BA18 

; E42: TrackplayerX; wrapped(effectY-playerY+10hex)<40hex stops velocity and restores readytype76.
FinishLightningNearPlayer:
    LDA $cb                  ; BA19 
    STA a:$051b              ; BA1B 
    LDA $cc                  ; BA1E 
    STA a:$052f              ; BA20 
    LDA a:$04f3              ; BA23 
    SEC                      ; BA26 
    SBC $c9                  ; BA27 
    CLC                      ; BA29 
    ADC #$10                 ; BA2A 
    CMP #$40                 ; BA2C 
    BCS $ba3a                ; BA2E 
    LDA #$00                 ; BA30 
    STA a:$0557              ; BA32 
    LDA #$76                 ; BA35 
    STA a:$056b              ; BA37 
    RTS                      ; BA3A 

; E43: NegativeD3 blocks before any cost; Select togglesCEbit0 and clearsCD to facing. Starting or every30 active handler updates spends10MP; failure clears flightbit.
ToggleAndRechargeFlight:
    LDA $d3                  ; BA3B 
    BMI $ba74                ; BA3D 
    LDA $1f                  ; BA3F 
    AND #$20                 ; BA41 
    BNE $ba50                ; BA43 
    LDA $ce                  ; BA45 
    LSR A                    ; BA47 
    BCC $ba74                ; BA48 
    DEC a:$0593              ; BA4A 
    BEQ $ba5b                ; BA4D 
    RTS                      ; BA4F 
    LDA $cd                  ; BA50 
    AND #$01                 ; BA52 
    STA $cd                  ; BA54 
    LDA $ce                  ; BA56 
    LSR A                    ; BA58 
    BCS $ba6e                ; BA59 
    LDA #$10                 ; BA5B 10 is packed decimal10MP; counter1E is30 handler calls,not verified seconds.
    JSR a:$bd46              ; BA5D 
    BCS $ba6e                ; BA60 
    LDA #$1e                 ; BA62 
    STA a:$0593              ; BA64 
    LDA $ce                  ; BA67 
    ORA #$01                 ; BA69 
    STA $ce                  ; BA6B 
    RTS                      ; BA6D 
    LDA $ce                  ; BA6E 
    AND #$fe                 ; BA70 
    STA $ce                  ; BA72 
    RTS                      ; BA74 

; E44: If not active, Select and30MP set0593=1 and populate global slots0..2 atcameraX+20/80/E0,cameraY+CF,types98,flags84.
StartThreeColumnLightning:
    LDA a:$0593              ; BA75 
    BNE $bac3                ; BA78 
    LDA $1f                  ; BA7A 
    AND #$20                 ; BA7C 
    BEQ $bac3                ; BA7E 
    LDA #$30                 ; BA80 
    JSR a:$bd46              ; BA82 
    BCS $bac3                ; BA85 
    INC a:$0593              ; BA87 
    LDY #$02                 ; BA8A 
    LDA $a7                  ; BA8C 
    CLC                      ; BA8E 
    ADC a:$bac4,Y            ; BA8F 
    STA a:$0518,Y            ; BA92 
    LDA $a8                  ; BA95 
    ADC #$00                 ; BA97 
    STA a:$052c,Y            ; BA99 
    LDA $a9                  ; BA9C 
    CLC                      ; BA9E 
    ADC #$cf                 ; BA9F 
    STA a:$04f0,Y            ; BAA1 
    LDA $aa                  ; BAA4 
    ADC #$00                 ; BAA6 
    STA a:$0504,Y            ; BAA8 
    LDA #$00                 ; BAAB 
    STA a:$0540,Y            ; BAAD 
    STA a:$0554,Y            ; BAB0 
    STA a:$0590,Y            ; BAB3 
    LDA #$98                 ; BAB6 
    STA a:$0568,Y            ; BAB8 
    LDA #$84                 ; BABB 
    STA a:$057c,Y            ; BABD 
    DEY                      ; BAC0 
    BPL $ba8c                ; BAC1 
    RTS                      ; BAC3 

; E45: Three camera-relative X offsets20,80,E0.
LightningColumnOffsets:
    .byte $20,$80,$E0

; E46: Followcamera,increment0590; slot0 requests queued damage6 on ticks8/16/24. Tick30deactivates and clears selected active marker; type animation table otherwise.
UpdateLightningColumn:
    LDA $a7                  ; BAC7 
    CLC                      ; BAC9 
    ADC a:$bac4,X            ; BACA 
    STA a:$0518,X            ; BACD 
    LDA $a8                  ; BAD0 
    ADC #$00                 ; BAD2 
    STA a:$052c,X            ; BAD4 
    LDA $a9                  ; BAD7 
    CLC                      ; BAD9 
    ADC #$cf                 ; BADA 
    STA a:$04f0,X            ; BADC 
    LDA $aa                  ; BADF 
    ADC #$00                 ; BAE1 
    STA a:$0504,X            ; BAE3 
    INC a:$0590,X            ; BAE6 
    TXA                      ; BAE9 
    BNE $bafc                ; BAEA 
    LDA #$97                 ; BAEC 
    STA $01                  ; BAEE 
    LDA a:$0590,X            ; BAF0 
    AND #$07                 ; BAF3 
    BNE $bafc                ; BAF5 
    LDA #$06                 ; BAF7 
    JSR a:$bd1b              ; BAF9 
    LDA a:$0590,X            ; BAFC 
    CMP #$1e                 ; BAFF 
    BEQ $bb14                ; BB01 
    CPX #$01                 ; BB03 
    BNE $bb0a                ; BB05 
    CLC                      ; BB07 
    ADC #$07                 ; BB08 
    AND #$0f                 ; BB0A 
    TAY                      ; BB0C 
    LDA a:$bb1d,Y            ; BB0D 
    STA a:$0568,X            ; BB10 
    RTS                      ; BB13 
    LDA #$00                 ; BB14 
    STA a:$057c,X            ; BB16 
    STA a:$0593              ; BB19 
    RTS                      ; BB1C 

; E47: Sixteen even/odd type bytes; facing ignored by handler dispatch, preserved by rendering.
LightningColumnTypeSequence:
    .byte $98,$E0,$9C,$9E,$9F,$9D,$9B,$99,$99,$9B,$9D,$9E,$9E,$9C,$9A,$98
    .incbin "inputs/original.nes", $013B3D, $01EE ; UNINTERPRETED preserved bytes

; E48: Scan10 slots9..0; flags0469>=C0 and0473&3==0 accept raw requestA into0441,OR0469bit20,clear047Dlow3. Does not apply HP damage here.
QueueDamageForEligibleEnemies:
    STA $3c                  ; BD1B Queue request only; enemy HP, immunity and final resolution are separate.
    LDY #$09                 ; BD1D 
    LDA a:$0469,Y            ; BD1F 
    CMP #$c0                 ; BD22 
    BCC $bd42                ; BD24 
    LDA a:$0473,Y            ; BD26 
    AND #$03                 ; BD29 
    BNE $bd42                ; BD2B 
    LDA $3c                  ; BD2D 
    STA a:$0441,Y            ; BD2F 
    LDA a:$0469,Y            ; BD32 
    ORA #$20                 ; BD35 
    STA a:$0469,Y            ; BD37 
    LDA a:$047d,Y            ; BD3A 
    AND #$f8                 ; BD3D 
    STA a:$047d,Y            ; BD3F 
    DEY                      ; BD42 
    BPL $bd1f                ; BD43 
    RTS                      ; BD45 

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

; E49: Scan global slots2..0 for nonnegative057C; allbusy returnsY=FF/Nset. Distinct from general collectible allocator.
FindFreeReservedProjectileSlot:
    LDY #$02                 ; BDA8 
    LDA a:$057c,Y            ; BDAA 
    BPL $bdb2                ; BDAD 
    DEY                      ; BDAF 
    BPL $bdaa                ; BDB0 
    RTS                      ; BDB2 
    .incbin "inputs/original.nes", $013DC3, $00DD ; UNINTERPRETED preserved bytes

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
