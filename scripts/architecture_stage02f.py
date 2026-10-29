#!/usr/bin/env python3
"""Stage02F bounded melee/contact, collision schemas, enemy dispatch and HP aggregate.
Replaces H-series only. Retains prior reviewed ranges and historical CPU evidence.
"""
import argparse,json
from baseline import ROOT,verified_rom,write_csv,write_json
from architecture_stage01b import read,loc as oldloc,MPU,Disassembler
def loc(bank,base,pc):
    r=oldloc(bank,base,pc)
    if base==0x8000:r['mapping_condition']=f'MMC3 mode0; R6={bank:02X} at8000'
    return r
REGIONS=[]
def region(bank,lo,hi,name,kind,desc):
    base=0x8000 if bank in (6,10,11) else 0xC000 if bank==14 else 0xA000
    REGIONS.append((bank,base,lo,hi,name,kind,desc))
region(6,33172,33273,'PlayerAttackVerticalOffset','data','101 bytes indexed CD>>1 byA452. Separate from player hurtbox tables8000..8193.')
region(6,33273,33374,'PlayerAttackVerticalExtent','data','101 unsigned extent terms; modular comparison includes enemy body extent. Zero size can still act as a point test.')
region(6,33374,33475,'PlayerAttackMinusXOffset','data','101 signed offsets for subtract endpoint, exchanged with plus side on oddCD.')
region(6,33475,33576,'PlayerAttackPlusXOffset','data','101 signed offsets for add endpoint; A452 replaces out-of-camera-page endpoint with camera origin.')
region(6,33576,33677,'PlayerMeleeDamageRequests','data','101 raw damage requests indexed by CD>>1 after first overlapping enemy. A197 does not apply level scaling itself. Zero request returns without continuing scan.')
region(6,33677,33778,'PlayerTerrainAttackYOffset','data','101 signed Y offsets consumed by08:A1E8. Local call-argument schema; full terrain mutation pending.')
region(6,33778,33879,'PlayerTerrainAttackXOffset','data','101 X offsets; A1E8 negates for oddCD beforeC773.')
region(6,33879,33980,'PlayerTerrainAttackStrength','data','101 strength bytes; zero suppresses C773 call, otherwise copied to2C.')
region(6,34140,34338,'EnemyKindCollisionStatePointers','data','99 physical little-endian state-table pointers for kinds00..62. Parallel99-entry renderer table corroborates boundary. This is not proof that all kinds/states are reachable or valid in AI.')
region(6,38108,38138,'EnemyBodyVerticalOffset','data','30 byte shape offsets used byA354.')
region(6,38138,38168,'EnemyBodyVerticalExtent','data','30 body height-like extent terms.')
region(6,38168,38198,'EnemyBodyXSide0','data','30 signed body side offsets; A354 checks both world endpoints against camera page.')
region(6,38198,38228,'EnemyBodyXSide1','data','30 opposite signed body offsets; swapped when flags469bit0 clear.')
region(6,38228,38276,'EnemyAttackVerticalOffset','data','48 secondary shape offsets; A0B0 selects via frame byte3 if frame byte2 damage nonzero.')
region(6,38276,38324,'EnemyAttackVerticalExtent','data','48 secondary vertical extent terms; overlap uses modular low-byte arithmetic.')
region(6,38324,38372,'EnemyAttackXSide0','data','48 raw secondary side terms; no world-page rejection inA0B0.')
region(6,38372,38420,'EnemyAttackXSide1','data','48 opposite secondary side terms; swap for flags469bit0 clear, then sum modulo256.')
region(8,41077,41136,'CollideEnemyAttackWithPlayer','code','Count06F8 zero returns; descending flags>=C0 and473low2zero. Secondary damage zero rejects. First overlapping attack calls playerdamage with directioncarry from high/low position compare.')
region(8,41136,41248,'LoadEnemyAttackBounds','code','Kind->state->four-byte frame. Bytes2/3 are secondarydamage/shape; zero damage carryset. Computes low-byte bounds only, without primary-body camera-page gate.')
region(8,41248,41295,'ProbePlayerFeetForSceneTerrain','code','SceneA8C6 flag andA8F2[CD>>1] gate twoC776 calls atX-6/+6,Y+2. FullC776mutations pending.')
region(8,41367,41448,'QueueFirstPlayerMeleeHit','code','CE01 alternate family disables. Zero count returns; descending enemy scan uses primarybody andplayerattack geometry. First overlap: zero8328damage returns, otherwise queue0441,set469bit20,derive047Dlow3. At most one queued enemy per call.')
region(8,41448,41520,'ProbePlayerAttackTerrain','code','SceneA8A6 flag andstrength8457[CD>>1] gateC773. Copyplayer16-bitbase; offsetX mirrored for oddCD,Yfrom838D,strengthto2C. Fullcallee notcomplete.')
region(8,41667,41733,'CollideEnemyBodyWithPlayer','code','Descending count-1 loop; unlikeA075/A197 no countzero guard. GateA05B may unwind whole scan. Flags>=C0 and473low2zero; primarybody damage nonzero andoverlap thenplayerdamage. Validtestedcounts1..10; no zerocount safety claim.')
region(8,42066,42220,'OverlapPlayerAttackBounds','code','CD>>1 selects melee shape. Strict modularY comparison; signed16-bitX endpoints, any endpoint outsidecamera page0 replacedwithcameraorigin, thenstrict modularX comparison. Carryclear overlap; Y retains statepair index.')
region(8,42476,42557,'SelectEnemyHitDirectionFromPlayer','code','Signed low-byte player-minus-enemy deltas, abs magnitudes and half/double ratio choose16-entry directiontable. High coordinates ignored; result0..7.')
region(8,42557,42573,'PlayerHitDirectionQuadrants','data','Four four-entry groups for signs of X/Y differences; combines axis/diagonal directioncodes.')
region(8,43174,43206,'ScenePlayerTerrainAttackFlags','data','32 scene flags enabling A1E8 attack-to-terrain probe.')
region(8,43206,43238,'ScenePlayerFootTerrainFlags','data','32 scene flags enabling A120 feet-to-terrain probes.')
region(8,43251,43351,'PlayerFootTerrainFlagsAfterSharedByte','data','Next100 confirmed state-indexed flags; first flag atA8F2 aliases final entry of earlierF16 magic-slot table. This reviewed101-index domain doesnotestablish complete physical array length.')
region(10,32768,32791,'DispatchSpecialEnemyAi','code','Reloadslot2C; kind-46 indexes29 stored return-address-minus-one pointers; pushhigh/low andRTS.8016 is sharedRTS. Valid tableindices0..28; nativekindreachability notclaimed.')
region(10,32791,32849,'SpecialEnemyAiReturnPointers','data','29 stored addresses for kinds46..62; executabletarget=word+1. Next8051 isCMP0423,X code, not anotherpointer.')
region(11,32768,32785,'DispatchOrdinaryEnemyAi','code','Reloadslot2C; kind indexes64 stored return-address-minus-one pointers; pushhigh/low andRTS.8010sharedRTS. Schedulerthreshold46 doesnotestablishkind40..45validity.')
region(11,32785,32913,'OrdinaryEnemyAiReturnPointers','data','64 physical entries kinds00..3F.8091startsCMP0423,X code; do not reinterpret followinginstructions asentries40..45.')
region(14,55129,55179,'UpdateOrRenderEnemySlot','code','Inactive469bit80 clear returns. Matching slotparity/06F9 skipsAI; otherwise kind<46 mapsR6=0B,elseR6=0A, then8000dispatcher. R7=0D required fromD6F0caller forA000 render tail. ActualAI/renderbodies remainopen.')
region(14,55179,55213,'AccumulateSpecialEnemyHp','code','Kind>=50 except5B/60 adds0437,X to0440, unsigned saturating atAF includingcarry. Slot9aliases accumulator; no independent HP field there inthislocalcontract.')
COMMENTS={(8,0xA1C9):"Zero damage returns from entire scan, not next enemy.",(8,0xA2C6):"No zero-count guard here; tested1..10 only.",(8,0xA4B1):"Any high-page mismatch maps this endpoint to camera origin, not far edge255.",(14,0xD79A):"0440 aliases0437+9; tested separately.",(11,0x800F):"RTS adds1 to stored target address."}
BANK_AT_CALL={0xD774:11,0xD777:13,0xD781:10,0xD787:13}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();rom,_=verified_rom(a.rom);prg=rom[16:0x20010]
    ranges=[];ins=[];func=[];evidence=[];edges=[];access=[]
    for i,(bank,base,lo,hi,name,kind,desc) in enumerate(REGIONS,1):
        rid=f'H{i:02d}';m=MPU();m.memory[base:base+8192]=prg[bank*8192:(bank+1)*8192];d=Disassembler(m)
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
                tb=15 if target>=0xE000 else 14 if target>=0xC000 else bank if base<=target<base+8192 else BANK_AT_CALL.get(pc)
                edges.append({'from_bank':f'{bank:02X}','from_cpu':f'0x{pc:04X}','from_prg_offset':loc(bank,base,pc)['prg_offset'],'to_cpu':f'0x{target:04X}','to_bank':f'{tb:02X}' if tb is not None else 'UNRESOLVED','kind':k,'status':'STATIC_REVIEWED_SOURCE','mapping_condition':'mode0; fixed target, same resident window, explicit R6 write or caller-established R7=0D' if tb is not None else 'target bank unresolved across unreviewed callees'})
            if mode in {'zpg','zpx','zpy','abs','abx','aby','inx','iny','ind'} and op not in {'JSR','JMP'}:
                adr=m.memory[pc+1]|(m.memory[pc+2]<<8 if n==3 else 0);ak='write' if op in {'STA','STX','STY'} else 'read_modify_write' if op in {'INC','DEC','ASL','LSR','ROL','ROR'} else 'read'
                access.append({**loc(bank,base,pc),'instruction':t,'operand_base':f'0x{adr:04X}','mode':mode,'access':ak,'effective_address_known':mode in ('zpg','abs'),'status':'REVIEWED'})
            pc+=n
    all_ranges=[r for r in read('analysis/reviewed_ranges.csv') if not r['id'].startswith('H')]+ranges
    all_ins=[r for r in read('analysis/reviewed_instructions.csv') if not r['region_id'].startswith('H')]+ins
    all_ranges.sort(key=lambda r:int(r['prg_offset'],16));all_ins.sort(key=lambda r:int(r['prg_offset'],16))
    covered=set();code=set();data=set()
    for r in all_ranges:
        lo=int(r['prg_offset'],16);span=set(range(lo,lo+int(r['size'])));assert not covered&span,r;covered|=span;(code if r['classification']=='code' else data).update(span)
    write_csv(ROOT/'analysis/reviewed_ranges.csv',all_ranges);write_csv(ROOT/'analysis/reviewed_instructions.csv',all_ins)
    for rel,new in [('analysis/functions.csv',func),('analysis/evidence.csv',evidence)]:write_csv(ROOT/rel,[r for r in read(rel) if not r['id'].startswith('H')]+new)
    def is_new(bank,pc):return any(int(r['bank'],16)==bank and int(r['cpu'],16)<=pc<int(r['end_cpu_exclusive'],16) for r in ranges)
    for rel,new,bk,pc in [('analysis/cross_references.csv',edges,'from_bank','from_cpu'),('analysis/memory_accesses.csv',access,'bank','cpu')]:write_csv(ROOT/rel,[r for r in read(rel) if not is_new(int(r[bk],16),int(r[pc],16))]+new)
    accesses=read('analysis/memory_accesses.csv');write_csv(ROOT/'analysis/hardware_accesses.csv',[r for r in accesses if 0x2000<=int(r['operand_base'],16)<=0x4017 or r['access']!='read' and int(r['operand_base'],16)>=0x8000])
    candidates=read('analysis/fixed_window_candidates.csv');keys={(r['bank'],r['cpu']) for r in all_ins}
    for r in candidates:
        if (r['bank'],r['cpu']) in keys:r['status']='REVIEWED'
        elif is_new(int(r['bank'],16),int(r['cpu'],16)):r['status']='CONFLICT_WITH_REVIEWED_RANGE'
    write_csv(ROOT/'analysis/fixed_window_candidates.csv',candidates)



    def byte(bank,addr):return prg[bank*8192+(addr&8191)]
    def word(bank,addr):return byte(bank,addr)|byte(bank,addr+1)<<8
    def source(bank,addr):return {f'source_{k}':v for k,v in loc(bank,0x8000 if bank in (6,10,11) else 0xA000,addr).items()}
    fields=[('vertical_offset',0x8194),('vertical_extent',0x81F9),('minus_x_raw',0x825E),('plus_x_raw',0x82C3),('queued_damage',0x8328),('terrain_y_raw',0x838D),('terrain_x_raw',0x83F2),('terrain_strength',0x8457)]
    profiles=[]
    for i in range(101):
        r={'state_pair':i,'state_even':f'0x{2*i:02X}',**source(6,0x8328+i),**{n:byte(6,addr+i) for n,addr in fields}}
        for n in ('minus_x','plus_x'):r[n+'_signed']=r[n+'_raw'] if r[n+'_raw']<128 else r[n+'_raw']-256
        r['scope']='physical101-entrytables; fullgameplayreachability requiresstate/gateconstraints';profiles.append(r)
    write_csv(ROOT/'analysis/player_attack_profiles.csv',profiles)
    for name,count,bases in [('body',30,(0x94DC,0x94FA,0x9518,0x9536)),('attack',48,(0x9554,0x9584,0x95B4,0x95E4))]:
        write_csv(ROOT/f'analysis/enemy_{name}_collision_shapes.csv',[{'shape_id':i,**source(6,bases[0]+i),**{n:byte(6,b+i) for n,b in zip(('vertical_offset_raw','vertical_extent','side0_raw','side1_raw'),bases)}} for i in range(count)])
    kinds=[];frames=[]
    for kind in range(99):
        ptr=word(6,0x855C+2*kind);frame=word(6,ptr)
        assert 0x8622<=ptr<0x9000 and 0x8000<=frame<0xA000
        kinds.append({'kind':f'0x{kind:02X}',**source(6,0x855C+2*kind),'target_bank':'06','state_table_cpu':f'0x{ptr:04X}','target_file_offset':f'0x{16+6*8192+ptr-0x8000:06X}','runtime_kind_validity':'NOT_ESTABLISHED'})
        frames.append({'kind':f'0x{kind:02X}','state':0,'frame':0,**source(6,frame),'primary_damage':byte(6,frame),'body_shape':byte(6,frame+1),'secondary_damage':byte(6,frame+2),'attack_shape':byte(6,frame+3),'scope':'data sample; no claim state0/frame0 is gameplayreachable for everykind'})
    write_csv(ROOT/'analysis/enemy_kind_collision_pointers.csv',kinds);write_csv(ROOT/'analysis/enemy_state0_collision_records.csv',frames)
    directions=[{'index':i,**source(8,0xA63D+i),'direction_code':byte(8,0xA63D+i)} for i in range(16)]
    write_csv(ROOT/'analysis/player_hit_direction_table.csv',directions)
    write_csv(ROOT/'analysis/player_terrain_probe_flags.csv',[{'scene_index':i,'attack_probe_enabled':byte(8,0xA8A6+i),'foot_probe_enabled':byte(8,0xA8C6+i),**source(8,0xA8A6+i)} for i in range(32)])
    write_csv(ROOT/'analysis/player_foot_terrain_state_flags.csv',[{'state_pair':i,**source(8,0xA8F2+i),'enabled':byte(8,0xA8F2+i),'shared_with_magic_last_slot':i==0} for i in range(101)])
    indirect=[r for r in read('analysis/indirect_dispatch_tables.csv') if not r['group'].startswith('H_')];dispatch=[]
    for bank,base,count,start,pc in [(11,0x8011,64,0,0x800F),(10,0x8017,29,0x46,0x8015)]:
        for i in range(count):
            stored=word(bank,base+2*i);target=(stored+1)&65535;assert 0x8000<=target<0xA000
            r={'kind':f'0x{start+i:02X}',**source(bank,base+2*i),'stored_return_address':f'0x{stored:04X}','target_bank':f'{bank:02X}','target_cpu':f'0x{target:04X}','target_file_offset':f'0x{16+bank*8192+target-0x8000:06X}','handler_review':'SHARED_RTS' if target in (0x8010,0x8016) else 'UNREVIEWED_BODY'};dispatch.append(r)
            indirect.append({'group':f'H_EnemyAi{bank:02X}','dispatch_bank':f'{bank:02X}','dispatch_cpu':f'0x{pc:04X}','index':i,'selector':f'kind={start+i:02X}; validphysicaltableonly','table_bank':f'{bank:02X}','table_cpu':f'0x{base+2*i:04X}','target_bank':r['target_bank'],'target_cpu':r['target_cpu'],'target_semantics':r['handler_review']})
    write_csv(ROOT/'analysis/enemy_ai_dispatch.csv',dispatch)
    for r in indirect:
        for area in ranges:
            if area['classification']=='code' and r['target_bank']==area['bank'] and int(area['cpu'],16)<=int(r['target_cpu'],16)<int(area['end_cpu_exclusive'],16):r['target_semantics']=area['symbol']
    write_csv(ROOT/'analysis/indirect_dispatch_tables.csv',indirect)
    cov=json.loads((ROOT/'analysis/coverage.json').read_text());cov.update({'reviewed_code_bytes':len(code),'reviewed_data_bytes':len(data),'reviewed_code_plus_data_bytes':len(covered),'reviewed_prg_fraction':len(covered)/131072,'reviewed_code_range_count':sum(r['classification']=='code' for r in all_ranges),'reviewed_data_range_count':sum(r['classification']=='data' for r in all_ranges),'stage02F_added_bytes':sum(int(r['size']) for r in ranges)})
    write_json(ROOT/'analysis/coverage.json',cov)
    result={'new_ranges':len(ranges),'new_code_ranges':sum(r['classification']=='code' for r in ranges),'new_data_ranges':sum(r['classification']=='data' for r in ranges),'new_instructions':len(ins),'new_bytes':sum(int(r['size']) for r in ranges),'player_attack_profiles':101,'enemy_body_shapes':30,'enemy_attack_shapes':48,'kind_collision_pointers':99,'new_indirect_edges':93,'unresolved_targets_from_new_code':[r for r in edges if r['to_bank']=='UNRESOLVED'],'scope':'local melee/contact, schemas, AI entry dispatch and HPaggregate; full AI,terrainmutation,nativeNES remainopen'}
    write_json(ROOT/'analysis/stage02F_static_summary.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
