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

; D07: Skip when A1 bit40/80 set; otherwise A1 indexes six split pointers. Valid low selector0..5.
DispatchCollisionWorkPhase:
    BIT $a1                  ; A012 
    BVS $a027                ; A014 
    BMI $a027                ; A016 
    LDY $a1                  ; A018 
    LDA a:$a028,Y            ; A01A 
    STA $22                  ; A01D 
    LDA a:$a02e,Y            ; A01F 
    STA $23                  ; A022 
    JMP ($0022)              ; A024 
    RTS                      ; A027 

; D08: Six low bytes followed by six high bytes; index0 returns, index4 scans pickups directly.
CollisionWorkPhaseTargets:
    .byte $68,$3D,$34,$46,$4F,$55,$A6,$A0,$A0,$A0,$A0,$A0

; D09: Phase-specific wrappers; preserve explicit unreviewed collision/attack callees.
CollisionWorkPhaseEntries:
    JSR a:$a05b              ; A034 
    JSR a:$a2c3              ; A037 
    JMP a:$a197              ; A03A 
    JSR a:$a05b              ; A03D 
    JSR a:$a075              ; A040 
    JMP a:$a120              ; A043 
    JSR a:$a05b              ; A046 
    JSR a:$a305              ; A049 
    JMP a:$a197              ; A04C 
    JSR a:$a14f              ; A04F 
    JMP a:$a1e8              ; A052 
    JSR a:$a05b              ; A055 
    JMP a:$a230              ; A058 

; D10: 03D8/03D9 or D3&A0 may discard own return address and return caller-of-caller; one partial gate maps CHR R1=2.
GateCollisionWorkAndUnwind:
    LDA a:$03d8              ; A05B 
    BEQ $a06c                ; A05E 
    LDA a:$03d9              ; A060 
    BNE $a072                ; A063 
    LDX #$01                 ; A065 
    LDA #$02                 ; A067 
    JSR a:$c76a              ; A069 
    LDA $d3                  ; A06C 
    AND #$a0                 ; A06E 
    BEQ $a074                ; A070 
    PLA                      ; A072 PLA; PLA; RTS deliberately drops the immediate caller continuation.
    PLA                      ; A073 
    RTS                      ; A074 
    .incbin "inputs/original.nes", $010085, $00DA ; UNINTERPRETED preserved bytes

; D11: Scan indices04EF down to1; types40..6F, active flag, low-coordinate overlap and signed velocity gate precede effect dispatch.
ScanPlayerCollectibles:
    LDA a:$04ef              ; A14F 
    STA $3c                  ; A152 
    JSR a:$a05b              ; A154 
    LDY $3c                  ; A157 
    LDA a:$056b,Y            ; A159 
    CMP #$70                 ; A15C 
    BCS $a192                ; A15E 
    CMP #$40                 ; A160 
    BCC $a192                ; A162 
    LDA a:$057f,Y            ; A164 
    BPL $a192                ; A167 
    LDA a:$04f3,Y            ; A169 
    SEC                      ; A16C 
    SBC #$06                 ; A16D 
    STA $22                  ; A16F 
    LDA #$0f                 ; A171 
    STA $23                  ; A173 
    LDA a:$051b,Y            ; A175 
    CLC                      ; A178 
    ADC #$04                 ; A179 
    STA $24                  ; A17B 
    LDA #$09                 ; A17D 
    STA $25                  ; A17F 
    JSR a:$a528              ; A181 
    BCS $a192                ; A184 
    LDA a:$0557,Y            ; A186 
    BPL $a18f                ; A189 
    CMP #$fb                 ; A18B 
    BCC $a192                ; A18D 
    JSR a:$a64d              ; A18F 
    DEC $3c                  ; A192 
    BNE $a154                ; A194 
    RTS                      ; A196 
    .incbin "inputs/original.nes", $0101A7, $0391 ; UNINTERPRETED preserved bytes

; D12: Two wrapped low-byte inequalities; carry clear means overlap. Does not consult high coordinate bytes.
TestPlayerPickupRectangle:
    LDA $23                  ; A528 
    CLC                      ; A52A 
    ADC #$20                 ; A52B 
    STA $3e                  ; A52D 
    LDA $22                  ; A52F 
    CLC                      ; A531 
    ADC #$20                 ; A532 
    SEC                      ; A534 
    SBC $c9                  ; A535 
    CMP $3e                  ; A537 
    BCS $a54c                ; A539 
    LDA $25                  ; A53B 
    CLC                      ; A53D 
    ADC #$11                 ; A53E 
    STA $3e                  ; A540 
    LDA $24                  ; A542 
    CLC                      ; A544 
    ADC #$08                 ; A545 
    SEC                      ; A547 
    SBC $cb                  ; A548 
    CMP $3e                  ; A54A 
    RTS                      ; A54C 
    .incbin "inputs/original.nes", $01055D, $0100 ; UNINTERPRETED preserved bytes

; D13: Require type40..6F, clear facing bit, use A629+evenType pointer then JMP(2C).
DispatchCollectibleEffect:
    LDA a:$056b,Y            ; A64D 
    CMP #$70                 ; A650 
    BCS $a668                ; A652 
    CMP #$40                 ; A654 
    BCC $a668                ; A656 
    AND #$fe                 ; A658 
    TAX                      ; A65A 
    LDA a:$a629,X            ; A65B 
    STA $2c                  ; A65E 
    LDA a:$a62a,X            ; A660 
    STA $2d                  ; A663 
    JMP ($002c)              ; A665 
    RTS                      ; A668 

; D14: Twenty-four little-endian targets for paired types40/41..6E/6F; twelve entries point to unreviewed A7DB.
CollectibleEffectPointers:
    .byte $8A,$A7,$3D,$A7,$44,$A7,$AB,$A6,$B4,$A6,$BD,$A6,$A3,$A7,$B5,$A7
    .byte $DB,$A7,$DB,$A7,$DB,$A7,$DB,$A7,$DB,$A7,$DB,$A7,$DB,$A7,$DB,$A7
    .byte $DB,$A7,$DB,$A7,$DB,$A7,$DB,$A7,$CB,$A7,$99,$A6,$CE,$A7,$CB,$A7

; D15: Deactivate collectible; increment030E unless exactly0A; successful increment requests soundDC.
CollectExtraAttempt:
    JSR a:$a7af              ; A699 
    LDA a:$030e              ; A69C 
    CMP #$0a                 ; A69F Equality to0A blocks increment; not a greater-than-or-equal clamp.
    BEQ $a6aa                ; A6A1 
    LDA #$dc                 ; A6A3 
    STA $01                  ; A6A5 
    INC a:$030e              ; A6A7 
    RTS                      ; A6AA 

; D16: Deactivate collectible and add10,30 or50 decimal EXP through common digit accumulator.
CollectExperienceEntries:
    JSR a:$a7af              ; A6AB 
    LDA #$01                 ; A6AE 
    LDX #$01                 ; A6B0 
    BNE $a6c4                ; A6B2 
    JSR a:$a7af              ; A6B4 
    LDA #$03                 ; A6B7 
    LDX #$01                 ; A6B9 
    BNE $a6c4                ; A6BB 
    JSR a:$a7af              ; A6BD 
    LDA #$05                 ; A6C0 
    LDX #$01                 ; A6C2 

; D17: Add base60 decimal digits; overflow saturates9999 and returns early. Otherwise compare next threshold and advance at most one level up to7, update maxima/threshold and spawn effect.
AddExperienceAndCheckLevel:
    CLC                      ; A6C4 
    ADC $ed,X                ; A6C5 
    CMP #$6a                 ; A6C7 
    BCC $a6e4                ; A6C9 
    INX                      ; A6CB 
    CPX #$04                 ; A6CC 
    BEQ $a6d9                ; A6CE 
    SEC                      ; A6D0 
    SBC #$0a                 ; A6D1 
    STA $ec,X                ; A6D3 
    LDA #$01                 ; A6D5 
    BNE $a6c4                ; A6D7 
    LDA #$69                 ; A6D9 Overflow clamps all EXP digits and returns before level or sound checks.
    STA $ed                  ; A6DB 
    STA $ee                  ; A6DD 
    STA $ef                  ; A6DF 
    STA $f0                  ; A6E1 
    RTS                      ; A6E3 
    STA $ed,X                ; A6E4 
    LDX #$03                 ; A6E6 
    LDA $f1,X                ; A6E8 
    CMP $ed,X                ; A6EA 
    BCC $a6f3                ; A6EC 
    BNE $a738                ; A6EE 
    DEX                      ; A6F0 
    BPL $a6e8                ; A6F1 
    LDA $d3                  ; A6F3 
    AND #$07                 ; A6F5 
    CMP #$07                 ; A6F7 
    BEQ $a738                ; A6F9 
    INC $d3                  ; A6FB 
    LDY $d3                  ; A6FD Unmasked D3 used as HP table index after INC. Valid level-only D3 is0..7; high flags require caller invariants.
    LDA a:$fde0,Y            ; A6FF 
    STA a:$06bb              ; A702 
    LDA $d3                  ; A705 
    AND #$07                 ; A707 
    STA $43                  ; A709 
    ASL A                    ; A70B 
    ASL A                    ; A70C 
    TAY                      ; A70D 
    LDX #$03                 ; A70E 
    LDA a:$fda8,Y            ; A710 
    STA $f1,X                ; A713 
    INY                      ; A715 
    DEX                      ; A716 
    BPL $a710                ; A717 
    LDA $43                  ; A719 
    ASL A                    ; A71B 
    CLC                      ; A71C 
    ADC $43                  ; A71D 
    TAY                      ; A71F 
    LDX #$02                 ; A720 
    LDA a:$fdc8,Y            ; A722 
    STA $f5,X                ; A725 
    INY                      ; A727 
    DEX                      ; A728 
    BPL $a722                ; A729 
    JSR a:$a878              ; A72B 
    LDA #$b4                 ; A72E 
    STA a:$03d5              ; A730 
    LDA #$e4                 ; A733 
    STA $01                  ; A735 
    RTS                      ; A737 
    LDA #$2b                 ; A738 
    STA $01                  ; A73A 
    RTS                      ; A73C 

; D18: Add5 or10 decimal MP; carry between base60 digits, saturate999 then clamp to F5..F7 maximum; deactivate collectible and request sound2B.
CollectMagicPoints:
    LDA #$05                 ; A73D 
    LDX #$00                 ; A73F 
    JMP a:$a747              ; A741 
    LDA #$01                 ; A744 
    TAX                      ; A746 
    PHA                      ; A747 
    JSR a:$a7af              ; A748 
    LDA #$2b                 ; A74B 
    STA $01                  ; A74D 
    PLA                      ; A74F 
    CLC                      ; A750 
    ADC $ea,X                ; A751 
    CMP #$6a                 ; A753 
    BCC $a76d                ; A755 
    INX                      ; A757 
    CPX #$03                 ; A758 
    BEQ $a765                ; A75A 
    SEC                      ; A75C 
    SBC #$0a                 ; A75D 
    STA $e9,X                ; A75F 
    LDA #$01                 ; A761 
    BNE $a750                ; A763 
    LDA #$69                 ; A765 
    STA $ea                  ; A767 
    STA $eb                  ; A769 
    LDX #$02                 ; A76B 
    STA $ea,X                ; A76D 
    LDX #$02                 ; A76F 
    LDA $f5,X                ; A771 
    CMP $ea,X                ; A773 
    BCC $a77d                ; A775 
    BNE $a77c                ; A777 
    DEX                      ; A779 
    BPL $a771                ; A77A 
    RTS                      ; A77C 
    LDA $f5                  ; A77D 
    STA $ea                  ; A77F 
    LDA $f6                  ; A781 
    STA $eb                  ; A783 
    LDA $f7                  ; A785 
    STA $ec                  ; A787 
    RTS                      ; A789 

; D19: Add10 hex raw HP and cap at06BB in valid HP domain; deactivate collectible, request soundA1.
CollectHealingHeart:
    LDA #$10                 ; A78A 
    CLC                      ; A78C 
    ADC a:$06b9              ; A78D 
    CMP a:$06bb              ; A790 
    BCC $a798                ; A793 
    LDA a:$06bb              ; A795 
    STA a:$06b9              ; A798 
    JSR a:$a7af              ; A79B 
    LDA #$a1                 ; A79E 
    STA $01                  ; A7A0 
    RTS                      ; A7A2 

; D20: Deactivate collectible; request sound2B; A=12 tails to C746/D8B5 for100 decimal score.
CollectScoreHundred:
    JSR a:$a7af              ; A7A3 
    LDA #$2b                 ; A7A6 
    STA $01                  ; A7A8 
    LDA #$12                 ; A7AA 
    JMP a:$c746              ; A7AC 

; D21: Set057F,Y to zero; preserve X/Y.
DeactivateCollectible:
    LDA #$00                 ; A7AF 
    STA a:$057f,Y            ; A7B1 
    RTS                      ; A7B4 

; D22: Clear audio commands, deactivate, copy0593,Y to scene9A then call fade C788 and tail C77F; downstream transition outside this range.
CollectSceneTransition:
    LDA #$c0                 ; A7B5 
    STA $01                  ; A7B7 
    LDA #$00                 ; A7B9 
    STA $00                  ; A7BB 
    JSR a:$a7af              ; A7BD 
    LDA a:$0593,Y            ; A7C0 
    STA $9a                  ; A7C3 
    JSR a:$c788              ; A7C5 
    JMP a:$c77f              ; A7C8 

; D23: A7CB deactivates first; A7CE entry does not. If D3 nonnegative, tail to damage4 with carry from player facing bit.
CollectDamageHazard:
    JSR a:$a7af              ; A7CB 
    LDA $d3                  ; A7CE 
    BMI $a7da                ; A7D0 
    LDA $cd                  ; A7D2 
    LSR A                    ; A7D4 
    LDA #$04                 ; A7D5 
    JMP a:$c76d              ; A7D7 
    RTS                      ; A7DA 
    .incbin "inputs/original.nes", $0107EB, $009D ; UNINTERPRETED preserved bytes

; D24: Allocate collectible-relative slot; if available, type96 active80 at player position with velocityY=FD and velocityX=0.
SpawnLevelUpObject:
    JSR a:$c79a              ; A878 
    BMI $a8a5                ; A87B 
    LDA #$80                 ; A87D 
    STA a:$057f,Y            ; A87F 
    LDA $cb                  ; A882 
    STA a:$051b,Y            ; A884 
    LDA $cc                  ; A887 
    STA a:$052f,Y            ; A889 
    LDA $c9                  ; A88C 
    STA a:$04f3,Y            ; A88E 
    LDA $ca                  ; A891 
    STA a:$0507,Y            ; A893 
    LDA #$00                 ; A896 
    STA a:$0543,Y            ; A898 
    LDA #$fd                 ; A89B 
    STA a:$0557,Y            ; A89D 
    LDA #$96                 ; A8A0 
    STA a:$056b,Y            ; A8A2 
    RTS                      ; A8A5 
    .incbin "inputs/original.nes", $0108B6, $0270 ; UNINTERPRETED preserved bytes

; C33: Tail through C79D to scene advance D1AA when F8 bit20 is set.
PlayerStageAdvanceTail:
    JMP a:$c79d              ; AB16 

; C34: Clear transient D3 bit7, honor advance flag, retain only CE bit0, dispatch player state, compute camera-relative coordinates, service hurt display and draw metasprite.
UpdateAndDrawPlayer:
    ASL $d3                  ; AB19 Bit7 is cleared then reasserted by active terminal/hurt state handlers; not a permanent global game-over flag.
    CLC                      ; AB1B 
    ROR $d3                  ; AB1C 
    LDA $f8                  ; AB1E 
    AND #$20                 ; AB20 
    BNE $ab16                ; AB22 
    STA $b0                  ; AB24 
    STA $99                  ; AB26 
    LDX #$02                 ; AB28 
    STX $b1                  ; AB2A 
    LSR $ce                  ; AB2C A is zero here. LSR CE; ROL A retains only old CE bit0.
    ROL A                    ; AB2E 
    STA $ce                  ; AB2F 
    JSR a:$acf7              ; AB31 A=old CE&1 selects the normal or alternate state-table family.
    LDA $c9                  ; AB34 
    SEC                      ; AB36 
    SBC $a9                  ; AB37 
    STA $22                  ; AB39 
    LDA $ca                  ; AB3B 
    SBC $aa                  ; AB3D 
    STA $23                  ; AB3F 
    LDA $cb                  ; AB41 
    SEC                      ; AB43 
    SBC $a7                  ; AB44 
    STA $24                  ; AB46 
    LDA $cc                  ; AB48 
    SBC $a8                  ; AB4A 
    STA $25                  ; AB4C 
    LDA $22                  ; AB4E 
    CMP #$ce                 ; AB50 
    BCC $ab5f                ; AB52 
    LDA $cd                  ; AB54 
    AND #$fe                 ; AB56 
    CMP #$c4                 ; AB58 
    BEQ $ab5f                ; AB5A 
    JSR a:$b007              ; AB5C 
    LDA $d2                  ; AB5F 
    BEQ $ab71                ; AB61 
    DEC $d2                  ; AB63 
    LDA $d2                  ; AB65 
    AND #$02                 ; AB67 
    BNE $ab6f                ; AB69 
    LDA #$01                 ; AB6B 
    BNE $ab71                ; AB6D 
    LDA #$03                 ; AB6F 
    STA $2c                  ; AB71 
    LDA $ce                  ; AB73 
    AND #$08                 ; AB75 
    ASL A                    ; AB77 
    ASL A                    ; AB78 
    ORA $2c                  ; AB79 
    STA $2c                  ; AB7B 
    LDA $d3                  ; AB7D 
    AND #$20                 ; AB7F 
    BEQ $ab9a                ; AB81 
    LDA $d3                  ; AB83 
    AND #$10                 ; AB85 
    BNE $ab8d                ; AB87 
    LDA #$c8                 ; AB89 
    BNE $ab8f                ; AB8B 
    LDA #$c6                 ; AB8D 
    LSR A                    ; AB8F 
    LSR $cd                  ; AB90 
    ROL A                    ; AB92 
    STA $cd                  ; AB93 
    LSR $ce                  ; AB95 
    CLC                      ; AB97 
    ROL $ce                  ; AB98 
    LDA $cd                  ; AB9A 
    LSR A                    ; AB9C 
    BCS $aba5                ; AB9D 
    JSR a:$f6ed              ; AB9F 
    JMP a:$aba8              ; ABA2 
    JSR a:$f737              ; ABA5 
    LDA a:$06bd              ; ABA8 
    CMP #$0b                 ; ABAB 
    BNE $abb4                ; ABAD 
    LDA a:$0593              ; ABAF 
    BNE $abc4                ; ABB2 
    LDA $c9                  ; ABB4 
    STA $d4                  ; ABB6 
    LDA $ca                  ; ABB8 
    STA $d5                  ; ABBA 
    LDA $cb                  ; ABBC 
    STA $d6                  ; ABBE 
    LDA $cc                  ; ABC0 
    STA $d7                  ; ABC2 
    RTS                      ; ABC4 
    .incbin "inputs/original.nes", $010BD5, $0132 ; UNINTERPRETED preserved bytes

; C35: A selects normal/alternate table family; CD>>1 selects CHR and CD&FE selects metasprite pointer plus handler; tail JMP through 2C/2D.
DispatchPlayerState:
    ASL A                    ; ACF7 
    TAY                      ; ACF8 
    LDA a:$b099,Y            ; ACF9 
    STA $c3                  ; ACFC 
    LDA a:$b09a,Y            ; ACFE 
    STA $c4                  ; AD01 
    LDA a:$b09d,Y            ; AD03 
    STA $c7                  ; AD06 
    LDA a:$b09e,Y            ; AD08 
    STA $c8                  ; AD0B 
    LDA a:$b0a1,Y            ; AD0D 
    STA $c5                  ; AD10 
    LDA a:$b0a2,Y            ; AD12 
    STA $c6                  ; AD15 
    LDA $cd                  ; AD17 
    LSR A                    ; AD19 
    TAY                      ; AD1A 
    LDA ($c3),Y              ; AD1B 
    STA a:$0046              ; AD1D 
    LDA $cd                  ; AD20 
    AND #$fe                 ; AD22 
    TAY                      ; AD24 Even CD indexes little-endian pointer pairs; bit0 is rendering direction.
    LDA ($c7),Y              ; AD25 
    STA $b6                  ; AD27 
    LDA ($c5),Y              ; AD29 
    STA $2c                  ; AD2B 
    INY                      ; AD2D 
    LDA ($c7),Y              ; AD2E 
    STA $b7                  ; AD30 
    LDA ($c5),Y              ; AD32 
    STA $2d                  ; AD34 
    JMP ($002c)              ; AD36 

; C36: Replace CD bits7..1 with A bits7..1, preserve old CD bit0 and clear CF.
SetPlayerStateKeepFacing:
    LSR A                    ; AD39 
    LSR $cd                  ; AD3A 
    ROL A                    ; AD3C 
    STA $cd                  ; AD3D 
    LDA #$00                 ; AD3F 
    STA $cf                  ; AD41 
    RTS                      ; AD43 
    .incbin "inputs/original.nes", $010D54, $008B ; UNINTERPRETED preserved bytes

; C37: ADCF sets CE bit40; ADD6 sets DB bit80; ADDC clears DB bit80.
SetPlayerMotionAndScrollFlags:
    LDA $ce                  ; ADCF 
    ORA #$40                 ; ADD1 
    STA $ce                  ; ADD3 
    RTS                      ; ADD5 
    ASL $db                  ; ADD6 
    SEC                      ; ADD8 
    ROR $db                  ; ADD9 
    RTS                      ; ADDB 
    ASL $db                  ; ADDC 
    CLC                      ; ADDE 
    ROR $db                  ; ADDF 
    RTS                      ; ADE1 

; C38: OR current and two previous held inputs; Right takes precedence and clears CD bit0, otherwise Left sets it.
UpdateFacingFromInputHistory:
    LDA $20                  ; ADE2 
    ORA a:$0713              ; ADE4 
    ORA a:$0714              ; ADE7 
    LSR A                    ; ADEA 
    BCS $adf1                ; ADEB 
    LSR A                    ; ADED 
    BCS $adf7                ; ADEE 
    RTS                      ; ADF0 
    LSR $cd                  ; ADF1 
    CLC                      ; ADF3 
    ROL $cd                  ; ADF4 
    RTS                      ; ADF6 
    LSR $cd                  ; ADF7 
    SEC                      ; ADF9 
    ROL $cd                  ; ADFA 
    RTS                      ; ADFC 
    .incbin "inputs/original.nes", $010E0D, $020A ; UNINTERPRETED preserved bytes

; C39: Set D3 bit80, CD=C4/C5 preserving facing, CF=0 and CE=0.
EnterPlayerFallState:
    ASL $d3                  ; B007 
    SEC                      ; B009 
    ROR $d3                  ; B00A 
    LDA #$c4                 ; B00C 
    JSR a:$ad39              ; B00E 
    LDA #$00                 ; B011 
    STA $ce                  ; B013 
    RTS                      ; B015 
    .incbin "inputs/original.nes", $011026, $0014 ; UNINTERPRETED preserved bytes

; C40: Copy ten bytes to C9..D2, then clear active flags 057C..057C+0013 inclusive under valid small slot-count precondition.
InitializePlayerStateBlock:
    LDX #$00                 ; B02A 
    LDA a:$b042,X            ; B02C 
    STA $c9,X                ; B02F 
    INX                      ; B031 
    CPX #$0a                 ; B032 
    BNE $b02c                ; B034 
    LDX a:$0013              ; B036 
    LDA #$00                 ; B039 
    STA a:$057c,X            ; B03B 
    DEX                      ; B03E 
    BPL $b03b                ; B03F 
    RTS                      ; B041 

; C41: C9..D2 initial bytes 80 00 80 00 00 00 00 00 00 00.
InitialPlayerStateBytes:
    .byte $80,$00,$80,$00,$00,$00,$00,$00,$00,$00

; C42: Require DB bits08 and01; set DB bit80 and dispatch direction (DB>>1)&3.
DispatchAutomaticCameraStep:
    LDA $db                  ; B04C 
    AND #$08                 ; B04E 
    BEQ $b06a                ; B050 
    LDA $db                  ; B052 
    LSR A                    ; B054 
    BCC $b06a                ; B055 
    AND #$03                 ; B057 
    TAY                      ; B059 
    JSR a:$add6              ; B05A 
    LDA a:$b06b,Y            ; B05D 
    STA $22                  ; B060 
    LDA a:$b06f,Y            ; B062 
    STA $23                  ; B065 
    JMP ($0022)              ; B067 
    RTS                      ; B06A 

; C43: Four split low/high pointers: B073,B07A,B086,B08D.
AutomaticCameraStepTargets:
    .byte $73,$7A,$86,$8D,$B0,$B0,$B0,$B0

; C44: Four entries add/subtract one to 16-bit camera Y or X, wrapping naturally.
StepCameraOnePixel:
    INC $a9                  ; B073 
    BNE $b079                ; B075 
    INC $aa                  ; B077 
    RTS                      ; B079 
    SEC                      ; B07A 
    LDA $a9                  ; B07B 
    SBC #$01                 ; B07D 
    STA $a9                  ; B07F 
    BCS $b085                ; B081 
    DEC $aa                  ; B083 
    RTS                      ; B085 
    INC $a7                  ; B086 
    BNE $b08c                ; B088 
    INC $a8                  ; B08A 
    RTS                      ; B08C 
    SEC                      ; B08D 
    LDA $a7                  ; B08E 
    SBC #$01                 ; B090 
    STA $a7                  ; B092 
    BCS $b098                ; B094 
    DEC $a8                  ; B096 
    RTS                      ; B098 

; C45: Three two-entry pointer arrays for CHR, metasprites and state handlers; ACF7 input A=0/1 selects family.
PlayerTableFamilyPointers:
    .byte $A5,$B0,$F3,$BD,$14,$B1,$F8,$BD,$F2,$B1,$02,$BE

; C46: 111 CHR bank bytes indexed by CD>>1; table contents identified, not every corresponding state behavior.
PlayerNormalChrTable:
    .byte $10,$11,$10,$12,$10,$10,$11,$12,$10,$11,$11,$11,$11,$11,$13,$11
    .byte $13,$12,$12,$12,$10,$14,$11,$13,$12,$14,$15,$11,$14,$16,$16,$16
    .byte $14,$11,$13,$12,$10,$14,$16,$16,$17,$17,$17,$10,$10,$14,$11,$13
    .byte $12,$10,$10,$14,$11,$13,$13,$13,$13,$13,$11,$12,$12,$12,$14,$11
    .byte $13,$12,$14,$15,$15,$14,$14,$15,$15,$15,$15,$15,$16,$15,$11,$10
    .byte $11,$13,$13,$13,$13,$11,$11,$12,$12,$12,$12,$12,$11,$07,$17,$07
    .byte $07,$07,$12,$07,$07,$10,$07,$17,$17,$11,$10,$12,$10,$10,$02

; C47: 111 little-endian metasprite pointers indexed by even CD.
PlayerNormalSpritePointers:
    .byte $D0,$B2,$D0,$B2,$E9,$B2,$D0,$B2,$FA,$B2,$0B,$B3,$0B,$B3,$0B,$B3
    .byte $20,$B3,$35,$B3,$4E,$B3,$4E,$B3,$4E,$B3,$35,$B3,$F9,$B3,$67,$B3
    .byte $80,$B3,$99,$B3,$99,$B3,$99,$B3,$B2,$B3,$80,$B3,$67,$B3,$80,$B3
    .byte $99,$B3,$3E,$B5,$2F,$B6,$44,$B6,$59,$B6,$72,$B6,$8F,$B6,$8F,$B6
    .byte $59,$B6,$67,$B3,$4C,$B4,$99,$B3,$65,$B4,$A4,$B6,$BD,$B6,$D6,$B6
    .byte $F3,$B6,$0C,$B7,$25,$B7,$3E,$B7,$B2,$B3,$80,$B3,$67,$B3,$4C,$B4
    .byte $99,$B3,$65,$B4,$65,$B4,$7E,$B4,$97,$B4,$B0,$B4,$C9,$B4,$C9,$B4
    .byte $C9,$B4,$B0,$B4,$97,$B4,$EA,$B4,$FF,$B4,$14,$B5,$29,$B5,$67,$B3
    .byte $80,$B3,$99,$B3,$3E,$B5,$53,$B5,$16,$B6,$68,$B5,$68,$B5,$89,$B5
    .byte $A1,$B5,$BA,$B5,$CF,$B5,$CF,$B5,$EC,$B5,$53,$B5,$01,$B6,$D0,$B2
    .byte $35,$B3,$12,$B4,$2B,$B4,$2B,$B4,$12,$B4,$35,$B3,$35,$B3,$C3,$B3
    .byte $DC,$B3,$DC,$B3,$DC,$B3,$C3,$B3,$35,$B3,$D0,$B2,$53,$B7,$6C,$B7
    .byte $85,$B7,$53,$B7,$0B,$B3,$D0,$B2,$D0,$B2,$E8,$B2,$9E,$B7,$BF,$B7
    .byte $E0,$B7,$D0,$B2,$E9,$B2,$D0,$B2,$E9,$B2,$D0,$B2,$01,$B8

; C48: 111 little-endian handler pointers covering CD pairs 00/01 through DC/DD; many handlers remain unreviewed.
PlayerNormalHandlerPointers:
    .byte $1D,$B8,$B5,$B8,$B5,$B8,$B5,$B8,$B5,$B8,$12,$B9,$2F,$B9,$47,$B9
    .byte $A4,$B9,$D4,$B9,$D4,$B9,$D4,$B9,$D4,$B9,$D4,$B9,$F8,$B9,$38,$BA
    .byte $38,$BA,$38,$BA,$38,$BA,$38,$BA,$38,$BA,$38,$BA,$42,$BA,$42,$BA
    .byte $42,$BA,$42,$BA,$42,$BA,$42,$BA,$42,$BA,$42,$BA,$42,$BA,$42,$BA
    .byte $42,$BA,$4C,$BA,$4C,$BA,$4C,$BA,$4C,$BA,$4C,$BA,$4C,$BA,$4C,$BA
    .byte $4C,$BA,$4C,$BA,$4C,$BA,$4C,$BA,$4C,$BA,$4C,$BA,$84,$BA,$84,$BA
    .byte $84,$BA,$84,$BA,$84,$BA,$84,$BA,$84,$BA,$84,$BA,$84,$BA,$84,$BA
    .byte $84,$BA,$84,$BA,$84,$BA,$84,$BA,$84,$BA,$84,$BA,$84,$BA,$8E,$BA
    .byte $8E,$BA,$8E,$BA,$8E,$BA,$8E,$BA,$8E,$BA,$8E,$BA,$8E,$BA,$8E,$BA
    .byte $8E,$BA,$8E,$BA,$8E,$BA,$8E,$BA,$8E,$BA,$8E,$BA,$8E,$BA,$8E,$BA
    .byte $98,$BA,$98,$BA,$98,$BA,$98,$BA,$98,$BA,$98,$BA,$21,$BB,$21,$BB
    .byte $21,$BB,$21,$BB,$21,$BB,$21,$BB,$21,$BB,$2B,$BB,$2B,$BB,$2B,$BB
    .byte $2B,$BB,$2B,$BB,$4F,$BB,$6E,$BB,$6E,$BB,$99,$BB,$AD,$BB,$AD,$BB
    .byte $AD,$BB,$E9,$BB,$E9,$BB,$E9,$BB,$E9,$BB,$B4,$B8,$B4,$B8
    .incbin "inputs/original.nes", $0112E0, $085B ; UNINTERPRETED preserved bytes

; C49: Set D3 bit80; every exact 0F CF updates advance CD by2; after C2/C3 select CA/CB and reset CF.
AdvancePlayerDeathAnimation:
    ASL $d3                  ; BB2B 
    SEC                      ; BB2D 
    ROR $d3                  ; BB2E 
    INC $cf                  ; BB30 
    LDA $cf                  ; BB32 
    SEC                      ; BB34 
    SBC #$0f                 ; BB35 
    BNE $bb4e                ; BB37 
    STA $cf                  ; BB39 
    LDA $cd                  ; BB3B 
    CLC                      ; BB3D 
    ADC #$02                 ; BB3E 
    STA $cd                  ; BB40 
    CMP #$c4                 ; BB42 Five states BA,BC,BE,C0,C2 each last 15 updates; CA then waits 15 more.
    BCC $bb4e                ; BB44 
    LDA $cd                  ; BB46 
    AND #$01                 ; BB48 
    ORA #$ca                 ; BB4A 
    STA $cd                  ; BB4C 
    RTS                      ; BB4E 

; C50: Set D3 bit80; add4 to player Y; set CE bit80 if low-byte camera-relative Y >=F0.
UpdatePlayerFallExit:
    ASL $d3                  ; BB4F 
    SEC                      ; BB51 
    ROR $d3                  ; BB52 
    CLC                      ; BB54 
    LDA $c9                  ; BB55 
    ADC #$04                 ; BB57 
    STA $c9                  ; BB59 
    BCC $bb5f                ; BB5B 
    INC $ca                  ; BB5D 
    LDA $c9                  ; BB5F 
    SEC                      ; BB61 
    SBC $a9                  ; BB62 
    CMP #$f0                 ; BB64 Comparison uses low-byte subtraction only, not a full 16-bit distance.
    BCC $bb6d                ; BB66 
    ASL $ce                  ; BB68 
    SEC                      ; BB6A 
    ROR $ce                  ; BB6B 
    RTS                      ; BB6D 

; C51: Set D3 bit80; call unreviewed BCEF; while D2>=30 request horizontal movement by2 using CD bit08, otherwise clear D3 bits30 and reset CD to facing.
UpdatePlayerHurtReaction:
    ASL $d3                  ; BB6E 
    SEC                      ; BB70 
    ROR $d3                  ; BB71 
    JSR a:$bcef              ; BB73 
    LDA $d2                  ; BB76 
    CMP #$30                 ; BB78 
    BCC $bb8c                ; BB7A 
    LDA $cd                  ; BB7C 
    AND #$08                 ; BB7E 
    BNE $bb87                ; BB80 
    LDA #$02                 ; BB82 
    JMP a:$aeb1              ; BB84 
    LDA #$02                 ; BB87 
    JMP a:$ae14              ; BB89 
    LDA $d3                  ; BB8C 
    AND #$cf                 ; BB8E 
    STA $d3                  ; BB90 
    LDA $cd                  ; BB92 
    AND #$01                 ; BB94 
    STA $cd                  ; BB96 
    RTS                      ; BB98 

; C52: Set D3 bit80; increment CF; exact CF=0F sets CE bit80 without resetting CF.
FinishPlayerDeathDelay:
    ASL $d3                  ; BB99 
    SEC                      ; BB9B 
    ROR $d3                  ; BB9C 
    INC $cf                  ; BB9E 
    LDA $cf                  ; BBA0 
    SEC                      ; BBA2 
    SBC #$0f                 ; BBA3 
    BNE $bbac                ; BBA5 
    ASL $ce                  ; BBA7 
    SEC                      ; BBA9 
    ROR $ce                  ; BBAA 
    RTS                      ; BBAC 
    .incbin "inputs/original.nes", $011BBD, $0246 ; UNINTERPRETED preserved bytes

; C53: Five CHR bytes for alternate family; precise gameplay activation not assigned.
PlayerAlternateChrTable:
    .byte $18,$18,$18,$18,$18

; C54: Five little-endian metasprite pointers for alternate family.
PlayerAlternateSpritePointers:
    .byte $0C,$BE,$25,$BE,$25,$BE,$4A,$BE,$63,$BE

; C55: Five little-endian handler pointers for alternate family.
PlayerAlternateHandlerPointers:
    .byte $88,$BE,$BE,$BE,$D0,$BE,$D0,$BE,$D0,$BE
    .incbin "inputs/original.nes", $011E1C, $01F4 ; UNINTERPRETED preserved bytes
