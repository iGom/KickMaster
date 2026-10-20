; Reviewed local routines. Gaps are intentionally absent; not a standalone whole-bank file.
.setcpu "6502"

; A12: Initialize hardware, bank mapping, selected RAM, PPU shadow and palette; jump to PRG0E CF50.
; {'bank': '0F', 'cpu': '0xF010', 'bank_offset': '0x1010', 'prg_offset': '0x01F010', 'file_offset': '0x01F020', 'mapping_condition': 'last bank fixed at E000'}
.org $F010
ResetEntry:
    SEI                      ; F010 78       
    LDX #$00                 ; F011 A2 00    
    STX a:$e000              ; F013 8E 00 E0 Disable and acknowledge MMC3 IRQ.
    CLD                      ; F016 D8       
    STX a:$8000              ; F017 8E 00 80 Select R0, PRG mode 0, CHR inversion 0.
    STX a:$a000              ; F01A 8E 00 A0 MMC3 mirroring 0: CIRAM A10 / conventional vertical mirroring.
    STX a:$2000              ; F01D 8E 00 20 
    STX a:$2001              ; F020 8E 01 20 
    DEX                      ; F023 CA       
    TXS                      ; F024 9A       
    LDX #$04                 ; F025 A2 04    Wait for four observed vblank assertion/clear cycles.
    BIT a:$2002              ; F027 2C 02 20 
    BPL $f027                ; F02A 10 FB    
    BIT a:$2002              ; F02C 2C 02 20 
    BMI $f02c                ; F02F 30 FB    
    DEX                      ; F031 CA       
    BNE $f027                ; F032 D0 F3    
    LDX #$06                 ; F034 A2 06    R6 <- 04; R7 <- 05; fixed banks 0E at C000, 0F at E000.
    LDY #$04                 ; F036 A0 04    
    STX a:$8000              ; F038 8E 00 80 
    STY a:$8001              ; F03B 8C 01 80 
    INX                      ; F03E E8       
    INY                      ; F03F C8       
    STX a:$8000              ; F040 8E 00 80 
    STY a:$8001              ; F043 8C 01 80 
    LDX #$00                 ; F046 A2 00    
    STX a:$2005              ; F048 8E 05 20 
    STX a:$2005              ; F04B 8E 05 20 
    STX a:$e000              ; F04E 8E 00 E0 
    STX a:$4010              ; F051 8E 10 40 
    STX a:$a000              ; F054 8E 00 A0 
    INX                      ; F057 E8       
    LDA #$0f                 ; F058 A9 0F    
    STA a:$4015              ; F05A 8D 15 40 
    LDA #$40                 ; F05D A9 40    
    STA a:$4017              ; F05F 8D 17 40 
    STX a:$a001              ; F062 8E 01 A0 A001 receives 01, although the physical reference board has no PRG RAM.
    LDA a:$2002              ; F065 AD 02 20 
    LDA #$10                 ; F068 A9 10    
    TAX                      ; F06A AA       
    STA a:$2006              ; F06B 8D 06 20 
    STA a:$2006              ; F06E 8D 06 20 
    EOR #$10                 ; F071 49 10    
    DEX                      ; F073 CA       
    BNE $f06b                ; F074 D0 F5    
    LDA #$00                 ; F076 A9 00    
    TAX                      ; F078 AA       
    STA a:$0000,X            ; F079 9D 00 00 Clear internal RAM except 0100 and 0300..0307. Indexed bases are intentionally unusual.
    STA a:$0101,X            ; F07C 9D 01 01 
    STA a:$0200,X            ; F07F 9D 00 02 
    STA a:$0308,X            ; F082 9D 08 03 
    STA a:$0400,X            ; F085 9D 00 04 
    STA a:$0500,X            ; F088 9D 00 05 
    STA a:$0600,X            ; F08B 9D 00 06 
    STA a:$0700,X            ; F08E 9D 00 07 
    INX                      ; F091 E8       
    BNE $f079                ; F092 D0 E5    
    JSR a:$d60c              ; F094 20 0C D6 Retention/default processing is in fixed PRG0E.
    LDA #$88                 ; F097 A9 88    
    STA $4a                  ; F099 85 4A    
    STA a:$2000              ; F09B 8D 00 20 
    LDA #$0e                 ; F09E A9 0E    
    STA $5f                  ; F0A0 85 5F    
    STA $95                  ; F0A2 85 95    
    LDA #$0f                 ; F0A4 A9 0F    
    LDY #$1f                 ; F0A6 A0 1F    
    STA a:$0143,Y            ; F0A8 99 43 01 Initialize 32 palette-buffer bytes at 0143..0162.
    DEY                      ; F0AB 88       
    BPL $f0a8                ; F0AC 10 FA    
    LDY #$00                 ; F0AE A0 00    
    JSR a:$f24b              ; F0B0 20 4B F2 
    CLI                      ; F0B3 58       
    LDA #$f0                 ; F0B4 A9 F0    
    STA $7f                  ; F0B6 85 7F    
    JMP a:$cf50              ; F0B8 4C 50 CF 

; A13: Save A/X/Y, OAM DMA, PPU task, scrolling, optional IRQ setup, CHR writes, epoch increment and RTI.
; {'bank': '0F', 'cpu': '0xF0BB', 'bank_offset': '0x10BB', 'prg_offset': '0x01F0BB', 'file_offset': '0x01F0CB', 'mapping_condition': 'last bank fixed at E000'}
.org $F0BB
NmiEntry:
    STA $e7                  ; F0BB 85 E7    NMI stores registers in RAM rather than pushing them.
    STY $e9                  ; F0BD 84 E9    
    STX $e8                  ; F0BF 86 E8    
    LDA a:$2002              ; F0C1 AD 02 20 
    LDY #$00                 ; F0C4 A0 00    
    STY a:$2003              ; F0C6 8C 03 20 
    LDA #$02                 ; F0C9 A9 02    
    STA a:$4014              ; F0CB 8D 14 40 DMA source page 02 = RAM 0200..02FF.
    JSR a:$f156              ; F0CE 20 56 F1 Y=0 is a precondition for clearing A0 in the dispatcher.
    LDA $d9                  ; F0D1 A5 D9    
    LSR A                    ; F0D3 4A       
    BCC $f0d9                ; F0D4 90 03    
    JSR a:$f28e              ; F0D6 20 8E F2 
    LDY $68                  ; F0D9 A4 68    
    LDX $68                  ; F0DB A6 68    
    BNE $f0e3                ; F0DD D0 04    
    LDY #$00                 ; F0DF A0 00    
    LDX $6a                  ; F0E1 A6 6A    
    LDA $4a,X                ; F0E3 B5 4A    
    STA a:$2000              ; F0E5 8D 00 20 
    STA a:$2000              ; F0E8 8D 00 20 
    LDA a:$005f,Y            ; F0EB B9 5F 00 
    STA a:$2001              ; F0EE 8D 01 20 
    LDA $51,X                ; F0F1 B5 51    
    STA a:$2005              ; F0F3 8D 05 20 
    LDA $58,X                ; F0F6 B5 58    
    STA a:$2005              ; F0F8 8D 05 20 
    LDX $96                  ; F0FB A6 96    
    BEQ $f116                ; F0FD F0 17    
    LDA $dc                  ; F0FF A5 DC    Restore IRQ dispatch pointer from DC/DD after the PPU task used E5/E6.
    STA $e5                  ; F101 85 E5    
    LDA $dd                  ; F103 A5 DD    
    STA $e6                  ; F105 85 E6    
    LDA a:$007f,Y            ; F107 B9 7F 00 
    STA a:$c000              ; F10A 8D 00 C0 
    STX $67                  ; F10D 86 67    
    STX a:$c001              ; F10F 8E 01 C0 
    DEX                      ; F112 CA       
    STX a:$e001              ; F113 8E 01 E0 
    STX $95                  ; F116 86 95    For 96=0 or 1, X=0 here; this condition is documented, not assumed for arbitrary RAM.
    LDA $44                  ; F118 A5 44    
    STX a:$8000              ; F11A 8E 00 80 Under the above condition, six writes select CHR R0..R5 using RAM 44..49.
    STA a:$8001              ; F11D 8D 01 80 
    LDA $45                  ; F120 A5 45    
    INX                      ; F122 E8       
    STX a:$8000              ; F123 8E 00 80 
    STA a:$8001              ; F126 8D 01 80 
    LDA $46                  ; F129 A5 46    
    INX                      ; F12B E8       
    STX a:$8000              ; F12C 8E 00 80 
    STA a:$8001              ; F12F 8D 01 80 
    LDA $47                  ; F132 A5 47    
    INX                      ; F134 E8       
    STX a:$8000              ; F135 8E 00 80 
    STA a:$8001              ; F138 8D 01 80 
    LDA $48                  ; F13B A5 48    
    INX                      ; F13D E8       
    STX a:$8000              ; F13E 8E 00 80 
    STA a:$8001              ; F141 8D 01 80 
    LDA $49                  ; F144 A5 49    
    INX                      ; F146 E8       
    STX a:$8000              ; F147 8E 00 80 
    STA a:$8001              ; F14A 8D 01 80 
    INC $a6                  ; F14D E6 A6    A6 tracks mapper-interrupt activity; it is not safely a pure frame counter.
    LDY $e9                  ; F14F A4 E9    
    LDX $e8                  ; F151 A6 E8    
    LDA $e7                  ; F153 A5 E7    
    RTI                      ; F155 40       

; A14: Clear A0 using Y; select one of sixteen little-endian pointers with old A0 & 1E.
; {'bank': '0F', 'cpu': '0xF156', 'bank_offset': '0x1156', 'prg_offset': '0x01F156', 'file_offset': '0x01F166', 'mapping_condition': 'last bank fixed at E000'}
.org $F156
DispatchPpuTask:
    LDA $a0                  ; F156 A5 A0    Index mask 1E selects 16 word entries; odd command bit ignored here.
    STY $a0                  ; F158 84 A0    
    AND #$1e                 ; F15A 29 1E    
    TAX                      ; F15C AA       
    LDA a:$f16a,X            ; F15D BD 6A F1 
    STA $e5                  ; F160 85 E5    
    LDA a:$f16b,X            ; F162 BD 6B F1 
    STA $e6                  ; F165 85 E6    
    JMP ($00e5)              ; F167 6C E5 00 Computed jump, not ordinary fallthrough into the pointer table.

; A15: 16 little-endian pointers; indices are command&1E divided by 2.
; {'bank': '0F', 'cpu': '0xF16A', 'bank_offset': '0x116A', 'prg_offset': '0x01F16A', 'file_offset': '0x01F17A', 'mapping_condition': 'last bank fixed at E000'}
.org $F16A
PpuTaskPointers:
    .byte $B7,$F1,$8A,$F1,$EA,$F1,$B8,$F1,$0E,$F2,$B7,$F1,$B7,$F1,$4B,$F2
    .byte $78,$F3,$65,$F3,$AA,$F3,$E0,$FB,$C8,$FA,$CD,$FC,$12,$FD,$71,$FD

; A16: Stream 27 bytes from 0101..011B using PLA, restore SP; increment PPU by 32.
; {'bank': '0F', 'cpu': '0xF18A', 'bank_offset': '0x118A', 'prg_offset': '0x01F18A', 'file_offset': '0x01F19A', 'mapping_condition': 'last bank fixed at E000'}
.org $F18A
PpuUpload27ViaStack:
    LDA $4a                  ; F18A A5 4A    
    ORA #$8c                 ; F18C 09 8C    
    STA a:$2000              ; F18E 8D 00 20 
    LDA $9c                  ; F191 A5 9C    
    STA a:$2006              ; F193 8D 06 20 
    LDA $9b                  ; F196 A5 9B    
    STA a:$2006              ; F198 8D 06 20 
    TSX                      ; F19B BA       
    STX a:$0170              ; F19C 8E 70 01 
    LDX #$00                 ; F19F A2 00    Temporary stack pointer 00: PLA reads upward from 0101.
    TXS                      ; F1A1 9A       
    LDX #$09                 ; F1A2 A2 09    
    PLA                      ; F1A4 68       
    STA a:$2007              ; F1A5 8D 07 20 
    PLA                      ; F1A8 68       
    STA a:$2007              ; F1A9 8D 07 20 
    PLA                      ; F1AC 68       
    STA a:$2007              ; F1AD 8D 07 20 
    DEX                      ; F1B0 CA       
    BNE $f1a4                ; F1B1 D0 F1    
    LDX a:$0170              ; F1B3 AE 70 01 
    TXS                      ; F1B6 9A       

; A17: Shared RTS target; also fallthrough from A16.
; {'bank': '0F', 'cpu': '0xF1B7', 'bank_offset': '0x11B7', 'prg_offset': '0x01F1B7', 'file_offset': '0x01F1C7', 'mapping_condition': 'last bank fixed at E000'}
.org $F1B7
PpuTaskReturn:
    RTS                      ; F1B7 60       

; A18: Read 0143..0162 through PLA; write 32 bytes to PPU; restore SP and service 06EE flag.
; {'bank': '0F', 'cpu': '0xF24B', 'bank_offset': '0x124B', 'prg_offset': '0x01F24B', 'file_offset': '0x01F25B', 'mapping_condition': 'last bank fixed at E000'}
.org $F24B
UploadPalette32ViaStack:
    LDA #$3f                 ; F24B A9 3F    
    STA a:$2006              ; F24D 8D 06 20 
    STY a:$2006              ; F250 8C 06 20 
    TSX                      ; F253 BA       
    STX a:$0170              ; F254 8E 70 01 
    LDX #$42                 ; F257 A2 42    Temporary SP=42 makes PLA read palette bytes starting at 0143.
    TXS                      ; F259 9A       
    LDX #$08                 ; F25A A2 08    
    PLA                      ; F25C 68       
    STA a:$2007              ; F25D 8D 07 20 
    PLA                      ; F260 68       
    STA a:$2007              ; F261 8D 07 20 
    PLA                      ; F264 68       
    STA a:$2007              ; F265 8D 07 20 
    PLA                      ; F268 68       
    STA a:$2007              ; F269 8D 07 20 
    DEX                      ; F26C CA       
    BNE $f25c                ; F26D D0 ED    
    LDA #$3f                 ; F26F A9 3F    
    STA a:$2006              ; F271 8D 06 20 
    LDA #$00                 ; F274 A9 00    
    STA a:$2006              ; F276 8D 06 20 
    STA a:$2006              ; F279 8D 06 20 
    STA a:$2006              ; F27C 8D 06 20 
    LDX a:$0170              ; F27F AE 70 01 Restore the real stack before RTS.
    TXS                      ; F282 9A       
    LDX a:$06ee              ; F283 AE EE 06 
    BEQ $f28d                ; F286 F0 05    
    LDX #$ff                 ; F288 A2 FF    
    STX a:$06ee              ; F28A 8E EE 06 
    RTS                      ; F28D 60       

; A19: Clear PPUMASK and shadows 5F/66; clear bit 1 of 4A.
; {'bank': '0F', 'cpu': '0xF4BA', 'bank_offset': '0x14BA', 'prg_offset': '0x01F4BA', 'file_offset': '0x01F4CA', 'mapping_condition': 'last bank fixed at E000'}
.org $F4BA
DisableRendering:
    LDY #$00                 ; F4BA A0 00    
    STY a:$2001              ; F4BC 8C 01 20 
    STY $5f                  ; F4BF 84 5F    
    STY $66                  ; F4C1 84 66    
    LDA $4a                  ; F4C3 A5 4A    
    AND #$fd                 ; F4C5 29 FD    
    STA $4a                  ; F4C7 85 4A    
    RTS                      ; F4C9 60       

; A20: Save bank tags and registers, map 04EC into A000, call pointer 04EA, restore both PRG windows and result registers/flags.
; {'bank': '0F', 'cpu': '0xF4CA', 'bank_offset': '0x14CA', 'prg_offset': '0x01F4CA', 'file_offset': '0x01F4DA', 'mapping_condition': 'last bank fixed at E000'}
.org $F4CA
FarCallViaA000:
    PHP                      ; F4CA 08       
    PHA                      ; F4CB 48       
    TYA                      ; F4CC 98       
    PHA                      ; F4CD 48       
    TXA                      ; F4CE 8A       
    PHA                      ; F4CF 48       
    LDA a:$9fff              ; F4D0 AD FF 9F Read live bank identity from the final byte of the 8000 window.
    STA a:$04ee              ; F4D3 8D EE 04 
    LDA a:$bfff              ; F4D6 AD FF BF Read live bank identity from the final byte of the A000 window.
    STA a:$04ed              ; F4D9 8D ED 04 
    LDX #$07                 ; F4DC A2 07    
    LDA a:$04ec              ; F4DE AD EC 04 Target A000 bank is supplied through RAM 04EC.
    JSR a:$d6c3              ; F4E1 20 C3 D6 
    PLA                      ; F4E4 68       
    TAX                      ; F4E5 AA       
    PLA                      ; F4E6 68       
    TAY                      ; F4E7 A8       
    PLA                      ; F4E8 68       
    PLP                      ; F4E9 28       
    JSR a:$f50a              ; F4EA 20 0A F5 JSR into an indirect JMP allows the destination RTS to return here.
    PHP                      ; F4ED 08       Preserve callee output registers and flags while restoring mappings.
    PHA                      ; F4EE 48       
    TYA                      ; F4EF 98       
    PHA                      ; F4F0 48       
    TXA                      ; F4F1 8A       
    PHA                      ; F4F2 48       
    LDX #$07                 ; F4F3 A2 07    
    LDA a:$04ed              ; F4F5 AD ED 04 
    JSR a:$d6c3              ; F4F8 20 C3 D6 
    LDX #$06                 ; F4FB A2 06    Restore both R7 and R6, even though entry changes only R7.
    LDA a:$04ee              ; F4FD AD EE 04 
    JSR a:$d6c3              ; F500 20 C3 D6 
    PLA                      ; F503 68       
    TAX                      ; F504 AA       
    PLA                      ; F505 68       
    TAY                      ; F506 A8       
    PLA                      ; F507 68       
    PLP                      ; F508 28       
    RTS                      ; F509 60       

; A21: Indirect JMP through RAM 04EA/04EB; called with JSR to make the callee return to wrapper.
; {'bank': '0F', 'cpu': '0xF50A', 'bank_offset': '0x150A', 'prg_offset': '0x01F50A', 'file_offset': '0x01F51A', 'mapping_condition': 'last bank fixed at E000'}
.org $F50A
FarCallIndirect:
    JMP ($04ea)              ; F50A 6C EA 04 

; A22: Save A/X/Y in E2..E4; acknowledge/disable IRQ, enable again, dispatch through E5/E6.
; {'bank': '0F', 'cpu': '0xF7B1', 'bank_offset': '0x17B1', 'prg_offset': '0x01F7B1', 'file_offset': '0x01F7C1', 'mapping_condition': 'last bank fixed at E000'}
.org $F7B1
IrqEntry:
    STA $e2                  ; F7B1 85 E2    
    STX $e3                  ; F7B3 86 E3    
    STY $e4                  ; F7B5 84 E4    
    LDA #$00                 ; F7B7 A9 00    
    STA a:$e000              ; F7B9 8D 00 E0 
    STA a:$e001              ; F7BC 8D 01 E0 
    JMP ($00e5)              ; F7BF 6C E5 00 IRQ pointer is shared with temporary PPU dispatch pointer E5/E6.

; A23: Timed PPU address/scroll writes indexed by 67; choose terminal split at F0 sentinel; share IRQ return.
; {'bank': '0F', 'cpu': '0xF7C2', 'bank_offset': '0x17C2', 'prg_offset': '0x01F7C2', 'file_offset': '0x01F7D2', 'mapping_condition': 'last bank fixed at E000'}
.org $F7C2
IrqSplitPpuAddress:
    LDA a:$2002              ; F7C2 AD 02 20 
    LDX #$09                 ; F7C5 A2 09    
    DEX                      ; F7C7 CA       
    BNE $f7c7                ; F7C8 D0 FD    
    LDY $67                  ; F7CA A4 67    
    LDA a:$0080,Y            ; F7CC B9 80 00 
    STA a:$c000              ; F7CF 8D 00 C0 
    LDA a:$004b,Y            ; F7D2 B9 4B 00 
    STA a:$2000              ; F7D5 8D 00 20 
    LDA a:$0701,Y            ; F7D8 B9 01 07 
    STA a:$2006              ; F7DB 8D 06 20 
    LDA a:$06fa,Y            ; F7DE B9 FA 06 
    STA a:$2006              ; F7E1 8D 06 20 
    LDA $51                  ; F7E4 A5 51    
    STA a:$2005              ; F7E6 8D 05 20 
    LDA a:$0059,Y            ; F7E9 B9 59 00 
    STA a:$2005              ; F7EC 8D 05 20 
    LDA a:$0081,Y            ; F7EF B9 81 00 
    CMP #$f0                 ; F7F2 C9 F0    
    BNE $f7fe                ; F7F4 D0 08    
    LDA #$3d                 ; F7F6 A9 3D    Switch to terminal split handler F83D when next count is F0.
    STA $e5                  ; F7F8 85 E5    
    LDA #$f8                 ; F7FA A9 F8    
    STA $e6                  ; F7FC 85 E6    
    INC $67                  ; F7FE E6 67    
    JMP a:$f834              ; F800 4C 34 F8 

; A24: Timed indexed scroll/control writes; select F83D on F0 sentinel.
; {'bank': '0F', 'cpu': '0xF803', 'bank_offset': '0x1803', 'prg_offset': '0x01F803', 'file_offset': '0x01F813', 'mapping_condition': 'last bank fixed at E000'}
.org $F803
IrqSplitScroll:
    LDA a:$2002              ; F803 AD 02 20 
    LDX #$09                 ; F806 A2 09    
    DEX                      ; F808 CA       
    BNE $f808                ; F809 D0 FD    
    LDY $67                  ; F80B A4 67    
    LDA a:$007f,Y            ; F80D B9 7F 00 
    STA a:$c000              ; F810 8D 00 C0 
    LDX a:$006a,Y            ; F813 BE 6A 00 
    LDA $4a,X                ; F816 B5 4A    
    ORA #$88                 ; F818 09 88    
    STA a:$2000              ; F81A 8D 00 20 
    LDA $51,X                ; F81D B5 51    
    STA a:$2005              ; F81F 8D 05 20 
    LDA $58                  ; F822 A5 58    
    STA a:$2005              ; F824 8D 05 20 
    LDA a:$0080,Y            ; F827 B9 80 00 
    CMP #$f0                 ; F82A C9 F0    
    BNE $f832                ; F82C D0 04    
    LDA #$3d                 ; F82E A9 3D    Only low pointer byte changes; high byte F8 is a caller/state precondition.
    STA $e5                  ; F830 85 E5    
    INC $67                  ; F832 E6 67    

; A25: Increment A6, restore Y/X/A from E4/E3/E2, RTI.
; {'bank': '0F', 'cpu': '0xF834', 'bank_offset': '0x1834', 'prg_offset': '0x01F834', 'file_offset': '0x01F844', 'mapping_condition': 'last bank fixed at E000'}
.org $F834
IrqRestoreRegisters:
    INC $a6                  ; F834 E6 A6    
    LDY $e4                  ; F836 A4 E4    
    LDX $e3                  ; F838 A6 E3    
    LDA $e2                  ; F83A A5 E2    
    RTI                      ; F83C 40       

; A26: Timed split setting control, mask, address and CHR registers 0/1 to 0/2; set next IRQ low pointer 82.
; {'bank': '0F', 'cpu': '0xF83D', 'bank_offset': '0x183D', 'prg_offset': '0x01F83D', 'file_offset': '0x01F84D', 'mapping_condition': 'last bank fixed at E000'}
.org $F83D
IrqSplitSwitchChr01:
    LDA a:$2002              ; F83D AD 02 20 
    LDX #$09                 ; F840 A2 09    
    DEX                      ; F842 CA       
    BNE $f842                ; F843 D0 FD    
    LDA #$15                 ; F845 A9 15    
    STA a:$c000              ; F847 8D 00 C0 
    LDA #$89                 ; F84A A9 89    
    STA a:$2000              ; F84C 8D 00 20 
    LDA $66                  ; F84F A5 66    
    STA a:$2001              ; F851 8D 01 20 
    LDA #$27                 ; F854 A9 27    
    STA a:$2006              ; F856 8D 06 20 
    LDA #$60                 ; F859 A9 60    
    STA a:$2006              ; F85B 8D 06 20 
    STX a:$2005              ; F85E 8E 05 20 
    STX a:$2005              ; F861 8E 05 20 
    STX a:$8000              ; F864 8E 00 80 X=0 after delay loop; select CHR R0 and set it to 00.
    STX a:$8001              ; F867 8E 01 80 
    INX                      ; F86A E8       
    STX a:$03d8              ; F86B 8E D8 03 
    STX a:$8000              ; F86E 8E 00 80 
    INX                      ; F871 E8       
    STX a:$8001              ; F872 8E 01 80 
    LDA #$82                 ; F875 A9 82    Only pointer low byte changes to 82; high F8 must already be set.
    STA $e5                  ; F877 85 E5    
    INC $a6                  ; F879 E6 A6    
    LDY $e4                  ; F87B A4 E4    
    LDX $e3                  ; F87D A6 E3    
    LDA $e2                  ; F87F A5 E2    
    RTI                      ; F881 40       

; A27: Little-endian NMI, RESET and IRQ/BRK vectors in the fixed final bank.
; {'bank': '0F', 'cpu': '0xFFFA', 'bank_offset': '0x1FFA', 'prg_offset': '0x01FFFA', 'file_offset': '0x02000A', 'mapping_condition': 'last bank fixed at E000'}
.org $FFFA
InterruptVectors:
    .byte $BB,$F0,$10,$F0,$B1,$F7

