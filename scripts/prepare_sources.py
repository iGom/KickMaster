#!/usr/bin/env python3
"""Explicitly regenerate the mixed source scaffold. Does not run during build.py."""
import argparse,sys
from baseline import ROOT,verified_rom
from architecture import REGIONS,COMMENTS,loc
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler

def main():
    ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();b,h=verified_rom(a.rom)
    m=MPU();m.memory[0xC000:]=b[16+14*8192:16+16*8192];d=Disassembler(m)
    main=['; Input-dependent byte-matching scaffold. Unknown regions remain explicit .incbin slices.',
          '; Run prepare_sources.py only when intentionally regenerating source.','.setcpu "6502"',
          '.segment "HEADER"','.byte '+','.join(f'${x:02X}' for x in b[:16])]
    cfg=['MEMORY {','  HEADER: start=$0000, size=$0010, file=%O;']
    seg=['SEGMENTS {','  HEADER: load=HEADER, type=ro;']
    for bank in range(16):
        base=0xE000 if bank==15 else 0xC000 if bank==14 else 0x8000
        cfg.append(f'  PRG{bank:02X}: start=${base:04X}, size=$2000, file=%O;')
        seg.append(f'  PRG{bank:02X}: load=PRG{bank:02X}, type=ro;')
        main.append(f'.include "banks/prg{bank:02X}.asm"')
        lines=[f'; PRG bank {bank:02X}; CPU base used here is ${base:04X}.',
               '; For unreviewed banks, the base is a scaffold convention, not a recovered mapping.',f'.segment "PRG{bank:02X}"',f'.org ${base:04X}']
        cursor=base
        def raw(lo,hi):
            if hi>lo:lines.append(f'    .incbin "inputs/original.nes", ${16+bank*8192+lo-base:06X}, ${hi-lo:04X} ; UNINTERPRETED preserved bytes')
        for rid,name,lo,hi,kind,desc in REGIONS:
            if int(loc(lo)['bank'],16)!=bank:continue
            raw(cursor,lo);lines += ['',f'; {rid}: {desc}',f'{name}:']
            if kind=='data':
                for pc in range(lo,hi,16):lines.append('    .byte '+','.join(f'${x:02X}' for x in m.memory[pc:min(pc+16,hi)]))
            else:
                pc=lo
                while pc<hi:
                    n,t=d.instruction_at(pc);op,mode=m.disassemble[m.memory[pc]]
                    if mode in {'abs','abx','aby'}:t=t.replace(' $',' a:$',1)
                    lines.append(f'    {t:24} ; {pc:04X} {COMMENTS.get(pc,"")}');pc+=n
            cursor=hi
        raw(cursor,base+8192)
        (ROOT/f'disassembly/banks/prg{bank:02X}.asm').write_text('\n'.join(lines)+'\n')
    cfg += ['  CHR: start=$0000, size=$20000, file=%O;','}'];seg+=['  CHR: load=CHR, type=ro;','}']
    main+=['.segment "CHR"','.incbin "inputs/original.nes", $020010, $020000 ; UNINTERPRETED CHR bytes']
    (ROOT/'disassembly/main.asm').write_text('\n'.join(main)+'\n')
    (ROOT/'disassembly/linker.cfg').write_text('\n'.join(cfg+seg)+'\n')
    print('Prepared annotated instruction/data sources plus explicit input-ROM slices.')
if __name__=='__main__':main()
