#!/usr/bin/env python3
"""Incremental reviewed ranges for stage 01B; retain stage 01A evidence and candidates."""
import argparse,csv,json,sys
from baseline import ROOT,verified_rom,write_csv,write_json
sys.path.insert(0,str(ROOT/'tools/vendor'))
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler

# bank, mapped CPU base, start, end-exclusive, name, kind, bounded local claim
REGIONS=[
(14,0xC000,0xC749,0xC7C7,'FixedServiceJumpTable','code','42 absolute JMP service entries; this identifies destinations, not all destination semantics.'),
(14,0xC000,0xCF50,0xCF6D,'BootFrontEndLoop','code','Map bank 09 at A000, initialize audio and call front end; carry clear loops via A00C.'),
(14,0xC000,0xCF6D,0xCFA2,'SelectInitialRoute','code','Clear 00/2D; nonzero 2C calls bank 07 A0D8 and chooses resume path using 43.'),
(14,0xC000,0xCFA2,0xCFE5,'InitializeRunContext','code','Mask 2C to five-bit index 9A and 2D to two-bit 030C; save SP at 016F and invoke initialization.'),
(14,0xC000,0xCFE5,0xD046,'PrepareMainLoop','code','Restore saved SP; initialize PPU shadows, IRQ source F83D, loop flags and per-index audio byte.'),
(14,0xC000,0xD046,0xD0B7,'FourPhaseMainLoop','code','Four D90C-synchronized phases; phase-specific call order and two D9CB mixer calls per cycle.'),
(14,0xC000,0xD0B7,0xD0BA,'RunControlGate','code','Tail jump to CE/D3/Start control gate D39F.'),
(14,0xC000,0xD0BA,0xD0D2,'CallBank08FrameGroup','code','Map 03B9 through R6 and 08 through R7; call A006,A000 then tail A009; later targets need callee bank-preservation contract.'),
(14,0xC000,0xD0D2,0xD0DC,'TailBank09Frame','code','Map R7=09 and tail jump to A000.'),
(14,0xC000,0xD0DC,0xD0F3,'CallBank07EvenGroup','code','Map R6 from 03B9 and R7=07; call A078,A07E then tail A0B1.'),
(14,0xC000,0xD0F3,0xD107,'CallBank07OddGroup','code','Map R6 from 03B9 and R7=07; call A07B then tail A0B1.'),
(14,0xC000,0xD107,0xD110,'CallBank0CAndFixedGroup','code','Call bank-0C trampoline D6D2, fixed D805, then tail D6F0; gameplay meanings unresolved.'),
(14,0xC000,0xD110,0xD126,'FinalizeFrameGroup','code','Service palette effect, map R6=06/R7=08, call A00C, then tail E2E2 scroll adjustment.'),
(14,0xC000,0xD178,0xD19A,'RestartThroughIndexTable','code','Entry D178 pushes zero; D17A can accept one from CE route; remap 9A with D25F, initialize, restore block and choose D21C/D225.'),
(14,0xC000,0xD19A,0xD1AA,'ContinueThroughIndexTable','code','Remap 9A through D27F, reset fields, restore saved eleven-byte block, then jump D21C.'),
(14,0xC000,0xD1AA,0xD210,'AdvanceThroughIndexTable','code','Load next index from D23F; FF invokes bank-09 A012 and increments 030C unless equal 03; restart at index 00.'),
(14,0xC000,0xD210,0xD225,'ReenterSceneClearFlag','code','Clear bit 20 of F8, call EEA7 and reenter CFE2, or fall through to restore path at D225.'),
(14,0xC000,0xD225,0xD23F,'RestoreTripletAndReenter','code','Index FDE0 with D3&07; copy byte to 06B9/06BA/06BB; jump CFE2. Gameplay meaning is not assigned here.'),
(14,0xC000,0xD23F,0xD25F,'NextSceneIndexTable','data','32-byte successor table; index 1B contains FF end-of-cycle marker.'),
(14,0xC000,0xD25F,0xD27F,'RestartSceneIndexTable','data','32-byte table used by D178 and D363; physical-stage correspondence unresolved.'),
(14,0xC000,0xD27F,0xD29F,'ContinueSceneIndexTable','data','32-byte table used by D19A; physical-stage correspondence unresolved.'),
(14,0xC000,0xD2F7,0xD363,'ResetRunFields','code','Reset selected fields; if 030E is zero set it to 03 and initialize 0306..030B; set digit-like buffers and call F65F.'),
(14,0xC000,0xD37F,0xD38B,'SaveElevenByteBlock','code','Copy 06C2..06CC to 06CD..06D7, high index first.'),
(14,0xC000,0xD38B,0xD396,'RestoreElevenByteBlock','code','Copy 06CD..06D7 to 06C2..06CC, high index first; fall through D396.'),
(14,0xC000,0xD396,0xD39F,'TailBank07Restore','code','Map R7=07 and tail A0C9.'),
(14,0xC000,0xD39F,0xD3C4,'CheckRunControl','code','Negative CE decrements 030E and selects D17A/D487; otherwise negative D3 blocks Start, and pressed Start enters D3C4.'),
(14,0xC000,0xD3C4,0xD459,'StartOverlayFlow','code','Save palette and CHR 47/48; invoke bank-07 overlay entries; restore palette/CHR, discard return word and jump D046.'),
(14,0xC000,0xD459,0xD469,'OverlayPalette16','data','16 palette bytes copied to 0133..0142 and 0153..0162 during Start overlay.'),
(14,0xC000,0xD487,0xD535,'InitializeCounterZeroMenu','code','Initialize PPU layout, retained-field displays and two-choice selection after 030E reaches zero.'),
(14,0xC000,0xD535,0xD588,'CounterZeroMenuLoop','code','Wait/poll; A/B/Start confirm, Up/Down/Select change 2C, draw cursor and repeat.'),
(14,0xC000,0xD588,0xD5AE,'CounterZeroMenuConfirm','code','Choice 00 jumps D19A; nonzero restores block and ED80 then JMP through RESET vector.'),
(14,0xC000,0xD5AE,0xD5B2,'CounterZeroCursorPointers','data','Two little-endian cursor pointers selected with 2C*2; pointed data not interpreted.'),
(14,0xC000,0xD90C,0xD949,'WaitNmiAndServiceAudio','code','Save X/Y, evolve 97 while 95 is nonzero, set 95=1; temporarily map 00/01 for C7C7 then restore bank tags.'),
(14,0xC000,0xD949,0xD977,'UpdateControllerState','code','Shift held-button history; poll twice and AND; compute rising edges, shift A history, restore caller X/Y from stack.'),
(14,0xC000,0xD977,0xD9CB,'ReadControllerSerial','code','Strobe 4016 high then low; read eight times, accept either low data bit, shift into 1F and return it in A.'),
(14,0xC000,0xD9CB,0xD9D7,'MixTimingStateWithX','code','97 <- ((((X+97) mod 256) XOR AA)+BD) mod 256; preserves X/Y.'),
(15,0xE000,0xE2A3,0xE2E2,'ServicePaletteEffect','code','Restore palette when 06EE=FF; decrement 03D5 and choose fixed palette colors using D9 bit 10.'),
(15,0xE000,0xE2E2,0xE2F9,'AdjustScrollOnOddEffect','code','If 03D6 is odd add 04 to 58; add 10 again when the wrapped first sum is at least F0.'),
(15,0xE000,0xF6CC,0xF6D3,'WaitCountedUpdates','code','Call D90C and decrement X until zero; initial X=00 means 256 updates.'),
(15,0xE000,0xF6D3,0xF6E0,'WaitCountedOrAStart','code','Counted wait with early exit on newly pressed A or Start; returns masked input in A.'),
(15,0xE000,0xF6E0,0xF6EA,'WaitForAStart','code','Repeat D90C until newly pressed A or Start.'),
(15,0xE000,0xF6EA,0xF6ED,'EnterInitialRunContext','code','Tail jump to fixed CFA2.'),
(7,0xA000,0xA078,0xA0DB,'Bank07ServiceJumpTable','code','33 absolute JMP entry points in R7 bank 07; callee gameplay semantics mostly unresolved.'),
(8,0xA000,0xA000,0xA012,'Bank08ServiceJumpTable','code','Six absolute JMP entry points in R7 bank 08.'),
(9,0xA000,0xA000,0xA015,'Bank09ServiceJumpTable','code','Seven absolute JMP entry points in R7 bank 09; A009 reaches front-end sequence A499.'),
(9,0xA000,0xA499,0xA555,'FrontEndSequence','code','Initialize display and animation, wait on split index 67, then poll two-choice input; preserve outcome carry across cleanup.'),
(9,0xA000,0xA555,0xA557,'FrontEndObjectXPair','data','Two X bytes 1C/E4 copied to 051B/051C by A4B9.'),
(9,0xA000,0xA557,0xA62E,'InitializeFrontEndLayout','code','Map R6=05, far-call bank07 A0BD, set tile transfer arguments, PPU split fields and IRQ source FA59.'),
(9,0xA000,0xA62E,0xA630,'FrontEndTilePair','data','Two bytes 21/00 used as a PPU transfer source at A585..A599.'),
(9,0xA000,0xA630,0xA657,'PollFrontEndChoice','code','A/Start return carry set; otherwise Select/Left/Right toggle 2C, draw cursor and return carry clear.'),
(9,0xA000,0xA672,0xA695,'DrawFrontEndCursor','code','Write one four-byte OAM sprite at index 99; choose X through 2C; increment 99.'),
(9,0xA000,0xA695,0xA697,'FrontEndCursorXPair','data','Two cursor X bytes 38/88 for selections 00/01.')
]

COMMENTS={
(14,0xCF5F):'First front-end iteration bypasses A00C. R7 has just been set to 09.',
(14,0xCF6B):'Carry is an interface result, not a global state ID.',
(14,0xCFB6):'A later TXS at CFE8 abandons intervening call frames.',
(14,0xD046):'Four-phase cycle entry. 9A indexes data, not this control-flow phase.',
(14,0xD07B):'Mixer after phase 1; X is whatever preceding calls leave.',
(14,0xD0AE):'Second explicit mixer call after phase 3.',
(14,0xD1C0):'Only FF selects end-of-cycle path; no stage-name assignment.',
(14,0xD1D3):'Equal-to-03 guard, not a general clamp of arbitrary corrupt values.',
(14,0xD230):'Table bytes independently observed; HP semantics deliberately not imported from user notes.',
(14,0xD33E):'This loop initializes overlapping buffers; 60/61 alone does not prove complete numeric encoding.',
(14,0xD3A7):'1F contains newly pressed buttons after D90C.',
(14,0xD3B7):'030E precondition is nonzero; zero would wrap to FF here.',
(14,0xD454):'Discard the D0B7 caller return word, then restart the four-phase cycle.',
(14,0xD53F):'Mask D0 = A, B, Start under verified serial-to-bit mapping.',
(14,0xD5AB):'Indirect JMP loads the supplied ROM reset vector F010.',
(14,0xD910):'Always executes at least once, even if 95 was already zero.',
(14,0xD914):'CMP supplies carry equal to the incremented byte bit 7; ROL therefore rotates that byte.',
(14,0xD918):'NMI writes 00 at F116 under the documented normal 96=0/1 condition.',
(14,0xD926):'Read tags before mapping audio banks; shared-call restoration depends on correct bank tags.',
(14,0xD949):'0714 <- old 0713; 0713 <- previous held byte.',
(14,0xD95E):'Held = sample1 AND sample2, not a retry-until-equal loop.',
(14,0xD962):'Pressed = held AND NOT previous held.',
(14,0xD96F):'ASL places A-button bit 7 in carry; ROL 21 appends it to an eight-update history.',
(14,0xD983):'AND 03 + CMP 01 accepts D0 OR D1; other six bus bits are ignored.',
(14,0xD9CB):'Timing state consumer X is supplied implicitly by preceding code.',
(15,0xE2F3):'Second addition intentionally skips the F0..FF interval for relevant scroll values.',
(15,0xF6CF):'Initial zero wraps to FF and takes 256 calls to reach zero.',
(9,0xA4DD):'Busy wait on IRQ-owned index; exact scanline and screen effect remain unobserved.',
(9,0xA54C):'Save outcome flags across cleanup calls and restore before RTS.',
(9,0xA633):'Mask 90 confirms A or Start. B does not confirm this front-end choice.',
(9,0xA63B):'Mask 23 combines Select, Left and Right; multiple set bits still toggle only once.'
}

# Fixed-window sources immediately dominated by explicit R7 mapping. Later calls after
# unreviewed callees stay unresolved; no optimistic propagation across those callees.
R7_AT_CALL={0xCF68:9,0xCF7D:7,0xCFC3:9,0xD0C9:8,0xD0D9:9,0xD0EA:7,
0xD101:7,0xD120:8,0xD18E:7,0xD1CB:9,0xD1EA:8,0xD20D:9,0xD39C:7}

def read(rel):
    with (ROOT/rel).open() as f:return list(csv.DictReader(f))

def loc(bank,base,pc):
    off=pc-base;po=bank*8192+off
    assert 0<=off<8192
    condition='MMC3 PRG mode 0' if bank==14 else 'last bank fixed at E000' if bank==15 else f'MMC3 PRG mode 0; R7={bank:02X} at A000'
    return {'bank':f'{bank:02X}','cpu':f'0x{pc:04X}','bank_offset':f'0x{off:04X}',
            'prg_offset':f'0x{po:06X}','file_offset':f'0x{po+16:06X}','mapping_condition':condition}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();b,_=verified_rom(a.rom)
    prg=b[16:0x20010];ranges=[];ins=[];func=[];evidence=[];edges=[];access=[];tables=[]
    for i,(bank,base,lo,hi,name,kind,desc) in enumerate(REGIONS,1):
        rid=f'B{i:02d}';m=MPU();m.memory[base:base+8192]=prg[bank*8192:(bank+1)*8192];d=Disassembler(m)
        ranges.append({'id':rid,'symbol':name,**loc(bank,base,lo),'size':hi-lo,'end_cpu_exclusive':f'0x{hi:04X}','classification':kind,'status':'STATIC_REVIEWED','description':desc})
        evidence.append({'id':rid,'class':'STATIC','subject':name,'source':f'disassembly/banks/prg{bank:02X}.asm','location':f'PRG{bank:02X}:{lo:04X}-{hi:04X} exclusive','claim':desc,'confidence':'high for local effect; unreviewed callees and gameplay labels explicitly bounded'})
        if kind=='data':continue
        func.append({'id':rid,'name':name,**loc(bank,base,lo),'size':hi-lo,'status':'STATIC_REVIEWED','description':desc,'callers_callees':'cross_references.csv; multi-entry code ranges are not exact function-count claims'})
        pc=lo
        while pc<hi:
            n,t=d.instruction_at(pc);op,mode=m.disassemble[m.memory[pc]]
            assert op!='???' and pc+n<=hi,(bank,hex(pc),t)
            ins.append({'region_id':rid,'symbol':name,**loc(bank,base,pc),'size':n,'bytes':bytes(m.memory[pc:pc+n]).hex(' ').upper(),'instruction':t,'comment':COMMENTS.get((bank,pc),'')})
            target=None;k=None
            if op in {'BPL','BMI','BVC','BVS','BCC','BCS','BNE','BEQ'}:
                v=m.memory[pc+1];target=(pc+n+(v if v<128 else v-256))&65535;k='branch'
            elif op in {'JSR','JMP'} and mode=='abs':target=m.memory[pc+1]|m.memory[pc+2]<<8;k='call' if op=='JSR' else 'jump'
            if target is not None:
                tb=15 if target>=0xE000 else 14 if target>=0xC000 else bank if base==0xA000 and 0xA000<=target<0xC000 else R7_AT_CALL.get(pc) if bank==14 and 0xA000<=target<0xC000 else None
                edges.append({'from_bank':f'{bank:02X}','from_cpu':f'0x{pc:04X}','from_prg_offset':loc(bank,base,pc)['prg_offset'],'to_cpu':f'0x{target:04X}','to_bank':f'{tb:02X}' if tb is not None else 'UNRESOLVED','kind':k,'status':'STATIC_REVIEWED_SOURCE','mapping_condition':loc(bank,base,pc)['mapping_condition']+'; target bank unresolved across unknown callees' if tb is None else 'mode 0; fixed target, same mapped source window, or explicit R7 domination'})
                if name.endswith('JumpTable'):tables.append({'group':name,**loc(bank,base,pc),'target_cpu':f'0x{target:04X}','target_bank':f'{tb:02X}' if tb is not None else 'UNRESOLVED','callee_semantics':'see reviewed ranges; otherwise unresolved'})
            if mode in {'zpg','zpx','zpy','abs','abx','aby','inx','iny','ind'} and op not in {'JSR','JMP'}:
                adr=m.memory[pc+1] | (m.memory[pc+2]<<8 if n==3 else 0)
                ak='write' if op in {'STA','STX','STY'} else 'read_modify_write' if op in {'INC','DEC','ASL','LSR','ROL','ROR'} else 'read'
                access.append({**loc(bank,base,pc),'instruction':t,'operand_base':f'0x{adr:04X}','mode':mode,'access':ak,'effective_address_known':mode in ('zpg','abs'),'status':'REVIEWED'})
            pc+=n
    all_ranges=[r for r in read('analysis/reviewed_ranges.csv') if not r['id'].startswith('B')]+ranges
    all_ins=[r for r in read('analysis/reviewed_instructions.csv') if not r['region_id'].startswith('B')]+ins
    all_ranges.sort(key=lambda r:int(r['prg_offset'],16));all_ins.sort(key=lambda r:int(r['prg_offset'],16))
    covered=set();code=set();data=set()
    for r in all_ranges:
        lo=int(r['prg_offset'],16);span=set(range(lo,lo+int(r['size'])));assert not covered&span
        covered|=span;(code if r['classification']=='code' else data).update(span)
    for rel,oldfield,new in [('analysis/reviewed_ranges.csv','id',all_ranges),('analysis/reviewed_instructions.csv','region_id',all_ins)]:write_csv(ROOT/rel,new)
    for rel,new in [('analysis/functions.csv',func),('analysis/evidence.csv',evidence)]:
        write_csv(ROOT/rel,[r for r in read(rel) if not r['id'].startswith('B')]+new)
    def is_new(bank,pc):return any(int(r['bank'],16)==bank and int(r['cpu'],16)<=pc<int(r['end_cpu_exclusive'],16) for r in ranges)
    for rel,new,bk,pc in [('analysis/cross_references.csv',edges,'from_bank','from_cpu'),('analysis/memory_accesses.csv',access,'bank','cpu')]:
        write_csv(ROOT/rel,[r for r in read(rel) if not is_new(int(r[bk],16),int(r[pc],16))]+new)
    accesses=read('analysis/memory_accesses.csv')
    write_csv(ROOT/'analysis/hardware_accesses.csv',[r for r in accesses if 0x2000<=int(r['operand_base'],16)<=0x4017 or r['access']!='read' and int(r['operand_base'],16)>=0x8000])
    candidates=read('analysis/fixed_window_candidates.csv')
    instruction_keys={(r['bank'],r['cpu']) for r in all_ins}
    for r in candidates:
        if (r['bank'],r['cpu']) in instruction_keys:r['status']='REVIEWED'
        elif is_new(int(r['bank'],16),int(r['cpu'],16)):r['status']='CONFLICT_WITH_REVIEWED_RANGE'
    write_csv(ROOT/'analysis/fixed_window_candidates.csv',candidates)
    write_csv(ROOT/'analysis/service_jump_tables.csv',tables)
    seq=[]
    for i in range(32):
        seq.append({'index_hex':f'{i:02X}','next_hex':f'{prg[14*8192+0x123F+i]:02X}','restart_hex':f'{prg[14*8192+0x125F+i]:02X}','continue_hex':f'{prg[14*8192+0x127F+i]:02X}','physical_stage_name':'UNRESOLVED'})
    write_csv(ROOT/'analysis/scene_index_routes.csv',seq)
    phases=[]
    for phase,lo,hi in [(0,0xD04E,0xD066),(1,0xD066,0xD081),(2,0xD081,0xD099),(3,0xD099,0xD0B4)]:
        for r in ins:
            pc=int(r['cpu'],16)
            if r['bank']=='0E' and lo<=pc<hi and r['instruction'].startswith('JSR'):
                target=int(r['instruction'].split('$')[1],16)
                phases.append({'phase':phase,'call_cpu':r['cpu'],'target_cpu':f'0x{target:04X}','target_bank':'0E','target_name':next((x['symbol'] for x in all_ranges if x['bank']=='0E' and int(x['cpu'],16)==target),'UNREVIEWED'),'timing':'one D90C handshake per phase; real frame rate not measured'})
    write_csv(ROOT/'analysis/main_loop_phases.csv',phases)
    cov=json.loads((ROOT/'analysis/coverage.json').read_text())
    cov.update({'reviewed_code_bytes':len(code),'reviewed_data_bytes':len(data),'reviewed_code_plus_data_bytes':len(covered),'reviewed_prg_fraction':len(covered)/131072,'reviewed_code_range_count':sum(r['classification']=='code' for r in all_ranges),'reviewed_data_range_count':sum(r['classification']=='data' for r in all_ranges),'stage01B_added_bytes':sum(int(r['size']) for r in ranges),'rebuild_status':'see analysis/rebuild_verification.json; matching does not establish full semantics'})
    write_json(ROOT/'analysis/coverage.json',cov)
    write_json(ROOT/'analysis/stage01B_static_summary.json',{'new_ranges':len(ranges),'new_instructions':len(ins),'new_bytes':sum(int(r['size']) for r in ranges),'service_jump_entries':len(tables),'main_loop_phase_calls':len(phases),'unresolved_targets_from_new_code':[r for r in edges if r['to_bank']=='UNRESOLVED'],'candidate_unresolved_file':'analysis/unresolved.csv is the preserved stage01A candidate traversal, not a current global unresolved count'})
    print(json.dumps(cov,indent=2))
if __name__=='__main__':main()
