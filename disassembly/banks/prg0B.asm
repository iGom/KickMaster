; PRG bank 0B; CPU base used here is $8000.
; For unreviewed banks, the base is a scaffold convention, not a recovered mapping.
.segment "PRG0B"
.org $8000

; H32: Reloadslot2C; kind indexes64 stored return-address-minus-one pointers; pushhigh/low andRTS.8010sharedRTS. Schedulerthreshold46 doesnotestablishkind40..45validity.
DispatchOrdinaryEnemyAi:
    LDX $2c                  ; 8000 
    LDA a:$03dd,X            ; 8002 
    ASL A                    ; 8005 
    TAY                      ; 8006 
    LDA a:$8012,Y            ; 8007 
    PHA                      ; 800A 
    LDA a:$8011,Y            ; 800B 
    PHA                      ; 800E 
    RTS                      ; 800F RTS adds1 to stored target address.
    RTS                      ; 8010 

; H33: 64 physical entries kinds00..3F.8091startsCMP0423,X code; do not reinterpret followinginstructions asentries40..45.
OrdinaryEnemyAiReturnPointers:
    .byte $4B,$81,$06,$83,$50,$83,$96,$84,$6E,$83,$1C,$85,$0A,$93,$7C,$87
    .byte $21,$88,$21,$88,$21,$88,$21,$88,$21,$88,$6E,$83,$03,$89,$A5,$89
    .byte $6D,$8B,$51,$8B,$30,$8A,$FF,$8A,$2D,$8C,$1C,$8C,$EF,$8D,$0E,$8F
    .byte $E0,$9C,$11,$9E,$C8,$9D,$33,$8F,$89,$94,$AA,$96,$AA,$96,$FE,$84
    .byte $51,$8C,$44,$86,$F0,$90,$5B,$91,$3F,$90,$82,$90,$C0,$9A,$C0,$9A
    .byte $32,$83,$AB,$98,$AB,$98,$8A,$99,$8A,$99,$8D,$8B,$6A,$99,$29,$81
    .byte $0E,$8A,$5B,$91,$CA,$99,$2C,$9A,$2C,$9A,$2C,$9A,$89,$92,$E8,$9B
    .byte $C6,$9C,$7B,$9D,$2A,$9E,$10,$9F,$89,$9F,$0F,$80,$71,$98,$71,$98

; I03: If A>0423,X unwind caller; otherwise return to caller without resetting timer.
OrdinaryEnemyTimerGate:
    CMP a:$0423,X            ; 8091 
    BEQ $809a                ; 8094 
    BCC $809a                ; 8096 
    PLA                      ; 8098 
    PLA                      ; 8099 
    RTS                      ; 809A 
    .incbin "inputs/original.nes", $0160AB, $0019 ; UNINTERPRETED preserved bytes

; I04: Increment0419,X and reset only when equal to A; returns Z flag of equality/reset.
AdvanceOrdinaryEnemyFrame:
    INC a:$0419,X            ; 80B4 
    CMP a:$0419,X            ; 80B7 
    BNE $80c1                ; 80BA 
    LDA #$00                 ; 80BC 
    STA a:$0419,X            ; 80BE 
    RTS                      ; 80C1 
    .incbin "inputs/original.nes", $0160D2, $0013 ; UNINTERPRETED preserved bytes

; I05: On entry-state change to2F,47Dbit10 suppresses drops and score; otherwise C78E drops then C746 encoded045F score. Sound51 unless0487bit40. Reset state/frame/timer, advance eight animation calls then clear469/473/47D.
OrdinaryEnemyDeathLifecycle:
    LDA a:$040f,X            ; 80D5 
    CMP $2f                  ; 80D8 
    BEQ $8108                ; 80DA 
    LDA a:$047d,X            ; 80DC 
    AND #$10                 ; 80DF 
    BNE $80ee                ; 80E1 
    JSR a:$c78e              ; 80E3 
    LDA a:$045f,X            ; 80E6 
    JSR a:$c746              ; 80E9 
    LDX $2c                  ; 80EC 
    LDA a:$0487,X            ; 80EE 
    AND #$40                 ; 80F1 
    BNE $80f9                ; 80F3 
    LDA #$51                 ; 80F5 
    STA $01                  ; 80F7 
    LDX $2c                  ; 80F9 
    LDA $2f                  ; 80FB 
    STA a:$040f,X            ; 80FD 
    LDA #$00                 ; 8100 
    STA a:$0419,X            ; 8102 
    STA a:$0423,X            ; 8105 
    INC a:$0423,X            ; 8108 
    LDA a:$0423,X            ; 810B 
    CMP #$01                 ; 810E 
    BCC $8129                ; 8110 
    LDA #$00                 ; 8112 
    STA a:$0423,X            ; 8114 
    LDA #$08                 ; 8117 
    JSR a:$80b4              ; 8119 
    BNE $8129                ; 811C 
    LDA #$00                 ; 811E 
    STA a:$0469,X            ; 8120 
    STA a:$0473,X            ; 8123 
    STA a:$047d,X            ; 8126 
    RTS                      ; 8129 
    .incbin "inputs/original.nes", $01613A, $0022 ; UNINTERPRETED preserved bytes

; I06: C7A0 with A0,Y6 selects normal/death/hit/quake; push stored pointer and RTS. Target bodies locally reviewed; terrain collision callees remain partial.
DispatchKind00State:
    LDA #$00                 ; 814C 
    LDY #$06                 ; 814E 
    JSR a:$c7a0              ; 8150 
    LDA a:$815d,Y            ; 8153 
    PHA                      ; 8156 
    LDA a:$815c,Y            ; 8157 
    PHA                      ; 815A 
    RTS                      ; 815B 

; I07: Nine stored addresses: normal0..5,death6,hit7,quake8. Code/frame table normal domain is only0..5.
Kind00StateReturnPointers:
    .byte $6D,$81,$EF,$81,$10,$82,$10,$82,$10,$82,$27,$82,$D4,$80,$A2,$C7
    .byte $0F,$80

; I08: Every3 selected normal calls, classify target X distance. Walk unless signed enemy-minus-target X is-32..-25 or24..31; in band choose next state from16 entries using(97+slot)&0F without updating RNG97.
Kind00WalkAndChooseAttack:
    LDA #$03                 ; 816E 
    JSR a:$8091              ; 8170 
    JSR a:$81ce              ; 8173 
    BNE $817b                ; 8176 
    JMP a:$8190              ; 8178 
    LDA #$01                 ; 817B 
    LDY #$00                 ; 817D 
    JSR a:$c7a9              ; 817F 
    LDA #$00                 ; 8182 
    STA a:$0423,X            ; 8184 
    LDA #$08                 ; 8187 
    JSR a:$80b4              ; 8189 
    JMP a:$8cc5              ; 818C 
    RTS                      ; 818F 
    JSR a:$846b              ; 8190 
    LDA $97                  ; 8193 
    CLC                      ; 8195 
    ADC $2c                  ; 8196 
    AND #$0f                 ; 8198 
    TAY                      ; 819A 
    LDA a:$81be,Y            ; 819B 
    STA a:$040f,X            ; 819E 
    CMP #$05                 ; 81A1 
    BNE $81b5                ; 81A3 
    LDA a:$047d,X            ; 81A5 
    ORA #$40                 ; 81A8 
    STA a:$047d,X            ; 81AA 
    LDA a:$0469,X            ; 81AD 
    ORA #$02                 ; 81B0 
    STA a:$0469,X            ; 81B2 
    LDA #$00                 ; 81B5 
    STA a:$0419,X            ; 81B7 
    STA a:$0423,X            ; 81BA 
    RTS                      ; 81BD 

; I09: 16 state choices, mostly2 with3/4/5; not independent random draws or measured gameplay probabilities.
Kind00AttackChoiceTable:
    .byte $02,$03,$02,$04,$02,$03,$02,$02,$05,$02,$03,$02,$03,$02,$04,$02

; I10: C7A6 distance masks3F&C0:80 sets469bit0,other nonzero clearsbit0; zero returns A0. Low flag from table is not a plain signed-distance comparison.
Kind00TargetBandFacing:
    JSR a:$c7a6              ; 81CE 
    LDA $3f                  ; 81D1 
    AND #$c0                 ; 81D3 
    BEQ $81ed                ; 81D5 
    CMP #$80                 ; 81D7 
    BEQ $81e4                ; 81D9 
    LDA a:$0469,X            ; 81DB 
    AND #$fe                 ; 81DE 
    STA a:$0469,X            ; 81E0 
    RTS                      ; 81E3 
    LDA a:$0469,X            ; 81E4 
    ORA #$01                 ; 81E7 
    STA a:$0469,X            ; 81E9 
    RTS                      ; 81EC 
    LDA #$00                 ; 81ED 
    RTS                      ; 81EF 

; I11: Fall entry movesY5 then resets frame/timer; negative36 clears47D40 and state0. Attack entry advances nine frames every3 timer calls then returns state0.
Kind00FallAndStationaryAttacks:
    LDA #$00                 ; 81F0 
    LDY #$05                 ; 81F2 
    JSR a:$c7a9              ; 81F4 
    LDA #$00                 ; 81F7 
    STA a:$0419,X            ; 81F9 
    STA a:$0423,X            ; 81FC 
    LDA $36                  ; 81FF 
    BPL $8210                ; 8201 
    LDA a:$047d,X            ; 8203 
    AND #$bf                 ; 8206 
    STA a:$047d,X            ; 8208 
    LDA #$00                 ; 820B 
    STA a:$040f,X            ; 820D 
    RTS                      ; 8210 
    LDA #$03                 ; 8211 
    JSR a:$8091              ; 8213 
    LDA #$00                 ; 8216 
    STA a:$0423,X            ; 8218 
    LDA #$09                 ; 821B 
    JSR a:$80b4              ; 821D 
    BNE $8227                ; 8220 
    LDA #$00                 ; 8222 
    STA a:$040f,X            ; 8224 
    RTS                      ; 8227 

; I12: Every2 timer calls use nine X/Y movement pairs, clear469bit1 at frame4; 8281 terrain response chooses states, otherwise frame9 resets to state1 and clears47D40.
Kind00ArcingAttack:
    LDA #$02                 ; 8228 
    JSR a:$8091              ; 822A 
    LDY a:$0419,X            ; 822D 
    CPY #$04                 ; 8230 
    BNE $823c                ; 8232 
    LDA a:$0469,X            ; 8234 
    AND #$fd                 ; 8237 
    STA a:$0469,X            ; 8239 
    LDA a:$826f,Y            ; 823C 
    PHA                      ; 823F 
    LDA a:$8278,Y            ; 8240 
    TAY                      ; 8243 
    PLA                      ; 8244 
    JSR a:$c7a9              ; 8245 
    LDA #$00                 ; 8248 
    STA a:$0423,X            ; 824A 
    LDA #$01                 ; 824D 
    STA $41                  ; 824F 
    LDA #$00                 ; 8251 
    STA $42                  ; 8253 
    JSR a:$8281              ; 8255 
    BEQ $826e                ; 8258 
    LDA #$09                 ; 825A 
    JSR a:$80b4              ; 825C 
    BNE $826e                ; 825F 
    LDA a:$047d,X            ; 8261 
    AND #$bf                 ; 8264 
    STA a:$047d,X            ; 8266 
    LDA #$01                 ; 8269 
    STA a:$040f,X            ; 826B 
    RTS                      ; 826E 

; I13: Nine X magnitudes followed by nine Y magnitudes; direction from469low2.
Kind00ArcingAttackSteps:
    .byte $00,$02,$03,$04,$05,$06,$07,$08,$08,$08,$06,$04,$02,$00,$02,$04
    .byte $06,$08

; I14: 36bit40 selects41 andsets47D40/clears46902; else36negative selects42/clears47D40; both resetframe/timer; otherwise returnsA1.
SelectEnemyStateFromMovementResult:
    BIT $36                  ; 8281 
    BVC $82a3                ; 8283 
    LDA $41                  ; 8285 
    STA a:$040f,X            ; 8287 
    LDA a:$0469,X            ; 828A 
    AND #$fd                 ; 828D 
    STA a:$0469,X            ; 828F 
    LDA a:$047d,X            ; 8292 
    ORA #$40                 ; 8295 
    STA a:$047d,X            ; 8297 
    LDA #$00                 ; 829A 
    STA a:$0419,X            ; 829C 
    STA a:$0423,X            ; 829F 
    RTS                      ; 82A2 
    BPL $82b5                ; 82A3 
    LDA a:$047d,X            ; 82A5 
    AND #$bf                 ; 82A8 
    STA a:$047d,X            ; 82AA 
    LDA $42                  ; 82AD 
    STA a:$040f,X            ; 82AF 
    JMP a:$829a              ; 82B2 
    LDA #$01                 ; 82B5 
    RTS                      ; 82B7 
    .incbin "inputs/original.nes", $0162C8, $01B3 ; UNINTERPRETED preserved bytes

; I15: UsesC7A6 3F&0C; ifnonzero and469bit04 allowed, sets/clears facing accordingbit08. Otherflagbits retained.
FaceTargetFromFarDistanceBits:
    JSR a:$c7a6              ; 846B 
    LDA $3f                  ; 846E 
    AND #$0c                 ; 8470 
    BEQ $8496                ; 8472 
    STA $3f                  ; 8474 
    LDA a:$0469,X            ; 8476 
    AND #$04                 ; 8479 
    BEQ $848b                ; 847B 
    LDA $3f                  ; 847D 
    CMP #$08                 ; 847F 
    BEQ $848e                ; 8481 
    LDA a:$0469,X            ; 8483 
    AND #$fe                 ; 8486 
    STA a:$0469,X            ; 8488 
    LDA #$01                 ; 848B 
    RTS                      ; 848D 
    LDA a:$0469,X            ; 848E 
    ORA #$01                 ; 8491 
    STA a:$0469,X            ; 8493 
    RTS                      ; 8496 
    .incbin "inputs/original.nes", $0164A7, $082E ; UNINTERPRETED preserved bytes

; I16: Entries choose state1 or2 when36nonnegative, set47D40,clear46902,resetframe/timer. Negative36 returnsA1.
EnterEnemyFallUnlessGrounded:
    LDA #$01                 ; 8CC5 
    BNE $8ccb                ; 8CC7 
    LDA #$02                 ; 8CC9 
    BIT $36                  ; 8CCB 
    BMI $8ceb                ; 8CCD 
    STA a:$040f,X            ; 8CCF 
    LDA a:$047d,X            ; 8CD2 
    ORA #$40                 ; 8CD5 
    STA a:$047d,X            ; 8CD7 
    LDA a:$0469,X            ; 8CDA 
    AND #$fd                 ; 8CDD 
    STA a:$0469,X            ; 8CDF 
    LDA #$00                 ; 8CE2 
    STA a:$0419,X            ; 8CE4 
    STA a:$0423,X            ; 8CE7 
    RTS                      ; 8CEA 
    LDA #$01                 ; 8CEB 
    RTS                      ; 8CED 
    .incbin "inputs/original.nes", $016CFE, $1312 ; UNINTERPRETED preserved bytes
