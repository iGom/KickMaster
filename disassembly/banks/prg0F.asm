; PRG bank 0F; CPU base used here is $E000.
; For unreviewed banks, the base is a scaffold convention, not a recovered mapping.
.segment "PRG0F"
.org $E000
    .incbin "inputs/original.nes", $01E010, $00ED ; UNINTERPRETED preserved bytes

; D36: Scan04EF-1 down to1 for nonnegative057F,Y, return A=0; full pool A=FF. Tested valid slot counts>=2.
FindFreeCollectibleSlot:
    LDY a:$04ef              ; E0ED 
    DEY                      ; E0F0 
    LDA a:$057f,Y            ; E0F1 
    BPL $e0fc                ; E0F4 
    DEY                      ; E0F6 
    BNE $e0f1                ; E0F7 
    LDA #$ff                 ; E0F9 
    RTS                      ; E0FB 
    LDA #$00                 ; E0FC 
    RTS                      ; E0FE 
    .incbin "inputs/original.nes", $01E10F, $01A4 ; UNINTERPRETED preserved bytes

; B37: Restore palette when 06EE=FF; decrement 03D5 and choose fixed palette colors using D9 bit 10.
ServicePaletteEffect:
    LDA a:$06ee              ; E2A3 
    BEQ $e2be                ; E2A6 
    CMP #$ff                 ; E2A8 
    BNE $e2be                ; E2AA 
    LDY #$20                 ; E2AC 
    LDA a:$01a5,Y            ; E2AE 
    STA a:$0142,Y            ; E2B1 
    DEY                      ; E2B4 
    BNE $e2ae                ; E2B5 
    STY a:$06ee              ; E2B7 
    LDA #$0e                 ; E2BA 
    STA $a0                  ; E2BC 
    LDA a:$03d5              ; E2BE 
    BEQ $e2d0                ; E2C1 
    DEC a:$03d5              ; E2C3 
    LDA $d9                  ; E2C6 
    AND #$10                 ; E2C8 
    BEQ $e2d0                ; E2CA 
    LDA #$30                 ; E2CC 
    BNE $e2db                ; E2CE 
    LDA a:$ffb3              ; E2D0 
    STA a:$0155              ; E2D3 
    LDA a:$ffb6              ; E2D6 
    BNE $e2de                ; E2D9 
    STA a:$0155              ; E2DB 
    STA a:$0159              ; E2DE 
    RTS                      ; E2E1 

; B38: If 03D6 is odd add 04 to 58; add 10 again when the wrapped first sum is at least F0.
AdjustScrollOnOddEffect:
    LDA a:$03d6              ; E2E2 
    BEQ $e2f8                ; E2E5 
    LSR A                    ; E2E7 
    BCC $e2f8                ; E2E8 
    LDA $58                  ; E2EA 
    CLC                      ; E2EC 
    ADC #$04                 ; E2ED 
    CMP #$f0                 ; E2EF 
    BCC $e2f6                ; E2F1 
    CLC                      ; E2F3 Second addition intentionally skips the F0..FF interval for relevant scroll values.
    ADC #$10                 ; E2F4 
    STA $58                  ; E2F6 
    RTS                      ; E2F8 
    .incbin "inputs/original.nes", $01E309, $0D17 ; UNINTERPRETED preserved bytes

; A12: Initialize hardware, bank mapping, selected RAM, PPU shadow and palette; jump to PRG0E CF50.
ResetEntry:
    SEI                      ; F010 
    LDX #$00                 ; F011 
    STX a:$e000              ; F013 Disable and acknowledge MMC3 IRQ.
    CLD                      ; F016 
    STX a:$8000              ; F017 Select R0, PRG mode 0, CHR inversion 0.
    STX a:$a000              ; F01A MMC3 mirroring 0: CIRAM A10 / conventional vertical mirroring.
    STX a:$2000              ; F01D 
    STX a:$2001              ; F020 
    DEX                      ; F023 
    TXS                      ; F024 
    LDX #$04                 ; F025 Wait for four observed vblank assertion/clear cycles.
    BIT a:$2002              ; F027 
    BPL $f027                ; F02A 
    BIT a:$2002              ; F02C 
    BMI $f02c                ; F02F 
    DEX                      ; F031 
    BNE $f027                ; F032 
    LDX #$06                 ; F034 R6 <- 04; R7 <- 05; fixed banks 0E at C000, 0F at E000.
    LDY #$04                 ; F036 
    STX a:$8000              ; F038 
    STY a:$8001              ; F03B 
    INX                      ; F03E 
    INY                      ; F03F 
    STX a:$8000              ; F040 
    STY a:$8001              ; F043 
    LDX #$00                 ; F046 
    STX a:$2005              ; F048 
    STX a:$2005              ; F04B 
    STX a:$e000              ; F04E 
    STX a:$4010              ; F051 
    STX a:$a000              ; F054 
    INX                      ; F057 
    LDA #$0f                 ; F058 
    STA a:$4015              ; F05A 
    LDA #$40                 ; F05D 
    STA a:$4017              ; F05F 
    STX a:$a001              ; F062 A001 receives 01, although the physical reference board has no PRG RAM.
    LDA a:$2002              ; F065 
    LDA #$10                 ; F068 
    TAX                      ; F06A 
    STA a:$2006              ; F06B 
    STA a:$2006              ; F06E 
    EOR #$10                 ; F071 
    DEX                      ; F073 
    BNE $f06b                ; F074 
    LDA #$00                 ; F076 
    TAX                      ; F078 
    STA a:$0000,X            ; F079 Clear internal RAM except 0100 and 0300..0307. Indexed bases are intentionally unusual.
    STA a:$0101,X            ; F07C 
    STA a:$0200,X            ; F07F 
    STA a:$0308,X            ; F082 
    STA a:$0400,X            ; F085 
    STA a:$0500,X            ; F088 
    STA a:$0600,X            ; F08B 
    STA a:$0700,X            ; F08E 
    INX                      ; F091 
    BNE $f079                ; F092 
    JSR a:$d60c              ; F094 Retention/default processing is in fixed PRG0E.
    LDA #$88                 ; F097 
    STA $4a                  ; F099 
    STA a:$2000              ; F09B 
    LDA #$0e                 ; F09E 
    STA $5f                  ; F0A0 
    STA $95                  ; F0A2 
    LDA #$0f                 ; F0A4 
    LDY #$1f                 ; F0A6 
    STA a:$0143,Y            ; F0A8 Initialize 32 palette-buffer bytes at 0143..0162.
    DEY                      ; F0AB 
    BPL $f0a8                ; F0AC 
    LDY #$00                 ; F0AE 
    JSR a:$f24b              ; F0B0 
    CLI                      ; F0B3 
    LDA #$f0                 ; F0B4 
    STA $7f                  ; F0B6 
    JMP a:$cf50              ; F0B8 

; A13: Save A/X/Y, OAM DMA, PPU task, scrolling, optional IRQ setup, CHR writes, epoch increment and RTI.
NmiEntry:
    STA $e7                  ; F0BB NMI stores registers in RAM rather than pushing them.
    STY $e9                  ; F0BD 
    STX $e8                  ; F0BF 
    LDA a:$2002              ; F0C1 
    LDY #$00                 ; F0C4 
    STY a:$2003              ; F0C6 
    LDA #$02                 ; F0C9 
    STA a:$4014              ; F0CB DMA source page 02 = RAM 0200..02FF.
    JSR a:$f156              ; F0CE Y=0 is a precondition for clearing A0 in the dispatcher.
    LDA $d9                  ; F0D1 
    LSR A                    ; F0D3 
    BCC $f0d9                ; F0D4 
    JSR a:$f28e              ; F0D6 
    LDY $68                  ; F0D9 
    LDX $68                  ; F0DB 
    BNE $f0e3                ; F0DD 
    LDY #$00                 ; F0DF 
    LDX $6a                  ; F0E1 
    LDA $4a,X                ; F0E3 
    STA a:$2000              ; F0E5 
    STA a:$2000              ; F0E8 
    LDA a:$005f,Y            ; F0EB 
    STA a:$2001              ; F0EE 
    LDA $51,X                ; F0F1 
    STA a:$2005              ; F0F3 
    LDA $58,X                ; F0F6 
    STA a:$2005              ; F0F8 
    LDX $96                  ; F0FB 
    BEQ $f116                ; F0FD 
    LDA $dc                  ; F0FF Restore IRQ dispatch pointer from DC/DD after the PPU task used E5/E6.
    STA $e5                  ; F101 
    LDA $dd                  ; F103 
    STA $e6                  ; F105 
    LDA a:$007f,Y            ; F107 
    STA a:$c000              ; F10A 
    STX $67                  ; F10D 
    STX a:$c001              ; F10F 
    DEX                      ; F112 
    STX a:$e001              ; F113 
    STX $95                  ; F116 For 96=0 or 1, X=0 here; this condition is documented, not assumed for arbitrary RAM.
    LDA $44                  ; F118 
    STX a:$8000              ; F11A Under the above condition, six writes select CHR R0..R5 using RAM 44..49.
    STA a:$8001              ; F11D 
    LDA $45                  ; F120 
    INX                      ; F122 
    STX a:$8000              ; F123 
    STA a:$8001              ; F126 
    LDA $46                  ; F129 
    INX                      ; F12B 
    STX a:$8000              ; F12C 
    STA a:$8001              ; F12F 
    LDA $47                  ; F132 
    INX                      ; F134 
    STX a:$8000              ; F135 
    STA a:$8001              ; F138 
    LDA $48                  ; F13B 
    INX                      ; F13D 
    STX a:$8000              ; F13E 
    STA a:$8001              ; F141 
    LDA $49                  ; F144 
    INX                      ; F146 
    STX a:$8000              ; F147 
    STA a:$8001              ; F14A 
    INC $a6                  ; F14D A6 tracks mapper-interrupt activity; it is not safely a pure frame counter.
    LDY $e9                  ; F14F 
    LDX $e8                  ; F151 
    LDA $e7                  ; F153 
    RTI                      ; F155 

; A14: Clear A0 using Y; select one of sixteen little-endian pointers with old A0 & 1E.
DispatchPpuTask:
    LDA $a0                  ; F156 Index mask 1E selects 16 word entries; odd command bit ignored here.
    STY $a0                  ; F158 
    AND #$1e                 ; F15A 
    TAX                      ; F15C 
    LDA a:$f16a,X            ; F15D 
    STA $e5                  ; F160 
    LDA a:$f16b,X            ; F162 
    STA $e6                  ; F165 
    JMP ($00e5)              ; F167 Computed jump, not ordinary fallthrough into the pointer table.

; A15: 16 little-endian pointers; indices are command&1E divided by 2.
PpuTaskPointers:
    .byte $B7,$F1,$8A,$F1,$EA,$F1,$B8,$F1,$0E,$F2,$B7,$F1,$B7,$F1,$4B,$F2
    .byte $78,$F3,$65,$F3,$AA,$F3,$E0,$FB,$C8,$FA,$CD,$FC,$12,$FD,$71,$FD

; A16: Stream 27 bytes from 0101..011B using PLA, restore SP; increment PPU by 32.
PpuUpload27ViaStack:
    LDA $4a                  ; F18A 
    ORA #$8c                 ; F18C 
    STA a:$2000              ; F18E 
    LDA $9c                  ; F191 
    STA a:$2006              ; F193 
    LDA $9b                  ; F196 
    STA a:$2006              ; F198 
    TSX                      ; F19B 
    STX a:$0170              ; F19C 
    LDX #$00                 ; F19F Temporary stack pointer 00: PLA reads upward from 0101.
    TXS                      ; F1A1 
    LDX #$09                 ; F1A2 
    PLA                      ; F1A4 
    STA a:$2007              ; F1A5 
    PLA                      ; F1A8 
    STA a:$2007              ; F1A9 
    PLA                      ; F1AC 
    STA a:$2007              ; F1AD 
    DEX                      ; F1B0 
    BNE $f1a4                ; F1B1 
    LDX a:$0170              ; F1B3 
    TXS                      ; F1B6 

; A17: Shared RTS target; also fallthrough from A16.
PpuTaskReturn:
    RTS                      ; F1B7 
    .incbin "inputs/original.nes", $01F1C8, $0093 ; UNINTERPRETED preserved bytes

; A18: Read 0143..0162 through PLA; write 32 bytes to PPU; restore SP and service 06EE flag.
UploadPalette32ViaStack:
    LDA #$3f                 ; F24B 
    STA a:$2006              ; F24D 
    STY a:$2006              ; F250 
    TSX                      ; F253 
    STX a:$0170              ; F254 
    LDX #$42                 ; F257 Temporary SP=42 makes PLA read palette bytes starting at 0143.
    TXS                      ; F259 
    LDX #$08                 ; F25A 
    PLA                      ; F25C 
    STA a:$2007              ; F25D 
    PLA                      ; F260 
    STA a:$2007              ; F261 
    PLA                      ; F264 
    STA a:$2007              ; F265 
    PLA                      ; F268 
    STA a:$2007              ; F269 
    DEX                      ; F26C 
    BNE $f25c                ; F26D 
    LDA #$3f                 ; F26F 
    STA a:$2006              ; F271 
    LDA #$00                 ; F274 
    STA a:$2006              ; F276 
    STA a:$2006              ; F279 
    STA a:$2006              ; F27C 
    LDX a:$0170              ; F27F Restore the real stack before RTS.
    TXS                      ; F282 
    LDX a:$06ee              ; F283 
    BEQ $f28d                ; F286 
    LDX #$ff                 ; F288 
    STX a:$06ee              ; F28A 
    RTS                      ; F28D 
    .incbin "inputs/original.nes", $01F29E, $022C ; UNINTERPRETED preserved bytes

; A19: Clear PPUMASK and shadows 5F/66; clear bit 1 of 4A.
DisableRendering:
    LDY #$00                 ; F4BA 
    STY a:$2001              ; F4BC 
    STY $5f                  ; F4BF 
    STY $66                  ; F4C1 
    LDA $4a                  ; F4C3 
    AND #$fd                 ; F4C5 
    STA $4a                  ; F4C7 
    RTS                      ; F4C9 

; A20: Save bank tags and registers, map 04EC into A000, call pointer 04EA, restore both PRG windows and result registers/flags.
FarCallViaA000:
    PHP                      ; F4CA 
    PHA                      ; F4CB 
    TYA                      ; F4CC 
    PHA                      ; F4CD 
    TXA                      ; F4CE 
    PHA                      ; F4CF 
    LDA a:$9fff              ; F4D0 Read live bank identity from the final byte of the 8000 window.
    STA a:$04ee              ; F4D3 
    LDA a:$bfff              ; F4D6 Read live bank identity from the final byte of the A000 window.
    STA a:$04ed              ; F4D9 
    LDX #$07                 ; F4DC 
    LDA a:$04ec              ; F4DE Target A000 bank is supplied through RAM 04EC.
    JSR a:$d6c3              ; F4E1 
    PLA                      ; F4E4 
    TAX                      ; F4E5 
    PLA                      ; F4E6 
    TAY                      ; F4E7 
    PLA                      ; F4E8 
    PLP                      ; F4E9 
    JSR a:$f50a              ; F4EA JSR into an indirect JMP allows the destination RTS to return here.
    PHP                      ; F4ED Preserve callee output registers and flags while restoring mappings.
    PHA                      ; F4EE 
    TYA                      ; F4EF 
    PHA                      ; F4F0 
    TXA                      ; F4F1 
    PHA                      ; F4F2 
    LDX #$07                 ; F4F3 
    LDA a:$04ed              ; F4F5 
    JSR a:$d6c3              ; F4F8 
    LDX #$06                 ; F4FB Restore both R7 and R6, even though entry changes only R7.
    LDA a:$04ee              ; F4FD 
    JSR a:$d6c3              ; F500 
    PLA                      ; F503 
    TAX                      ; F504 
    PLA                      ; F505 
    TAY                      ; F506 
    PLA                      ; F507 
    PLP                      ; F508 
    RTS                      ; F509 

; A21: Indirect JMP through RAM 04EA/04EB; called with JSR to make the callee return to wrapper.
FarCallIndirect:
    JMP ($04ea)              ; F50A 
    .incbin "inputs/original.nes", $01F51D, $0152 ; UNINTERPRETED preserved bytes

; D37: Copy four tile IDs indexed06BD*4 fromFF2A to0185..0188; A0=16, fall through HUD staging.
RefreshSelectedSpellIcon:
    LDA a:$06bd              ; F65F 
    ASL A                    ; F662 
    ASL A                    ; F663 
    TAY                      ; F664 
    LDA a:$ff2a,Y            ; F665 
    STA a:$0185              ; F668 
    LDA a:$ff2b,Y            ; F66B 
    STA a:$0186              ; F66E 
    LDA a:$ff2c,Y            ; F671 
    STA a:$0187              ; F674 
    LDA a:$ff2d,Y            ; F677 
    STA a:$0188              ; F67A 
    LDA #$16                 ; F67D 
    STA $a0                  ; F67F 

; D38: Stage icon and fixed tiles; level digit=(D3&7)+60, attempts digit=030E+5F, displaying internal attempts minus1.
BuildLevelAndAttemptsHud:
    LDA a:$0185              ; F681 
    STA a:$0163              ; F684 
    LDA a:$0186              ; F687 
    STA a:$0164              ; F68A 
    LDA #$40                 ; F68D 
    STA a:$0165              ; F68F 
    LDA #$7a                 ; F692 
    STA a:$0166              ; F694 
    LDA $d3                  ; F697 
    AND #$07                 ; F699 
    CLC                      ; F69B 
    ADC #$60                 ; F69C 
    STA a:$0167              ; F69E 
    LDA a:$0187              ; F6A1 
    STA a:$0168              ; F6A4 
    LDA a:$0188              ; F6A7 
    STA a:$0169              ; F6AA 
    LDA #$51                 ; F6AD 
    STA a:$016a              ; F6AF 
    LDA #$7b                 ; F6B2 
    STA a:$016b              ; F6B4 
    LDA a:$030e              ; F6B7 
    CLC                      ; F6BA 
    ADC #$5f                 ; F6BB 
    STA a:$016c              ; F6BD 
    RTS                      ; F6C0 
    .incbin "inputs/original.nes", $01F6D1, $000B ; UNINTERPRETED preserved bytes

; B39: Call D90C and decrement X until zero; initial X=00 means 256 updates.
WaitCountedUpdates:
    JSR a:$d90c              ; F6CC 
    DEX                      ; F6CF Initial zero wraps to FF and takes 256 calls to reach zero.
    BNE $f6cc                ; F6D0 
    RTS                      ; F6D2 

; B40: Counted wait with early exit on newly pressed A or Start; returns masked input in A.
WaitCountedOrAStart:
    JSR a:$d90c              ; F6D3 
    LDA $1f                  ; F6D6 
    AND #$90                 ; F6D8 
    BNE $f6df                ; F6DA 
    DEX                      ; F6DC 
    BNE $f6d3                ; F6DD 
    RTS                      ; F6DF 

; B41: Repeat D90C until newly pressed A or Start.
WaitForAStart:
    JSR a:$d90c              ; F6E0 
    LDA $1f                  ; F6E3 
    AND #$90                 ; F6E5 
    BEQ $f6e0                ; F6E7 
    RTS                      ; F6E9 

; B42: Tail jump to fixed CFA2.
EnterInitialRunContext:
    JMP a:$cfa2              ; F6EA 

; C59: Draw FF-terminated four-byte sprite records from B6/B7; relative Y from22, X from24/25, attribute OR2C; hide horizontally offscreen sprites and cap valid OAM count64.
DrawMetaspriteNormal:
    LDA $99                  ; F6ED 
    ASL A                    ; F6EF 
    ASL A                    ; F6F0 
    BCS $f736                ; F6F1 
    STA $b0                  ; F6F3 
    LDY #$00                 ; F6F5 
    LDA #$00                 ; F6F7 
    STA $3c                  ; F6F9 
    LDA ($b6),Y              ; F6FB 
    CMP #$ff                 ; F6FD 
    BEQ $f736                ; F6FF 
    ADC $22                  ; F701 CMP #FF cleared carry for each non-terminator record, supplying the implicit clear for ADC.
    STA ($b0),Y              ; F703 
    INY                      ; F705 
    LDA ($b6),Y              ; F706 
    STA ($b0),Y              ; F708 
    INY                      ; F70A 
    LDA ($b6),Y              ; F70B 
    ORA $2c                  ; F70D 
    STA ($b0),Y              ; F70F 
    INY                      ; F711 
    LDA ($b6),Y              ; F712 
    BPL $f718                ; F714 
    DEC $3c                  ; F716 
    CLC                      ; F718 
    ADC $24                  ; F719 
    STA ($b0),Y              ; F71B 
    LDA $25                  ; F71D 
    ADC $3c                  ; F71F 
    BEQ $f72f                ; F721 
    TYA                      ; F723 
    PHA                      ; F724 
    TYA                      ; F725 
    AND #$fc                 ; F726 
    TAY                      ; F728 
    LDA #$f1                 ; F729 
    STA ($b0),Y              ; F72B 
    PLA                      ; F72D 
    TAY                      ; F72E 
    INY                      ; F72F 
    INC $99                  ; F730 
    BIT $99                  ; F732 
    BVC $f6f7                ; F734 
    RTS                      ; F736 

; C60: As normal renderer, XOR attribute40 and mirror signed X offset using -(offset+8).
DrawMetaspriteFlipped:
    LDA $99                  ; F737 
    ASL A                    ; F739 
    ASL A                    ; F73A 
    BCS $f78a                ; F73B 
    STA $b0                  ; F73D 
    LDY #$00                 ; F73F 
    LDA #$00                 ; F741 
    STA $3c                  ; F743 
    LDA ($b6),Y              ; F745 
    CMP #$ff                 ; F747 
    BEQ $f78a                ; F749 
    ADC $22                  ; F74B 
    STA ($b0),Y              ; F74D 
    INY                      ; F74F 
    LDA ($b6),Y              ; F750 
    STA ($b0),Y              ; F752 
    INY                      ; F754 
    LDA ($b6),Y              ; F755 
    EOR #$40                 ; F757 
    ORA $2c                  ; F759 
    STA ($b0),Y              ; F75B 
    INY                      ; F75D 
    LDA ($b6),Y              ; F75E 
    CLC                      ; F760 
    ADC #$08                 ; F761 Eight-pixel sprite width is part of horizontal mirroring.
    EOR #$ff                 ; F763 
    CLC                      ; F765 
    ADC #$01                 ; F766 
    BPL $f76c                ; F768 
    DEC $3c                  ; F76A 
    CLC                      ; F76C 
    ADC $24                  ; F76D 
    STA ($b0),Y              ; F76F 
    LDA $25                  ; F771 
    ADC $3c                  ; F773 
    BEQ $f783                ; F775 
    TYA                      ; F777 
    PHA                      ; F778 
    TYA                      ; F779 
    AND #$fc                 ; F77A 
    TAY                      ; F77C 
    LDA #$f1                 ; F77D 
    STA ($b0),Y              ; F77F 
    PLA                      ; F781 
    TAY                      ; F782 
    INY                      ; F783 
    INC $99                  ; F784 
    BIT $99                  ; F786 
    BVC $f741                ; F788 
    RTS                      ; F78A 

; C61: For input A high 00..0F and Y low, return A=remainder and Y=quotient of the 16-bit position divided by F0.
NormalizeYTo240LinePages:
    STY $3c                  ; F78B 
    TAY                      ; F78D 
    LDA a:$f7a1,Y            ; F78E 
    CLC                      ; F791 
    ADC $3c                  ; F792 
    BCC $f799                ; F794 
    INY                      ; F796 
    ADC #$0f                 ; F797 
    CMP #$f0                 ; F799 
    BCC $f7a0                ; F79B 
    SBC #$f0                 ; F79D 
    INY                      ; F79F 
    RTS                      ; F7A0 

; C62: 16 bytes 00,10,...F0 used by Y-coordinate normalization.
YPageCorrectionTable:
    .byte $00,$10,$20,$30,$40,$50,$60,$70,$80,$90,$A0,$B0,$C0,$D0,$E0,$F0

; A22: Save A/X/Y in E2..E4; acknowledge/disable IRQ, enable again, dispatch through E5/E6.
IrqEntry:
    STA $e2                  ; F7B1 
    STX $e3                  ; F7B3 
    STY $e4                  ; F7B5 
    LDA #$00                 ; F7B7 
    STA a:$e000              ; F7B9 
    STA a:$e001              ; F7BC 
    JMP ($00e5)              ; F7BF IRQ pointer is shared with temporary PPU dispatch pointer E5/E6.

; A23: Timed PPU address/scroll writes indexed by 67; choose terminal split at F0 sentinel; share IRQ return.
IrqSplitPpuAddress:
    LDA a:$2002              ; F7C2 
    LDX #$09                 ; F7C5 
    DEX                      ; F7C7 
    BNE $f7c7                ; F7C8 
    LDY $67                  ; F7CA 
    LDA a:$0080,Y            ; F7CC 
    STA a:$c000              ; F7CF 
    LDA a:$004b,Y            ; F7D2 
    STA a:$2000              ; F7D5 
    LDA a:$0701,Y            ; F7D8 
    STA a:$2006              ; F7DB 
    LDA a:$06fa,Y            ; F7DE 
    STA a:$2006              ; F7E1 
    LDA $51                  ; F7E4 
    STA a:$2005              ; F7E6 
    LDA a:$0059,Y            ; F7E9 
    STA a:$2005              ; F7EC 
    LDA a:$0081,Y            ; F7EF 
    CMP #$f0                 ; F7F2 
    BNE $f7fe                ; F7F4 
    LDA #$3d                 ; F7F6 Switch to terminal split handler F83D when next count is F0.
    STA $e5                  ; F7F8 
    LDA #$f8                 ; F7FA 
    STA $e6                  ; F7FC 
    INC $67                  ; F7FE 
    JMP a:$f834              ; F800 

; A24: Timed indexed scroll/control writes; select F83D on F0 sentinel.
IrqSplitScroll:
    LDA a:$2002              ; F803 
    LDX #$09                 ; F806 
    DEX                      ; F808 
    BNE $f808                ; F809 
    LDY $67                  ; F80B 
    LDA a:$007f,Y            ; F80D 
    STA a:$c000              ; F810 
    LDX a:$006a,Y            ; F813 
    LDA $4a,X                ; F816 
    ORA #$88                 ; F818 
    STA a:$2000              ; F81A 
    LDA $51,X                ; F81D 
    STA a:$2005              ; F81F 
    LDA $58                  ; F822 
    STA a:$2005              ; F824 
    LDA a:$0080,Y            ; F827 
    CMP #$f0                 ; F82A 
    BNE $f832                ; F82C 
    LDA #$3d                 ; F82E Only low pointer byte changes; high byte F8 is a caller/state precondition.
    STA $e5                  ; F830 
    INC $67                  ; F832 

; A25: Increment A6, restore Y/X/A from E4/E3/E2, RTI.
IrqRestoreRegisters:
    INC $a6                  ; F834 
    LDY $e4                  ; F836 
    LDX $e3                  ; F838 
    LDA $e2                  ; F83A 
    RTI                      ; F83C 

; A26: Timed split setting control, mask, address and CHR registers 0/1 to 0/2; set next IRQ low pointer 82.
IrqSplitSwitchChr01:
    LDA a:$2002              ; F83D 
    LDX #$09                 ; F840 
    DEX                      ; F842 
    BNE $f842                ; F843 
    LDA #$15                 ; F845 
    STA a:$c000              ; F847 
    LDA #$89                 ; F84A 
    STA a:$2000              ; F84C 
    LDA $66                  ; F84F 
    STA a:$2001              ; F851 
    LDA #$27                 ; F854 
    STA a:$2006              ; F856 
    LDA #$60                 ; F859 
    STA a:$2006              ; F85B 
    STX a:$2005              ; F85E 
    STX a:$2005              ; F861 
    STX a:$8000              ; F864 X=0 after delay loop; select CHR R0 and set it to 00.
    STX a:$8001              ; F867 
    INX                      ; F86A 
    STX a:$03d8              ; F86B 
    STX a:$8000              ; F86E 
    INX                      ; F871 
    STX a:$8001              ; F872 
    LDA #$82                 ; F875 Only pointer low byte changes to 82; high F8 must already be set.
    STA $e5                  ; F877 
    INC $a6                  ; F879 
    LDY $e4                  ; F87B 
    LDX $e3                  ; F87D 
    LDA $e2                  ; F87F 
    RTI                      ; F881 
    .incbin "inputs/original.nes", $01F892, $0251 ; UNINTERPRETED preserved bytes

; C63: Select profile with FE6C[9A], copy latch/index pairs until F0, then NMI selector and IRQ source chosen by selector and pair count.
LoadSceneIrqProfile:
    LDX $9a                  ; FAD3 
    LDA a:$fe6c,X            ; FAD5 
    ASL A                    ; FAD8 
    TAY                      ; FAD9 
    LDA a:$fe8c,Y            ; FADA 
    STA $e5                  ; FADD 
    LDA a:$fe8d,Y            ; FADF 
    STA $e6                  ; FAE2 
    LDY #$00                 ; FAE4 
    LDX #$00                 ; FAE6 
    LDA ($e5),Y              ; FAE8 
    STA $7f,X                ; FAEA 
    INY                      ; FAEC 
    CMP #$f0                 ; FAED 
    BEQ $faf9                ; FAEF 
    LDA ($e5),Y              ; FAF1 
    STA $6a,X                ; FAF3 
    INY                      ; FAF5 
    INX                      ; FAF6 
    BNE $fae8                ; FAF7 
    LDA ($e5),Y              ; FAF9 
    STA $68                  ; FAFB 
    BNE $fb15                ; FAFD 
    CPX #$01                 ; FAFF 
    BNE $fb0c                ; FB01 
    LDA #$3d                 ; FB03 
    STA $dc                  ; FB05 
    LDA #$f8                 ; FB07 
    STA $dd                  ; FB09 
    RTS                      ; FB0B 
    LDA #$03                 ; FB0C 
    STA $dc                  ; FB0E 
    LDA #$f8                 ; FB10 
    STA $dd                  ; FB12 
    RTS                      ; FB14 
    LDA #$c2                 ; FB15 
    STA $dc                  ; FB17 
    LDA #$f7                 ; FB19 
    STA $dd                  ; FB1B 
    RTS                      ; FB1D 
    .incbin "inputs/original.nes", $01FB2E, $028A ; UNINTERPRETED preserved bytes

; D39: Eight four-byte MSD-first base60 decimal thresholds1000..7000,9999 indexed by current level.
NextExperienceThresholds:
    .byte $61,$60,$60,$60,$62,$60,$60,$60,$63,$60,$60,$60,$64,$60,$60,$60
    .byte $65,$60,$60,$60,$66,$60,$60,$60,$67,$60,$60,$60,$69,$69,$69,$69

; D40: Eight three-byte MSD-first base60 decimal maxima100,200,300,400,500,600,700,999.
MaximumMpByLevel:
    .byte $61,$60,$60,$62,$60,$60,$63,$60,$60,$64,$60,$60,$65,$60,$60,$66
    .byte $60,$60,$67,$60,$60,$69,$69,$69

; C64: Eight raw capacities 40,50,60,70,80,90,A0,B0 indexed by D3&07 on restore; match 4..11 sixteen-unit cells.
PlayerHpCapacityByIndex:
    .byte $40,$50,$60,$70,$80,$90,$A0,$B0

; D41: Six six-byte MSD-first base20 thresholds10000,50000,100000,200000,500000,999999. Last sentinel is not followed by another reviewed threshold.
ExtraAttemptScoreThresholds:
    .byte $20,$21,$20,$20,$20,$20,$20,$25,$20,$20,$20,$20,$21,$20,$20,$20
    .byte $20,$20,$22,$20,$20,$20,$20,$20,$25,$20,$20,$20,$20,$20,$29,$29
    .byte $29,$29,$29,$29
    .incbin "inputs/original.nes", $01FE1C, $0060 ; UNINTERPRETED preserved bytes

; C65: 32 selectors for six IRQ profiles.
SceneIrqProfileIndex:
    .byte $00,$00,$00,$00,$00,$00,$00,$05,$00,$00,$00,$00,$04,$04,$04,$00
    .byte $00,$00,$00,$02,$01,$01,$01,$00,$03,$03,$00,$00,$00,$00,$00,$00

; C66: Six little-endian pointers to F0-terminated latch/index streams.
SceneIrqProfilePointers:
    .byte $98,$FE,$9C,$FE,$BC,$FE,$C6,$FE,$CC,$FE,$D4,$FE

; C67: Six streams; final F0 byte is a terminal latch followed by NMI selector, not an ordinary latch/index pair.
SceneIrqProfiles:
    .byte $CE,$00,$F0,$00,$41,$02,$01,$05,$01,$04,$01,$03,$01,$06,$01,$05
    .byte $01,$04,$01,$03,$01,$06,$01,$05,$01,$04,$01,$03,$01,$06,$01,$05
    .byte $71,$00,$F0,$00,$00,$00,$83,$00,$0D,$00,$3B,$00,$F0,$01,$AF,$01
    .byte $1E,$00,$F0,$00,$3D,$02,$50,$01,$3E,$00,$F0,$00,$00,$00,$61,$00
    .byte $3F,$00,$2C,$00,$F0,$01
    .incbin "inputs/original.nes", $01FEEE, $0018 ; UNINTERPRETED preserved bytes

; E51: Thirteen four-byte icon argument groups; two A/X pairs consumed by menu sprite calls; last group used for locked icons.
MagicMenuIconSpriteArguments:
    .byte $01,$01,$11,$01,$03,$01,$13,$01,$0B,$02,$1B,$02,$23,$00,$33,$00
    .byte $25,$00,$35,$00,$21,$00,$31,$00,$0F,$00,$1F,$00,$27,$00,$37,$00
    .byte $05,$01,$15,$01,$0D,$02,$1D,$02,$07,$01,$17,$01,$09,$02,$19,$02
    .byte $29,$03,$39,$03

; D42: Thirteen four-tile glyph groups for06BD0..0C; visual identity not independently rendered.
SelectedSpellIconTiles:
    .byte $80,$90,$81,$91,$82,$92,$83,$93,$8A,$9A,$8B,$9B,$A2,$B2,$A3,$B3
    .byte $A4,$B4,$A5,$B5,$A0,$B0,$A1,$B1,$8E,$9E,$8F,$9F,$A6,$B6,$A7,$B7
    .byte $84,$94,$85,$95,$8C,$9C,$8D,$9D,$86,$96,$87,$97,$88,$98,$89,$99
    .byte $A8,$B8,$A9,$B9
    .incbin "inputs/original.nes", $01FF6E, $009C ; UNINTERPRETED preserved bytes

; A27: Little-endian NMI, RESET and IRQ/BRK vectors in the fixed final bank.
InterruptVectors:
    .byte $BB,$F0,$10,$F0,$B1,$F7
