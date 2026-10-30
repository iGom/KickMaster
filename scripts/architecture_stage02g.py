#!/usr/bin/env python3
"""Stage02G enemy death/rewards, kind00 local AI and special death-object lifecycles.
Replaces I-series only. Retains prior reviewed ranges and historical CPU evidence.
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
    base=0x8000 if bank<14 else 0xC000 if bank==14 else 0xE000
    REGIONS.append((bank,base,lo,hi,name,kind,desc))
region(6,34338,34350,'Kind00CollisionStatePointers','data','Six normal state pointers; virtual AI selectors6/7/8 are death/hit/quake, not three more normal collision states.')
region(6,36864,37044,'Kind00CollisionFrames','data','45 four-byte frames: normal state counts8,1,9,9,9,9; independently corroborated by AI frame loops and next kind pointer.')
region(11,32913,32923,'OrdinaryEnemyTimerGate','code','If A>0423,X unwind caller; otherwise return to caller without resetting timer.')
region(11,32948,32962,'AdvanceOrdinaryEnemyFrame','code','Increment0419,X and reset only when equal to A; returns Z flag of equality/reset.')
region(11,32981,33066,'OrdinaryEnemyDeathLifecycle','code','On entry-state change to2F,47Dbit10 suppresses drops and score; otherwise C78E drops then C746 encoded045F score. Sound51 unless0487bit40. Reset state/frame/timer, advance eight animation calls then clear469/473/47D.')
region(11,33100,33116,'DispatchKind00State','code','C7A0 with A0,Y6 selects normal/death/hit/quake; push stored pointer and RTS. Target bodies locally reviewed; terrain collision callees remain partial.')
region(11,33116,33134,'Kind00StateReturnPointers','data','Nine stored addresses: normal0..5,death6,hit7,quake8. Code/frame table normal domain is only0..5.')
region(11,33134,33214,'Kind00WalkAndChooseAttack','code','Every3 selected normal calls, classify target X distance. Walk unless signed enemy-minus-target X is-32..-25 or24..31; in band choose next state from16 entries using(97+slot)&0F without updating RNG97.')
region(11,33214,33230,'Kind00AttackChoiceTable','data','16 state choices, mostly2 with3/4/5; not independent random draws or measured gameplay probabilities.')
region(11,33230,33264,'Kind00TargetBandFacing','code','C7A6 distance masks3F&C0:80 sets469bit0,other nonzero clearsbit0; zero returns A0. Low flag from table is not a plain signed-distance comparison.')
region(11,33264,33320,'Kind00FallAndStationaryAttacks','code','Fall entry movesY5 then resets frame/timer; negative36 clears47D40 and state0. Attack entry advances nine frames every3 timer calls then returns state0.')
region(11,33320,33391,'Kind00ArcingAttack','code','Every2 timer calls use nine X/Y movement pairs, clear469bit1 at frame4; 8281 terrain response chooses states, otherwise frame9 resets to state1 and clears47D40.')
region(11,33391,33409,'Kind00ArcingAttackSteps','data','Nine X magnitudes followed by nine Y magnitudes; direction from469low2.')
region(11,33409,33464,'SelectEnemyStateFromMovementResult','code','36bit40 selects41 andsets47D40/clears46902; else36negative selects42/clears47D40; both resetframe/timer; otherwise returnsA1.')
region(11,33899,33943,'FaceTargetFromFarDistanceBits','code','UsesC7A6 3F&0C; ifnonzero and469bit04 allowed, sets/clears facing accordingbit08. Otherflagbits retained.')
region(11,36037,36078,'EnterEnemyFallUnlessGrounded','code','Entries choose state1 or2 when36nonnegative, set47D40,clear46902,resetframe/timer. Negative36 returnsA1.')
region(15,58259,58338,'ClassifyEnemyTargetDistance','code','Subtract target snapshotD6/D7 from enemyX andD4/D5 fromenemyY; EB63 selectorY1/3 and eight-entry masks produce3F.')
region(15,58338,58354,'EnemyTargetDistanceMasks','data','Eight X masks followed by eight Y masks, ORcombined. Does not read current player coordinates directly.')
region(15,58354,58366,'InitializeEnemyMovementFlags','code','30=469low2 direction;36=0 movement result scratch.')
region(15,58446,58488,'StepEnemyByMagnitude','code','Store A/Y magnitudes3D/3E, initialize flags, compute16-bit targets, optional terrain pathE4AC if473negative, then commitE72D. Terrain callee remains unreviewed.')
region(15,60259,60329,'ClassifySignedDistanceEightBands','code','Uses entry N plus22/23 signed16-bit difference and selectorY0..4. Six threshold arrays distinguish bands0..7; local tests use coherent N/high byte.')
region(15,60329,60359,'SignedDistanceBandThresholds','data','Six arrays of five bytes: negative far/middle/near then positive far/middle/near.')
region(14,55767,55784,'FindInactiveEnemySlot','code','Scan469bit80 fromindex0 to06F8-1. Free returnsA1,Yindex; exhausted returnsAfromlastactiveflags, ZfromCPY. Callers8061 useZ. Countzero contract notestablished.')
region(14,57143,57211,'SpawnSpecialDeathDropTriple','code','Three correlated draws using(D8>>1)&1F and+10,+20. DF9B table; firsttwo velocityX-1/+1,Y-6,thirddefault0/-7. Stopatfirstallocationfailure; no rare1UP gate.')
region(14,57211,57275,'EnemyDropChoiceTables','data','Two32-byte tables; ordinary includesselector6 HP and7 damage, special tableonly0..5. Frequencies underuniformindex are not measured gameplay probabilities.')
region(14,57275,57291,'EnemyDropSpawnReturnPointers','data','Eight storedreturn addresses into0F:E01F..E037; targetsword+1.')
region(14,57291,57344,'SpawnOrdinaryDeathDropPrefix','code','IfDA&3==0 andD9&FC==0 spawnone6A extraattempt; else three correlatedDF7Bdraws. InstructionSTA0543,Y atDFFF straddlesfixed0E/0F boundary.')
region(15,57344,57346,'OrdinaryDropInstructionOperands','code','Operandbytes43 05 completing0E:DFFF opcode99. Notanentrypoint; one logicalinstructionisindexedatDFFF.')
region(15,57346,57371,'SpawnOrdinaryDeathDropTail','code','Third correlated draw andsharedDF7Bselector dispatcher; E019 discards savedindex onallocationfailure.')
region(15,57371,57485,'SpawnEnemyDropObject','code','Literaltypes6A,46,48,4B,43,44,41,69,4C toE03D. ExistingallocatorE0ED excludes0. CopyenemyXY withY-16,initializevelocity0/-7,timer7,counter0,flagsFEDE. Returncarry failure; preserveenemyX.')
region(15,57485,57557,'SpawnRewardObjectAtEnemy','code','E0D5[(type-40)>>1] selects forcedslot1 ifnonzero elseallocator. Forcedslot replaces activeobject. CopyenemyXY,type,flagsFEDE|40,zerovelocities; doesnot reset0593or05A7; Xisclobberedtotypeindex.')
region(15,57557,57581,'RewardForcedSlotFlags','data','24 flags for typepairs40..6E; nonzero bypassesallocatorandforces slot1.')
region(15,65246,65270,'CollectibleInitialFlags','data','24 initial flags indexed(type-40)>>1; sharedbydrop/rewardspawners.')
region(10,32849,32865,'SpecialEnemyTimerGate','code','A>0423 unwinds caller; thresholdreached resets0423to0 thenreturns, unlikeordinarygate.')
region(10,32865,33078,'CreateSpecialDeathObjectAndAnchor','code','Allocate lowestinactive enemy or reuse current iffull; reset selectedfields, subtypeHP=originalkind-50, kind5B (8098 changes60), flags90, copyscore045F. Saveclamped anchor0189..018C relativecameraY30..B0,X30..D0; newslotcoordinates/reactionflagsnotinitializedhere.')
region(10,33078,33104,'AdvanceSpecialFrameAndDeactivate','code','8136 frameincrement/equalitywrap;8144 clears469/473/47D only.')
region(10,33134,33150,'DispatchKind50State','code','C7A0 withA0,Y4 selectsnormal0..3,death4,hit5,quake6; onlydeathpathanddispatchreviewed, alivehandlersremainopen.')
region(10,33150,33164,'Kind50StateReturnPointers','data','Seven storedreturn addresses; death82C5,hitC7A3,quake8016. No claimalivehandlerscomplete.')
region(10,33477,33532,'ConvertKind50DeathAndCheckCompanion','code','Create5Bobject, soundD2; deactivateoldslotifdifferent; scanactivekind50. Ifanotherfound,setnewkind60and47Dbit08 to suppressendflag later.')
region(10,35322,35342,'DispatchSpecialDeathObject','code','Kind5B direct040Fdispatch, noHPdamagegate because0437is subtype. Two entries0/1.')
region(10,35342,35346,'SpecialDeathStateReturnPointers','data','Two storedreturn addresses to8A12effect and8A43delay.')
region(10,35346,35473,'SpecialDeathBurstRewardAndDelay','code','Scoreonce; eightframes16cycles=128 calls, oddframescall8AA9. Then repositionandspawnrewardfrom12-entrysubtypetable;state1 waits100calls then clears flags, plusF8bit20 inscene1B.')
region(10,35473,35497,'SpecialDeathRewardTables','data','12 rewardtypes and12Yoffsets; subtypefield0437 indexes. Nonzero rewardcodes are54,50,5C,56,66,58,5E; no unconditionalboss-name mapping.')
region(10,35497,35573,'SpecialDeathScatterAndDrop','code','Restoreanchor; ifcycle042Dzero spawnDF37triple. DirectiontablebyD8&3; offsetindex=(D8 OR024D)+97+inheritedcarry masked1F, adjacent bytepair! Callmovement with473=0 onconstructorpath.')
region(10,35573,35610,'SpecialDeathScatterTables','data','33bytes support32overlappingoffsetpairs, plus4directioncodes. Oddindicesarevalid; donotdecodeas16wordpairs.')
region(10,35610,35668,'AlternateSpecialDeathLifecycle','code','Kind60:scoreonce,scattereverycall;128calls thenF8bit80 unless47D08 set;deactivate,clear070A/B. Firstcycle8tripleattempts, nofinalrewardtablecall.')
COMMENTS={(14,0xDFFF):'STA0543,Y opcode in0E, operand43 05 in0F:E000/E001; one logicalinstruction.'}
BANK_AT_CALL={}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();rom,_=verified_rom(a.rom);prg=rom[16:0x20010]
    ranges=[];ins=[];func=[];evidence=[];edges=[];access=[]
    for i,(bank,base,lo,hi,name,kind,desc) in enumerate(REGIONS,1):
        rid=f'I{i:02d}';m=MPU();m.memory[base:base+8192]=prg[bank*8192:(bank+1)*8192]
        if bank>=14:m.memory[0xC000:0x10000]=prg[14*8192:16*8192]
        d=Disassembler(m)
        r={'id':rid,'symbol':name,**loc(bank,base,lo),'size':hi-lo,'end_cpu_exclusive':f'0x{hi:04X}','classification':kind,'status':'STATIC_REVIEWED','description':desc};ranges.append(r)
        evidence.append({'id':rid,'class':'STATIC','subject':name,'source':f'disassembly/banks/prg{bank:02X}.asm','location':f'PRG{bank:02X}:{lo:04X}-{hi:04X} exclusive','claim':desc,'confidence':'high for bounded local effect; see explicit input domains and unreviewed callees'})
        if kind=='data' or (bank,lo)==(15,0xE000):continue
        func.append({'id':rid,'name':name,**loc(bank,base,lo),'size':hi-lo,'status':'STATIC_REVIEWED','description':desc,'callers_callees':'cross_references.csv; ranges may have multiple entry points'})
        pc=lo
        while pc<hi:
            n,t=d.instruction_at(pc);op,mode=m.disassemble[m.memory[pc]];assert op!='???' and (pc+n<=hi or (bank,pc,n,hi)==(14,0xDFFF,3,0xE000)),(bank,hex(pc),t)
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
    all_ranges=[r for r in read('analysis/reviewed_ranges.csv') if not r['id'].startswith('I')]+ranges
    all_ins=[r for r in read('analysis/reviewed_instructions.csv') if not r['region_id'].startswith('I')]+ins
    all_ranges.sort(key=lambda r:int(r['prg_offset'],16));all_ins.sort(key=lambda r:int(r['prg_offset'],16))
    covered=set();code=set();data=set()
    for r in all_ranges:
        lo=int(r['prg_offset'],16);span=set(range(lo,lo+int(r['size'])));assert not covered&span,r;covered|=span;(code if r['classification']=='code' else data).update(span)
    write_csv(ROOT/'analysis/reviewed_ranges.csv',all_ranges);write_csv(ROOT/'analysis/reviewed_instructions.csv',all_ins)
    for rel,new in [('analysis/functions.csv',func),('analysis/evidence.csv',evidence)]:write_csv(ROOT/rel,[r for r in read(rel) if not r['id'].startswith('I')]+new)
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
    def source(bank,addr):return {f'source_{k}':v for k,v in loc(bank,0x8000 if bank<14 else 0xC000 if bank==14 else 0xE000,addr).items()}
    indirect=[r for r in read('analysis/indirect_dispatch_tables.csv') if not r['group'].startswith('I_')];dispatch=[]
    for bank,addr,count,pc,group in [(11,0x815C,9,0x815B,'Kind00'),(10,0x817E,7,0x817D,'Kind50'),(10,0x8A0E,2,0x8A0D,'Death5B'),(14,0xDFBB,8,0xDF78,'SpecialDrop'),(14,0xDFBB,8,0xE018,'OrdinaryDrop')]:
        for i in range(count):
            stored=word(bank,addr+2*i);target=(stored+1)&65535;tb=15 if target>=0xE000 else 14 if target>=0xC000 else bank
            row={'group':group,'index':i,**source(bank,addr+2*i),'stored_return_address':f'0x{stored:04X}','target_bank':f'{tb:02X}','target_cpu':f'0x{target:04X}','target_file_offset':f'0x{16+tb*8192+(target&8191):06X}'};dispatch.append(row)
            indirect.append({'group':'I_'+group,'dispatch_bank':f'{15 if pc>=0xE000 else bank:02X}','dispatch_cpu':f'0x{pc:04X}','index':i,'selector':group+' local index','table_bank':f'{bank:02X}','table_cpu':f'0x{addr+2*i:04X}','target_bank':row['target_bank'],'target_cpu':row['target_cpu'],'target_semantics':'see reviewed entry and explicitcallee boundaries'})
    write_csv(ROOT/'analysis/enemy_state_and_drop_dispatch.csv',dispatch)
    for row in indirect:
        for area in ranges:
            if area['classification']=='code' and row['target_bank']==area['bank'] and int(area['cpu'],16)<=int(row['target_cpu'],16)<int(area['end_cpu_exclusive'],16):row['target_semantics']=area['symbol']
    write_csv(ROOT/'analysis/indirect_dispatch_tables.csv',indirect)
    choices=[];triples=[];types=(0x46,0x48,0x4B,0x43,0x44,0x4C,0x41,0x69)
    for name,addr in [('ordinary',0xDF7B),('special_death',0xDF9B)]:
        for i in range(32):
            v=byte(14,addr+i);choices.append({'family':name,'index':i,**source(14,addr+i),'selector':v,'type_code':f'0x{types[v&7]:02X}'})
            ids=[(i+10*k)&31 for k in range(3)];triples.append({'family':name,'seed_index':i,'draw_indices':','.join(map(str,ids)),'type_codes':','.join(f'{types[byte(14,addr+j)&7]:02X}' for j in ids),'scope':'normal three-spawn path, sufficient free slots; not independent random draws'})
    write_csv(ROOT/'analysis/enemy_drop_choices.csv',choices);write_csv(ROOT/'analysis/enemy_drop_triplets.csv',triples)
    write_csv(ROOT/'analysis/collectible_spawn_profiles.csv',[{'type_even':f'0x{0x40+2*i:02X}',**source(15,0xFEDE+i),'initial_flags':byte(15,0xFEDE+i),'forced_slot1':byte(15,0xE0D5+i)} for i in range(24)])
    write_csv(ROOT/'analysis/special_death_rewards.csv',[{'subtype':i,**source(10,0x8A91+i),'reward_type':f'0x{byte(10,0x8A91+i):02X}','camera_y_offset':byte(10,0x8A9D+i)} for i in range(12)])
    write_csv(ROOT/'analysis/special_death_scatter_pairs.csv',[{'index':i,**source(10,0x8AF5+i),'x_magnitude':byte(10,0x8AF5+i),'y_magnitude':byte(10,0x8AF6+i)} for i in range(32)])
    frames=[]
    for state,count in enumerate((8,1,9,9,9,9)):
        ptr=word(6,0x8622+2*state)
        for frame in range(count):
            address=ptr+4*frame;frames.append({'kind':0,'state':state,'frame':frame,**source(6,address),**{field:byte(6,address+i) for i,field in enumerate(('primary_damage','body_shape','secondary_damage','attack_shape'))}})
    write_csv(ROOT/'analysis/kind00_collision_frames.csv',frames)
    write_csv(ROOT/'analysis/enemy_distance_band_tables.csv',[{'selector':i,**source(15,0xEBA9+i),**{field:byte(15,addr+i) for field,addr in [('negative_far',0xEBA9),('negative_middle',0xEBAE),('negative_near',0xEBB3),('positive_far',0xEBB8),('positive_middle',0xEBBD),('positive_near',0xEBC2)]}} for i in range(5)])
    write_csv(ROOT/'analysis/cross_bank_instructions.csv',[{'bank':'0E','cpu':'0xDFFF','file_offset':'0x01E00F','size':3,'bytes':'99 43 05','instruction':'STA $0543,Y','continuation_bank':'0F','continuation_cpu':'0xE000','continuation_size':2,'mapping_condition':'Both fixed windows adjacent in MMC3mode0; CPU fetch spans physical banks0E/0F'}])
    # Existing top-level target entries can now distinguish a reviewed dispatcher from its unreviewed bodies.
    ai=read('analysis/enemy_ai_dispatch.csv')
    for row in ai:
        kind=int(row['kind'],16)
        if kind==0:row['handler_review']='KIND00_LOCAL_STATES_REVIEWED; movementterraincalleeopen'
        elif kind==0x50:row['handler_review']='DISPATCH_AND_DEATH_REVIEWED; alivehandlersopen'
        elif kind in (0x5B,0x60):row['handler_review']='DEATH_OBJECT_LIFECYCLE_REVIEWED_LOCAL'
    write_csv(ROOT/'analysis/enemy_ai_dispatch.csv',ai)
    cov=json.loads((ROOT/'analysis/coverage.json').read_text());cov.update({'reviewed_code_bytes':len(code),'reviewed_data_bytes':len(data),'reviewed_code_plus_data_bytes':len(covered),'reviewed_prg_fraction':len(covered)/131072,'reviewed_code_range_count':sum(r['classification']=='code' for r in all_ranges),'reviewed_data_range_count':sum(r['classification']=='data' for r in all_ranges),'stage02G_added_bytes':sum(int(r['size']) for r in ranges)})
    write_json(ROOT/'analysis/coverage.json',cov)
    summary={'new_ranges':len(ranges),'new_code_ranges':sum(r['classification']=='code' for r in ranges),'new_data_ranges':sum(r['classification']=='data' for r in ranges),'new_instructions':len(ins),'new_bytes':sum(int(r['size']) for r in ranges),'new_indirect_edges':len(dispatch),'kind00_normal_collision_frames':45,'cross_bank_instructions':1,'unresolved_target_banks':[r for r in edges if r['to_bank']=='UNRESOLVED'],'scope':'kind00 local AI, reward creation and special death lifecycle; full terrain and other AI remain open'}
    write_json(ROOT/'analysis/stage02G_static_summary.json',summary);print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
