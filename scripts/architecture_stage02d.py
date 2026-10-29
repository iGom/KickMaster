#!/usr/bin/env python3
"""Stage02D: projectile collision, bounded enemy hit response, shield and quake consumers."""
import argparse,json
from baseline import ROOT,verified_rom,write_csv,write_json
from architecture_stage01b import read,loc as oldloc,MPU,Disassembler

def loc(bank,base,pc):
    r=oldloc(bank,base,pc)
    if base==0x8000:r['mapping_condition']=f'MMC3 PRG mode0; R6={bank:02X} at8000; collision caller requires06'
    return r
REGIONS=[]
def region(bank,lo,hi,name,kind,desc):
    base=0x8000 if bank==6 else 0xC000 if bank==14 else 0xE000 if bank==15 else 0xA000
    REGIONS.append((bank,base,lo,hi,name,kind,desc))
for bank,entries in [
(6,[
(0x8000,0x8065,'PlayerCollisionVerticalOffset','data','101 byte offsets indexed by CD>>1; R6=06 collision context; later acquisition/death states may be gated before lookup.'),
(0x8065,0x80CA,'PlayerCollisionVerticalExtent','data','101 height-like extents combined with counterpart extent using8-bit arithmetic.'),
(0x80CA,0x812F,'PlayerCollisionHorizontalSide0','data','101 horizontal extent bytes, facing-selected by A4EC.'),
(0x812F,0x8194,'PlayerCollisionHorizontalSide1','data','Opposite101 horizontal extents. Valid gameplay domain not inferred from arbitrary state bytes.'),
(0x84BC,0x84DC,'ProjectileCollisionVerticalOffset','data','32 bytes indexed by projectile(type&FE)/2; used by08:A54D.'),
(0x84DC,0x84FC,'ProjectileCollisionVerticalExtent','data','32 vertical extents for types00..3F.'),
(0x84FC,0x851C,'ProjectileCollisionMinusXExtent','data','32 horizontal extents, swapped with other side for odd type.'),
(0x851C,0x853C,'ProjectileCollisionPlusXExtent','data','32 horizontal extents; projectile endpoints are clipped against camera page by08:A54D.'),
(0x853C,0x855C,'ProjectileDamageRequests','data','32 raw queued-damage values: pulse3; bouncing types10/12 alternate3/2; lightning2. Final HP consumer is0F:E32A.')]),
(8,[
(0xA230,0xA2C3,'CollideMagicProjectilesWithEnemies','code','Selected-effect slot limit; descending enemy scan with flags>=C0 andsecondary&3==0; descending projectile scan; queue first hit per enemy. Nonpersistent projectile cleared before queue; branch withzero slotlimit tails body-contact path.'),
(0xA305,0xA354,'CollideEnemyProjectilesWithPlayer','code','Scan10 enemy projectiles; requireactive80 andnot40, nonzero damage and overlap; clear projectile. Selected0A decrements05A7 and absorbs while resultnonnegative, otherwise invokes playerdamage.03D9 may discardcaller return.'),
(0xA354,0xA404,'LoadEnemyCollisionBounds','code','R6=06 kind/state/animation indirection produces damage and box; facing swapsX extents; bothX endpoints must lie in camera-relative page0. Carryset rejects.'),
(0xA404,0xA452,'LoadEnemyProjectileCollisionBounds','code','R6=06 pointer indexed0491&3F and state049B&7; produces damage and shape-derived8-bit collision bounds. Full validkind/state inventory remainsopen.'),
(0xA4EC,0xA528,'OverlapPlayerCollisionBounds','code','Strict8-bit modular vertical/horizontal interval tests against CD>>1 profile. Carryclear means overlap; highY isnot checked.'),
(0xA54D,0xA5EC,'OverlapMagicProjectileCollisionBounds','code','Strict modular vertical test; signed horizontal extents mirrored for oddtype and clipped to camera page; carryclear overlap.'),
(0xA8E6,0xA8F3,'MagicCollisionLastSlot','data','13 selected-effect entries:03 and0C=>1;05/06=>2; others0route to bodycontact. Lightning slot2 isnot scanned by this path.')]),
(9,[
(0xAB87,0xABC7,'ProjectileObjectHandlerPointers','data','32 little-endian handler pointers for paired types00..3F; sprite table remains separately addressed.'),
(0xB55C,0xB571,'GrowPulseProjectile','code','Increment counter; everythirdcall reset andadvance even typeby2. Type0A dispatches shared RTS B570 andholds finalshape.'),
(0xB571,0xB5EF,'UpdateBouncingProjectile','code','Toggle typebit1; sample separate futureY/futureX and negate corresponding velocity for result&3. Currentpoint result&3 deactivates, bit3setsattribute20; typebit4 determines persistencebit10. Terrain service callees remain partiallyreviewed.'),
(0xB5EF,0xB608,'AdvanceLightningSegment','code','EntryB5EF clears activeflags when counterzero; B5F4 advances type by signed05A4, sound93, then anchors toselected slot3; zeroresult clearsflags.'),
(0xB608,0xB620,'CycleCentralLightningSegment','code','Decrementcounter at type26; nonzero resets type20; zero sets deltaFE andtype1E for reversefinish.'),
(0xB620,0xB63A,'CycleSideLightningSegment','code','At type2E/2F decrement counter; nonzero sets step+2 and advances type by2; zero steps back by2 WITHOUT changing step. Synthetic seed1 therefore wraps counter before eventual expiry.'),
(0xB63A,0xB645,'ReverseSideLightningSegment','code','At type3A setdeltaFE andstepbackto38.'),
(0xB645,0xB65E,'AnchorLightningSegment','code','Copy selectedslot3 16-bitX/Y to currentprojectileslot; no independent velocity here.')]),
(14,[
(0xD6F0,0xD745,'ScheduleEnemyUpdatePass','code','Map R7=0D; clear0440; odd D8 ticks quake counter; walk one of two ten-entry cycles from D8 low3; copy0440 to06BC. D759 and accumulator producer remain unreviewed;0440 aliases indexed HP slot9.'),
(0xD745,0xD759,'EnemyUpdateOrderCycles','data','Two10-byte successor permutations for ascending/descending enemy passes.'),
(0xD7AD,0xD7E7,'TickQuakeLifetime','code','Nonzero03DC increments; beforeincrementD2 addsflag40 tofirst8 flagged10 entries; F0 clears03DC andbits10/40 inallfirst8. Counter1expires after240calls.')]),
(15,[
(0xE2F9,0xE32A,'SelectEnemyHitOrQuakeState','code','Store A to2E; HP zero with Y nonzero selectsY; pending20 selects Y+1 and applies hit; quake10 selects Y+2; otherwise increment0423 and select040F. 2F stores selector; Y=selector*2. Increment-wrap branches require separate interpretation; tested bases0/2/5.'),
(0xE32A,0xE35B,'ApplyQueuedEnemyDamage','code','Onlywhen0469bit40:0437=max(HP-0441,0),clear0455,clearflag40,set047Dbit80,sound55,restoreXfrom2C. Pendingbit20/queuedvalue remain; caller providespendinggate.'),
(0xE35B,0xE393,'TickEnemyHitRecovery','code','Increment0423; onodd result increment0455. At0455=0A clearpending20,setaccept40,clearreaction80,reset0455; otherwise originalknockback. Reset0423 afteroddwork.'),
(0xE3FE,0xE436,'StepEnemyHitKnockback','code','Direction047Dlow3 selects3 eight-byte tables; compute targetY/X, optionally terrain-adjust when0473negative, thencommit. Terrainadjustment notfullyreviewed.'),
(0xE436,0xE44E,'EnemyHitKnockbackTables','data','Eight directionflags, eightY magnitudes(all0), eightX magnitudes(0or2).'),
(0xE478,0xE4AC,'CalculateEnemyPositionStep','code','Twoentrypoints derive16-bitY/X target usingunsigned magnitudes3E/3D anddirectionbits30; originaladd/sub helpers.'),
(0xE72D,0xE764,'CommitEnemyTargetPosition','code','If36negative snaplowY bynibble threshold0C, includingcarry; store32/33 and34/35 to currentenemyX indexedcoordinatearrays.'),
(0xE90C,0xE925,'OffsetUnsigned16ByX','code','E90C addsunsignedX to22/23; E917 subtractsunsignedX withcarry/borrow. Doesnot interpretXassignedsigned.')])]:
    for args in entries:region(bank,*args)
COMMENTS={(8,0xA271):'Zero damage ends this enemy scan immediately, not just this projectile.',(8,0xA289):'A cleared projectile can no longer hit lower-index enemies in this pass.',(8,0xA32D):'Only selected effect0A gates the decrement; no active-type check here. Counter10 absorbs10 intersections; next becomesFF.',(15,0xE335):'Unsigned raw HP subtraction with saturation tozero; equality also giveszero.',(15,0xE34C):'Consumption clearsaccept40 but preservespending20; recovery later restoresacceptance.',(14,0xD7B6):'Warning flag40 is added onentryD2, before counter becomesD3.',(14,0xD7D4):'Expiry clearsbits10/40 even on entries excluded by the originalquake producer.',(9,0xB574):'Alternating type10/12 also selects damage3/2 in R6=06 collision table.'}
R7_AT_CALL={}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();rom,_=verified_rom(a.rom);prg=rom[16:0x20010]
    ranges=[];ins=[];func=[];evidence=[];edges=[];access=[]
    for i,(bank,base,lo,hi,name,kind,desc) in enumerate(REGIONS,1):
        rid=f'F{i:02d}';m=MPU();m.memory[base:base+8192]=prg[bank*8192:(bank+1)*8192];d=Disassembler(m)
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
    all_ranges=[r for r in read('analysis/reviewed_ranges.csv') if not r['id'].startswith('F')]+ranges
    all_ins=[r for r in read('analysis/reviewed_instructions.csv') if not r['region_id'].startswith('F')]+ins
    all_ranges.sort(key=lambda r:int(r['prg_offset'],16));all_ins.sort(key=lambda r:int(r['prg_offset'],16))
    covered=set();code=set();data=set()
    for r in all_ranges:
        lo=int(r['prg_offset'],16);span=set(range(lo,lo+int(r['size'])));assert not covered&span,r;covered|=span;(code if r['classification']=='code' else data).update(span)
    write_csv(ROOT/'analysis/reviewed_ranges.csv',all_ranges);write_csv(ROOT/'analysis/reviewed_instructions.csv',all_ins)
    for rel,new in [('analysis/functions.csv',func),('analysis/evidence.csv',evidence)]:write_csv(ROOT/rel,[r for r in read(rel) if not r['id'].startswith('F')]+new)
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
    def source(bank,addr):return {f'source_{k}':v for k,v in loc(bank,0x8000 if bank==6 else 0xA000,addr).items()}
    profiles=[];dispatch=[]
    for i in range(32):
        profiles.append({'type_even':f'0x{2*i:02X}','type_odd':f'0x{2*i+1:02X}',**source(6,0x853C+i),'vertical_offset':byte(6,0x84BC+i),'vertical_extent':byte(6,0x84DC+i),'minus_x_extent':byte(6,0x84FC+i),'plus_x_extent':byte(6,0x851C+i),'queued_damage':byte(6,0x853C+i),'odd_type_swaps_x_extents':True,'not_a_final_damage_or_reachability_claim':True})
        target=word(9,0xAB87+2*i)
        name=next(r['symbol'] for r in ranges if r['bank']=='09' and r['classification']=='code' and int(r['cpu'],16)<=target<int(r['end_cpu_exclusive'],16))
        dispatch.append({'type_even':f'0x{2*i:02X}','type_odd':f'0x{2*i+1:02X}',**source(9,0xAB87+2*i),'handler_bank':'09','handler_cpu':f'0x{target:04X}','handler':name})
    write_csv(ROOT/'analysis/projectile_collision_profiles.csv',profiles);write_csv(ROOT/'analysis/projectile_object_dispatch.csv',dispatch)
    write_csv(ROOT/'analysis/player_hurtbox_profiles.csv',[{'state_pair':i,'even_state':f'0x{2*i:02X}',**source(6,0x8000+i),'vertical_offset':byte(6,0x8000+i),'vertical_extent':byte(6,0x8065+i),'side0':byte(6,0x80CA+i),'side1':byte(6,0x812F+i),'scope':'tablelayout; reachablecollisiondomain mustrespectplayergates'} for i in range(101)])
    write_csv(ROOT/'analysis/magic_collision_slot_limits.csv',[{'selected_effect':f'0x{i:02X}',**source(8,0xA8E6+i),'last_slot':byte(8,0xA8E6+i),'route':'projectile scan descending through0' if byte(8,0xA8E6+i) else 'tailbodycontactA2C3'} for i in range(13)])
    indirect=[r for r in read('analysis/indirect_dispatch_tables.csv') if not r['group'].startswith('F_')]
    for i,r in enumerate(dispatch):indirect.append({'group':'F_Projectiles','dispatch_bank':'09','dispatch_cpu':'0xBF65','index':i,'selector':f'0568,X&FE equals0x{2*i:02X}','table_bank':'09','table_cpu':r['source_cpu'],'target_bank':'09','target_cpu':r['handler_cpu'],'target_semantics':r['handler']})
    for r in indirect:
        for area in ranges:
            if area['classification']=='code' and r['target_bank']==area['bank'] and int(area['cpu'],16)<=int(r['target_cpu'],16)<int(area['end_cpu_exclusive'],16):r['target_semantics']=area['symbol']
    write_csv(ROOT/'analysis/indirect_dispatch_tables.csv',indirect)
    cov=json.loads((ROOT/'analysis/coverage.json').read_text());cov.update({'reviewed_code_bytes':len(code),'reviewed_data_bytes':len(data),'reviewed_code_plus_data_bytes':len(covered),'reviewed_prg_fraction':len(covered)/131072,'reviewed_code_range_count':sum(r['classification']=='code' for r in all_ranges),'reviewed_data_range_count':sum(r['classification']=='data' for r in all_ranges),'stage02D_added_bytes':sum(int(r['size']) for r in ranges)})
    write_json(ROOT/'analysis/coverage.json',cov)
    result={'new_ranges':len(ranges),'new_code_ranges':sum(r['classification']=='code' for r in ranges),'new_data_ranges':sum(r['classification']=='data' for r in ranges),'new_instructions':len(ins),'new_bytes':sum(int(r['size']) for r in ranges),'projectile_profiles':32,'player_profiles':101,'slot_limits':13,'new_indirect_edges':32,'unresolved_targets_from_new_code':[r for r in edges if r['to_bank']=='UNRESOLVED'],'scope':'localprojectile collision/hit/quake/shield; fullterrain/enemyAI/nativeNES timing notcomplete'}
    write_json(ROOT/'analysis/stage02D_static_summary.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
