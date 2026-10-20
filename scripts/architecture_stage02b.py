#!/usr/bin/env python3
"""Stage 02B: bounded progression, collectible and healing-effect reconstruction.

Retains A/B/C evidence. Unreviewed table targets are not promoted to code coverage.
"""
import argparse,json
from baseline import ROOT,verified_rom,write_csv,write_json
from architecture_stage01b import read,loc,MPU,Disassembler

REGIONS=[]
def region(bank,lo,hi,name,kind,description):
    base=0xC000 if bank==14 else 0xE000 if bank==15 else 0xA000
    REGIONS.append((bank,base,lo,hi,name,kind,description))
for bank,entries in [
 (7,[
 (0xAE3A,0xAE93,'InitializeSelectedSpellObject','code','Clear three reserved active flags; 06BD selects encoded type; initialize global slot3, flags88/8C, player position and zero velocities; refresh HUD icon.'),
 (0xAE93,0xAEA0,'SelectedSpellObjectTypes','data','Thirteen bytes for selector00..0C; 00/01 map70/72 healing handlers,0C disables slot3. Full spell identities unresolved.'),
 (0xAEC6,0xAEF7,'SnapshotPlayerProgression','code','Save level, current HP, MP, EXP and two flag bytes in eleven-byte block06C2..06CC.'),
 (0xAEF7,0xAF28,'RestorePlayerProgression','code','Restore snapshot fields then tail to B7F4, which overwrites restored current HP with full table capacity; does not write06BB.'),
 (0xB7F4,0xB829,'RefreshProgressionDerivedValues','code','D3&0F indexes tables; for valid0..7 set current/display HP to full capacity, copy maxMP and nextEXP; leave06BB unchanged.'),
 (0xB829,0xB83C,'CompareCurrentMpToMaximum','code','Compare three base60 decimal digits most significant first; return carry set iff currentMP exceeds maxMP.')]),
 (8,[
 (0xA012,0xA028,'DispatchCollisionWorkPhase','code','Skip when A1 bit40/80 set; otherwise A1 indexes six split pointers. Valid low selector0..5.'),
 (0xA028,0xA034,'CollisionWorkPhaseTargets','data','Six low bytes followed by six high bytes; index0 returns, index4 scans pickups directly.'),
 (0xA034,0xA05B,'CollisionWorkPhaseEntries','code','Phase-specific wrappers; preserve explicit unreviewed collision/attack callees.'),
 (0xA05B,0xA075,'GateCollisionWorkAndUnwind','code','03D8/03D9 or D3&A0 may discard own return address and return caller-of-caller; one partial gate maps CHR R1=2.'),
 (0xA14F,0xA197,'ScanPlayerCollectibles','code','Scan indices04EF down to1; types40..6F, active flag, low-coordinate overlap and signed velocity gate precede effect dispatch.'),
 (0xA528,0xA54D,'TestPlayerPickupRectangle','code','Two wrapped low-byte inequalities; carry clear means overlap. Does not consult high coordinate bytes.'),
 (0xA64D,0xA669,'DispatchCollectibleEffect','code','Require type40..6F, clear facing bit, use A629+evenType pointer then JMP(2C).'),
 (0xA669,0xA699,'CollectibleEffectPointers','data','Twenty-four little-endian targets for paired types40/41..6E/6F; twelve entries point to unreviewed A7DB.'),
 (0xA699,0xA6AB,'CollectExtraAttempt','code','Deactivate collectible; increment030E unless exactly0A; successful increment requests soundDC.'),
 (0xA6AB,0xA6C4,'CollectExperienceEntries','code','Deactivate collectible and add10,30 or50 decimal EXP through common digit accumulator.'),
 (0xA6C4,0xA73D,'AddExperienceAndCheckLevel','code','Add base60 decimal digits; overflow saturates9999 and returns early. Otherwise compare next threshold and advance at most one level up to7, update maxima/threshold and spawn effect.'),
 (0xA73D,0xA78A,'CollectMagicPoints','code','Add5 or10 decimal MP; carry between base60 digits, saturate999 then clamp to F5..F7 maximum; deactivate collectible and request sound2B.'),
 (0xA78A,0xA7A3,'CollectHealingHeart','code','Add10 hex raw HP and cap at06BB in valid HP domain; deactivate collectible, request soundA1.'),
 (0xA7A3,0xA7AF,'CollectScoreHundred','code','Deactivate collectible; request sound2B; A=12 tails to C746/D8B5 for100 decimal score.'),
 (0xA7AF,0xA7B5,'DeactivateCollectible','code','Set057F,Y to zero; preserve X/Y.'),
 (0xA7B5,0xA7CB,'CollectSceneTransition','code','Clear audio commands, deactivate, copy0593,Y to scene9A then call fade C788 and tail C77F; downstream transition outside this range.'),
 (0xA7CB,0xA7DB,'CollectDamageHazard','code','A7CB deactivates first; A7CE entry does not. If D3 nonnegative, tail to damage4 with carry from player facing bit.'),
 (0xA878,0xA8A6,'SpawnLevelUpObject','code','Allocate collectible-relative slot; if available, type96 active80 at player position with velocityY=FD and velocityX=0.')]),
 (9,[
 (0xAB15,0xAB2D,'SelectedSpellSpritePointers','data','Twelve sprite pointers from generic object table, corresponding to even object types70..86.'),
 (0xABF7,0xAC0F,'SelectedSpellHandlerPointers','data','Twelve handler pointers; types70/72 target B6BA/B6CD. Remaining target behavior not inferred.'),
 (0xB6BA,0xB6CD,'HealSpellTwoCells','code','New Select bit20 triggers cost60 decimal MP; on success add20 hex raw HP through BD98.'),
 (0xB6CD,0xB6DF,'HealSpellFourCells','code','New Select bit20 triggers cost90 decimal MP; on success add40 hex raw HP through BD98.'),
 (0xBD46,0xBD98,'SpendMagicPoints','code','A packed decimal cost;01A5 nonzero bypasses cost before D3 bit80 gate. Subtract base60 digits with borrow; insufficient MP rolls back all three digits and returns carry set.'),
 (0xBD98,0xBDA8,'AddHpClamped','code','Add raw A to06B9 and cap to06BB; valid normal HP plus supported heal does not overflow the eight-bit ADC.'),
 (0xBE90,0xBF0B,'UpdateAndDrawObjects','code','Increment object clocks, scan04EF+4 global slots, apply flags/parity gates, dispatch handlers, integrate/cull, preserve reserved slot3 offscreen, draw visible sprites.'),
 (0xBF3E,0xBF68,'DispatchObjectHandler','code','Even0568,X indexes sprite tableAAA5 and handler tableAB87; load B6/B7 and tail JMP(2C).'),
 (0xBF68,0xBFD3,'MoveAndCullObject','code','Flag40 skips velocity integration; signed X/Y velocities update coordinates. Low Y>=D8 or nonzero relative X high culls. Y high scratch subtract uses carry from CMP D8.')]),
 (14,[
 (0xC746,0xC749,'AddScoreService','code','Tail JMP D8B5 in fixed bank0E.'),
 (0xD8B5,0xD90C,'AddScoreAndCheckAttemptAward','code','A high nibble increment, low3 digit position; six base20 decimal digits. Overflow clamps999999 and skips awards; otherwise at most one threshold award, advancing threshold by6 even at attempts cap0A.')]),
 (15,[
 (0xE0ED,0xE0FF,'FindFreeCollectibleSlot','code','Scan04EF-1 down to1 for nonnegative057F,Y, return A=0; full pool A=FF. Tested valid slot counts>=2.'),
 (0xF65F,0xF681,'RefreshSelectedSpellIcon','code','Copy four tile IDs indexed06BD*4 fromFF2A to0185..0188; A0=16, fall through HUD staging.'),
 (0xF681,0xF6C1,'BuildLevelAndAttemptsHud','code','Stage icon and fixed tiles; level digit=(D3&7)+60, attempts digit=030E+5F, displaying internal attempts minus1.'),
 (0xFDA8,0xFDC8,'NextExperienceThresholds','data','Eight four-byte MSD-first base60 decimal thresholds1000..7000,9999 indexed by current level.'),
 (0xFDC8,0xFDE0,'MaximumMpByLevel','data','Eight three-byte MSD-first base60 decimal maxima100,200,300,400,500,600,700,999.'),
 (0xFDE8,0xFE0C,'ExtraAttemptScoreThresholds','data','Six six-byte MSD-first base20 thresholds10000,50000,100000,200000,500000,999999. Last sentinel is not followed by another reviewed threshold.'),
 (0xFF2A,0xFF5E,'SelectedSpellIconTiles','data','Thirteen four-tile glyph groups for06BD0..0C; visual identity not independently rendered.')])
]:
    for lo,hi,name,kind,desc in entries:region(bank,lo,hi,name,kind,desc)

COMMENTS={
 (7,0xB7F4):'Only low4 are masked: table domain established here is0..7, not all nibble values.',
 (8,0xA072):'PLA; PLA; RTS deliberately drops the immediate caller continuation.',
 (8,0xA6D9):'Overflow clamps all EXP digits and returns before level or sound checks.',
 (8,0xA6FD):'Unmasked D3 used as HP table index after INC. Valid level-only D3 is0..7; high flags require caller invariants.',
 (8,0xA69F):'Equality to0A blocks increment; not a greater-than-or-equal clamp.',
 (9,0xBD46):'Cost-bypass flag is checked before the D3 negative-state guard; its activation path is not established.',
 (9,0xBD8A):'Rollback preserves current MP on insufficient funds, but scratch bytes can change.',
 (9,0xBD98):'No carry-overflow handling; assertions about min(HP+heal,max) require valid HP/cost domain.',
 (14,0xD8F4):'Threshold advancement and attempt cap require separate interpretation; see bounded report.'
}
R7_AT_CALL={}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();rom,_=verified_rom(a.rom);prg=rom[16:0x20010]
    ranges=[];ins=[];func=[];evidence=[];edges=[];access=[]
    for i,(bank,base,lo,hi,name,kind,desc) in enumerate(REGIONS,1):
        rid=f'D{i:02d}';m=MPU();m.memory[base:base+8192]=prg[bank*8192:(bank+1)*8192];d=Disassembler(m)
        r={'id':rid,'symbol':name,**loc(bank,base,lo),'size':hi-lo,'end_cpu_exclusive':f'0x{hi:04X}','classification':kind,'status':'STATIC_REVIEWED','description':desc};ranges.append(r)
        evidence.append({'id':rid,'class':'STATIC','subject':name,'source':f'disassembly/banks/prg{bank:02X}.asm','location':f'PRG{bank:02X}:{lo:04X}-{hi:04X} exclusive','claim':desc,'confidence':'high for bounded local effect; see explicit input domains and unreviewed callees'})
        if kind=='data':continue
        func.append({'id':rid,'name':name,**loc(bank,base,lo),'size':hi-lo,'status':'STATIC_REVIEWED','description':desc,'callers_callees':'cross_references.csv; ranges may have multiple entry points'})
        pc=lo
        while pc<hi:
            n,t=d.instruction_at(pc);op,mode=m.disassemble[m.memory[pc]];assert op!='???' and pc+n<=hi,(bank,hex(pc),t)
            ins.append({'region_id':rid,'symbol':name,**loc(bank,base,pc),'size':n,'bytes':bytes(m.memory[pc:pc+n]).hex(' ').upper(),'instruction':t,'comment':COMMENTS.get((bank,pc),'')})
            target=None;k=None
            if op in {'BPL','BMI','BVC','BVS','BCC','BCS','BNE','BEQ'}:
                v=m.memory[pc+1];target=(pc+n+(v if v<128 else v-256))&65535;k='branch'
            elif op in {'JSR','JMP'} and mode=='abs':target=m.memory[pc+1]|m.memory[pc+2]<<8;k='call' if op=='JSR' else 'jump'
            if target is not None:
                tb=15 if target>=0xE000 else 14 if target>=0xC000 else bank if base==0xA000 and 0xA000<=target<0xC000 else R7_AT_CALL.get(pc)
                edges.append({'from_bank':f'{bank:02X}','from_cpu':f'0x{pc:04X}','from_prg_offset':loc(bank,base,pc)['prg_offset'],'to_cpu':f'0x{target:04X}','to_bank':f'{tb:02X}' if tb is not None else 'UNRESOLVED','kind':k,'status':'STATIC_REVIEWED_SOURCE','mapping_condition':'mode0; fixed target, same resident window, or explicit R7 domination' if tb is not None else 'target bank unresolved across unreviewed callees'})
            if mode in {'zpg','zpx','zpy','abs','abx','aby','inx','iny','ind'} and op not in {'JSR','JMP'}:
                adr=m.memory[pc+1]|(m.memory[pc+2]<<8 if n==3 else 0);ak='write' if op in {'STA','STX','STY'} else 'read_modify_write' if op in {'INC','DEC','ASL','LSR','ROL','ROR'} else 'read'
                access.append({**loc(bank,base,pc),'instruction':t,'operand_base':f'0x{adr:04X}','mode':mode,'access':ak,'effective_address_known':mode in ('zpg','abs'),'status':'REVIEWED'})
            pc+=n
    all_ranges=[r for r in read('analysis/reviewed_ranges.csv') if not r['id'].startswith('D')]+ranges
    all_ins=[r for r in read('analysis/reviewed_instructions.csv') if not r['region_id'].startswith('D')]+ins
    all_ranges.sort(key=lambda r:int(r['prg_offset'],16));all_ins.sort(key=lambda r:int(r['prg_offset'],16))
    covered=set();code=set();data=set()
    for r in all_ranges:
        lo=int(r['prg_offset'],16);span=set(range(lo,lo+int(r['size'])));assert not covered&span,r;covered|=span;(code if r['classification']=='code' else data).update(span)
    write_csv(ROOT/'analysis/reviewed_ranges.csv',all_ranges);write_csv(ROOT/'analysis/reviewed_instructions.csv',all_ins)
    for rel,new in [('analysis/functions.csv',func),('analysis/evidence.csv',evidence)]:write_csv(ROOT/rel,[r for r in read(rel) if not r['id'].startswith('D')]+new)
    def is_new(bank,pc):return any(int(r['bank'],16)==bank and int(r['cpu'],16)<=pc<int(r['end_cpu_exclusive'],16) for r in ranges)
    for rel,new,bk,pc in [('analysis/cross_references.csv',edges,'from_bank','from_cpu'),('analysis/memory_accesses.csv',access,'bank','cpu')]:write_csv(ROOT/rel,[r for r in read(rel) if not is_new(int(r[bk],16),int(r[pc],16))]+new)
    accesses=read('analysis/memory_accesses.csv');write_csv(ROOT/'analysis/hardware_accesses.csv',[r for r in accesses if 0x2000<=int(r['operand_base'],16)<=0x4017 or r['access']!='read' and int(r['operand_base'],16)>=0x8000])
    candidates=read('analysis/fixed_window_candidates.csv');keys={(r['bank'],r['cpu']) for r in all_ins}
    for r in candidates:
        if (r['bank'],r['cpu']) in keys:r['status']='REVIEWED'
        elif is_new(int(r['bank'],16),int(r['cpu'],16)):r['status']='CONFLICT_WITH_REVIEWED_RANGE'
    write_csv(ROOT/'analysis/fixed_window_candidates.csv',candidates)


    def byte(b,a):return prg[b*8192+(a&8191)]
    def raw(b,a,n):return bytes(byte(b,a+j) for j in range(n))
    def word(b,a):return byte(b,a)|byte(b,a+1)<<8
    def decimal(bs,bias):return int(''.join(str(x-bias) for x in bs))
    def source(b,a):return {f'source_{k}':v for k,v in loc(b,0xC000 if b==14 else 0xE000 if b==15 else 0xA000,a).items()}
    levels=[]
    for i in range(8):
        exp=raw(15,0xFDA8+4*i,4);mp=raw(15,0xFDC8+3*i,3);hp=byte(15,0xFDE0+i)
        levels.append({'level':i,'next_EXP_decimal':decimal(exp,0x60),'EXP_bytes_MSD_first':exp.hex(' ').upper(),'maximum_MP_decimal':decimal(mp,0x60),'MP_bytes_MSD_first':mp.hex(' ').upper(),'maximum_HP_raw':f'0x{hp:02X}','HP_cells':hp//16,**source(15,0xFDA8+4*i),'MP_source_cpu':f'0x{0xFDC8+3*i:04X}','MP_source_prg_offset':f'0x{15*8192+0x1DC8+3*i:06X}','MP_source_file_offset':f'0x{16+15*8192+0x1DC8+3*i:06X}','HP_source_cpu':f'0x{0xFDE0+i:04X}','HP_source_prg_offset':f'0x{15*8192+0x1DE0+i:06X}','HP_source_file_offset':f'0x{16+15*8192+0x1DE0+i:06X}'})
    write_csv(ROOT/'analysis/progression_levels.csv',levels)
    effects={0xA78A:'HP +16 raw, clamp to maximum',0xA73D:'MP +5 decimal',0xA744:'MP +10 decimal',0xA6AB:'EXP +10 decimal',0xA6B4:'EXP +30 decimal',0xA6BD:'EXP +50 decimal',0xA7A3:'score +100 decimal',0xA7B5:'scene transition from object field',0xA7DB:'UNREVIEWED shared handler; no spell identity assigned',0xA7CB:'deactivate then damage4 raw',0xA699:'extra attempt unless exactly10',0xA7CE:'damage4 raw without initial deactivation'}
    pickups=[];indirect=[r for r in read('analysis/indirect_dispatch_tables.csv') if not r['group'].startswith('D_')]
    def edge(group,bank,dispatch,index,selector,tablebank,table,targetbank,target,semantics):
        indirect.append({'group':group,'dispatch_bank':f'{bank:02X}','dispatch_cpu':f'0x{dispatch:04X}','index':index,'selector':selector,'table_bank':f'{tablebank:02X}','table_cpu':table,'target_bank':f'{targetbank:02X}','target_cpu':f'0x{target:04X}','target_semantics':semantics})
    for i in range(24):
        table=0xA669+2*i;target=word(8,table)
        pickups.append({'type_even':f'0x{0x40+2*i:02X}','type_odd':f'0x{0x41+2*i:02X}',**source(8,table),'target_bank':'08','target_cpu':f'0x{target:04X}','target_prg_offset':f'0x{8*8192+(target&8191):06X}','target_file_offset':f'0x{16+8*8192+(target&8191):06X}','effect':effects[target],'handler_review':'UNREVIEWED' if target==0xA7DB else 'STATIC_REVIEWED','visual_pickup_identity':'UNRESOLVED'})
        edge('D_Collectibles',8,0xA665,i,'056B,Y in40..6F; even type',8,f'0x{table:04X}',8,target,effects[target])
    write_csv(ROOT/'analysis/pickup_effects.csv',pickups)
    spells=[]
    for i in range(13):
        encoded=byte(7,0xAE93+i);typ=encoded&0xFE;handler=word(9,0xAB87+typ) if encoded else None;sprite=word(9,0xAAA5+typ) if encoded else None
        spells.append({'selected_index':f'0x{i:02X}','encoded_type':f'0x{encoded:02X}','object_type_even':f'0x{typ:02X}' if encoded else '', 'initial_flags':f'0x{0x8C if encoded&1 else 0x88:02X}' if encoded else '0x00',**source(7,0xAE93+i),'dispatch_bank':'09' if encoded else '', 'handler_table_cpu':f'0x{0xAB87+typ:04X}' if encoded else '', 'handler_table_prg_offset':f'0x{9*8192+0xB87+typ:06X}' if encoded else '', 'handler_table_file_offset':f'0x{16+9*8192+0xB87+typ:06X}' if encoded else '', 'handler_cpu':f'0x{handler:04X}' if encoded else '', 'handler_prg_offset':f'0x{9*8192+(handler&8191):06X}' if encoded else '', 'handler_file_offset':f'0x{16+9*8192+(handler&8191):06X}' if encoded else '', 'sprite_table_cpu':f'0x{0xAAA5+typ:04X}' if encoded else '', 'sprite_pointer_cpu':f'0x{sprite:04X}' if encoded else '', 'MP_cost_decimal':60 if i==0 else 90 if i==1 else '', 'HP_gain_raw':32 if i==0 else 64 if i==1 else '', 'effect':'heal2cells' if i==0 else 'heal4cells' if i==1 else 'none' if not encoded else 'UNREVIEWED'})
        if encoded:edge('D_SelectedSpellObjects',9,0xBF65,i,'0568,X&FE; selected effect global slot3',9,f'0x{0xAB87+typ:04X}',9,handler,spells[-1]['effect'])
    write_csv(ROOT/'analysis/selected_spell_dispatch.csv',spells)
    for i in range(6):
        target=byte(8,0xA028+i)|byte(8,0xA02E+i)<<8
        edge('D_CollisionPhases',8,0xA024,i,'A1 low phase0..5; bitsC0 skip',8,f'0x{0xA028+i:04X} + high at 0x{0xA02E+i:04X}',8,target,'phase entry; downstream code may remain unreviewed')
    write_csv(ROOT/'analysis/indirect_dispatch_tables.csv',indirect)
    thresholds=[]
    for i in range(6):
        bs=raw(15,0xFDE8+i*6,6)
        thresholds.append({'index':i,'RAM_030F_byte_offset':i*6,'score_decimal':decimal(bs,0x20),'ROM_bytes_MSD_first':bs.hex(' ').upper(),**source(15,0xFDE8+i*6),'caveat':'sentinel; exact comparison can advance beyond reviewed table; ordinary multiples10/100 reach saturation by early-return overflow' if i==5 else 'one threshold maximum per call'})
    write_csv(ROOT/'analysis/score_thresholds.csv',thresholds)
    formats=[]
    for address,n,bias,name,cap in [(0xEA,3,0x60,'CurrentMP','level-dependent100..999'),(0xED,4,0x60,'CurrentEXP','9999'),(0xF1,4,0x60,'NextEXPThreshold','1000..7000 or9999'),(0xF5,3,0x60,'MaximumMP','100..700 or999'),(0x306,6,0x20,'Score','999999')]:
        formats.append({'name':name,'RAM_address':f'0x{address:04X}','digits':n,'digit_bias':f'0x{bias:02X}','RAM_order':'least significant first','numeric_domain':'unpacked decimal digit0..9 plus bias; not binary and not packed BCD','cap_or_values':cap})
    write_csv(ROOT/'analysis/numeric_formats.csv',formats)
    snapshot=[]
    for address,size,live,name in [(0x6C2,1,0xD3,'level low3'),(0x6C3,1,0x6B9,'HP; overwritten full by derived-value restore'),(0x6C4,3,0xEA,'current MP'),(0x6C7,4,0xED,'current EXP'),(0x6CB,2,0x6BE,'two progression flag bytes; full bit meaning unresolved')]:
        snapshot.append({'snapshot_RAM':f'0x{address:04X}','size':size,'live_RAM':f'0x{live:04X}','meaning':name,'save_source':'07:AEC6','restore_source':'07:AEF7 + B7F4','second_snapshot_copy_RAM':f'0x{address+11:04X}'})
    write_csv(ROOT/'analysis/progression_snapshot_layout.csv',snapshot)
    cov=json.loads((ROOT/'analysis/coverage.json').read_text());cov.update({'reviewed_code_bytes':len(code),'reviewed_data_bytes':len(data),'reviewed_code_plus_data_bytes':len(covered),'reviewed_prg_fraction':len(covered)/131072,'reviewed_code_range_count':sum(r['classification']=='code' for r in all_ranges),'reviewed_data_range_count':sum(r['classification']=='data' for r in all_ranges),'stage02B_added_bytes':sum(int(r['size']) for r in ranges)})
    write_json(ROOT/'analysis/coverage.json',cov)
    result={'new_ranges':len(ranges),'new_code_ranges':sum(r['classification']=='code' for r in ranges),'new_data_ranges':sum(r['classification']=='data' for r in ranges),'new_instructions':len(ins),'new_bytes':sum(int(r['size']) for r in ranges),'levels':len(levels),'pickup_type_pairs':len(pickups),'selected_spell_entries':len(spells),'new_indirect_edges':sum(r['group'].startswith('D_') for r in indirect),'unresolved_targets_from_new_code':[r for r in edges if r['to_bank']=='UNRESOLVED']}
    write_json(ROOT/'analysis/stage02B_static_summary.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
