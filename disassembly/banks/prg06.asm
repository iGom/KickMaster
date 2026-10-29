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
    .incbin "inputs/original.nes", $00C1A4, $0328 ; UNINTERPRETED preserved bytes

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
    .incbin "inputs/original.nes", $00C56C, $1AA4 ; UNINTERPRETED preserved bytes
