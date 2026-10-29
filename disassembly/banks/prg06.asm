; PRG bank 06; CPU base used here is $8000.
; For unreviewed banks, the base is a scaffold convention, not a recovered mapping.
.segment "PRG06"
.org $8000

; F01: 101 byte offsets indexed by CD>>1; R6=06 collision context; later acquisition/death states may be gated before lookup.
PlayerCollisionVerticalOffset:
    .byte $1C,$1C,$1C,$1C,$1C,$1C,$18,$18,$0F,$0F,$0F,$0F,$0F,$0F,$1C,$1C
    .byte $16,$1C,$1C,$1C,$1C,$16,$1C,$16,$1C,$1C,$18,$18,$18,$18,$18,$18
    .byte $18,$1A,$18,$18,$10,$10,$10,$10,$10,$10,$10,$1C,$1C,$16,$1A,$18
    .byte $18,$10,$10,$20,$20,$20,$18,$18,$18,$20,$20,$1C,$1C,$18,$1C,$1C
    .byte $16,$1C,$1C,$18,$10,$10,$10,$10,$10,$10,$10,$10,$10,$18,$1C,$1C
    .byte $0F,$0C,$08,$08,$0C,$0F,$0F,$10,$10,$10,$10,$10,$0F,$00,$00,$00
    .byte $00,$00,$00,$00,$00

; F02: 101 height-like extents combined with counterpart extent using8-bit arithmetic.
PlayerCollisionVerticalExtent:
    .byte $1C,$1C,$1C,$1C,$1C,$18,$18,$18,$0F,$0F,$0F,$0F,$0F,$0F,$00,$1C
    .byte $16,$1C,$1C,$1C,$1C,$16,$1C,$16,$1C,$1C,$00,$00,$00,$00,$18,$18
    .byte $10,$1A,$18,$18,$10,$00,$00,$00,$00,$00,$00,$1C,$1C,$16,$18,$18
    .byte $18,$10,$10,$18,$10,$10,$00,$00,$00,$10,$10,$10,$10,$10,$14,$1C
    .byte $18,$18,$10,$18,$00,$00,$00,$00,$00,$00,$00,$00,$00,$18,$1C,$1C
    .byte $0F,$09,$00,$00,$09,$0F,$0F,$10,$10,$10,$10,$10,$0F,$00,$00,$00
    .byte $00,$00,$00,$00,$00

; F03: 101 horizontal extent bytes, facing-selected by A4EC.
PlayerCollisionHorizontalSide0:
    .byte $04,$04,$04,$04,$04,$04,$04,$04,$04,$04,$02,$02,$02,$04,$00,$04
    .byte $02,$00,$00,$00,$FC,$04,$04,$02,$00,$FE,$00,$00,$00,$00,$08,$08
    .byte $04,$04,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$FE,$04,$04,$00
    .byte $00,$00,$00,$04,$FC,$FC,$00,$00,$00,$FC,$FC,$00,$04,$08,$08,$04
    .byte $02,$00,$FE,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$04
    .byte $04,$04,$04,$04,$04,$04,$04,$04,$04,$04,$04,$04,$04,$00,$00,$00
    .byte $00,$00,$00,$00,$00

; F04: Opposite101 horizontal extents. Valid gameplay domain not inferred from arbitrary state bytes.
PlayerCollisionHorizontalSide1:
    .byte $04,$04,$04,$04,$04,$04,$04,$04,$04,$04,$06,$06,$06,$04,$00,$04
    .byte $06,$06,$06,$06,$0C,$04,$04,$04,$04,$0A,$00,$00,$00,$00,$00,$00
    .byte $04,$04,$06,$06,$06,$00,$00,$00,$00,$00,$00,$08,$0A,$04,$04,$06
    .byte $06,$06,$06,$04,$04,$04,$00,$00,$00,$0C,$0C,$08,$04,$00,$00,$04
    .byte $04,$04,$04,$06,$00,$00,$00,$00,$00,$00,$00,$00,$00,$08,$06,$04
    .byte $04,$04,$FC,$FC,$04,$04,$06,$02,$02,$02,$02,$02,$06,$00,$00,$00
    .byte $00,$00,$00,$00,$00

; H01: 101 bytes indexed CD>>1 byA452. Separate from player hurtbox tables8000..8193.
PlayerAttackVerticalOffset:
    .byte $00,$00,$00,$00,$00,$00,$00,$00,$00,$08,$08,$08,$08,$08,$16,$00
    .byte $00,$20,$20,$20,$00,$00,$00,$00,$20,$20,$00,$00,$00,$00,$20,$20
    .byte $00,$00,$00,$22,$22,$1A,$20,$24,$20,$1C,$18,$00,$00,$00,$00,$00
    .byte $22,$22,$22,$00,$18,$20,$20,$20,$20,$20,$18,$00,$00,$00,$00,$00
    .byte $00,$20,$20,$00,$18,$18,$18,$18,$18,$18,$18,$18,$18,$00,$00,$00
    .byte $08,$10,$10,$10,$10,$08,$08,$18,$2A,$2A,$2A,$18,$08,$00,$00,$00
    .byte $00,$00,$00,$00,$00

; H02: 101 unsigned extent terms; modular comparison includes enemy body extent. Zero size can still act as a point test.
PlayerAttackVerticalExtent:
    .byte $00,$00,$00,$00,$00,$00,$00,$00,$00,$08,$0A,$0A,$0A,$08,$18,$00
    .byte $00,$10,$10,$10,$00,$00,$00,$00,$10,$10,$00,$00,$00,$00,$10,$10
    .byte $00,$00,$00,$10,$14,$12,$12,$14,$12,$12,$12,$00,$00,$00,$00,$00
    .byte $10,$14,$14,$00,$08,$10,$10,$10,$10,$10,$08,$00,$00,$00,$00,$00
    .byte $00,$10,$10,$00,$0C,$10,$10,$0C,$0C,$0C,$10,$10,$0C,$00,$00,$00
    .byte $08,$10,$10,$10,$10,$08,$0C,$14,$1E,$1E,$1E,$14,$0C,$00,$00,$00
    .byte $00,$00,$00,$00,$00

; H03: 101 signed offsets for subtract endpoint, exchanged with plus side on oddCD.
PlayerAttackMinusXOffset:
    .byte $00,$00,$00,$00,$00,$00,$00,$00,$00,$FC,$FB,$FB,$FB,$FC,$0A,$00
    .byte $00,$F8,$F8,$F8,$00,$00,$00,$00,$F8,$F9,$00,$00,$00,$00,$00,$00
    .byte $00,$00,$00,$F8,$04,$F8,$F8,$04,$08,$08,$08,$00,$00,$00,$00,$00
    .byte $F8,$04,$04,$00,$F0,$F0,$FD,$FD,$FD,$F0,$F0,$00,$00,$00,$00,$00
    .byte $00,$F8,$F9,$00,$05,$10,$10,$10,$08,$08,$10,$10,$0C,$00,$00,$00
    .byte $FC,$00,$05,$05,$00,$FC,$FC,$08,$08,$08,$08,$08,$FC,$00,$00,$00
    .byte $00,$00,$00,$00,$00

; H04: 101 signed offsets for add endpoint; A452 replaces out-of-camera-page endpoint with camera origin.
PlayerAttackPlusXOffset:
    .byte $00,$00,$00,$00,$00,$00,$00,$00,$00,$0B,$11,$11,$11,$0B,$0A,$00
    .byte $00,$10,$10,$10,$00,$00,$00,$00,$0E,$18,$00,$00,$00,$00,$14,$14
    .byte $00,$00,$00,$0E,$0E,$10,$18,$0C,$10,$10,$10,$00,$00,$00,$00,$00
    .byte $0E,$0E,$0E,$00,$18,$1A,$1A,$1A,$1A,$1A,$18,$00,$00,$00,$00,$00
    .byte $00,$0E,$18,$00,$12,$18,$18,$10,$0C,$10,$18,$18,$14,$00,$00,$00
    .byte $0B,$10,$12,$12,$10,$0B,$0B,$08,$08,$08,$08,$08,$0B,$00,$00,$00
    .byte $00,$00,$00,$00,$00

; H05: 101 raw damage requests indexed by CD>>1 after first overlapping enemy. A197 does not apply level scaling itself. Zero request returns without continuing scan.
PlayerMeleeDamageRequests:
    .byte $00,$00,$00,$00,$00,$00,$00,$00,$00,$03,$03,$03,$03,$03,$08,$00
    .byte $00,$04,$04,$04,$00,$00,$00,$00,$04,$04,$01,$01,$01,$01,$05,$05
    .byte $00,$00,$00,$04,$04,$04,$08,$08,$04,$04,$08,$00,$00,$00,$00,$00
    .byte $08,$08,$08,$00,$08,$0A,$0C,$0C,$0C,$0A,$08,$00,$00,$00,$00,$00
    .byte $00,$04,$05,$00,$06,$08,$08,$06,$04,$05,$08,$08,$05,$00,$00,$00
    .byte $01,$03,$08,$08,$03,$01,$02,$03,$04,$04,$04,$03,$02,$00,$00,$00
    .byte $00,$00,$00,$00,$00

; H06: 101 signed Y offsets consumed by08:A1E8. Local call-argument schema; full terrain mutation pending.
PlayerTerrainAttackYOffset:
    .byte $EF,$00,$00,$00,$00,$00,$00,$00,$00,$FC,$FC,$FC,$FC,$FC,$01,$00
    .byte $00,$E6,$E4,$E4,$00,$00,$00,$00,$E6,$E6,$00,$00,$00,$00,$E4,$E4
    .byte $00,$FC,$FC,$EE,$E8,$E8,$DE,$DE,$DE,$DE,$E8,$EE,$F6,$F8,$DE,$DE
    .byte $DE,$DE,$DE,$00,$EC,$EC,$EC,$EC,$EC,$EC,$EC,$00,$00,$00,$00,$00
    .byte $00,$E4,$E8,$00,$F6,$EC,$EC,$F8,$F6,$F8,$EC,$EC,$F8,$00,$00,$00
    .byte $F8,$F8,$F8,$F8,$F8,$F8,$F8,$E8,$D8,$D6,$D8,$E8,$F8,$00,$00,$00
    .byte $00,$00,$00,$00,$00

; H07: 101 X offsets; A1E8 negates for oddCD beforeC773.
PlayerTerrainAttackXOffset:
    .byte $00,$00,$00,$00,$00,$00,$00,$00,$00,$0B,$13,$13,$13,$0B,$00,$00
    .byte $00,$10,$13,$10,$00,$00,$00,$00,$0E,$15,$00,$00,$00,$00,$10,$10
    .byte $00,$14,$14,$0E,$09,$04,$00,$FC,$F8,$F4,$F2,$F2,$F4,$F8,$06,$FA
    .byte $0E,$08,$00,$00,$0E,$12,$15,$15,$15,$15,$15,$00,$00,$00,$00,$00
    .byte $00,$0E,$12,$00,$10,$14,$F0,$F0,$F4,$10,$14,$F0,$F4,$00,$00,$00
    .byte $0B,$10,$12,$12,$10,$0B,$0B,$FF,$FE,$02,$01,$FF,$0B,$00,$00,$00
    .byte $00,$00,$00,$00,$00

; H08: 101 strength bytes; zero suppresses C773 call, otherwise copied to2C.
PlayerTerrainAttackStrength:
    .byte $FF,$00,$00,$00,$00,$00,$00,$00,$00,$01,$01,$01,$01,$01,$5A,$00
    .byte $00,$01,$01,$01,$00,$00,$00,$00,$01,$02,$00,$00,$00,$00,$02,$02
    .byte $00,$28,$28,$28,$28,$28,$28,$28,$28,$28,$14,$28,$28,$28,$05,$05
    .byte $04,$07,$07,$00,$07,$07,$0A,$0A,$0A,$07,$07,$00,$00,$00,$00,$00
    .byte $00,$05,$05,$00,$05,$0A,$0A,$0F,$05,$0F,$1E,$1E,$0F,$00,$00,$00
    .byte $05,$07,$0A,$0A,$07,$05,$05,$05,$05,$05,$05,$05,$05,$00,$00,$00
    .byte $00,$00,$00,$00,$00

; F05: 32 bytes indexed by projectile(type&FE)/2; used by08:A54D.
ProjectileCollisionVerticalOffset:
    .byte $08,$10,$18,$20,$28,$30,$0E,$0E,$10,$10,$10,$10,$00,$00,$00,$00
    .byte $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00

; F06: 32 vertical extents for types00..3F.
ProjectileCollisionVerticalExtent:
    .byte $0A,$20,$30,$40,$50,$60,$0C,$0C,$10,$10,$10,$10,$20,$48,$48,$48
    .byte $48,$48,$48,$48,$20,$48,$70,$A8,$80,$80,$80,$80,$C0,$C0,$C0,$C0

; F07: 32 horizontal extents, swapped with other side for odd type.
ProjectileCollisionMinusXExtent:
    .byte $0C,$0C,$0C,$0C,$0C,$0C,$08,$08,$08,$08,$08,$08,$08,$08,$08,$08
    .byte $08,$08,$08,$08,$00,$08,$10,$18,$18,$18,$18,$18,$28,$28,$28,$28

; F08: 32 horizontal extents; projectile endpoints are clipped against camera page by08:A54D.
ProjectileCollisionPlusXExtent:
    .byte $04,$04,$04,$04,$04,$04,$08,$08,$08,$08,$08,$08,$08,$08,$08,$08
    .byte $08,$08,$08,$08,$00,$08,$10,$18,$18,$18,$18,$18,$28,$28,$28,$28

; F09: 32 raw queued-damage values: pulse3; bouncing types10/12 alternate3/2; lightning2. Final HP consumer is0F:E32A.
ProjectileDamageRequests:
    .byte $03,$03,$03,$03,$03,$03,$03,$03,$03,$02,$03,$02,$02,$02,$02,$02
    .byte $02,$02,$02,$02,$02,$02,$02,$02,$02,$02,$02,$02,$02,$02,$02,$02

; H09: 99 physical little-endian state-table pointers for kinds00..62. Parallel99-entry renderer table corroborates boundary. This is not proof that all kinds/states are reachable or valid in AI.
EnemyKindCollisionStatePointers:
    .byte $22,$86,$2E,$86,$36,$86,$3E,$86,$44,$86,$54,$86,$5C,$86,$72,$86
    .byte $7A,$86,$7A,$86,$7A,$86,$7A,$86,$7A,$86,$4C,$86,$98,$86,$A2,$86
    .byte $A8,$86,$A8,$86,$BC,$86,$BC,$86,$C8,$86,$C8,$86,$D6,$86,$E8,$86
    .byte $EA,$86,$F2,$86,$F4,$86,$F8,$86,$FE,$86,$0A,$87,$14,$87,$54,$86
    .byte $D6,$86,$64,$86,$1E,$87,$1E,$87,$22,$87,$2A,$87,$32,$87,$32,$87
    .byte $44,$86,$3E,$87,$3E,$87,$48,$87,$52,$87,$B2,$86,$52,$87,$22,$86
    .byte $BC,$86,$1E,$87,$5C,$87,$62,$87,$62,$87,$62,$87,$68,$87,$70,$87
    .byte $76,$87,$7A,$87,$82,$87,$88,$87,$88,$87,$8C,$87,$94,$87,$9E,$87
    .byte $22,$86,$22,$86,$22,$86,$22,$86,$22,$86,$22,$86,$22,$86,$22,$86
    .byte $22,$86,$22,$86,$22,$86,$22,$86,$22,$86,$22,$86,$22,$86,$34,$88
    .byte $A8,$87,$B0,$87,$BC,$87,$CA,$87,$D8,$87,$E4,$87,$F2,$87,$FC,$87
    .byte $06,$88,$0E,$88,$1A,$88,$40,$88,$84,$86,$A8,$87,$BC,$87,$CA,$87
    .byte $40,$88,$2C,$88,$36,$88
    .incbin "inputs/original.nes", $00C632, $0EBA ; UNINTERPRETED preserved bytes

; H10: 30 byte shape offsets used byA354.
EnemyBodyVerticalOffset:
    .byte $00,$00,$00,$F4,$00,$08,$F0,$02,$00,$00,$00,$00,$F8,$10,$00,$F0
    .byte $F0,$20,$F8,$30,$00,$28,$00,$08,$F4,$FC,$08,$00,$00,$02

; H11: 30 body height-like extent terms.
EnemyBodyVerticalExtent:
    .byte $20,$20,$20,$00,$18,$00,$00,$14,$38,$28,$16,$14,$10,$00,$28,$30
    .byte $13,$00,$1C,$40,$20,$40,$20,$20,$18,$20,$20,$18,$28,$14

; H12: 30 signed body side offsets; A354 checks both world endpoints against camera page.
EnemyBodyXSide0:
    .byte $0C,$F4,$08,$F9,$0B,$00,$00,$0A,$08,$10,$10,$10,$0C,$00,$12,$18
    .byte $18,$00,$08,$10,$10,$F8,$10,$0C,$0C,$0C,$10,$10,$08,$10

; H13: 30 opposite signed body offsets; swapped when flags469bit0 clear.
EnemyBodyXSide1:
    .byte $0C,$10,$08,$07,$0B,$00,$00,$0A,$08,$07,$10,$18,$0C,$00,$12,$18
    .byte $18,$00,$18,$10,$0C,$17,$10,$0C,$08,$08,$10,$10,$08,$06

; H14: 48 secondary shape offsets; A0B0 selects via frame byte3 if frame byte2 damage nonzero.
EnemyAttackVerticalOffset:
    .byte $F8,$F8,$F8,$00,$FB,$FB,$FB,$FB,$FB,$00,$00,$00,$EB,$E8,$FB,$FB
    .byte $FB,$F4,$00,$E8,$E8,$00,$00,$F4,$FC,$F8,$F0,$00,$F0,$F8,$F8,$F0
    .byte $F6,$F0,$F0,$F0,$F4,$F8,$F8,$00,$28,$00,$00,$00,$00,$00,$00,$00

; H15: 48 secondary vertical extent terms; overlap uses modular low-byte arithmetic.
EnemyAttackVerticalExtent:
    .byte $10,$10,$10,$18,$0F,$07,$00,$04,$04,$08,$10,$18,$27,$20,$20,$0E
    .byte $10,$14,$10,$38,$1C,$10,$10,$10,$14,$10,$0A,$0A,$10,$10,$10,$10
    .byte $10,$18,$18,$10,$10,$10,$10,$20,$40,$10,$10,$00,$00,$00,$00,$00

; H16: 48 raw secondary side terms; no world-page rejection inA0B0.
EnemyAttackXSide0:
    .byte $08,$30,$1C,$0B,$08,$04,$02,$18,$28,$04,$06,$08,$0B,$14,$04,$0B
    .byte $14,$08,$10,$10,$10,$08,$1B,$14,$14,$10,$20,$20,$17,$18,$14,$18
    .byte $10,$18,$0C,$10,$10,$10,$38,$10,$F8,$08,$10,$00,$00,$00,$00,$00

; H17: 48 opposite secondary side terms; swap for flags469bit0 clear, then sum modulo256.
EnemyAttackXSide1:
    .byte $08,$00,$00,$0B,$08,$04,$02,$04,$04,$04,$06,$08,$0B,$14,$04,$0B
    .byte $14,$08,$00,$10,$10,$00,$00,$04,$04,$00,$00,$00,$00,$10,$0C,$00
    .byte $F8,$F8,$04,$08,$08,$08,$F0,$10,$18,$08,$10,$00,$00,$00,$00,$00
    .incbin "inputs/original.nes", $00D624, $09EC ; UNINTERPRETED preserved bytes
