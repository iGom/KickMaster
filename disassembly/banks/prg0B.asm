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
    .incbin "inputs/original.nes", $0160A1, $1F6F ; UNINTERPRETED preserved bytes
