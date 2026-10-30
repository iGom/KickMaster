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

; I34: A>0423 unwinds caller; thresholdreached resets0423to0 thenreturns, unlikeordinarygate.
SpecialEnemyTimerGate:
    CMP a:$0423,X            ; 8051 
    BEQ $805b                ; 8054 
    BCC $805b                ; 8056 
    PLA                      ; 8058 
    PLA                      ; 8059 
    RTS                      ; 805A 
    LDA #$00                 ; 805B 
    STA a:$0423,X            ; 805D 
    RTS                      ; 8060 

; I35: Allocate lowestinactive enemy or reuse current iffull; reset selectedfields, subtypeHP=originalkind-50, kind5B (8098 changes60), flags90, copyscore045F. Saveclamped anchor0189..018C relativecameraY30..B0,X30..D0; newslotcoordinates/reactionflagsnotinitializedhere.
CreateSpecialDeathObjectAndAnchor:
    JSR a:$c779              ; 8061 
    BNE $8068                ; 8064 
    LDY $2c                  ; 8066 
    LDX $2c                  ; 8068 
    LDA #$00                 ; 806A 
    STA a:$0419,Y            ; 806C 
    STA a:$042d,Y            ; 806F 
    STA a:$0423,Y            ; 8072 
    STA a:$040f,Y            ; 8075 
    STA a:$0473,Y            ; 8078 
    LDA a:$03dd,X            ; 807B 
    SEC                      ; 807E 
    SBC #$50                 ; 807F 
    STA a:$0437,Y            ; 8081 
    LDA #$5b                 ; 8084 
    STA a:$03dd,Y            ; 8086 
    LDA #$90                 ; 8089 
    STA a:$0469,Y            ; 808B 
    LDA a:$045f,X            ; 808E 
    STA a:$045f,Y            ; 8091 
    JSR a:$80a1              ; 8094 
    RTS                      ; 8097 
    JSR a:$8061              ; 8098 
    LDA #$60                 ; 809B 
    STA a:$03dd,Y            ; 809D 
    RTS                      ; 80A0 
    LDA a:$03e7,X            ; 80A1 
    STA a:$0189              ; 80A4 
    STA $22                  ; 80A7 
    LDA a:$03f1,X            ; 80A9 
    STA a:$018a              ; 80AC 
    STA $23                  ; 80AF 
    LDA $a9                  ; 80B1 
    CLC                      ; 80B3 
    ADC #$30                 ; 80B4 
    STA $24                  ; 80B6 
    LDA $aa                  ; 80B8 
    ADC #$00                 ; 80BA 
    STA $25                  ; 80BC 
    LDA $22                  ; 80BE 
    SEC                      ; 80C0 
    SBC $24                  ; 80C1 
    LDA $23                  ; 80C3 
    SBC $25                  ; 80C5 
    BMI $80e1                ; 80C7 
    LDA $a9                  ; 80C9 
    CLC                      ; 80CB 
    ADC #$b0                 ; 80CC 
    STA $24                  ; 80CE 
    LDA $aa                  ; 80D0 
    ADC #$00                 ; 80D2 
    STA $25                  ; 80D4 
    LDA $24                  ; 80D6 
    SEC                      ; 80D8 
    SBC $22                  ; 80D9 
    LDA $25                  ; 80DB 
    SBC $23                  ; 80DD 
    BPL $80eb                ; 80DF 
    LDA $24                  ; 80E1 
    STA a:$0189              ; 80E3 
    LDA $25                  ; 80E6 
    STA a:$018a              ; 80E8 
    LDA a:$03fb,X            ; 80EB 
    STA a:$018b              ; 80EE 
    STA $22                  ; 80F1 
    LDA a:$0405,X            ; 80F3 
    STA a:$018c              ; 80F6 
    STA $23                  ; 80F9 
    LDA $a7                  ; 80FB 
    CLC                      ; 80FD 
    ADC #$30                 ; 80FE 
    STA $24                  ; 8100 
    LDA $a8                  ; 8102 
    ADC #$00                 ; 8104 
    STA $25                  ; 8106 
    LDA $22                  ; 8108 
    SEC                      ; 810A 
    SBC $24                  ; 810B 
    LDA $23                  ; 810D 
    SBC $25                  ; 810F 
    BMI $812b                ; 8111 
    LDA $a7                  ; 8113 
    CLC                      ; 8115 
    ADC #$d0                 ; 8116 
    STA $24                  ; 8118 
    LDA $a8                  ; 811A 
    ADC #$00                 ; 811C 
    STA $25                  ; 811E 
    LDA $24                  ; 8120 
    SEC                      ; 8122 
    SBC $22                  ; 8123 
    LDA $25                  ; 8125 
    SBC $23                  ; 8127 
    BPL $8135                ; 8129 
    LDA $24                  ; 812B 
    STA a:$018b              ; 812D 
    LDA $25                  ; 8130 
    STA a:$018c              ; 8132 
    RTS                      ; 8135 

; I36: 8136 frameincrement/equalitywrap;8144 clears469/473/47D only.
AdvanceSpecialFrameAndDeactivate:
    INC a:$0419,X            ; 8136 
    CMP a:$0419,X            ; 8139 
    BNE $8143                ; 813C 
    LDA #$00                 ; 813E 
    STA a:$0419,X            ; 8140 
    RTS                      ; 8143 
    LDA #$00                 ; 8144 
    STA a:$0469,X            ; 8146 
    STA a:$0473,X            ; 8149 
    STA a:$047d,X            ; 814C 
    RTS                      ; 814F 
    .incbin "inputs/original.nes", $014160, $001E ; UNINTERPRETED preserved bytes

; I37: C7A0 withA0,Y4 selectsnormal0..3,death4,hit5,quake6; onlydeathpathanddispatchreviewed, alivehandlersremainopen.
DispatchKind50State:
    LDA #$00                 ; 816E 
    LDY #$04                 ; 8170 
    JSR a:$c7a0              ; 8172 
    LDA a:$817f,Y            ; 8175 
    PHA                      ; 8178 
    LDA a:$817e,Y            ; 8179 
    PHA                      ; 817C 
    RTS                      ; 817D 

; I38: Seven storedreturn addresses; death82C5,hitC7A3,quake8016. No claimalivehandlerscomplete.
Kind50StateReturnPointers:
    .byte $8B,$81,$B8,$81,$01,$82,$81,$82,$C4,$82,$A2,$C7,$15,$80
    .incbin "inputs/original.nes", $01419C, $0139 ; UNINTERPRETED preserved bytes

; I39: Create5Bobject, soundD2; deactivateoldslotifdifferent; scanactivekind50. Ifanotherfound,setnewkind60and47Dbit08 to suppressendflag later.
ConvertKind50DeathAndCheckCompanion:
    JSR a:$8061              ; 82C5 
    STY $3c                  ; 82C8 
    LDA #$d2                 ; 82CA 
    STA $01                  ; 82CC 
    CPY $2c                  ; 82CE 
    BEQ $82d7                ; 82D0 
    LDX $2c                  ; 82D2 
    JSR a:$8144              ; 82D4 
    LDY #$00                 ; 82D7 
    LDA a:$0469,Y            ; 82D9 
    BPL $82e5                ; 82DC 
    LDA a:$03dd,Y            ; 82DE 
    CMP #$50                 ; 82E1 
    BEQ $82ec                ; 82E3 
    INY                      ; 82E5 
    CPY a:$06f8              ; 82E6 
    BNE $82d9                ; 82E9 
    RTS                      ; 82EB 
    LDY $3c                  ; 82EC 
    LDA #$60                 ; 82EE 
    STA a:$03dd,Y            ; 82F0 
    LDA a:$047d,Y            ; 82F3 
    ORA #$08                 ; 82F6 
    STA a:$047d,Y            ; 82F8 
    RTS                      ; 82FB 
    .incbin "inputs/original.nes", $01430C, $06FE ; UNINTERPRETED preserved bytes

; I40: Kind5B direct040Fdispatch, noHPdamagegate because0437is subtype. Two entries0/1.
DispatchSpecialDeathObject:
    LDA #$00                 ; 89FA 
    STA $2e                  ; 89FC 
    LDA a:$040f,X            ; 89FE 
    STA $2f                  ; 8A01 
    ASL A                    ; 8A03 
    TAY                      ; 8A04 
    LDA a:$8a0f,Y            ; 8A05 
    PHA                      ; 8A08 
    LDA a:$8a0e,Y            ; 8A09 
    PHA                      ; 8A0C 
    RTS                      ; 8A0D 

; I41: Two storedreturn addresses to8A12effect and8A43delay.
SpecialDeathStateReturnPointers:
    .byte $11,$8A,$42,$8A

; I42: Scoreonce; eightframes16cycles=128 calls, oddframescall8AA9. Then repositionandspawnrewardfrom12-entrysubtypetable;state1 waits100calls then clears flags, plusF8bit20 inscene1B.
SpecialDeathBurstRewardAndDelay:
    LDA a:$0419,X            ; 8A12 
    ORA a:$042d,X            ; 8A15 
    BNE $8a22                ; 8A18 
    LDA a:$045f,X            ; 8A1A 
    JSR a:$c746              ; 8A1D 
    LDX $2c                  ; 8A20 
    LDA a:$0419,X            ; 8A22 
    LSR A                    ; 8A25 
    BCC $8a2b                ; 8A26 
    JSR a:$8aa9              ; 8A28 
    LDA #$08                 ; 8A2B 
    JSR a:$8136              ; 8A2D 
    BNE $8a42                ; 8A30 
    INC a:$042d,X            ; 8A32 
    LDA a:$042d,X            ; 8A35 
    CMP #$10                 ; 8A38 
    BCC $8a42                ; 8A3A 
    JSR a:$8a5d              ; 8A3C 
    INC a:$040f,X            ; 8A3F 
    RTS                      ; 8A42 
    INC a:$0423,X            ; 8A43 
    LDA #$64                 ; 8A46 
    JSR a:$8051              ; 8A48 
    LDA $9a                  ; 8A4B 
    CMP #$1b                 ; 8A4D 
    BNE $8a59                ; 8A4F 
    LDA a:$00f8              ; 8A51 
    ORA #$20                 ; 8A54 
    STA a:$00f8              ; 8A56 
    JMP a:$8144              ; 8A59 
    RTS                      ; 8A5C 
    LDA #$02                 ; 8A5D 
    STA $49                  ; 8A5F 
    LDY a:$0437,X            ; 8A61 
    LDA $a7                  ; 8A64 
    CLC                      ; 8A66 
    ADC #$d0                 ; 8A67 
    STA a:$03fb,X            ; 8A69 
    LDA $a8                  ; 8A6C 
    ADC #$00                 ; 8A6E 
    STA a:$0405,X            ; 8A70 
    LDA $a9                  ; 8A73 
    CLC                      ; 8A75 
    ADC a:$8a9d,Y            ; 8A76 
    STA a:$03e7,X            ; 8A79 
    LDA $aa                  ; 8A7C 
    ADC #$00                 ; 8A7E 
    STA a:$03f1,X            ; 8A80 
    LDY a:$0437,X            ; 8A83 
    LDA a:$8a91,Y            ; 8A86 
    BEQ $8a8e                ; 8A89 
    JSR a:$c794              ; 8A8B 
    LDX $2c                  ; 8A8E 
    RTS                      ; 8A90 

; I43: 12 rewardtypes and12Yoffsets; subtypefield0437 indexes. Nonzero rewardcodes are54,50,5C,56,66,58,5E; no unconditionalboss-name mapping.
SpecialDeathRewardTables:
    .byte $54,$50,$5C,$56,$00,$00,$00,$66,$58,$5E,$00,$00,$C0,$C0,$B0,$C0
    .byte $00,$00,$00,$C0,$B0,$B0,$00,$00

; I44: Restoreanchor; ifcycle042Dzero spawnDF37triple. DirectiontablebyD8&3; offsetindex=(D8 OR024D)+97+inheritedcarry masked1F, adjacent bytepair! Callmovement with473=0 onconstructorpath.
SpecialDeathScatterAndDrop:
    LDA a:$0189              ; 8AA9 
    STA a:$03e7,X            ; 8AAC 
    LDA a:$018a              ; 8AAF 
    STA a:$03f1,X            ; 8AB2 
    LDA a:$018b              ; 8AB5 
    STA a:$03fb,X            ; 8AB8 
    LDA a:$018c              ; 8ABB 
    STA a:$0405,X            ; 8ABE 
    LDA a:$042d,X            ; 8AC1 
    BNE $8ac9                ; 8AC4 
    JSR a:$8aef              ; 8AC6 
    LDA $d8                  ; 8AC9 
    AND #$03                 ; 8ACB 
    TAY                      ; 8ACD 
    LDA a:$0469,X            ; 8ACE 
    AND #$fc                 ; 8AD1 
    ORA a:$8b16,Y            ; 8AD3 
    STA a:$0469,X            ; 8AD6 
    LDA $d8                  ; 8AD9 
    ORA a:$024d              ; 8ADB 
    ADC $97                  ; 8ADE 
    AND #$1f                 ; 8AE0 
    TAY                      ; 8AE2 
    LDA a:$8af5,Y            ; 8AE3 
    PHA                      ; 8AE6 
    LDA a:$8af6,Y            ; 8AE7 
    TAY                      ; 8AEA 
    PLA                      ; 8AEB 
    JMP a:$c7a9              ; 8AEC 
    JSR a:$c791              ; 8AEF 
    LDX $2c                  ; 8AF2 
    RTS                      ; 8AF4 

; I45: 33bytes support32overlappingoffsetpairs, plus4directioncodes. Oddindicesarevalid; donotdecodeas16wordpairs.
SpecialDeathScatterTables:
    .byte $20,$30,$26,$32,$4C,$50,$1A,$2C,$04,$42,$1E,$00,$24,$00,$32,$20
    .byte $00,$12,$40,$3A,$2A,$46,$3E,$58,$4A,$00,$4E,$54,$1C,$3C,$28,$06
    .byte $1E,$02,$00,$03,$01

; I46: Kind60:scoreonce,scattereverycall;128calls thenF8bit80 unless47D08 set;deactivate,clear070A/B. Firstcycle8tripleattempts, nofinalrewardtablecall.
AlternateSpecialDeathLifecycle:
    LDA a:$0419,X            ; 8B1A 
    ORA a:$042d,X            ; 8B1D 
    BNE $8b2a                ; 8B20 
    LDA a:$045f,X            ; 8B22 
    JSR a:$c746              ; 8B25 
    LDX $2c                  ; 8B28 
    JSR a:$8aa9              ; 8B2A 
    LDA #$08                 ; 8B2D 
    JSR a:$8136              ; 8B2F 
    BNE $8b53                ; 8B32 
    INC a:$042d,X            ; 8B34 
    LDA a:$042d,X            ; 8B37 
    CMP #$10                 ; 8B3A 
    BCC $8b53                ; 8B3C 
    LDA a:$047d,X            ; 8B3E 
    AND #$08                 ; 8B41 
    BNE $8b4a                ; 8B43 
    ASL $f8                  ; 8B45 
    SEC                      ; 8B47 
    ROR $f8                  ; 8B48 
    JSR a:$8144              ; 8B4A 
    STA a:$070a              ; 8B4D 
    STA a:$070b              ; 8B50 
    RTS                      ; 8B53 
    .incbin "inputs/original.nes", $014B64, $14AC ; UNINTERPRETED preserved bytes
