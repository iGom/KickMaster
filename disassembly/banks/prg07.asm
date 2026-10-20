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

; C01: Require DB bits 7 and 0; select one of four targets with (DB>>1)&3.
DispatchSceneEven:
    LDA $db                  ; A0DB 
    BPL $a138                ; A0DD 
    LSR A                    ; A0DF 
    BCC $a138                ; A0E0 
    AND #$03                 ; A0E2 
    TAY                      ; A0E4 
    LDA a:$a0f2,Y            ; A0E5 
    STA $22                  ; A0E8 
    LDA a:$a0f6,Y            ; A0EA 
    STA $23                  ; A0ED 
    JMP ($0022)              ; A0EF 

; C02: Four split low/high target bytes; down/up/right/left order follows DB direction selector.
SceneEvenTargets:
    .byte $15,$3E,$39,$90,$A3,$A3,$A1,$A1

; C03: Same DB gate and selector as even phase, different four-target table.
DispatchSceneOdd:
    LDA $db                  ; A0FA 
    BPL $a138                ; A0FC 
    LSR A                    ; A0FE 
    BCC $a138                ; A0FF 
    AND #$03                 ; A101 
    TAY                      ; A103 
    LDA a:$a111,Y            ; A104 
    STA $22                  ; A107 
    LDA a:$a115,Y            ; A109 
    STA $23                  ; A10C 
    JMP ($0022)              ; A10E 

; C04: Four split low/high target bytes for odd phase.
SceneOddTargets:
    .byte $7F,$BC,$5C,$BC,$A3,$A3,$A1,$A1

; C05: Third DB-gated four-target dispatch used in even phases.
DispatchSceneExtra:
    LDA $db                  ; A119 
    BPL $a138                ; A11B 
    LSR A                    ; A11D 
    BCC $a138                ; A11E 
    AND #$03                 ; A120 
    TAY                      ; A122 
    LDA a:$a130,Y            ; A123 
    STA $22                  ; A126 
    LDA a:$a134,Y            ; A128 
    STA $23                  ; A12B 
    JMP ($0022)              ; A12D 

; C06: Four split low/high target bytes for extra even-phase work.
SceneExtraTargets:
    .byte $62,$74,$82,$ED,$A3,$A3,$A1,$A1

; C07: Shared RTS when DB gate is closed.
SceneDispatchReturn:
    RTS                      ; A138 
    .incbin "inputs/original.nes", $00E149, $03B0 ; UNINTERPRETED preserved bytes

; C08: Mask scene index to 7 bits; initialize camera and player coordinates, scroll shadows and IRQ profile; fall through configuration loader.
InitializeSceneCoordinates:
    LDX #$00                 ; A4E9 
    STX $d8                  ; A4EB 
    STX $d9                  ; A4ED 
    STX $a0                  ; A4EF 
    STX $a1                  ; A4F1 
    LDA $9a                  ; A4F3 
    AND #$7f                 ; A4F5 
    STA $9a                  ; A4F7 
    TAX                      ; A4F9 
    LDA #$00                 ; A4FA 
    STA $a7                  ; A4FC 
    STA $d8                  ; A4FE 
    LDA a:$b1e2,X            ; A500 
    STA $a8                  ; A503 
    LDA a:$b202,X            ; A505 
    JSR a:$aab6              ; A508 
    LDA $22                  ; A50B 
    STA $a9                  ; A50D 
    LDA $23                  ; A50F 
    STA $aa                  ; A511 
    JSR a:$a916              ; A513 
    LDA a:$b222,X            ; A516 
    CLC                      ; A519 
    ADC $a7                  ; A51A 
    STA $cb                  ; A51C 
    LDA $a8                  ; A51E 
    ADC #$00                 ; A520 
    STA $cc                  ; A522 
    LDA a:$b242,X            ; A524 
    CLC                      ; A527 
    ADC $a9                  ; A528 
    STA $c9                  ; A52A 
    DEC $c9                  ; A52C 
    LDA $aa                  ; A52E 
    ADC #$00                 ; A530 
    STA $ca                  ; A532 
    JSR a:$fad3              ; A534 

; C09: Read 32-entry parallel arrays; set 03B9 and map R6, five pointers, DB flags, extents, palette selector and palette profile.
LoadSceneConfiguration:
    LDA $9a                  ; A537 
    TAX                      ; A539 
    ASL A                    ; A53A 
    TAY                      ; A53B 
    LDA a:$b262,X            ; A53C 
    STA a:$03b9              ; A53F 03B9 is data-driven, not a universal player-code bank.
    TXA                      ; A542 
    PHA                      ; A543 
    TYA                      ; A544 
    PHA                      ; A545 
    LDX #$06                 ; A546 
    LDA a:$03b9              ; A548 
    JSR a:$c76a              ; A54B 
    PLA                      ; A54E 
    TAY                      ; A54F 
    PLA                      ; A550 
    TAX                      ; A551 
    LDA a:$b282,Y            ; A552 
    STA $b9                  ; A555 
    LDA a:$b283,Y            ; A557 
    STA $ba                  ; A55A 
    LDA a:$b2c2,Y            ; A55C 
    STA $bb                  ; A55F 
    LDA a:$b2c3,Y            ; A561 
    STA $bc                  ; A564 
    LDA a:$b302,Y            ; A566 
    STA $bf                  ; A569 
    LDA a:$b303,Y            ; A56B 
    STA $c0                  ; A56E 
    LDA a:$b342,Y            ; A570 
    STA $bd                  ; A573 
    LDA a:$b343,Y            ; A575 
    STA $be                  ; A578 
    LDA a:$b382,Y            ; A57A 
    STA $c1                  ; A57D 
    LDA a:$b383,Y            ; A57F 
    STA $c2                  ; A582 
    LDA a:$b3c2,X            ; A584 
    STA a:$03ba              ; A587 
    LDA a:$b3e2,X            ; A58A 
    STA $db                  ; A58D 
    LDA a:$b402,X            ; A58F 
    STA $af                  ; A592 
    LDA a:$b422,X            ; A594 
    JSR a:$aab6              ; A597 
    LDA $22                  ; A59A 
    STA $ad                  ; A59C 
    LDA $23                  ; A59E 
    STA $ae                  ; A5A0 
    LDA $a1                  ; A5A2 
    ORA #$40                 ; A5A4 
    STA $a1                  ; A5A6 
    JMP a:$a935              ; A5A8 

; C10: 04E2 indexes 17-entry layout arrays; bank byte bit7 initializes camera X page then is cleared for R6; downstream A990/A6FE unreviewed.
InitializeSpecialLayout:
    JSR a:$c749              ; A5AB 
    JSR a:$f6c1              ; A5AE 
    LDX #$00                 ; A5B1 
    STX $a9                  ; A5B3 
    STX $aa                  ; A5B5 
    STX $a7                  ; A5B7 
    STX $a8                  ; A5B9 
    STX $51                  ; A5BB 
    STX $58                  ; A5BD 
    STX $52                  ; A5BF 
    STX $59                  ; A5C1 
    STX $d8                  ; A5C3 
    STX $d9                  ; A5C5 
    STX $a0                  ; A5C7 
    STX $a1                  ; A5C9 
    STX $68                  ; A5CB 
    STX $6a                  ; A5CD 
    INX                      ; A5CF 
    STX $96                  ; A5D0 
    LDA #$80                 ; A5D2 
    STA $4a                  ; A5D4 
    LDA #$06                 ; A5D6 
    STA $5f                  ; A5D8 
    LDA #$f0                 ; A5DA 
    STA $7f                  ; A5DC 
    LDA #$04                 ; A5DE 
    STA $db                  ; A5E0 
    LDA a:$04e2              ; A5E2 
    TAX                      ; A5E5 
    ASL A                    ; A5E6 
    TAY                      ; A5E7 
    LDA a:$b482,X            ; A5E8 
    STA a:$0044              ; A5EB 
    LDA a:$b493,X            ; A5EE 
    STA a:$0045              ; A5F1 
    LDA a:$b4a4,X            ; A5F4 
    BPL $a5fd                ; A5F7 Bit7 is metadata consumed here; R6 receives the low seven bits.
    AND #$7f                 ; A5F9 
    INC $a8                  ; A5FB 
    STA a:$03b9              ; A5FD 
    TXA                      ; A600 
    PHA                      ; A601 
    TYA                      ; A602 
    PHA                      ; A603 
    LDX #$06                 ; A604 
    LDA a:$03b9              ; A606 
    JSR a:$c76a              ; A609 
    PLA                      ; A60C 
    TAY                      ; A60D 
    PLA                      ; A60E 
    TAX                      ; A60F 
    LDA a:$b4b5,Y            ; A610 
    STA $b9                  ; A613 
    LDA a:$b4b6,Y            ; A615 
    STA $ba                  ; A618 
    LDA a:$b4d7,Y            ; A61A 
    STA $bb                  ; A61D 
    LDA a:$b4d8,Y            ; A61F 
    STA $bc                  ; A622 
    LDA a:$b4f9,Y            ; A624 
    STA $bf                  ; A627 
    LDA a:$b4fa,Y            ; A629 
    STA $c0                  ; A62C 
    LDA a:$b51b,Y            ; A62E 
    STA $bd                  ; A631 
    LDA a:$b51c,Y            ; A633 
    STA $be                  ; A636 
    JSR a:$a990              ; A638 
    JMP a:$a6fe              ; A63B 
    .incbin "inputs/original.nes", $00E64E, $02D8 ; UNINTERPRETED preserved bytes

; C11: Populate seven PPUCTRL/X/Y shadow entries from camera coordinates, preserving input X.
InitializeSevenScrollShadows:
    TXA                      ; A916 
    PHA                      ; A917 
    LDX #$06                 ; A918 
    LDA $a8                  ; A91A 
    AND #$01                 ; A91C 
    ORA #$a8                 ; A91E 
    STA $4a,X                ; A920 
    LDY $a9                  ; A922 
    LDA $aa                  ; A924 
    JSR a:$f78b              ; A926 
    STA $58,X                ; A929 
    LDA $a7                  ; A92B 
    STA $51,X                ; A92D 
    DEX                      ; A92F 
    BPL $a91a                ; A930 
    PLA                      ; A932 
    TAX                      ; A933 
    RTS                      ; A934 

; C12: Read 27-byte pointed profile into palette staging, eight bytes at 017D, 06B8 and CHR 44/45; install fixed sprite colors.
LoadScenePaletteProfile:
    LDA $9a                  ; A935 
    ASL A                    ; A937 
    TAY                      ; A938 
    LDA a:$b442,Y            ; A939 
    STA $22                  ; A93C 
    LDA a:$b443,Y            ; A93E 
    STA $23                  ; A941 
    LDY #$00                 ; A943 
    LDA ($22),Y              ; A945 
    STA a:$0123,Y            ; A947 
    LDA #$0f                 ; A94A 
    STA a:$0143,Y            ; A94C 
    INY                      ; A94F 
    CPY #$10                 ; A950 
    BNE $a945                ; A952 
    LDA ($22),Y              ; A954 
    STA a:$016d,Y            ; A956 
    INY                      ; A959 
    CPY #$18                 ; A95A 
    BNE $a954                ; A95C 
    LDA ($22),Y              ; A95E 
    STA a:$06b8              ; A960 
    INY                      ; A963 
    LDA ($22),Y              ; A964 
    STA a:$0044              ; A966 
    INY                      ; A969 
    LDA ($22),Y              ; A96A 
    STA a:$0045              ; A96C 
    LDY #$02                 ; A96F 
    LDA a:$ffb2,Y            ; A971 
    STA a:$0134,Y            ; A974 
    LDA a:$ffb5,Y            ; A977 
    STA a:$0138,Y            ; A97A 
    DEY                      ; A97D 
    BPL $a971                ; A97E 
    LDA a:$0123              ; A980 
    STA a:$0133              ; A983 
    STA a:$0137              ; A986 
    STA a:$013b              ; A989 
    STA a:$013f              ; A98C 
    RTS                      ; A98F 
    .incbin "inputs/original.nes", $00E9A0, $0126 ; UNINTERPRETED preserved bytes

; C13: Produce 16-bit 22/23 = input * F0 for input 00..80; 81..FF yield zero due to signed DEX gate; preserve X.
MultiplyScreenCountBy240:
    STA $22                  ; AAB6 
    TXA                      ; AAB8 
    PHA                      ; AAB9 
    LDX $22                  ; AABA 
    LDA #$00                 ; AABC 
    STA $22                  ; AABE 
    STA $23                  ; AAC0 
    JMP a:$aad2              ; AAC2 
    LDA $22                  ; AAC5 
    CLC                      ; AAC7 
    ADC #$f0                 ; AAC8 
    STA $22                  ; AACA 
    LDA $23                  ; AACC 
    ADC #$00                 ; AACE 
    STA $23                  ; AAD0 
    DEX                      ; AAD2 
    BPL $aac5                ; AAD3 Signed branch means 81..FF do not multiply as ordinary unsigned inputs.
    PLA                      ; AAD5 
    TAX                      ; AAD6 
    RTS                      ; AAD7 
    .incbin "inputs/original.nes", $00EAE8, $0362 ; UNINTERPRETED preserved bytes

; D01: Clear three reserved active flags; 06BD selects encoded type; initialize global slot3, flags88/8C, player position and zero velocities; refresh HUD icon.
InitializeSelectedSpellObject:
    LDA #$00                 ; AE3A 
    STA a:$057c              ; AE3C 
    STA a:$057d              ; AE3F 
    STA a:$057e              ; AE42 
    LDA #$ff                 ; AE45 
    STA a:$00b8              ; AE47 
    LDA a:$00ce              ; AE4A 
    AND #$fe                 ; AE4D 
    STA a:$00ce              ; AE4F 
    LDY a:$06bd              ; AE52 
    LDA a:$ae93,Y            ; AE55 
    BEQ $ae8c                ; AE58 
    TAY                      ; AE5A 
    AND #$fe                 ; AE5B 
    STA a:$056b              ; AE5D 
    LDA $cb                  ; AE60 
    STA a:$051b              ; AE62 
    LDA $cc                  ; AE65 
    STA a:$052f              ; AE67 
    LDA $c9                  ; AE6A 
    STA a:$04f3              ; AE6C 
    LDA $ca                  ; AE6F 
    STA a:$0507              ; AE71 
    LDA #$00                 ; AE74 
    STA a:$0543              ; AE76 
    STA a:$0557              ; AE79 
    STA a:$0593              ; AE7C 
    STA a:$05a7              ; AE7F 
    TYA                      ; AE82 
    LSR A                    ; AE83 
    BCS $ae8a                ; AE84 
    LDA #$88                 ; AE86 
    BNE $ae8c                ; AE88 
    LDA #$8c                 ; AE8A 
    STA a:$057f              ; AE8C 
    JSR a:$f65f              ; AE8F 
    RTS                      ; AE92 

; D02: Thirteen bytes for selector00..0C; 00/01 map70/72 healing handlers,0C disables slot3. Full spell identities unresolved.
SelectedSpellObjectTypes:
    .byte $70,$72,$74,$77,$78,$7A,$7C,$7E,$80,$82,$84,$86,$00
    .incbin "inputs/original.nes", $00EEB0, $0026 ; UNINTERPRETED preserved bytes

; D03: Save level, current HP, MP, EXP and two flag bytes in eleven-byte block06C2..06CC.
SnapshotPlayerProgression:
    LDA $d3                  ; AEC6 
    AND #$07                 ; AEC8 
    STA a:$06c2              ; AECA 
    LDA a:$06b9              ; AECD 
    STA a:$06c3              ; AED0 
    LDA a:$06be              ; AED3 
    STA a:$06cb              ; AED6 
    LDA a:$06bf              ; AED9 
    STA a:$06cc              ; AEDC 
    LDX #$02                 ; AEDF 
    LDA a:$00ed,X            ; AEE1 
    STA a:$06c7,X            ; AEE4 
    LDA a:$00ea,X            ; AEE7 
    STA a:$06c4,X            ; AEEA 
    DEX                      ; AEED 
    BPL $aee1                ; AEEE 
    LDA a:$00f0              ; AEF0 
    STA a:$06ca              ; AEF3 
    RTS                      ; AEF6 

; D04: Restore snapshot fields then tail to B7F4, which overwrites restored current HP with full table capacity; does not write06BB.
RestorePlayerProgression:
    LDA a:$06c2              ; AEF7 
    STA $d3                  ; AEFA 
    LDA a:$06c3              ; AEFC 
    STA a:$06b9              ; AEFF 
    LDA a:$06cb              ; AF02 
    STA a:$06be              ; AF05 
    LDA a:$06cc              ; AF08 
    STA a:$06bf              ; AF0B 
    LDX #$02                 ; AF0E 
    LDA a:$06c7,X            ; AF10 
    STA a:$00ed,X            ; AF13 
    LDA a:$06c4,X            ; AF16 
    STA a:$00ea,X            ; AF19 
    DEX                      ; AF1C 
    BPL $af10                ; AF1D 
    LDA a:$06ca              ; AF1F 
    STA a:$00f0              ; AF22 
    JMP a:$b7f4              ; AF25 
    .incbin "inputs/original.nes", $00EF38, $00FA ; UNINTERPRETED preserved bytes

; C14: Negative A1 returns; otherwise increment, wrap exact 06 to 01, then dispatch six-entry table; not a general out-of-range clamp.
DispatchHudMaintenance:
    LDY $a1                  ; B022 
    BMI $b03e                ; B024 
    INY                      ; B026 
    CPY #$06                 ; B027 Only exact 06 wraps. Normal callers must keep A1 in the expected range.
    BNE $b02d                ; B029 
    LDY #$01                 ; B02B 
    STY $a1                  ; B02D 
    LDA a:$b03f,Y            ; B02F 
    STA a:$002c              ; B032 
    LDA a:$b045,Y            ; B035 
    STA a:$002d              ; B038 
    JMP ($002c)              ; B03B 
    RTS                      ; B03E 

; C15: Six split low/high pointers; valid normal rotation is indexes 01..05, index00 is RTS.
HudMaintenanceTargets:
    .byte $3E,$65,$81,$4B,$04,$B0,$B0,$B1,$F6,$B0,$B1,$B0

; C16: 06BA decreases immediately to 06B9 or rises by one; encode full/partial/empty cells using capacity 06BB>>4 into eleven bytes at 0163.
BuildPlayerHpBar:
    LDA a:$06bb              ; B04B 
    LSR A                    ; B04E 
    LSR A                    ; B04F 
    LSR A                    ; B050 
    LSR A                    ; B051 
    STA $3d                  ; B052 
    LDA a:$06ba              ; B054 
    CMP a:$06b9              ; B057 
    BEQ $b072                ; B05A 
    BCC $b067                ; B05C 
    LDA a:$06b9              ; B05E 
    STA a:$06ba              ; B061 
    JMP a:$b072              ; B064 
    INC a:$06ba              ; B067 Displayed HP rises one raw unit per invocation; this routine is only one HUD phase.
    LDA #$a1                 ; B06A 
    STA a:$0001              ; B06C 
    LDA a:$06ba              ; B06F 
    LSR A                    ; B072 
    STA $3c                  ; B073 
    LDX #$00                 ; B075 
    LSR A                    ; B077 
    LSR A                    ; B078 
    LSR A                    ; B079 
    BEQ $b086                ; B07A 
    TAY                      ; B07C 
    LDA #$4f                 ; B07D 
    STA a:$0163,X            ; B07F 
    INX                      ; B082 
    DEY                      ; B083 
    BNE $b07f                ; B084 
    LDA $3c                  ; B086 
    AND #$07                 ; B088 
    BEQ $b093                ; B08A 
    CLC                      ; B08C 
    ADC #$47                 ; B08D 
    STA a:$0163,X            ; B08F 
    INX                      ; B092 
    CPX $3d                  ; B093 
    BEQ $b0a1                ; B095 
    LDA #$47                 ; B097 
    STA a:$0163,X            ; B099 
    INX                      ; B09C 
    CPX $3d                  ; B09D 
    BNE $b097                ; B09F 
    CPX #$0b                 ; B0A1 
    BEQ $b0af                ; B0A3 
    LDA #$3f                 ; B0A5 
    STA a:$0163,X            ; B0A7 
    INX                      ; B0AA 
    CPX #$0b                 ; B0AB 
    BNE $b0a7                ; B0AD 
    RTS                      ; B0AF 
    .incbin "inputs/original.nes", $00F0C0, $0132 ; UNINTERPRETED preserved bytes

; C18: 32 initial camera X high bytes; low byte is zero.
SceneInitialCameraXPages:
    .byte $00,$08,$00,$00,$01,$0C,$0C,$0E,$00,$02,$00,$0E,$00,$05,$0B,$00
    .byte $00,$03,$08,$08,$00,$06,$0E,$02,$02,$07,$02,$00,$02,$02,$00,$00

; C19: 32 initial camera Y screen counts multiplied by F0.
SceneInitialCameraYScreens:
    .byte $00,$00,$00,$01,$02,$02,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00
    .byte $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$06,$00,$0E,$0A,$0A,$06

; C20: 32 player X offsets added to initial camera X.
ScenePlayerXOffsets:
    .byte $18,$30,$B0,$80,$20,$18,$50,$80,$18,$18,$18,$40,$20,$30,$20,$80
    .byte $40,$18,$20,$20,$50,$30,$18,$20,$40,$60,$20,$80,$40,$80,$E8,$80

; C21: 32 player Y offsets added to initial camera Y; low result decremented once.
ScenePlayerYOffsets:
    .byte $C0,$80,$10,$C0,$C0,$C0,$B0,$C0,$B0,$40,$C0,$C0,$B0,$90,$B0,$80
    .byte $90,$B0,$B0,$B0,$A0,$80,$C0,$B0,$B0,$B0,$C0,$C0,$C0,$C0,$C0,$C0

; C22: 32 PRG bank bytes for 03B9 and MMC3 R6.
SceneBank8000Table:
    .byte $02,$02,$04,$04,$05,$05,$05,$05,$04,$04,$04,$02,$04,$04,$04,$04
    .byte $05,$05,$05,$05,$02,$02,$02,$03,$03,$03,$03,$03,$03,$03,$03,$03

; C23: 32 little-endian pointers loaded into B9/BA; target meaning not inferred from address alone.
ScenePointerB9Table:
    .byte $6D,$84,$6D,$84,$27,$80,$29,$80,$31,$82,$42,$82,$31,$82,$31,$82
    .byte $1B,$80,$23,$80,$26,$80,$6D,$84,$6A,$8B,$6A,$8B,$6A,$8B,$6A,$8B
    .byte $0C,$92,$0C,$92,$0C,$92,$0C,$92,$9E,$91,$9E,$91,$9E,$91,$9A,$B5
    .byte $7E,$B5,$7E,$B5,$14,$88,$60,$94,$14,$88,$23,$88,$26,$88,$35,$88

; C24: 32 little-endian pointers loaded into BB/BC.
ScenePointerBBTable:
    .byte $7D,$84,$7D,$84,$2D,$80,$2D,$80,$45,$82,$45,$82,$45,$82,$45,$82
    .byte $2D,$80,$2D,$80,$2D,$80,$7D,$84,$78,$8B,$78,$8B,$78,$8B,$78,$8B
    .byte $17,$92,$17,$92,$17,$92,$17,$92,$AE,$91,$AE,$91,$AE,$91,$B1,$83
    .byte $B1,$83,$B1,$83,$38,$88,$61,$94,$38,$88,$38,$88,$38,$88,$38,$88

; C25: 32 little-endian pointers loaded into BF/C0.
ScenePointerBFTable:
    .byte $7D,$88,$7D,$88,$ED,$83,$ED,$83,$45,$86,$45,$86,$45,$86,$45,$86
    .byte $ED,$83,$ED,$83,$ED,$83,$7D,$88,$78,$8E,$78,$8E,$78,$8E,$78,$8E
    .byte $D7,$93,$D7,$93,$D7,$93,$D7,$93,$AE,$95,$AE,$95,$AE,$95,$B1,$84
    .byte $B1,$84,$B1,$84,$F8,$8C,$99,$94,$F8,$8C,$F8,$8C,$F8,$8C,$F8,$8C

; C26: 32 little-endian pointers loaded into BD/BE.
ScenePointerBDTable:
    .byte $EB,$88,$EB,$88,$47,$84,$47,$84,$D2,$86,$D2,$86,$D2,$86,$D2,$86
    .byte $47,$84,$47,$84,$47,$84,$EB,$88,$01,$8F,$01,$8F,$01,$8F,$01,$8F
    .byte $42,$94,$42,$94,$42,$94,$42,$94,$D4,$95,$D4,$95,$D4,$95,$D9,$84
    .byte $D9,$84,$D9,$84,$51,$8D,$CA,$94,$51,$8D,$51,$8D,$51,$8D,$51,$8D

; C27: 32 little-endian pointers loaded into C1/C2; used by collision path DA3D.
ScenePointerC1Table:
    .byte $CB,$8F,$CB,$8F,$E7,$89,$E7,$89,$A2,$8F,$A2,$8F,$A2,$8F,$A2,$8F
    .byte $E7,$89,$E7,$89,$E7,$89,$CB,$8F,$91,$97,$91,$97,$91,$97,$91,$97
    .byte $F2,$9A,$F2,$9A,$F2,$9A,$F2,$9A,$34,$98,$34,$98,$34,$98,$59,$87
    .byte $59,$87,$59,$87,$E1,$92,$DA,$97,$E1,$92,$E1,$92,$E1,$92,$E1,$92

; C28: 32 bytes loaded into 03BA; downstream palette-cycle encoding not fully reviewed.
ScenePaletteCycleTable:
    .byte $00,$00,$00,$00,$01,$01,$01,$00,$00,$00,$00,$00,$00,$00,$00,$00
    .byte $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00

; C29: 32 DB flag bytes; low direction codes 01 down,03 up,05 right,07 left; bit7 is runtime scroll activity.
SceneDirectionFlagsTable:
    .byte $05,$05,$01,$05,$05,$03,$05,$05,$05,$01,$04,$04,$05,$05,$05,$05
    .byte $25,$25,$05,$05,$05,$05,$04,$04,$05,$05,$03,$04,$03,$07,$03,$05

; C30: 32 bytes loaded into AF; downstream movement compares camera X page.
SceneHorizontalBoundPages:
    .byte $08,$0E,$00,$02,$0B,$0C,$0E,$0F,$07,$00,$00,$0E,$05,$0C,$0C,$04
    .byte $03,$08,$08,$09,$06,$0E,$0E,$00,$07,$0C,$02,$00,$02,$00,$00,$02

; C31: 32 screen counts multiplied by F0 into AD/AE.
SceneVerticalBoundScreens:
    .byte $00,$00,$01,$01,$02,$02,$00,$00,$00,$02,$00,$00,$00,$00,$00,$03
    .byte $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$0E,$00,$0E,$0E,$0E,$0E

; C32: 32 pointers to 27-byte palette/CHR profiles; some targets reside in R7 bank07, others in R6-selected bank.
ScenePaletteProfilePointers:
    .byte $52,$84,$52,$84,$00,$80,$00,$80,$E0,$81,$E0,$81,$FB,$81,$16,$82
    .byte $00,$80,$00,$80,$00,$80,$52,$84,$4F,$8B,$4F,$8B,$4F,$8B,$4F,$8B
    .byte $D6,$91,$D6,$91,$D6,$91,$F1,$91,$83,$91,$83,$91,$83,$91,$63,$B5
    .byte $96,$83,$96,$83,$B9,$B5,$45,$94,$F9,$87,$F9,$87,$9E,$B5,$9E,$B5

; C17: 17-entry CHR0, CHR1 and bank/page arrays followed by four arrays of 17 little-endian pointers.
SpecialLayoutArrays:
    .byte $08,$78,$00,$60,$74,$60,$1C,$00,$70,$70,$70,$70,$70,$70,$70,$70
    .byte $54,$0A,$7A,$02,$62,$76,$62,$1E,$4E,$72,$72,$72,$72,$72,$72,$72
    .byte $72,$56,$84,$02,$05,$02,$02,$02,$02,$04,$03,$03,$03,$03,$03,$03
    .byte $03,$03,$03,$5F,$B5,$61,$B5,$BE,$9C,$5F,$B5,$5F,$B5,$5F,$B5,$61
    .byte $B5,$5F,$B5,$BE,$98,$BE,$98,$BF,$98,$BF,$98,$C0,$98,$C0,$98,$C1
    .byte $98,$C1,$98,$5F,$B5,$D5,$99,$73,$9C,$BF,$9C,$2C,$99,$9D,$9A,$84
    .byte $99,$64,$99,$76,$9D,$9D,$9D,$9D,$9D,$9D,$9D,$9D,$9D,$9D,$9D,$9D
    .byte $9D,$9D,$9D,$9D,$9D,$3D,$9F,$15,$9A,$F3,$9C,$FF,$9C,$7D,$88,$DD
    .byte $9A,$7D,$88,$E4,$99,$B6,$9D,$C4,$98,$C4,$98,$C4,$98,$C4,$98,$C4
    .byte $98,$C4,$98,$C4,$98,$C4,$98,$7D,$9F,$46,$9A,$15,$9D,$1A,$9D,$EB
    .byte $88,$F3,$9A,$EB,$88,$ED,$99,$CE,$9D,$0D,$99,$0D,$99,$0D,$99,$0D
    .byte $99,$0D,$99,$0D,$99,$0D,$99,$0D,$99,$7D,$9F
    .incbin "inputs/original.nes", $00F54D, $02B7 ; UNINTERPRETED preserved bytes

; D05: D3&0F indexes tables; for valid0..7 set current/display HP to full capacity, copy maxMP and nextEXP; leave06BB unchanged.
RefreshProgressionDerivedValues:
    LDA a:$00d3              ; B7F4 Only low4 are masked: table domain established here is0..7, not all nibble values.
    AND #$0f                 ; B7F7 
    STA $3c                  ; B7F9 
    TAY                      ; B7FB 
    LDA a:$fde0,Y            ; B7FC 
    STA a:$06b9              ; B7FF 
    STA a:$06ba              ; B802 
    LDA $3c                  ; B805 
    ASL A                    ; B807 
    ADC $3c                  ; B808 
    TAY                      ; B80A 
    LDX #$02                 ; B80B 
    LDA a:$fdc8,Y            ; B80D 
    STA a:$00f5,X            ; B810 
    INY                      ; B813 
    DEX                      ; B814 
    BPL $b80d                ; B815 
    LDA $3c                  ; B817 
    ASL A                    ; B819 
    ASL A                    ; B81A 
    TAY                      ; B81B 
    LDX #$03                 ; B81C 
    LDA a:$fda8,Y            ; B81E 
    STA a:$00f1,X            ; B821 
    INY                      ; B824 
    DEX                      ; B825 
    BPL $b81e                ; B826 
    RTS                      ; B828 

; D06: Compare three base60 decimal digits most significant first; return carry set iff currentMP exceeds maxMP.
CompareCurrentMpToMaximum:
    LDX #$02                 ; B829 
    LDA a:$00f5,X            ; B82B 
    CMP a:$00ea,X            ; B82E 
    BCC $b83a                ; B831 
    BNE $b838                ; B833 
    DEX                      ; B835 
    BPL $b82b                ; B836 
    CLC                      ; B838 
    RTS                      ; B839 
    SEC                      ; B83A 
    RTS                      ; B83B 
    .incbin "inputs/original.nes", $00F84C, $07C4 ; UNINTERPRETED preserved bytes
