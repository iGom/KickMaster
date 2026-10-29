#!/usr/bin/env python3
"""Stage02E: normal player control, jump phases and original terrain lookup path.
Regenerates only G-series. A-F analyses and CPU results are preserved.
"""
import argparse,json
from baseline import ROOT,verified_rom,write_csv,write_json
from architecture_stage01b import read,loc,MPU,Disassembler
REGIONS=[]
def region(bank,lo,hi,name,kind,desc):
    base=0xA000 if bank==8 else 0xC000 if bank==14 else 0xE000
    REGIONS.append((bank,base,lo,hi,name,kind,desc))
region(8,44356,44385,'AdvancePlayerAttackPhase','code','Increment CF; exact equality with Y resets CF and advances CD by2. A is exclusive end; crossing it selects idle preserving facing. Period is handler calls, not measured frames.')
region(8,44418,44440,'SamplePlayerOffsetTerrain','code','AD82 copies player16-bit position to26..29, preserves signed X offset A and Y offset; AD94 reuses base; tail C767.')
region(8,44440,44495,'SampleTwoPlayerTerrainPoints','code','Entry offsets Y=-28,-2,-5,+4,+3. Sample X=-5,+5 through actualC767 and OR results;42 saves Y.')
region(8,44541,44564,'SelectHorizontalPlayerMotion','code','One-pixel speed; OR held input and two prior samples. Right bit wins simultaneous left/right.')
region(8,44564,44721,'MovePlayerLeft','code','Explicit speed entry; three points X-9,Y-28/-14/0 block on bits03. CE04 suppresses translation on oddD8. Wall snap lowX to cellcenter8; camera mode07 and lower pageAF; left screen clamp20.')
region(8,44721,44871,'MovePlayerRight','code','Explicit speed; symmetric X+9 probes. Camera mode05 starts at relativeX128, caps at AF:00; right screen clamp235. Movement CE40 may be set even on slow-terrain skipped tick.')
region(8,44871,44890,'SelectFreeVerticalPlayerMotion','code','Speed2; held down wins up; no direction returns via sharedRTS. Not a jump integrator.')
region(8,44890,44988,'MovePlayerUp','code','Unsigned explicit speed; mode03 scroll when relativeY<96, camera-underflow clamp and flagclear; player top clamp31; CE10/40 motion bits.')
region(8,44988,45063,'MovePlayerDown','code','Unsigned explicit speed; mode01 scroll at relativeY>=128 and compare camera limitAD/AE; relativeY>=206 falls through reviewed terminal-fall entryB007. High/low limit compare is not a generic16-bit comparator for arbitrary synthetic pages.')
region(8,45078,45087,'MarkDownwardPlayerMotion','code','Clear CE10/20 then set40; tail after nonterminal downward move.')
region(8,47114,47127,'PlayerJumpStepMagnitudes','data','13 bytes:3 fourtimes,2 fourtimes,1 fourtimes,0. D1 low6 indexes; normal domain0..12 only.')
region(8,47127,47133,'PlayerForwardAttackStepMagnitudes','data','Six unsigned horizontal speeds2,3,3,3,3,2, indexed (CD-A0)/2.')
region(8,47133,47233,'UpdateStandingPlayer','code','Two ground probes, vertical alignment and embedded correction; newA wins newB. B selects down beforeup; no attack dispatches full direction nibble.')
region(8,47233,47265,'StandingDirectionSplitPointers','data','16 low bytes then16 highbytes: right/left enterwalk; down enterscrouch; other direction combinations RTS.')
region(8,47265,47285,'EnterWalkOrCrouchPlayer','code','B8A1 selects02,right; B8A5 selects03,left; both clearCF. B8AE ORs10 for crouch. B8B4 sharedRTS.')
region(8,47285,47378,'UpdateWalkingPlayer','code','Ground align; newA/newB priority; direction OR current and twohistorybytes. CD lowbit follows right priority. SBC07 inherits carry from oldCDbit7, so normal low states advance every8 calls, not7.')
region(8,47378,47407,'UpdateJumpingPlayer','code','BCEF physics then facing and newB dispatch; D1zero returnsidle unless downattack1C wasselected.')
region(8,47407,47431,'AdvancePlayerAirTransition','code','Facing/newB; horizontalmove; CD+=2 andD1&=3F. Caller can therefore modify freshly selectedattack code.')
region(8,47431,47474,'UpdateFallingPlayer','code','Facing/newB; landing probesY-5/+3. Else decrement lowphase but use predecrement index for down speed, thenhorizontalmove.')
region(8,47474,47492,'SelectAirbornePlayerAttack','code','16-way held direction nibble split-pointer dispatch; opposing/unsupported combinations return unchanged.')
region(8,47492,47524,'AirborneAttackSplitPointers','data','No direction normal; horizontal forwardtier; down/down-diagonal downwardtier; up/up-diagonal upwardtier; unsupported masks sharedRTS.')
region(8,47524,47572,'UpdateCrouchingPlayer','code','Ground required; newA jump; down current/history preservescrouch; optional facing fromcurrenthorizontal; newB entersBCAE grounded12 withoutlevel2 slidingreplacement.')
region(8,47572,47608,'UpdateCrouchingAttack','code','Groundrequired; five states12..1A each3calls, thenreturn10 facingpreserved.')
region(8,47608,47672,'UpdateDownwardAttack','code','Horizontalmove; lowerpoints use destructiveC773 withstrength4. Clearsolidbit meansdown4; solidbitalignsY andidle. Destructive highflagcallee remains partlyunreviewed.')
region(8,47672,47682,'UpdateAttack1E','code','Physics then linearphase period4 exclusiveend2C.')
region(8,47682,47692,'UpdateAttack2C','code','Physics then linearphase period4 exclusiveend42.')
region(8,47692,47715,'UpdateAttack42','code','Physics; D3&A0 freezes animation; otherwise++CF indexes BA63 preserving facing.')
region(8,47715,47748,'PlayerAttack42Sequence','data','33 statecodes; initializedCF0 displays42, firstcallindex1. Index32 returnsidle.')
region(8,47748,47758,'UpdateAttack5C','code','Physics then linearphase period3 exclusiveend7E.')
region(8,47758,47768,'UpdateAttack7E','code','Physics then linearphase period3 exclusiveendA0.')
region(8,47768,47905,'UpdateForwardAttack','code','Six A0..AA phases6calls. Speed table; two wall probes; wall/end checkshead, normallyenters0A. Blockinghead canflip facing ifCE40clear; seedD1=3. D1=80launch andgroundlaunchsharehandler.')
region(8,47905,47915,'UpdateAttackAC','code','Physics then period3 exclusiveendB8; AC..B6 take18calls, despiteB8alsohavingthishandler in dispatchtable.')
region(8,48146,48180,'EnterIdleJumpOrFall','code','BC12idle;BC17sound35,state0A,D1=E7 andimmediateup3;BC2Astate0E,D1zero.')
region(8,48180,48214,'SelectForwardAttackTier','code','Level>=5 andfacingcompatible direction selectsA0,D1=80;else normalattacktier. Zero horizontal is accepted atthisentry.')
region(8,48214,48257,'SelectNormalAttackTier','code','Level0..3=>1E,4..5=>2C,6..7=>7E; BC67 bypasseslevel6replacement. Statehelperpreservesfacing,clearsCF.')
region(8,48257,48281,'SelectDownwardAttackTier','code','Level>=1=>1C,D1zero;level0=>fall0E,D1zero.')
region(8,48281,48318,'SelectGroundDownAttackTier','code','Level>=2=>A0,D1zero;lowerlevels useBCAE requiringground andstate12. DirectBCAE bypasseshigherlevelreplacement.')
region(8,48318,48367,'SelectUpwardAttackTier','code','Level7=>42;elselevel>=3 plushorizontal=>5C;elseAC. BCCF bypasseslevel7replacement.')
region(8,48367,48470,'IntegratePlayerJumpPhase','code','D1bit40ascending; negativeholdphase continuesup3 whileheldA orhistorylow2. Release seeds40 withoutverticalstep; indexed taper endswith0C; descent uses predecrementindex; groundaligns andclearsD1. Ceilingsblockbit02.')
region(14,55784,55815,'SampleTerrainAtBase','code','Copy26..29 to22..25 then classifyDD5F; zero returns, negativeROMlookup, positivecache.')
region(14,55815,55869,'SampleTerrainAtSignedOffset','code','Signextend A Xoffset andY Yoffset, add16-bit base, classifyDD5F, selectcache/ROM/outside.')
region(14,55869,55987,'LookupTerrainFromSceneRom','code','Normalize linearY into240pixelpages;32pixelmetatile index and16pixelquadrant; saveR6andX,map03B9; B9pageorder,BB64-bytepages,C1fourattributes/metatile; restoreR6/X. Areturnsattribute but3Cremains03; DB02 caller returns3C ratherthanA.')
region(14,55987,56002,'SampleCachedTerrainAtBase','code','Direct cache base sampler; no domainclassifier.')
region(14,56002,56066,'SampleCachedTerrainAtSignedOffset','code','Signed16-bit coordinateaddition; normalizeY withF78B thenindex=(Ymod240&F0)|(Xlow>>4), load05B8+index toAand3C. EntryDAE6acceptsYlow/Ahigh.')
region(14,56671,56761,'SelectTerrainCacheOrRom','code','Scene bypassflag=>cache; otherwise negativeworldcoords=>outside, transversepage mismatch=>outside, longitudinalmismatch=>ROM; horizontalrelativeX>=248=>ROM. DD92..DD9B block has no path fromreviewedentry (precedingBCC/BCS exhaustive). Outside sets3C03,A0;ROMsets3C03,AFF.')
region(14,56761,56793,'SceneTerrainCacheBypassFlags','data','32 bytes; nonzero7,11,14,18,19,22,23,24,25 bypassDD5Fcoordinatechecks; no sectorassignmentinferred.')
region(15,62733,62752,'ResolveSceneMetatilePagePointer','code','Read pageID throughB9,Y; add64*ID splitoffsettables toBB/BC; return22/23. 32-byte tablesdefinevalidIDs0..31, no boundscheck.')
region(15,62752,62784,'ScenePageOffsetLow','data','32 lowbytes of64*ID.')
region(15,62784,62816,'ScenePageOffsetHigh','data','32 highbytes of64*ID.')
COMMENTS={(8,0xB8FA):"Carry from old CD bit7; normal walking states need8 calls.",(8,0xBD3F):"Lookup uses phase before decrement.",(14,0xDA9E):"3C is forced03; actual ROM attribute returned through3D/A.",(14,0xDB01):"Onlycachepath copies actualattribute to3C."}
R7_AT_CALL={}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();rom,_=verified_rom(a.rom);prg=rom[16:0x20010]
    ranges=[];ins=[];func=[];evidence=[];edges=[];access=[]
    for i,(bank,base,lo,hi,name,kind,desc) in enumerate(REGIONS,1):
        rid=f'G{i:02d}';m=MPU();m.memory[base:base+8192]=prg[bank*8192:(bank+1)*8192];d=Disassembler(m)
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
    all_ranges=[r for r in read('analysis/reviewed_ranges.csv') if not r['id'].startswith('G')]+ranges
    all_ins=[r for r in read('analysis/reviewed_instructions.csv') if not r['region_id'].startswith('G')]+ins
    all_ranges.sort(key=lambda r:int(r['prg_offset'],16));all_ins.sort(key=lambda r:int(r['prg_offset'],16))
    covered=set();code=set();data=set()
    for r in all_ranges:
        lo=int(r['prg_offset'],16);span=set(range(lo,lo+int(r['size'])));assert not covered&span,r;covered|=span;(code if r['classification']=='code' else data).update(span)
    write_csv(ROOT/'analysis/reviewed_ranges.csv',all_ranges);write_csv(ROOT/'analysis/reviewed_instructions.csv',all_ins)
    for rel,new in [('analysis/functions.csv',func),('analysis/evidence.csv',evidence)]:write_csv(ROOT/rel,[r for r in read(rel) if not r['id'].startswith('G')]+new)
    def is_new(bank,pc):return any(int(r['bank'],16)==bank and int(r['cpu'],16)<=pc<int(r['end_cpu_exclusive'],16) for r in ranges)
    for rel,new,bk,pc in [('analysis/cross_references.csv',edges,'from_bank','from_cpu'),('analysis/memory_accesses.csv',access,'bank','cpu')]:write_csv(ROOT/rel,[r for r in read(rel) if not is_new(int(r[bk],16),int(r[pc],16))]+new)
    accesses=read('analysis/memory_accesses.csv');write_csv(ROOT/'analysis/hardware_accesses.csv',[r for r in accesses if 0x2000<=int(r['operand_base'],16)<=0x4017 or r['access']!='read' and int(r['operand_base'],16)>=0x8000])
    candidates=read('analysis/fixed_window_candidates.csv');keys={(r['bank'],r['cpu']) for r in all_ins}
    for r in candidates:
        if (r['bank'],r['cpu']) in keys:r['status']='REVIEWED'
        elif is_new(int(r['bank'],16),int(r['cpu'],16)):r['status']='CONFLICT_WITH_REVIEWED_RANGE'
    write_csv(ROOT/'analysis/fixed_window_candidates.csv',candidates)



    def byte(bank,addr):return prg[bank*8192+(addr&8191)]
    def source(bank,addr):return {f'source_{k}':v for k,v in loc(bank,0xA000 if bank==8 else 0xC000 if bank==14 else 0xE000,addr).items()}
    dirs=[];indirect=[r for r in read('analysis/indirect_dispatch_tables.csv') if not r['group'].startswith('G_')]
    for family,lo,hi,dispatch in [('Standing',0xB881,0xB891,0xB84A),('AirAttack',0xB984,0xB994,0xB981)]:
        for i in range(16):
            target=byte(8,lo+i)|byte(8,hi+i)<<8
            name=next(r['symbol'] for r in ranges if r['classification']=='code' and r['bank']=='08' and int(r['cpu'],16)<=target<int(r['end_cpu_exclusive'],16))
            dirs.append({'family':family,'direction_mask':f'0x{i:02X}',**source(8,lo+i),'high_byte_cpu':f'0x{hi+i:04X}','target_bank':'08','target_cpu':f'0x{target:04X}','target_semantics':name})
            indirect.append({'group':'G_'+family,'dispatch_bank':'08','dispatch_cpu':f'0x{dispatch:04X}','index':i,'selector':f'held20&0F equals{i:02X}','table_bank':'08','table_cpu':f'0x{lo+i:04X}','target_bank':'08','target_cpu':f'0x{target:04X}','target_semantics':name})
    write_csv(ROOT/'analysis/player_direction_dispatch.csv',dirs)
    for r in indirect:
        for area in ranges:
            if area['classification']=='code' and r['target_bank']==area['bank'] and int(area['cpu'],16)<=int(r['target_cpu'],16)<int(area['end_cpu_exclusive'],16):r['target_semantics']=area['symbol']
    write_csv(ROOT/'analysis/indirect_dispatch_tables.csv',indirect)
    states=read('analysis/player_state_dispatch.csv')
    for r in states:
        if (r['handler_bank'],r['handler_cpu']) in keys:r['handler_review']='STATIC_REVIEWED'
    write_csv(ROOT/'analysis/player_state_dispatch.csv',states)
    write_csv(ROOT/'analysis/player_jump_step_table.csv',[{'phase':i,'magnitude_pixels':byte(8,0xB80A+i),**source(8,0xB80A+i),'scope':'normal valid phase0..12; ascending incrementfirst, descendinglookupfirst'} for i in range(13)])
    write_csv(ROOT/'analysis/player_attack42_sequence.csv',[{'index':i,'state_even':f'0x{byte(8,0xBA63+i):02X}',**source(8,0xBA63+i)} for i in range(33)])
    write_csv(ROOT/'analysis/scene_terrain_cache_flags.csv',[{'scene_index':f'0x{i:02X}','bypass_flag':byte(14,0xDDB9+i),**source(14,0xDDB9+i)} for i in range(32)])
    cov=json.loads((ROOT/'analysis/coverage.json').read_text());cov.update({'reviewed_code_bytes':len(code),'reviewed_data_bytes':len(data),'reviewed_code_plus_data_bytes':len(covered),'reviewed_prg_fraction':len(covered)/131072,'reviewed_code_range_count':sum(r['classification']=='code' for r in all_ranges),'reviewed_data_range_count':sum(r['classification']=='data' for r in all_ranges),'stage02E_added_bytes':sum(int(r['size']) for r in ranges)})
    write_json(ROOT/'analysis/coverage.json',cov)
    result={'new_ranges':len(ranges),'new_code_ranges':sum(r['classification']=='code' for r in ranges),'new_data_ranges':sum(r['classification']=='data' for r in ranges),'new_instructions':len(ins),'new_bytes':sum(int(r['size']) for r in ranges),'new_indirect_edges':32,'unresolved_targets_from_new_code':[r for r in edges if r['to_bank']=='UNRESOLVED'],'scope':'normalplayer inputs/jump/movement/localattacksequence; terrainlookup. No complete combat/terrain mutation/sector mapping/nativeNES claim.'}
    write_json(ROOT/'analysis/stage02E_static_summary.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
