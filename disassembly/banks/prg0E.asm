; PRG bank 0E; CPU base used here is $C000.
; For unreviewed banks, the base is a scaffold convention, not a recovered mapping.
.segment "PRG0E"
.org $C000
    .incbin "inputs/original.nes", $01C010, $0746 ; UNINTERPRETED preserved bytes

; D34: Tail JMP D8B5 in fixed bank0E.
AddScoreService:
    JMP a:$d8b5              ; C746 

; B01: 42 absolute JMP service entries; this identifies destinations, not all destination semantics.
FixedServiceJumpTable:
    JMP a:$d62d              ; C749 
    JMP a:$d90c              ; C74C 
    JMP a:$d63b              ; C74F 
    JMP a:$d65d              ; C752 
    JMP a:$d677              ; C755 
    JMP a:$d6a0              ; C758 
    JMP a:$d9e8              ; C75B 
    JMP a:$da07              ; C75E 
    JMP a:$dab3              ; C761 
    JMP a:$dac2              ; C764 
    JMP a:$db02              ; C767 
    JMP a:$d6c3              ; C76A 
    JMP a:$ddd9              ; C76D 
    JMP a:$ddeb              ; C770 
    JMP a:$dbb7              ; C773 
    JMP a:$dc1c              ; C776 
    JMP a:$d9d7              ; C779 
    JMP a:$d481              ; C77C 
    JMP a:$cfe2              ; C77F 
    JMP a:$e0ff              ; C782 
    JMP a:$e105              ; C785 
    JMP a:$e154              ; C788 
    JMP a:$e15e              ; C78B 
    JMP a:$dfcb              ; C78E 
    JMP a:$df37              ; C791 
    JMP a:$e08d              ; C794 
    JMP a:$e1a0              ; C797 
    JMP a:$e0ed              ; C79A 
    JMP a:$d1aa              ; C79D 
    JMP a:$e2f9              ; C7A0 
    JMP a:$e35b              ; C7A3 
    JMP a:$e393              ; C7A6 
    JMP a:$e44e              ; C7A9 
    JMP a:$e764              ; C7AC 
    JMP a:$e860              ; C7AF 
    JMP a:$e8c3              ; C7B2 
    JMP a:$e925              ; C7B5 
    JMP a:$eb1e              ; C7B8 
    JMP a:$eb63              ; C7BB 
    JMP a:$d7e7              ; C7BE 
    JMP a:$e3fe              ; C7C1 
    JMP a:$e279              ; C7C4 
    .incbin "inputs/original.nes", $01C7D7, $04BD ; UNINTERPRETED preserved bytes

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
    .incbin "inputs/original.nes", $01CCD9, $0287 ; UNINTERPRETED preserved bytes

; B02: Map bank 09 at A000, initialize audio and call front end; carry clear loops via A00C.
BootFrontEndLoop:
    LDA #$ff                 ; CF50 
    STA a:$0713              ; CF52 
    JSR a:$f4ba              ; CF55 
    LDX #$07                 ; CF58 
    LDA #$09                 ; CF5A 
    JSR a:$d6c3              ; CF5C 
    JMP a:$cf65              ; CF5F First front-end iteration bypasses A00C. R7 has just been set to 09.
    JSR a:$a00c              ; CF62 
    JSR a:$cc84              ; CF65 
    JSR a:$a009              ; CF68 
    BCC $cf62                ; CF6B Carry is an interface result, not a global state ID.

; B03: Clear 00/2D; nonzero 2C calls bank 07 A0D8 and chooses resume path using 43.
SelectInitialRoute:
    LDA #$00                 ; CF6D 
    STA $00                  ; CF6F 
    STA $2d                  ; CF71 
    LDA $2c                  ; CF73 
    BEQ $cfa2                ; CF75 
    LDA #$07                 ; CF77 
    TAX                      ; CF79 
    JSR a:$d6c3              ; CF7A 
    JSR a:$a0d8              ; CF7D 
    JSR a:$ebc7              ; CF80 
    LDA $43                  ; CF83 
    BNE $cfa2                ; CF85 
    LDA #$0c                 ; CF87 
    STA a:$06bd              ; CF89 
    STA a:$06c0              ; CF8C 
    STA a:$06c1              ; CF8F 
    JSR a:$d36d              ; CF92 
    JSR a:$d37f              ; CF95 
    LDX #$07                 ; CF98 
    LDA #$09                 ; CF9A 
    JSR a:$d6c3              ; CF9C 
    JMP a:$d21c              ; CF9F 

; B04: Mask 2C to five-bit index 9A and 2D to two-bit 030C; save SP at 016F and invoke initialization.
InitializeRunContext:
    LDA $2c                  ; CFA2 
    AND #$1f                 ; CFA4 
    STA $9a                  ; CFA6 
    LDA $2d                  ; CFA8 
    AND #$03                 ; CFAA 
    STA a:$030c              ; CFAC 
    JSR a:$d90c              ; CFAF 
    JSR a:$d64e              ; CFB2 
    TSX                      ; CFB5 
    STX a:$016f              ; CFB6 A later TXS at CFE8 abandons intervening call frames.
    JSR a:$e154              ; CFB9 
    LDX #$07                 ; CFBC 
    LDA #$09                 ; CFBE 
    JSR a:$d6c3              ; CFC0 
    JSR a:$a006              ; CFC3 
    JSR a:$eea7              ; CFC6 
    LDA #$00                 ; CFC9 
    STA a:$030e              ; CFCB 
    JSR a:$d2f7              ; CFCE 
    LDA #$0c                 ; CFD1 
    STA a:$06bd              ; CFD3 
    STA a:$06c0              ; CFD6 
    STA a:$06c1              ; CFD9 
    JSR a:$d36d              ; CFDC 
    JSR a:$d37f              ; CFDF 
    JSR a:$d29f              ; CFE2 

; B05: Restore saved SP; initialize PPU shadows, IRQ source F83D, loop flags and per-index audio byte.
PrepareMainLoop:
    LDX a:$016f              ; CFE5 
    TXS                      ; CFE8 
    LDA $4a                  ; CFE9 
    AND #$fe                 ; CFEB 
    ORA #$20                 ; CFED 
    STA $4a                  ; CFEF 
    LSR $4a                  ; CFF1 
    LDA $a8                  ; CFF3 
    LSR A                    ; CFF5 
    ROL $4a                  ; CFF6 
    LDA $a7                  ; CFF8 
    STA $51                  ; CFFA 
    LDY $a9                  ; CFFC 
    LDA $aa                  ; CFFE 
    JSR a:$f78b              ; D000 
    STA $58                  ; D003 
    LDA #$d0                 ; D005 
    STA $7f                  ; D007 
    LDA #$3d                 ; D009 
    STA $dc                  ; D00B 
    LDA #$f8                 ; D00D 
    STA $dd                  ; D00F 
    LDA #$41                 ; D011 
    STA $a1                  ; D013 
    LDX #$00                 ; D015 
    STX $a0                  ; D017 
    STX $68                  ; D019 
    STX $d8                  ; D01B 
    STX a:$03d6              ; D01D 
    STX a:$03d5              ; D020 
    INX                      ; D023 
    STX $96                  ; D024 
    LDA #$04                 ; D026 
    STA a:$0047              ; D028 
    JSR a:$e1c8              ; D02B 
    JSR a:$e0ff              ; D02E 
    LDX $9a                  ; D031 
    LDA a:$fe4c,X            ; D033 
    STA $00                  ; D036 
    STA a:$04e1              ; D038 
    LDA #$ff                 ; D03B 
    STA $d9                  ; D03D 
    LDA #$00                 ; D03F 
    STA $da                  ; D041 
    STA a:$06ee              ; D043 

; B06: Four D90C-synchronized phases; phase-specific call order and two D9CB mixer calls per cycle.
FourPhaseMainLoop:
    LDX $9a                  ; D046 Four-phase cycle entry. 9A indexes data, not this control-flow phase.
    LDA a:$fe2c,X            ; D048 
    STA a:$04ef              ; D04B 
    JSR a:$d90c              ; D04E 
    JSR a:$d0b7              ; D051 
    JSR a:$d0ba              ; D054 
    JSR a:$d0dc              ; D057 
    JSR a:$d0d2              ; D05A 
    JSR a:$d107              ; D05D 
    JSR a:$d63b              ; D060 
    JSR a:$d110              ; D063 
    JSR a:$d90c              ; D066 
    JSR a:$d0b7              ; D069 
    JSR a:$d0ba              ; D06C 
    JSR a:$d0f3              ; D06F 
    JSR a:$d0d2              ; D072 
    JSR a:$d107              ; D075 
    JSR a:$d63b              ; D078 
    JSR a:$d9cb              ; D07B Mixer after phase 1; X is whatever preceding calls leave.
    JSR a:$d110              ; D07E 
    JSR a:$d90c              ; D081 
    JSR a:$d0b7              ; D084 
    JSR a:$d0ba              ; D087 
    JSR a:$d0dc              ; D08A 
    JSR a:$d107              ; D08D 
    JSR a:$d0d2              ; D090 
    JSR a:$d63b              ; D093 
    JSR a:$d110              ; D096 
    JSR a:$d90c              ; D099 
    JSR a:$d0b7              ; D09C 
    JSR a:$d0ba              ; D09F 
    JSR a:$d0f3              ; D0A2 
    JSR a:$d107              ; D0A5 
    JSR a:$d0d2              ; D0A8 
    JSR a:$d63b              ; D0AB 
    JSR a:$d9cb              ; D0AE Second explicit mixer call after phase 3.
    JSR a:$d110              ; D0B1 
    JMP a:$d046              ; D0B4 

; B07: Tail jump to CE/D3/Start control gate D39F.
RunControlGate:
    JMP a:$d39f              ; D0B7 

; B08: Map 03B9 through R6 and 08 through R7; call A006,A000 then tail A009; later targets need callee bank-preservation contract.
CallBank08FrameGroup:
    LDX #$06                 ; D0BA 
    LDA a:$03b9              ; D0BC 
    JSR a:$d6c3              ; D0BF 
    LDX #$07                 ; D0C2 
    LDA #$08                 ; D0C4 
    JSR a:$d6c3              ; D0C6 
    JSR a:$a006              ; D0C9 
    JSR a:$a000              ; D0CC 
    JMP a:$a009              ; D0CF 

; B09: Map R7=09 and tail jump to A000.
TailBank09Frame:
    LDX #$07                 ; D0D2 
    LDA #$09                 ; D0D4 
    JSR a:$d6c3              ; D0D6 
    JMP a:$a000              ; D0D9 

; B10: Map R6 from 03B9 and R7=07; call A078,A07E then tail A0B1.
CallBank07EvenGroup:
    LDX #$06                 ; D0DC 
    LDA a:$03b9              ; D0DE 
    JSR a:$d6c3              ; D0E1 
    LDA #$07                 ; D0E4 
    TAX                      ; D0E6 
    JSR a:$d6c3              ; D0E7 
    JSR a:$a078              ; D0EA 
    JSR a:$a07e              ; D0ED 
    JMP a:$a0b1              ; D0F0 

; B11: Map R6 from 03B9 and R7=07; call A07B then tail A0B1.
CallBank07OddGroup:
    LDX #$06                 ; D0F3 
    LDA a:$03b9              ; D0F5 
    JSR a:$d6c3              ; D0F8 
    LDA #$07                 ; D0FB 
    TAX                      ; D0FD 
    JSR a:$d6c3              ; D0FE 
    JSR a:$a07b              ; D101 
    JMP a:$a0b1              ; D104 

; B12: Call bank-0C trampoline D6D2, fixed D805, then tail D6F0; gameplay meanings unresolved.
CallBank0CAndFixedGroup:
    JSR a:$d6d2              ; D107 
    JSR a:$d805              ; D10A 
    JMP a:$d6f0              ; D10D 

; B13: Service palette effect, map R6=06/R7=08, call A00C, then tail E2E2 scroll adjustment.
FinalizeFrameGroup:
    JSR a:$e2a3              ; D110 
    LDA #$06                 ; D113 
    TAX                      ; D115 
    JSR a:$d6c3              ; D116 
    LDX #$07                 ; D119 
    LDA #$08                 ; D11B 
    JSR a:$d6c3              ; D11D 
    JSR a:$a00c              ; D120 
    JMP a:$e2e2              ; D123 
    .incbin "inputs/original.nes", $01D136, $0052 ; UNINTERPRETED preserved bytes

; B14: Entry D178 pushes zero; D17A can accept one from CE route; remap 9A with D25F, initialize, restore block and choose D21C/D225.
RestartThroughIndexTable:
    LDA #$00                 ; D178 
    PHA                      ; D17A 
    LDY $9a                  ; D17B 
    LDA a:$d25f,Y            ; D17D 
    STA $9a                  ; D180 
    JSR a:$d2f7              ; D182 
    JSR a:$d396              ; D185 
    LDA #$07                 ; D188 
    TAX                      ; D18A 
    JSR a:$d6c3              ; D18B 
    JSR a:$a0d2              ; D18E 
    PLA                      ; D191 
    BNE $d197                ; D192 
    JMP a:$d21c              ; D194 
    JMP a:$d225              ; D197 

; B15: Remap 9A through D27F, reset fields, restore saved eleven-byte block, then jump D21C.
ContinueThroughIndexTable:
    LDY $9a                  ; D19A 
    LDA a:$d27f,Y            ; D19C 
    STA $9a                  ; D19F 
    JSR a:$d2f7              ; D1A1 
    JSR a:$d38b              ; D1A4 
    JMP a:$d21c              ; D1A7 

; B16: Load next index from D23F; FF invokes bank-09 A012 and increments 030C unless equal 03; restart at index 00.
AdvanceThroughIndexTable:
    JSR a:$e154              ; D1AA 
    LDA #$00                 ; D1AD 
    STA $00                  ; D1AF 
    LDA #$c0                 ; D1B1 
    STA $01                  ; D1B3 
    JSR a:$d36d              ; D1B5 
    JSR a:$d37f              ; D1B8 
    LDY $9a                  ; D1BB 
    LDA a:$d23f,Y            ; D1BD 
    CMP #$ff                 ; D1C0 Only FF selects end-of-cycle path; no stage-name assignment.
    BNE $d1fd                ; D1C2 
    LDX #$07                 ; D1C4 
    LDA #$09                 ; D1C6 
    JSR a:$d6c3              ; D1C8 
    JSR a:$a012              ; D1CB 
    LDA a:$030c              ; D1CE 
    CMP #$03                 ; D1D1 
    BEQ $d1d8                ; D1D3 Equal-to-03 guard, not a general clamp of arbitrary corrupt values.
    INC a:$030c              ; D1D5 
    LDA a:$030c              ; D1D8 
    CMP #$03                 ; D1DB 
    BCC $d1ed                ; D1DD 
    LDX #$07                 ; D1DF 
    LDA #$08                 ; D1E1 
    JSR a:$d6c3              ; D1E3 
    LDA #$00                 ; D1E6 
    STA $2d                  ; D1E8 
    JSR a:$a00f              ; D1EA 
    JSR a:$d2f7              ; D1ED 
    JSR a:$d36d              ; D1F0 
    JSR a:$d37f              ; D1F3 
    LDA #$0c                 ; D1F6 
    STA a:$06bd              ; D1F8 
    LDA #$00                 ; D1FB 
    STA $9a                  ; D1FD 
    JSR a:$ed80              ; D1FF 
    LDA $9a                  ; D202 
    BNE $d210                ; D204 
    LDX #$07                 ; D206 
    LDA #$09                 ; D208 
    JSR a:$d6c3              ; D20A 
    JSR a:$a006              ; D20D 

; B17: Clear bit 20 of F8, call EEA7 and reenter CFE2, or fall through to restore path at D225.
ReenterSceneClearFlag:
    LDA $f8                  ; D210 
    AND #$df                 ; D212 
    STA $f8                  ; D214 
    JSR a:$eea7              ; D216 
    JMP a:$cfe2              ; D219 
    LDA $f8                  ; D21C 
    AND #$df                 ; D21E 
    STA $f8                  ; D220 
    JSR a:$eea7              ; D222 

; B18: Index FDE0 with D3&07; copy byte to 06B9/06BA/06BB; jump CFE2. Gameplay meaning is not assigned here.
RestoreTripletAndReenter:
    LDA $f8                  ; D225 
    AND #$df                 ; D227 
    STA $f8                  ; D229 
    LDA $d3                  ; D22B 
    AND #$07                 ; D22D 
    TAY                      ; D22F 
    LDA a:$fde0,Y            ; D230 Table bytes independently observed; HP semantics deliberately not imported from user notes.
    STA a:$06b9              ; D233 
    STA a:$06ba              ; D236 
    STA a:$06bb              ; D239 
    JMP a:$cfe2              ; D23C 

; B19: 32-byte successor table; index 1B contains FF end-of-cycle marker.
NextSceneIndexTable:
    .byte $01,$0B,$03,$07,$05,$06,$07,$08,$09,$0A,$0C,$04,$0D,$0E,$10,$10
    .byte $11,$12,$13,$14,$15,$16,$18,$1C,$19,$17,$1B,$FF,$1D,$1E,$1F,$1A

; B20: 32-byte table used by D178 and D363; physical-stage correspondence unresolved.
RestartSceneIndexTable:
    .byte $00,$01,$02,$03,$04,$05,$06,$06,$08,$09,$0A,$0B,$0C,$0D,$0E,$0C
    .byte $10,$11,$12,$12,$14,$15,$16,$17,$18,$19,$1F,$1B,$1C,$1D,$1D,$1F

; B21: 32-byte table used by D19A; physical-stage correspondence unresolved.
ContinueSceneIndexTable:
    .byte $00,$00,$08,$08,$04,$04,$04,$04,$08,$08,$08,$00,$0C,$0C,$0C,$0C
    .byte $10,$10,$10,$10,$14,$14,$14,$18,$18,$18,$1C,$1C,$1C,$1C,$1C,$1C

; C56: Map scene bank and R7=08 for player initialization, then R7=07 for scene setup; preserve unresolved callee boundaries.
InitializeSceneBankedServices:
    JSR a:$d62d              ; D29F 
    LDX #$06                 ; D2A2 
    LDA a:$03b9              ; D2A4 
    JSR a:$d6c3              ; D2A7 
    LDX #$07                 ; D2AA 
    LDA #$08                 ; D2AC 
    JSR a:$d6c3              ; D2AE 
    JSR a:$a003              ; D2B1 
    LDA #$00                 ; D2B4 
    STA a:$03d4              ; D2B6 
    STA a:$03be              ; D2B9 
    JSR a:$d6dc              ; D2BC 
    LDA a:$00f8              ; D2BF 
    AND #$df                 ; D2C2 
    STA a:$00f8              ; D2C4 
    LDA #$07                 ; D2C7 
    TAX                      ; D2C9 
    JSR a:$d6c3              ; D2CA 
    JSR a:$a0ba              ; D2CD 
    LDX #$07                 ; D2D0 
    TXA                      ; D2D2 
    JSR a:$d6c3              ; D2D3 
    JSR a:$a081              ; D2D6 
    LDA #$04                 ; D2D9 
    STA $47                  ; D2DB 
    JSR a:$d2ec              ; D2DD 
    LDA #$ff                 ; D2E0 
    STA a:$04e2              ; D2E2 
    JSR a:$a087              ; D2E5 
    JSR a:$a0c3              ; D2E8 
    RTS                      ; D2EB 
    LDA #$00                 ; D2EC 
    LDX #$11                 ; D2EE 
    STA a:$057f,X            ; D2F0 
    DEX                      ; D2F3 
    BNE $d2f0                ; D2F4 
    RTS                      ; D2F6 

; B22: Reset selected fields; if 030E is zero set it to 03 and initialize 0306..030B; set digit-like buffers and call F65F.
ResetRunFields:
    LDA #$00                 ; D2F7 
    STA $a1                  ; D2F9 
    STA $d3                  ; D2FB 
    STA $96                  ; D2FD 
    STA a:$06be              ; D2FF 
    STA a:$06bf              ; D302 
    STA a:$057f              ; D305 
    LDA #$ff                 ; D308 
    STA $b8                  ; D30A 
    LDA a:$fde0              ; D30C 
    STA a:$06b9              ; D30F 
    STA a:$06ba              ; D312 
    STA a:$06bb              ; D315 
    LDA a:$030e              ; D318 
    BNE $d33a                ; D31B 
    STA a:$030f              ; D31D 
    LDA #$0c                 ; D320 
    STA a:$06bd              ; D322 
    STA a:$06c0              ; D325 
    STA a:$06c1              ; D328 
    LDA #$03                 ; D32B 
    STA a:$030e              ; D32D 
    LDA #$20                 ; D330 
    LDX #$05                 ; D332 
    STA a:$0306,X            ; D334 
    DEX                      ; D337 
    BPL $d334                ; D338 
    LDA #$60                 ; D33A 
    LDX #$04                 ; D33C 
    STA $ec,X                ; D33E This loop initializes overlapping buffers; 60/61 alone does not prove complete numeric encoding.
    STA $e9,X                ; D340 
    DEX                      ; D342 
    BNE $d33e                ; D343 
    LDA #$61                 ; D345 
    STA $f4                  ; D347 
    LDA #$60                 ; D349 
    LDX #$03                 ; D34B 
    STA $f0,X                ; D34D 
    DEX                      ; D34F 
    BNE $d34d                ; D350 
    LDA #$61                 ; D352 
    STA $f7                  ; D354 
    LDA #$60                 ; D356 
    LDX #$02                 ; D358 
    STA $f4,X                ; D35A 
    DEX                      ; D35C 
    BNE $d35a                ; D35D 
    JSR a:$f65f              ; D35F 
    RTS                      ; D362 
    .incbin "inputs/original.nes", $01D373, $001C ; UNINTERPRETED preserved bytes

; B23: Copy 06C2..06CC to 06CD..06D7, high index first.
SaveElevenByteBlock:
    LDX #$0a                 ; D37F 
    LDA a:$06c2,X            ; D381 
    STA a:$06cd,X            ; D384 
    DEX                      ; D387 
    BPL $d381                ; D388 
    RTS                      ; D38A 

; B24: Copy 06CD..06D7 to 06C2..06CC, high index first; fall through D396.
RestoreElevenByteBlock:
    LDX #$0a                 ; D38B 
    LDA a:$06cd,X            ; D38D 
    STA a:$06c2,X            ; D390 
    DEX                      ; D393 
    BPL $d38d                ; D394 

; B25: Map R7=07 and tail A0C9.
TailBank07Restore:
    LDA #$07                 ; D396 
    TAX                      ; D398 
    JSR a:$d6c3              ; D399 
    JMP a:$a0c9              ; D39C 

; B26: Negative CE decrements 030E and selects D17A/D487; otherwise negative D3 blocks Start, and pressed Start enters D3C4.
CheckRunControl:
    LDA $ce                  ; D39F 
    BMI $d3ae                ; D3A1 
    LDA $d3                  ; D3A3 
    BMI $d3ad                ; D3A5 
    LDA $1f                  ; D3A7 1F contains newly pressed buttons after D90C.
    AND #$10                 ; D3A9 
    BNE $d3c4                ; D3AB 
    RTS                      ; D3AD 
    JSR a:$e154              ; D3AE 
    LDA #$c0                 ; D3B1 
    STA $01                  ; D3B3 
    STA $00                  ; D3B5 
    DEC a:$030e              ; D3B7 030E precondition is nonzero; zero would wrap to FF here.
    BEQ $d3c1                ; D3BA 
    LDA #$01                 ; D3BC 
    JMP a:$d17a              ; D3BE 
    JMP a:$d487              ; D3C1 

; B27: Save palette and CHR 47/48; invoke bank-07 overlay entries; restore palette/CHR, discard return word and jump D046.
StartOverlayFlow:
    LDA #$00                 ; D3C4 
    STA $a1                  ; D3C6 
    LDA #$f7                 ; D3C8 
    STA $01                  ; D3CA 
    JSR a:$d62d              ; D3CC 
    LDA #$07                 ; D3CF 
    TAX                      ; D3D1 
    JSR a:$d6c3              ; D3D2 
    LDA $47                  ; D3D5 
    PHA                      ; D3D7 
    LDA $48                  ; D3D8 
    PHA                      ; D3DA 
    LDX #$1f                 ; D3DB 
    LDA a:$0143,X            ; D3DD 
    STA a:$0123,X            ; D3E0 
    DEX                      ; D3E3 
    BPL $d3dd                ; D3E4 
    LDX #$0f                 ; D3E6 
    LDA a:$0133,X            ; D3E8 
    PHA                      ; D3EB 
    LDA a:$0153,X            ; D3EC 
    PHA                      ; D3EF 
    LDA a:$d459,X            ; D3F0 
    STA a:$0153,X            ; D3F3 
    STA a:$0133,X            ; D3F6 
    DEX                      ; D3F9 
    BPL $d3e8                ; D3FA 
    TXA                      ; D3FC 
    JSR a:$e15e              ; D3FD 
    JSR a:$d5f0              ; D400 
    JSR a:$a0b7              ; D403 
    LDA #$0f                 ; D406 
    JSR a:$e105              ; D408 
    LDA #$1e                 ; D40B 
    STA $66                  ; D40D 
    JSR a:$a0b4              ; D40F 
    LDA #$0f                 ; D412 
    JSR a:$e15e              ; D414 
    JSR a:$d62d              ; D417 
    LDX #$00                 ; D41A 
    PLA                      ; D41C 
    STA a:$0153,X            ; D41D 
    PLA                      ; D420 
    STA a:$0133,X            ; D421 
    INX                      ; D424 
    CPX #$10                 ; D425 
    BNE $d41c                ; D427 
    LDA a:$06bd              ; D429 
    CMP #$08                 ; D42C 
    BEQ $d439                ; D42E 
    LDA a:$ffb5              ; D430 
    STA a:$0158              ; D433 
    STA a:$0138              ; D436 
    LDA #$ff                 ; D439 
    JSR a:$e105              ; D43B 
    PLA                      ; D43E 
    STA $48                  ; D43F 
    PLA                      ; D441 
    STA $47                  ; D442 
    LDA #$00                 ; D444 
    STA a:$03d6              ; D446 
    INC $a1                  ; D449 
    LDY $a9                  ; D44B 
    LDA $aa                  ; D44D 
    JSR a:$f78b              ; D44F 
    STA $58                  ; D452 
    PLA                      ; D454 Discard the D0B7 caller return word, then restart the four-phase cycle.
    PLA                      ; D455 
    JMP a:$d046              ; D456 

; B28: 16 palette bytes copied to 0133..0142 and 0153..0162 during Start overlay.
OverlayPalette16:
    .byte $0F,$29,$19,$0F,$0F,$26,$16,$0F,$0F,$24,$04,$0F,$0F,$30,$18,$0F
    .incbin "inputs/original.nes", $01D479, $001E ; UNINTERPRETED preserved bytes

; B29: Initialize PPU layout, retained-field displays and two-choice selection after 030E reaches zero.
InitializeCounterZeroMenu:
    JSR a:$d62d              ; D487 
    JSR a:$d5f0              ; D48A 
    LDA #$00                 ; D48D 
    LDY #$05                 ; D48F 
    STA a:$0044,Y            ; D491 
    DEY                      ; D494 
    BPL $d491                ; D495 
    STA $58                  ; D497 
    STA $51                  ; D499 
    STA $6a                  ; D49B 
    LDA $4a                  ; D49D 
    AND #$dc                 ; D49F 
    STA $4a                  ; D4A1 
    LDA #$ec                 ; D4A3 
    STA $7f                  ; D4A5 
    LDA #$82                 ; D4A7 
    STA $dc                  ; D4A9 
    LDA #$f8                 ; D4AB 
    STA $dd                  ; D4AD 
    LDA #$00                 ; D4AF 
    STA $68                  ; D4B1 
    JSR a:$f47c              ; D4B3 
    LDX #$21                 ; D4B6 
    LDY #$4d                 ; D4B8 
    LDA #$b2                 ; D4BA 
    STA $22                  ; D4BC 
    LDA #$d5                 ; D4BE 
    STA $23                  ; D4C0 
    JSR a:$f3d0              ; D4C2 
    LDX #$21                 ; D4C5 
    LDY #$8d                 ; D4C7 
    LDA #$bb                 ; D4C9 
    STA $22                  ; D4CB 
    LDA #$d5                 ; D4CD 
    STA $23                  ; D4CF 
    JSR a:$f3d0              ; D4D1 
    LDX #$21                 ; D4D4 
    LDY #$cd                 ; D4D6 
    LDA #$c3                 ; D4D8 
    STA $22                  ; D4DA 
    LDA #$d5                 ; D4DC 
    STA $23                  ; D4DE 
    JSR a:$f3d0              ; D4E0 
    LDX #$22                 ; D4E3 
    LDY #$ab                 ; D4E5 
    LDA #$c6                 ; D4E7 
    STA $22                  ; D4E9 
    LDA #$d5                 ; D4EB 
    STA $23                  ; D4ED 
    JSR a:$f3d0              ; D4EF 
    LDA #$06                 ; D4F2 
    STA $22                  ; D4F4 
    LDA #$03                 ; D4F6 
    STA $23                  ; D4F8 
    LDX #$22                 ; D4FA 
    LDY #$b1                 ; D4FC 
    JSR a:$f3ef              ; D4FE 
    LDX #$22                 ; D501 
    LDY #$eb                 ; D503 
    LDA #$cb                 ; D505 
    STA $22                  ; D507 
    LDA #$d5                 ; D509 
    STA $23                  ; D50B 
    JSR a:$f3d0              ; D50D 
    LDA #$00                 ; D510 
    STA $22                  ; D512 
    LDA #$03                 ; D514 
    STA $23                  ; D516 
    LDX #$22                 ; D518 
    LDY #$f1                 ; D51A 
    JSR a:$f3ef              ; D51C 
    LDA #$d0                 ; D51F 
    STA $22                  ; D521 
    LDA #$d5                 ; D523 
    STA $23                  ; D525 
    JSR a:$d6a0              ; D527 
    LDA #$00                 ; D52A 
    STA $2c                  ; D52C 
    JSR a:$e0ff              ; D52E 
    LDA #$03                 ; D531 
    STA $00                  ; D533 

; B30: Wait/poll; A/B/Start confirm, Up/Down/Select change 2C, draw cursor and repeat.
CounterZeroMenuLoop:
    JSR a:$d90c              ; D535 
    LDA #$00                 ; D538 
    STA $99                  ; D53A 
    LDA $1f                  ; D53C 
    TAY                      ; D53E 
    AND #$d0                 ; D53F Mask D0 = A, B, Start under verified serial-to-bit mapping.
    BNE $d588                ; D541 
    LDX $2c                  ; D543 
    TYA                      ; D545 
    LSR A                    ; D546 
    LSR A                    ; D547 
    LSR A                    ; D548 
    BCC $d554                ; D549 
    CPX #$01                 ; D54B 
    BEQ $d554                ; D54D 
    LDY #$39                 ; D54F 
    STY $01                  ; D551 
    INX                      ; D553 
    LSR A                    ; D554 
    BCC $d560                ; D555 
    CPX #$00                 ; D557 
    BEQ $d560                ; D559 
    DEX                      ; D55B 
    LDY #$39                 ; D55C 
    STY $01                  ; D55E 
    LSR A                    ; D560 
    LSR A                    ; D561 
    BCC $d56c                ; D562 
    TXA                      ; D564 
    EOR #$01                 ; D565 
    TAX                      ; D567 
    LDY #$39                 ; D568 
    STY $01                  ; D56A 
    TXA                      ; D56C 
    STA $2c                  ; D56D 
    ASL A                    ; D56F 
    TAY                      ; D570 
    LDA a:$d5ae,Y            ; D571 
    STA $22                  ; D574 
    LDA a:$d5af,Y            ; D576 
    STA $23                  ; D579 
    LDA #$2d                 ; D57B 
    LDX #$00                 ; D57D 
    JSR a:$d677              ; D57F 
    JSR a:$d63b              ; D582 
    JMP a:$d535              ; D585 

; B31: Choice 00 jumps D19A; nonzero restores block and ED80 then JMP through RESET vector.
CounterZeroMenuConfirm:
    LDA #$37                 ; D588 
    STA $01                  ; D58A 
    JSR a:$d62d              ; D58C 
    JSR a:$e154              ; D58F 
    LDA #$00                 ; D592 
    STA $00                  ; D594 
    STA $01                  ; D596 
    JSR a:$d90c              ; D598 
    LDA $2c                  ; D59B 
    BNE $d5a2                ; D59D 
    JMP a:$d19a              ; D59F 
    JSR a:$d38b              ; D5A2 
    JSR a:$ed80              ; D5A5 
    JSR a:$d90c              ; D5A8 
    JMP ($fffc)              ; D5AB Indirect JMP loads the supplied ROM reset vector F010.

; B32: Two little-endian cursor pointers selected with 2C*2; pointed data not interpreted.
CounterZeroCursorPointers:
    .byte $5E,$5C,$6E,$5C
    .incbin "inputs/original.nes", $01D5C2, $005A ; UNINTERPRETED preserved bytes

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

; F25: Map R7=0D; clear0440; odd D8 ticks quake counter; walk one of two ten-entry cycles from D8 low3; copy0440 to06BC. D759 and accumulator producer remain unreviewed;0440 aliases indexed HP slot9.
ScheduleEnemyUpdatePass:
    LDX #$07                 ; D6F0 
    LDA #$0d                 ; D6F2 
    JSR a:$d6c3              ; D6F4 
    LDA #$00                 ; D6F7 
    STA a:$0440              ; D6F9 
    LDA $d8                  ; D6FC 
    AND #$01                 ; D6FE 
    STA a:$06f9              ; D700 
    BEQ $d708                ; D703 
    JSR a:$d7ad              ; D705 
    LDA $d8                  ; D708 
    AND #$0f                 ; D70A 
    CMP #$08                 ; D70C 
    BCC $d713                ; D70E 
    SEC                      ; D710 
    SBC #$08                 ; D711 
    STA $2c                  ; D713 
    STA $3b                  ; D715 
    TAX                      ; D717 
    LDA $d8                  ; D718 
    AND #$01                 ; D71A 
    BNE $d72f                ; D71C 
    JSR a:$d759              ; D71E 
    LDY $2c                  ; D721 
    LDA a:$d745,Y            ; D723 
    STA $2c                  ; D726 
    TAX                      ; D728 
    CPX $3b                  ; D729 
    BNE $d71e                ; D72B 
    BEQ $d73e                ; D72D 
    JSR a:$d759              ; D72F 
    LDY $2c                  ; D732 
    LDA a:$d74f,Y            ; D734 
    STA $2c                  ; D737 
    TAX                      ; D739 
    CPX $3b                  ; D73A 
    BNE $d72f                ; D73C 
    LDA a:$0440              ; D73E 
    STA a:$06bc              ; D741 
    RTS                      ; D744 

; F26: Two10-byte successor permutations for ascending/descending enemy passes.
EnemyUpdateOrderCycles:
    .byte $01,$02,$03,$04,$05,$06,$07,$08,$09,$00,$09,$00,$01,$02,$03,$04
    .byte $05,$06,$07,$08
    .incbin "inputs/original.nes", $01D769, $0054 ; UNINTERPRETED preserved bytes

; F27: Nonzero03DC increments; beforeincrementD2 addsflag40 tofirst8 flagged10 entries; F0 clears03DC andbits10/40 inallfirst8. Counter1expires after240calls.
TickQuakeLifetime:
    LDA a:$03dc              ; D7AD 
    BEQ $d7d3                ; D7B0 
    CMP #$f0                 ; D7B2 
    BEQ $d7d4                ; D7B4 
    CMP #$d2                 ; D7B6 Warning flag40 is added onentryD2, before counter becomesD3.
    BNE $d7d0                ; D7B8 
    LDY #$00                 ; D7BA 
    LDA a:$0473,Y            ; D7BC 
    AND #$10                 ; D7BF 
    BEQ $d7cb                ; D7C1 
    LDA a:$0473,Y            ; D7C3 
    ORA #$40                 ; D7C6 
    STA a:$0473,Y            ; D7C8 
    INY                      ; D7CB 
    CPY #$08                 ; D7CC 
    BNE $d7bc                ; D7CE 
    INC a:$03dc              ; D7D0 
    RTS                      ; D7D3 
    LDY #$00                 ; D7D4 Expiry clearsbits10/40 even on entries excluded by the originalquake producer.
    STY a:$03dc              ; D7D6 
    LDA a:$0473,Y            ; D7D9 
    AND #$af                 ; D7DC 
    STA a:$0473,Y            ; D7DE 
    INY                      ; D7E1 
    CPY #$08                 ; D7E2 
    BNE $d7d9                ; D7E4 
    RTS                      ; D7E6 

; E50: For8 entries0473..047A,bit20 excludes; elseclearbits40/10 then set10. Set03DC=1. Freeze timer consumption not reconstructed.
MarkEnemiesForQuake:
    LDY #$00                 ; D7E7 
    LDA a:$0473,Y            ; D7E9 
    AND #$20                 ; D7EC 
    BNE $d7fa                ; D7EE 
    LDA a:$0473,Y            ; D7F0 
    AND #$af                 ; D7F3 
    ORA #$10                 ; D7F5 
    STA a:$0473,Y            ; D7F7 
    INY                      ; D7FA 
    CPY #$08                 ; D7FB 
    BNE $d7e9                ; D7FD 
    LDA #$01                 ; D7FF 
    STA a:$03dc              ; D801 
    RTS                      ; D804 
    .incbin "inputs/original.nes", $01D815, $00B0 ; UNINTERPRETED preserved bytes

; D35: A high nibble increment, low3 digit position; six base20 decimal digits. Overflow clamps999999 and skips awards; otherwise at most one threshold award, advancing threshold by6 even at attempts cap0A.
AddScoreAndCheckAttemptAward:
    PHA                      ; D8B5 
    AND #$07                 ; D8B6 
    TAX                      ; D8B8 
    PLA                      ; D8B9 
    LSR A                    ; D8BA 
    LSR A                    ; D8BB 
    LSR A                    ; D8BC 
    LSR A                    ; D8BD 
    CLC                      ; D8BE 
    ADC a:$0306,X            ; D8BF 
    CMP #$2a                 ; D8C2 
    BCC $d8de                ; D8C4 
    INX                      ; D8C6 
    CPX #$06                 ; D8C7 
    BEQ $d8d5                ; D8C9 
    SEC                      ; D8CB 
    SBC #$0a                 ; D8CC 
    STA a:$0305,X            ; D8CE 
    LDA #$01                 ; D8D1 
    BNE $d8be                ; D8D3 
    LDA #$29                 ; D8D5 
    STA a:$0305,X            ; D8D7 
    DEX                      ; D8DA 
    BNE $d8d7                ; D8DB 
    RTS                      ; D8DD 
    STA a:$0306,X            ; D8DE 
    LDY a:$030f              ; D8E1 
    LDX #$05                 ; D8E4 
    LDA a:$fde8,Y            ; D8E6 
    CMP a:$0306,X            ; D8E9 
    BCC $d8f4                ; D8EC 
    BNE $d90b                ; D8EE 
    INY                      ; D8F0 
    DEX                      ; D8F1 
    BPL $d8e6                ; D8F2 
    LDA a:$030f              ; D8F4 Threshold advancement and attempt cap require separate interpretation; see bounded report.
    CLC                      ; D8F7 
    ADC #$06                 ; D8F8 
    STA a:$030f              ; D8FA 
    LDA a:$030e              ; D8FD 
    CMP #$0a                 ; D900 
    BEQ $d90b                ; D902 
    LDA #$dc                 ; D904 
    STA $01                  ; D906 
    INC a:$030e              ; D908 
    RTS                      ; D90B 

; B33: Save X/Y, evolve 97 while 95 is nonzero, set 95=1; temporarily map 00/01 for C7C7 then restore bank tags.
WaitNmiAndServiceAudio:
    TXA                      ; D90C 
    PHA                      ; D90D 
    TYA                      ; D90E 
    PHA                      ; D90F 
    INC $97                  ; D910 Always executes at least once, even if 95 was already zero.
    LDA $97                  ; D912 
    CMP #$80                 ; D914 CMP supplies carry equal to the incremented byte bit 7; ROL therefore rotates that byte.
    ROL $97                  ; D916 
    LDA $95                  ; D918 NMI writes 00 at F116 under the documented normal 96=0/1 condition.
    BNE $d910                ; D91A 
    INC $95                  ; D91C 
    LDA #$00                 ; D91E 
    STA a:$03d8              ; D920 
    STA a:$03d9              ; D923 
    LDA a:$9fff              ; D926 Read tags before mapping audio banks; shared-call restoration depends on correct bank tags.
    PHA                      ; D929 
    LDA #$00                 ; D92A 
    LDX #$06                 ; D92C 
    JSR a:$d6c3              ; D92E 
    LDA a:$bfff              ; D931 
    PHA                      ; D934 
    INX                      ; D935 
    LDA #$01                 ; D936 
    JSR a:$d6c3              ; D938 
    JSR a:$c7c7              ; D93B 
    PLA                      ; D93E 
    LDX #$07                 ; D93F 
    JSR a:$d6c3              ; D941 
    PLA                      ; D944 
    DEX                      ; D945 
    JSR a:$d6c3              ; D946 

; B34: Shift held-button history; poll twice and AND; compute rising edges, shift A history, restore caller X/Y from stack.
UpdateControllerState:
    LDA a:$0713              ; D949 0714 <- old 0713; 0713 <- previous held byte.
    STA a:$0714              ; D94C 
    LDA $20                  ; D94F 
    STA a:$0713              ; D951 
    LDY $20                  ; D954 
    JSR a:$d977              ; D956 
    STA $20                  ; D959 
    JSR a:$d977              ; D95B 
    AND $20                  ; D95E Held = sample1 AND sample2, not a retry-until-equal loop.
    STA $1f                  ; D960 
    TYA                      ; D962 Pressed = held AND NOT previous held.
    EOR #$ff                 ; D963 
    AND $1f                  ; D965 
    LDX $1f                  ; D967 
    STA $1f                  ; D969 
    STX $20                  ; D96B 
    LDA $20                  ; D96D 
    ASL A                    ; D96F ASL places A-button bit 7 in carry; ROL 21 appends it to an eight-update history.
    ROL $21                  ; D970 
    PLA                      ; D972 
    TAY                      ; D973 
    PLA                      ; D974 
    TAX                      ; D975 
    RTS                      ; D976 

; B35: Strobe 4016 high then low; read eight times, accept either low data bit, shift into 1F and return it in A.
ReadControllerSerial:
    LDX #$01                 ; D977 
    STX a:$4016              ; D979 
    DEX                      ; D97C 
    STX a:$4016              ; D97D 
    LDA a:$4016              ; D980 
    AND #$03                 ; D983 AND 03 + CMP 01 accepts D0 OR D1; other six bus bits are ignored.
    CMP #$01                 ; D985 
    ROL $1f                  ; D987 
    LDA a:$4016              ; D989 
    AND #$03                 ; D98C 
    CMP #$01                 ; D98E 
    ROL $1f                  ; D990 
    LDA a:$4016              ; D992 
    AND #$03                 ; D995 
    CMP #$01                 ; D997 
    ROL $1f                  ; D999 
    LDA a:$4016              ; D99B 
    AND #$03                 ; D99E 
    CMP #$01                 ; D9A0 
    ROL $1f                  ; D9A2 
    LDA a:$4016              ; D9A4 
    AND #$03                 ; D9A7 
    CMP #$01                 ; D9A9 
    ROL $1f                  ; D9AB 
    LDA a:$4016              ; D9AD 
    AND #$03                 ; D9B0 
    CMP #$01                 ; D9B2 
    ROL $1f                  ; D9B4 
    LDA a:$4016              ; D9B6 
    AND #$03                 ; D9B9 
    CMP #$01                 ; D9BB 
    ROL $1f                  ; D9BD 
    LDA a:$4016              ; D9BF 
    AND #$03                 ; D9C2 
    CMP #$01                 ; D9C4 
    ROL $1f                  ; D9C6 
    LDA $1f                  ; D9C8 
    RTS                      ; D9CA 

; B36: 97 <- ((((X+97) mod 256) XOR AA)+BD) mod 256; preserves X/Y.
MixTimingStateWithX:
    CLC                      ; D9CB Timing state consumer X is supplied implicitly by preceding code.
    TXA                      ; D9CC 
    ADC $97                  ; D9CD 
    EOR #$aa                 ; D9CF 
    CLC                      ; D9D1 
    ADC #$bd                 ; D9D2 
    STA $97                  ; D9D4 
    RTS                      ; D9D6 
    .incbin "inputs/original.nes", $01D9E7, $012B ; UNINTERPRETED preserved bytes

; C57: Choose sample helper with DB bit04; priority bits40/80 return solid/empty; bit10 may invoke damage (9A+04) except active effect08; accumulate terrain bits0C into CE.
ClassifyPlayerTerrainSample:
    PHA                      ; DB02 
    LDA $db                  ; DB03 
    AND #$04                 ; DB05 
    BEQ $db10                ; DB07 
    PLA                      ; DB09 
    JSR a:$da07              ; DB0A 
    JMP a:$db14              ; DB0D 
    PLA                      ; DB10 
    JSR a:$dac2              ; DB11 
    BIT $3c                  ; DB14 
    BVS $db47                ; DB16 
    BMI $db44                ; DB18 
    LDA $3c                  ; DB1A 
    AND #$10                 ; DB1C 
    BEQ $db39                ; DB1E 
    LDA a:$06bd              ; DB20 
    CMP #$08                 ; DB23 
    BNE $db2c                ; DB25 
    LDA a:$0593              ; DB27 
    BNE $db39                ; DB2A 
    LDA $cd                  ; DB2C 
    LSR A                    ; DB2E 
    PHP                      ; DB2F 
    LDA $9a                  ; DB30 
    CLC                      ; DB32 
    ADC #$04                 ; DB33 
    PLP                      ; DB35 
    JSR a:$ddd9              ; DB36 
    LDA $3c                  ; DB39 
    AND #$0c                 ; DB3B 
    ORA $ce                  ; DB3D 
    STA $ce                  ; DB3F 
    LDA $3c                  ; DB41 
    RTS                      ; DB43 
    LDA #$00                 ; DB44 
    RTS                      ; DB46 
    LDA #$03                 ; DB47 
    RTS                      ; DB49 
    .incbin "inputs/original.nes", $01DB5A, $028F ; UNINTERPRETED preserved bytes

; C58: Ignore while D2 or01A4 nonzero; subtract raw A from06B9. Borrow starts BA/BB death animation; equality zero takes hurt path. Preserve input carry as reaction direction.
ApplyPlayerDamage:
    PHP                      ; DDD9 
    STA $2c                  ; DDDA 
    LDA $d2                  ; DDDC 
    ORA a:$01a4              ; DDDE 
    BNE $de0f                ; DDE1 
    LDA a:$06b9              ; DDE3 
    SEC                      ; DDE6 
    SBC $2c                  ; DDE7 
    BCS $de11                ; DDE9 BCS includes exact zero: death branch requires unsigned borrow (damage > current raw HP).
    LDA #$f4                 ; DDEB 
    STA $01                  ; DDED 
    LDA $ce                  ; DDEF 
    AND #$f0                 ; DDF1 
    STA $ce                  ; DDF3 
    LDA $db                  ; DDF5 
    AND #$fe                 ; DDF7 
    STA $db                  ; DDF9 
    LDA $d3                  ; DDFB 
    ORA #$80                 ; DDFD 
    STA $d3                  ; DDFF 
    LDA #$5d                 ; DE01 
    LSR $cd                  ; DE03 
    ROL A                    ; DE05 
    STA $cd                  ; DE06 
    LDA #$00                 ; DE08 
    STA $cf                  ; DE0A 
    STA a:$06b9              ; DE0C 
    PLP                      ; DE0F 
    RTS                      ; DE10 
    STA a:$06b9              ; DE11 
    LDA #$de                 ; DE14 
    STA $01                  ; DE16 
    LDA #$3c                 ; DE18 
    STA $d2                  ; DE1A 
    LDA $d3                  ; DE1C 
    ORA #$20                 ; DE1E 
    STA $d3                  ; DE20 
    LDA #$00                 ; DE22 
    STA $cf                  ; DE24 
    PLP                      ; DE26 Restore caller carry before encoding reaction direction in D3 bit10.
    BCS $de30                ; DE27 
    LDA $d3                  ; DE29 
    AND #$ef                 ; DE2B 
    STA $d3                  ; DE2D 
    RTS                      ; DE2F 
    LDA $d3                  ; DE30 
    ORA #$10                 ; DE32 
    STA $d3                  ; DE34 
    RTS                      ; DE36 
    .incbin "inputs/original.nes", $01DE47, $01C9 ; UNINTERPRETED preserved bytes
