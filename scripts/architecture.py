#!/usr/bin/env python3
"""Bounded static analysis: reviewed regions plus clearly separate fixed-window candidates."""
import argparse,collections,csv,json,sys
from pathlib import Path
from baseline import ROOT,verified_rom,write_csv,write_json
sys.path.insert(0,str(ROOT/'tools/vendor'))
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler

# End-exclusive ranges. Names describe established local effects, not full gameplay roles.
REGIONS=[
('A01','ApuInitialize',0xCC84,0xCCAB,'code','Initialize APU registers and call two five-entry index initializers.'),
('A02','InitializeAudioIndicesA',0xCCAB,0xCCBA,'code','Fill 0015..0019 with 05,0B,11,17,1D; audio role from A01 caller.'),
('A03','InitializeAudioIndicesB',0xCCBA,0xCCC9,'code','Fill 001A..001E with 23,29,2F,35,3B.'),
('A04','ResetRetentionCheck',0xD60C,0xD627,'code','Check retained 0100 marker 68; otherwise load six bytes at 0300; call D2F7.'),
('A05','ResetRetainedDefaults',0xD627,0xD62D,'data','Six default bytes copied to 0300..0305; purpose unresolved.'),
('A06','HideAllSprites',0xD62D,0xD63B,'code','Write F1 to every OAM Y byte in page 02.'),
('A07','HideSpritesFromIndex',0xD63B,0xD64E,'code','For index 99 below 64, fill remaining OAM Y bytes with F3.'),
('A08','MapperWriteRetry',0xD6C3,0xD6D2,'code','Write X to 8000 and A to 8001; retry if interrupt activity changes A6.'),
('A09','Bank0CEntry0',0xD6D2,0xD6DC,'code','Map PRG0C at 8000, then tail-jump to 8000.'),
('A10','Bank0CEntry3',0xD6DC,0xD6E6,'code','Map PRG0C at 8000, then tail-jump to 8003.'),
('A11','Bank0CEntry6',0xD6E6,0xD6F0,'code','Map PRG0C at 8000, then tail-jump to 8006.'),
('A12','ResetEntry',0xF010,0xF0BB,'code','Initialize hardware, bank mapping, selected RAM, PPU shadow and palette; jump to PRG0E CF50.'),
('A13','NmiEntry',0xF0BB,0xF156,'code','Save A/X/Y, OAM DMA, PPU task, scrolling, optional IRQ setup, CHR writes, epoch increment and RTI.'),
('A14','DispatchPpuTask',0xF156,0xF16A,'code','Clear A0 using Y; select one of sixteen little-endian pointers with old A0 & 1E.'),
('A15','PpuTaskPointers',0xF16A,0xF18A,'data','16 little-endian pointers; indices are command&1E divided by 2.'),
('A16','PpuUpload27ViaStack',0xF18A,0xF1B7,'code','Stream 27 bytes from 0101..011B using PLA, restore SP; increment PPU by 32.'),
('A17','PpuTaskReturn',0xF1B7,0xF1B8,'code','Shared RTS target; also fallthrough from A16.'),
('A18','UploadPalette32ViaStack',0xF24B,0xF28E,'code','Read 0143..0162 through PLA; write 32 bytes to PPU; restore SP and service 06EE flag.'),
('A19','DisableRendering',0xF4BA,0xF4CA,'code','Clear PPUMASK and shadows 5F/66; clear bit 1 of 4A.'),
('A20','FarCallViaA000',0xF4CA,0xF50A,'code','Save bank tags and registers, map 04EC into A000, call pointer 04EA, restore both PRG windows and result registers/flags.'),
('A21','FarCallIndirect',0xF50A,0xF50D,'code','Indirect JMP through RAM 04EA/04EB; called with JSR to make the callee return to wrapper.'),
('A22','IrqEntry',0xF7B1,0xF7C2,'code','Save A/X/Y in E2..E4; acknowledge/disable IRQ, enable again, dispatch through E5/E6.'),
('A23','IrqSplitPpuAddress',0xF7C2,0xF803,'code','Timed PPU address/scroll writes indexed by 67; choose terminal split at F0 sentinel; share IRQ return.'),
('A24','IrqSplitScroll',0xF803,0xF834,'code','Timed indexed scroll/control writes; select F83D on F0 sentinel.'),
('A25','IrqRestoreRegisters',0xF834,0xF83D,'code','Increment A6, restore Y/X/A from E4/E3/E2, RTI.'),
('A26','IrqSplitSwitchChr01',0xF83D,0xF882,'code','Timed split setting control, mask, address and CHR registers 0/1 to 0/2; set next IRQ low pointer 82.'),
('A27','InterruptVectors',0xFFFA,0x10000,'data','Little-endian NMI, RESET and IRQ/BRK vectors in the fixed final bank.')
]
COMMENTS={
0xD60C:'0100 was deliberately excluded from the reset clear loop.',0xD615:'Copy table backwards to retained 0300..0305.',
0xD6C3:'Contract: A=bank value, X=MMC3 selector. Y clobbered to zero.',
0xD6C5:'Clear epoch before each attempt, including a retry.',0xD6CD:'NMI/IRQ increments A6; a changed epoch repeats the two-write transaction.',
0xF013:'Disable and acknowledge MMC3 IRQ.',0xF017:'Select R0, PRG mode 0, CHR inversion 0.',
0xF01A:'MMC3 mirroring 0: CIRAM A10 / conventional vertical mirroring.',
0xF025:'Wait for four observed vblank assertion/clear cycles.',0xF034:'R6 <- 04; R7 <- 05; fixed banks 0E at C000, 0F at E000.',
0xF062:'A001 receives 01, although the physical reference board has no PRG RAM.',
0xF079:'Clear internal RAM except 0100 and 0300..0307. Indexed bases are intentionally unusual.',
0xF094:'Retention/default processing is in fixed PRG0E.',0xF0A8:'Initialize 32 palette-buffer bytes at 0143..0162.',
0xF0BB:'NMI stores registers in RAM rather than pushing them.',0xF0CB:'DMA source page 02 = RAM 0200..02FF.',
0xF0CE:'Y=0 is a precondition for clearing A0 in the dispatcher.',0xF0FF:'Restore IRQ dispatch pointer from DC/DD after the PPU task used E5/E6.',
0xF116:'For 96=0 or 1, X=0 here; this condition is documented, not assumed for arbitrary RAM.',
0xF11A:'Under the above condition, six writes select CHR R0..R5 using RAM 44..49.',
0xF14D:'A6 tracks mapper-interrupt activity; it is not safely a pure frame counter.',
0xF156:'Index mask 1E selects 16 word entries; odd command bit ignored here.',
0xF167:'Computed jump, not ordinary fallthrough into the pointer table.',
0xF19F:'Temporary stack pointer 00: PLA reads upward from 0101.',
0xF257:'Temporary SP=42 makes PLA read palette bytes starting at 0143.',
0xF27F:'Restore the real stack before RTS.',
0xF4D0:'Read live bank identity from the final byte of the 8000 window.',
0xF4D6:'Read live bank identity from the final byte of the A000 window.',
0xF4DE:'Target A000 bank is supplied through RAM 04EC.',
0xF4EA:'JSR into an indirect JMP allows the destination RTS to return here.',
0xF4ED:'Preserve callee output registers and flags while restoring mappings.',
0xF4FB:'Restore both R7 and R6, even though entry changes only R7.',
0xF7BF:'IRQ pointer is shared with temporary PPU dispatch pointer E5/E6.',
0xF7F6:'Switch to terminal split handler F83D when next count is F0.',
0xF82E:'Only low pointer byte changes; high byte F8 is a caller/state precondition.',
0xF864:'X=0 after delay loop; select CHR R0 and set it to 00.',
0xF875:'Only pointer low byte changes to 82; high F8 must already be set.'}
BRANCHES={'BPL','BMI','BVC','BVS','BCC','BCS','BNE','BEQ'}
def loc(pc):
    bank=14 if pc<0xE000 else 15;base=0xC000 if bank==14 else 0xE000
    off=pc-base;po=bank*8192+off
    return {'bank':f'{bank:02X}','cpu':f'0x{pc:04X}','bank_offset':f'0x{off:04X}',
            'prg_offset':f'0x{po:06X}','file_offset':f'0x{po+16:06X}',
            'mapping_condition':'MMC3 PRG mode 0' if bank==14 else 'last bank fixed at E000'}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();b,h=verified_rom(a.rom)
    p=b[16:16+131072];m=MPU();m.memory[0xC000:]=p[-16384:];d=Disassembler(m)
    symbols={s:n for _,n,s,_,_,_ in REGIONS}; instructions=[];ranges=[];functions=[];evidence=[]
    reviewed=set();known_data=set()
    for rid,name,lo,hi,kind,desc in REGIONS:
        ranges.append({'id':rid,'symbol':name,**loc(lo),'size':hi-lo,'end_cpu_exclusive':f'0x{hi:04X}','classification':kind,'status':'STATIC_REVIEWED','description':desc})
        evidence.append({'id':rid,'class':'STATIC','subject':name,'source':f'disassembly/banks/prg{loc(lo)["bank"]}_reviewed.asm','location':f'{lo:04X}-{hi:04X} exclusive','claim':desc,'confidence':'high within local routine; caller constraints documented'})
        if kind=='data':known_data.update(range(lo,hi));continue
        functions.append({'id':rid,'name':name,**loc(lo),'size':hi-lo,'status':'STATIC_REVIEWED','description':desc,'callers_callees':'see cross_references.csv; indirect targets explicitly unresolved'})
        pc=lo
        while pc<hi:
            n,t=d.instruction_at(pc)
            if t=='???' or pc+n>hi:raise ValueError(f'Invalid reviewed decode at {pc:X}')
            instructions.append({'region_id':rid,'symbol':name,**loc(pc),'size':n,'bytes':bytes(m.memory[pc:pc+n]).hex(' ').upper(),'instruction':t,'comment':COMMENTS.get(pc,'')})
            reviewed.update(range(pc,pc+n));pc+=n
    write_csv(ROOT/'analysis/reviewed_ranges.csv',ranges);write_csv(ROOT/'analysis/reviewed_instructions.csv',instructions)
    write_csv(ROOT/'analysis/functions.csv',functions);write_csv(ROOT/'analysis/evidence.csv',evidence)
    ptrs=[]
    for i in range(16):
        pc=0xF16A+i*2;target=m.memory[pc]|m.memory[pc+1]<<8
        ptrs.append({'entry':i,'command_masked':f'0x{i*2:02X}',**loc(pc),'target_cpu':f'0x{target:04X}','target_bank':loc(target)['bank'],'target_symbol':symbols.get(target,f'Unresolved_{target:04X}')})
    write_csv(ROOT/'analysis/ppu_task_table.csv',ptrs)
    seeds=[0xF010,0xF0BB,0xF7B1]+[r[2] for r in REGIONS if r[4]=='code']+[int(x['target_cpu'],16) for x in ptrs]
    queue=collections.deque(seeds);decoded={};owners={};edges=[];unresolved=[]
    while queue:
        pc=queue.popleft()
        if pc in decoded:continue
        if not 0xC000<=pc<0xFFFA:
            unresolved.append({'cpu':f'0x{pc:04X}','reason':'switchable/non-ROM target: bank context not propagated','status':'UNRESOLVED'});continue
        if pc in known_data:
            unresolved.append({'cpu':f'0x{pc:04X}','reason':'candidate flow enters reviewed data','status':'CONFLICT'});continue
        n,t=d.instruction_at(pc);op,mode=m.disassemble[m.memory[pc]]
        if op=='???' or pc+n>0x10000:
            unresolved.append({'cpu':f'0x{pc:04X}','reason':'unsupported opcode or boundary','status':'UNRESOLVED'});continue
        if any(a in owners and owners[a]!=pc for a in range(pc,pc+n)):
            unresolved.append({'cpu':f'0x{pc:04X}','reason':'overlapping candidate decode','status':'CONFLICT'});continue
        decoded[pc]=(n,t,op,mode)
        for a0 in range(pc,pc+n):owners[a0]=pc
        nxt=pc+n
        def edge(target,kind):
            edges.append({'from_bank':loc(pc)['bank'],'from_cpu':f'0x{pc:04X}','from_prg_offset':loc(pc)['prg_offset'],
                'to_cpu':f'0x{target:04X}','to_bank':loc(target)['bank'] if target>=0xC000 else 'UNRESOLVED',
                'kind':kind,'status':'STATIC_REVIEWED_SOURCE' if pc in reviewed else 'CANDIDATE_SOURCE',
                'mapping_condition':'fixed-window analysis assumes MMC3 PRG mode 0; no propagated switchable bank state'})
            queue.append(target)
        if op in BRANCHES:
            v=m.memory[pc+1];edge((nxt+(v if v<128 else v-256))&65535,'branch');queue.append(nxt)
        elif op=='JSR':edge(m.memory[pc+1]|m.memory[pc+2]<<8,'call');queue.append(nxt)
        elif op=='JMP':
            if mode=='abs':edge(m.memory[pc+1]|m.memory[pc+2]<<8,'jump')
            else:unresolved.append({'cpu':f'0x{pc:04X}','reason':'indirect jump; target not inferred automatically','status':'UNRESOLVED'})
        elif op not in {'RTS','RTI','BRK'}:queue.append(nxt)
    cand=[{**loc(pc),'size':n,'bytes':bytes(m.memory[pc:pc+n]).hex(' ').upper(),'instruction':t,'status':'REVIEWED' if pc in reviewed else 'CANDIDATE_ONLY'} for pc,(n,t,op,mode) in sorted(decoded.items())]
    write_csv(ROOT/'analysis/fixed_window_candidates.csv',cand)
    write_csv(ROOT/'analysis/cross_references.csv',edges)
    unresolved=list({(x['cpu'],x['reason']):x for x in unresolved}.values())
    write_csv(ROOT/'analysis/unresolved.csv',unresolved)
    accesses=[]
    for pc,(n,t,op,mode) in sorted(decoded.items()):
        if mode not in {'zpg','zpx','zpy','abs','abx','aby','inx','iny','ind'} or op in {'JSR','JMP'}:continue
        adr=m.memory[pc+1] | (m.memory[pc+2]<<8 if n==3 else 0)
        kind='write' if op in {'STA','STX','STY'} else 'read_modify_write' if op in {'INC','DEC','ASL','LSR','ROL','ROR'} else 'read'
        accesses.append({**loc(pc),'instruction':t,'operand_base':f'0x{adr:04X}','mode':mode,'access':kind,
            'effective_address_known':mode in ('zpg','abs'),'status':'REVIEWED' if pc in reviewed else 'CANDIDATE_ONLY'})
    write_csv(ROOT/'analysis/memory_accesses.csv',accesses)
    write_csv(ROOT/'analysis/hardware_accesses.csv',[x for x in accesses if 0x2000<=int(x['operand_base'],16)<=0x4017 or (x['access']!='read' and int(x['operand_base'],16)>=0x8000)])
    # A separate raw scan: opcode-shaped data are not claimed to be executable.
    raw=[]
    regs={0x8000,0x8001,0xA000,0xA001,0xC000,0xC001,0xE000,0xE001}
    for po in range(len(p)-2):
        adr=int.from_bytes(p[po+1:po+3],'little')
        if p[po] in [0x8C,0x8D,0x8E] and adr in regs:
            raw.append({'bank':f'{po//8192:02X}','bank_offset':f'0x{po%8192:04X}','prg_offset':f'0x{po:06X}','file_offset':f'0x{po+16:06X}','opcode':f'{p[po]:02X}','register':f'0x{adr:04X}','status':'RAW_PATTERN_ONLY; not exhaustive of all addressing modes/aliases'})
    write_csv(ROOT/'analysis/mapper_raw_patterns.csv',raw)
    tags=[{'bank':f'{i:02X}','bank_offset':'0x1FFF','prg_offset':f'0x{(i+1)*8192-1:06X}','file_offset':f'0x{16+(i+1)*8192-1:06X}','last_byte':f'{p[(i+1)*8192-1]:02X}','equals_bank_number':p[(i+1)*8192-1]==i} for i in range(16)]
    write_csv(ROOT/'analysis/bank_tags.csv',tags)
    for bank,base in [(14,0xC000),(15,0xE000)]:
        lines=['; Reviewed local routines. Gaps are intentionally absent; not a standalone whole-bank file.','.setcpu "6502"','']
        for rid,name,lo,hi,kind,desc in REGIONS:
            if int(loc(lo)['bank'],16)!=bank:continue
            lines += [f'; {rid}: {desc}',f'; {loc(lo)}',f'.org ${lo:04X}',f'{name}:']
            if kind=='data':
                for pc in range(lo,hi,16):lines.append('    .byte '+','.join(f'${v:02X}' for v in m.memory[pc:min(pc+16,hi)]))
            else:
                for row in instructions:
                    pc=int(row['cpu'],16)
                    if lo<=pc<hi:
                        instruction=row['instruction'];op,mode=m.disassemble[m.memory[pc]]
                        if mode in {'abs','abx','aby'}:instruction=instruction.replace(' $',' a:$',1)
                        lines.append(f'    {instruction:24} ; {pc:04X} {row["bytes"]:8} {row["comment"]}')
            lines.append('')
        (ROOT/f'disassembly/banks/prg{bank:02X}_reviewed.asm').write_text('\n'.join(lines)+'\n')
    cb=len(reviewed);db=len(known_data)
    write_json(ROOT/'analysis/coverage.json',{'prg_total_bytes':len(p),'chr_total_bytes':131072,
        'reviewed_code_bytes':cb,'reviewed_data_bytes':db,'reviewed_code_plus_data_bytes':cb+db,
        'reviewed_prg_fraction':(cb+db)/len(p),'candidate_instruction_count':len(decoded),'candidate_decode_bytes':len(owners),
        'candidate_note':'Reachability candidates are not semantic coverage; indirect flow and bank state incomplete.',
        'semantic_metric_definition':'Union of manually reviewed code/data ranges in reviewed_ranges.csv; bounded local semantics only.',
        'rebuild_status':'not yet built; see rebuild_verification.json when present'})
    print(json.dumps({'reviewed_code_bytes':cb,'reviewed_data_bytes':db,'candidate_instructions':len(decoded),'candidate_bytes':len(owners),'unresolved_count':len(unresolved)},indent=2))
if __name__=='__main__':main()
