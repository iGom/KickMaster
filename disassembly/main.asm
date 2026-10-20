; Input-dependent byte-matching scaffold. Unknown regions remain explicit .incbin slices.
; Run prepare_sources.py only when intentionally regenerating source.
.setcpu "6502"
.segment "HEADER"
.byte $4E,$45,$53,$1A,$08,$10,$40,$08,$00,$00,$00,$00,$00,$00,$00,$01
.include "banks/prg00.asm"
.include "banks/prg01.asm"
.include "banks/prg02.asm"
.include "banks/prg03.asm"
.include "banks/prg04.asm"
.include "banks/prg05.asm"
.include "banks/prg06.asm"
.include "banks/prg07.asm"
.include "banks/prg08.asm"
.include "banks/prg09.asm"
.include "banks/prg0A.asm"
.include "banks/prg0B.asm"
.include "banks/prg0C.asm"
.include "banks/prg0D.asm"
.include "banks/prg0E.asm"
.include "banks/prg0F.asm"
.segment "CHR"
.incbin "inputs/original.nes", $020010, $020000 ; UNINTERPRETED CHR bytes
