#!/usr/bin/env python3
"""Explicitly regenerate the mixed source scaffold. Does not run during build.py."""
import argparse,csv,json,sys
from baseline import ROOT,verified_rom,write_json
sys.path.insert(0,str(ROOT/'tools/vendor'))
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler

def main():
    ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();b,h=verified_rom(a.rom)
    with (ROOT/'analysis/reviewed_ranges.csv').open() as f:ranges=list(csv.DictReader(f))
    with (ROOT/'analysis/reviewed_instructions.csv').open() as f:
        comments={(int(r['bank'],16),int(r['cpu'],16)):r['comment'] for r in csv.DictReader(f)}
    split_path=ROOT/'analysis/cross_bank_instructions.csv'
    splits=list(csv.DictReader(split_path.open())) if split_path.exists() else []
    split_starts={(int(r['bank'],16),int(r['cpu'],16)):r for r in splits}
    split_tails={(int(r['continuation_bank'],16),int(r['continuation_cpu'],16)):r for r in splits}
    main=['; Input-dependent byte-matching scaffold. Unknown regions remain explicit .incbin slices.',
          '; Run prepare_sources.py only when intentionally regenerating source.','.setcpu "6502"',
          '.segment "HEADER"','.byte '+','.join(f'${x:02X}' for x in b[:16])]
    cfg=['MEMORY {','  HEADER: start=$0000, size=$0010, file=%O;']
    seg=['SEGMENTS {','  HEADER: load=HEADER, type=ro;']
    for bank in range(16):
        bank_ranges=sorted([r for r in ranges if int(r['bank'],16)==bank],key=lambda r:int(r['bank_offset'],16))
        bases={int(r['cpu'],16)-int(r['bank_offset'],16) for r in bank_ranges}
        assert len(bases)<=1,'Multiple CPU aliases in a single assembly segment need explicit handling'
        base=next(iter(bases)) if bases else 0xE000 if bank==15 else 0xC000 if bank==14 else 0x8000
        m=MPU();m.memory[base:base+8192]=b[16+bank*8192:16+(bank+1)*8192];d=Disassembler(m)
        cfg.append(f'  PRG{bank:02X}: start=${base:04X}, size=$2000, file=%O;')
        seg.append(f'  PRG{bank:02X}: load=PRG{bank:02X}, type=ro;')
        main.append(f'.include "banks/prg{bank:02X}.asm"')
        lines=[f'; PRG bank {bank:02X}; CPU base used here is ${base:04X}.',
               '; For unreviewed banks, the base is a scaffold convention, not a recovered mapping.',f'.segment "PRG{bank:02X}"',f'.org ${base:04X}']
        cursor=base
        def raw(lo,hi):
            if hi>lo:lines.append(f'    .incbin "inputs/original.nes", ${16+bank*8192+lo-base:06X}, ${hi-lo:04X} ; UNINTERPRETED preserved bytes')
        for row in bank_ranges:
            rid,name,kind,desc=(row[k] for k in ['id','symbol','classification','description'])
            lo=int(row['cpu'],16);hi=int(row['end_cpu_exclusive'],16)
            raw(cursor,lo);lines += ['',f'; {rid}: {desc}',f'{name}:']
            if kind=='data':
                for pc in range(lo,hi,16):lines.append('    .byte '+','.join(f'${x:02X}' for x in m.memory[pc:min(pc+16,hi)]))
            else:
                pc=lo
                while pc<hi:
                    # Fixed-window instruction operands can physically begin in the next bank.
                    # Emit each physical fragment exactly once; retain one logical instruction index.
                    if (bank,pc) in split_tails:
                        r=split_tails[(bank,pc)];n=int(r['continuation_size'])
                        assert pc+n<=hi
                        lines.append('    .byte '+','.join(f'${x:02X}' for x in m.memory[pc:pc+n])+f" ; operands of {r['bank']}:{r['cpu']} {r['instruction']}");pc+=n;continue
                    if (bank,pc) in split_starts:
                        r=split_starts[(bank,pc)];n=int(r['size'])-int(r['continuation_size'])
                        assert pc+n==hi==base+8192
                        lines.append('    .byte '+','.join(f'${x:02X}' for x in m.memory[pc:pc+n])+f" ; {pc:04X} {r['instruction']}; operands in next fixed bank");pc+=n;continue
                    n,t=d.instruction_at(pc);op,mode=m.disassemble[m.memory[pc]]
                    if mode in {'abs','abx','aby'}:t=t.replace(' $',' a:$',1)
                    lines.append(f'    {t:24} ; {pc:04X} {comments.get((bank,pc),"")}');pc+=n
            cursor=hi
        raw(cursor,base+8192)
        (ROOT/f'disassembly/banks/prg{bank:02X}.asm').write_text('\n'.join(lines)+'\n')
    cfg += ['  CHR: start=$0000, size=$20000, file=%O;','}'];seg+=['  CHR: load=CHR, type=ro;','}']
    main+=['.segment "CHR"','.incbin "inputs/original.nes", $020010, $020000 ; UNINTERPRETED CHR bytes']
    (ROOT/'disassembly/main.asm').write_text('\n'.join(main)+'\n')
    (ROOT/'disassembly/linker.cfg').write_text('\n'.join(cfg+seg)+'\n')
    cov=json.loads((ROOT/'analysis/coverage.json').read_text())
    explicit=16+sum(int(r['size']) for r in ranges)
    cov.update({'explicit_source_bytes':explicit,'input_incbin_bytes':len(b)-explicit})
    write_json(ROOT/'analysis/coverage.json',cov)
    print('Prepared annotated instruction/data sources plus explicit input-ROM slices.')
if __name__=='__main__':main()
