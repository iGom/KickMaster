#!/usr/bin/env python3
"""Stage02C: magic acquisition, selection and bounded effect control paths."""
import argparse,json
from baseline import ROOT,verified_rom,write_csv,write_json
from architecture_stage01b import read,loc,MPU,Disassembler
REGIONS=[]
def region(bank,lo,hi,name,kind,desc):
    REGIONS.append((bank,0xC000 if bank==14 else 0xE000 if bank==15 else 0xA000,lo,hi,name,kind,desc))
for bank,entries in [
(7,[
(0xABE0,0xABF8,'MagicMenuIconCoordinates','data','Twelve Y/X byte pairs for menu cells; not world coordinates.'),
(0xAC35,0xAC41,'MagicMenuCellToEffect','data','Twelve-cell order05,00,08,0B,09,03,01,06,04,0A,02,07; permutation of acquired-effect bits.'),
(0xAC42,0xAC75,'RunMagicSelectionMenu','code','Locate current cell, service frame and cursor, optional level cycle; Start exits before A selection, A requests selection, redraw then repeat. Frame/graphics callees not all reviewed.'),
(0xAC75,0xAC8D,'MagicCursorCoordinates','data','Twelve byte pairs used as cursor origin by AD21; not CPU pointers.'),
(0xAC8D,0xACBD,'MagicSelectionGlyphs','data','Twelve four-byte effect-indexed sprite arguments for selected-cell rendering.'),
(0xACBD,0xAD03,'MoveMagicMenuCursor','code','12-cell4-column grid; Right/Left/Down/Up priority from pressed1F; rejected first direction does not fall back. Restore1F, sound39 only on move.'),
(0xAD03,0xAD21,'CycleLevelUnderBypassFlag','code','Pressed B and01A5 nonzero: D3=(old&F0)|((old+1)&7), dropping bit3; does not recompute capacities.'),
(0xAD21,0xAD65,'DrawMagicMenuCursor','code','Draw cursor and four selected-effect glyphs only when acquired bit is set; calls sprite serviceC755.'),
(0xAD65,0xAE3A,'CommitMagicMenuSelection','code','Locked selection returns unchanged; acquired cell writes06BD, animates icon toward HUD in16 update steps and invokes AE3A. Frame/draw callees bounded separately.'),
(0xAEA0,0xAEB6,'TestMagicMenuCellOwned','code','Copy06BE/BF into scratch3A/B, translate cell viaAC35, shift to carry; carry equals acquired bit.'),
(0xAEB6,0xAEC6,'FindSelectedMagicMenuCell','code','Reverse-search cells11..1; match returns index, unmatched selection including0C falls back to cell0.')]),
(8,[
(0xA7DB,0xA831,'CollectMagicAndBeginPresentation','code','Remember pickup inD0, set acquired bit, audio00=2D/01=0,CF0,CEbit0clear,CD=CC/facing; move pickup to playerX±5,playerY-26hex. Does not immediately deactivate or change06BD.'),
(0xA831,0xA860,'UnlockMagicEffect','code','For type50..67, OR one of12 little-endian bit masks into06BE/BF;04E3=effectID; fill06C0 if exactly0C,otherwise overwrite06C1. Duplicate acquisition not suppressed.'),
(0xA860,0xA878,'MagicUnlockBitMasks','data','Twelve little-endian masks1<<effectID, bits0..11; internalID=(type&FE-50)/2.'),
(0xBBAD,0xBBDC,'AdvanceMagicAcquisitionAnimation','code','SetD3bit80, clear collected-object flag20, incrementCF; table indexedCF>>3 choosesCC/CE/D0 states. On terminal0 clearCF and pickup then jumpBD56.'),
(0xBBDC,0xBBE9,'MagicAcquisitionAnimationStates','data','Thirteen states CC CE D0 D0 D0 CE CC CC CC CC CC CC 00; startingCF0 reaches presentation on96th invocation.'),
(0xBD56,0xBDBB,'PresentAcquiredMagicAndRoute','code','Fade, far-call07:A0BD with layout7, mapR6=3 and read effect description pointer; wait Start/A then fade and use32-entry routing table. Presentation/NMI/text pipeline not fully executed.'),
(0xBDBB,0xBDDB,'MagicAcquisitionSceneRoutes','data','32 scene routes: FF tails scene-advance serviceC79D; other bytes replace9A then tail restartC77F.'),
(0xBDDB,0xBDF3,'MagicDescriptionPointers','data','Twelve little-endian pointers selected by04E3; explicit R6=03 maps text in8000 window. Text payload semantics unreviewed.')]),
(9,[
(0xAC0F,0xAC27,'MagicContinuationHandlerPointers','data','Twelve handlers for even types88..9E;96 level-up visual remains unreviewed; others control decoy/shield/lightning continuations.'),
(0xB65E,0xB677,'CopySelectedEffectPositionToObject','code','Copy selected effect slot3 Y/X pairs to global objectY; preservesY.'),
(0xB677,0xB68C,'AnchorSelectedEffectToPlayer','code','Copy player worldY/X to reserved global slot3.'),
(0xB6DF,0xB727,'CastDirectionalMagicProjectile','code','Update aiming orb; newSelect, free reserved projectile slot and cost3MP required; spawn type10 flags80 with one of16 direction velocities; restoreX.'),
(0xB727,0xB737,'DirectionalProjectileVelocityX','data','Sixteen signed X velocities indexed held direction nibble; no-direction uses player facing.'),
(0xB737,0xB747,'DirectionalProjectileVelocityY','data','Sixteen signed Y velocities paired with B727.'),
(0xB747,0xB7B2,'UpdateMagicAimingOrb','code','SaveX, copy facing, move current aim index one step toward previous target, position at signed offset from player, then derive next target from held-direction nibble.'),
(0xB7B2,0xB7C2,'MagicAimTargetIndices','data','Sixteen direction-nibble target indices0..8; default facing suppliesLeft/Right.'),
(0xB7C2,0xB7D4,'MagicAimOffsets','data','Nine signed X/Y offset pairs; original scale pixels, player-relative.'),
(0xB7D4,0xB830,'CastHorizontalMagicWave','code','Update aiming orb; newSelect, free reserved projectile slot and cost5MP required; spawn type00/01,flags90,velocityX±8,Y0 at orbY-8.'),
(0xB830,0xB869,'ToggleObjectAttributeEffect','code','Cost1MP starts240-count effect and setsB8=DF; active calls decrement, toggleB8bit20 on multiples4, restoreFF at expiry. Hidden-object reveal semantics not established.'),
(0xB869,0xB88E,'StartOverheadLightning','code','NewSelect and20MP reanchor slot3, set velocityY=F8,type8C,counter5,secondarycounter0.'),
(0xB88E,0xB8B7,'StartQuakeAndUpdateScrollPhase','code','Cost20MP invokesC7BE once; cycle0593/03D6 from1 through59 then0. Active calls ignore newSelect; enemy duration beyond flag setter unresolved.'),
(0xB8B7,0xB8F0,'StartTerrainProtectionTimer','code','Cost20MP sets palette0158=16,counters04:F0; same invocation decrements lowcounter. Expiry after1008 handler invocations restoresFFB5 palette byte.'),
(0xB8F0,0xB90C,'StartShieldEffect','code','Cost30MP sets sound9D,secondarycounter0A,type8A; actual hit consumption not reviewed.'),
(0xB90C,0xB930,'StartDecoyEffect','code','Cost20MP reanchors slot3,sets counterC9,type88,flags84.'),
(0xB930,0xB964,'UpdateDecoyLifetimeAndBounds','code','Require same cameraX page and relativeY in0..EF; then decrementC9 lifetime. Offscreen or zero resets type86 and counter0.'),
(0xB964,0xB972,'UpdateShieldAnchorOrFinish','code','While05A7 nonnegative anchor slot3 to player; negative returns type84. Consumer of shield budget outside this range.'),
(0xB972,0xB991,'RaiseLightningToCameraTop','code','Track playerX; low-byte effectY-cameraY<30 stops vertical velocity and changes type8E.'),
(0xB991,0xB9DB,'SpawnOverheadLightningBolts','code','Anchor selected effect at cameraY+30 and playerX; after5-count wait spawn3 slots with types28,18,29,flagsD4,zero velocities; selectedtype90.'),
(0xB9DB,0xB9E1,'LightningBoltTypesAndCounters','data','Three types28,18,29 then three counters08,15,08; not three-byte CPU pointers.'),
(0xB9E1,0xBA19,'HoldAndLowerLightning','code','Anchor at cameraY+30/playerX; decrement05A7 seeded0 (256 invocations), toggle90/92 on odd remaining count; zero selects94 and downwardvelocity8.'),
(0xBA19,0xBA3B,'FinishLightningNearPlayer','code','TrackplayerX; wrapped(effectY-playerY+10hex)<40hex stops velocity and restores readytype76.'),
(0xBA3B,0xBA75,'ToggleAndRechargeFlight','code','NegativeD3 blocks before any cost; Select togglesCEbit0 and clearsCD to facing. Starting or every30 active handler updates spends10MP; failure clears flightbit.'),
(0xBA75,0xBAC4,'StartThreeColumnLightning','code','If not active, Select and30MP set0593=1 and populate global slots0..2 atcameraX+20/80/E0,cameraY+CF,types98,flags84.'),
(0xBAC4,0xBAC7,'LightningColumnOffsets','data','Three camera-relative X offsets20,80,E0.'),
(0xBAC7,0xBB1D,'UpdateLightningColumn','code','Followcamera,increment0590; slot0 requests queued damage6 on ticks8/16/24. Tick30deactivates and clears selected active marker; type animation table otherwise.'),
(0xBB1D,0xBB2D,'LightningColumnTypeSequence','data','Sixteen even/odd type bytes; facing ignored by handler dispatch, preserved by rendering.'),
(0xBD1B,0xBD46,'QueueDamageForEligibleEnemies','code','Scan10 slots9..0; flags0469>=C0 and0473&3==0 accept raw requestA into0441,OR0469bit20,clear047Dlow3. Does not apply HP damage here.'),
(0xBDA8,0xBDB3,'FindFreeReservedProjectileSlot','code','Scan global slots2..0 for nonnegative057C; allbusy returnsY=FF/Nset. Distinct from general collectible allocator.')]),
(14,[
(0xD7E7,0xD805,'MarkEnemiesForQuake','code','For8 entries0473..047A,bit20 excludes; elseclearbits40/10 then set10. Set03DC=1. Freeze timer consumption not reconstructed.')]),
(15,[(0xFEF6,0xFF2A,'MagicMenuIconSpriteArguments','data','Thirteen four-byte icon argument groups; two A/X pairs consumed by menu sprite calls; last group used for locked icons.')])
]:
    for lo,hi,name,kind,desc in entries:region(bank,lo,hi,name,kind,desc)
COMMENTS={(8,0xA851):'06C0/06C1 are two pending icon slots; duplicates are not checked here.',(7,0xACBF):'First pressed direction wins even when blocked at an edge.',(7,0xAD1A):'Mask07 drops old bit3; high nibble is restored separately.',(9,0xB7DD):'Projectile allocation precedes MP charge: full reserved pool costs nothing.',(9,0xB8DF):'Activation falls through decrement; total is F0+3*100=3F0 hex handler calls.',(9,0xBA5B):'10 is packed decimal10MP; counter1E is30 handler calls,not verified seconds.',(9,0xBD1B):'Queue request only; enemy HP, immunity and final resolution are separate.'}
R7_AT_CALL={}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();rom,_=verified_rom(a.rom);prg=rom[16:0x20010]
    ranges=[];ins=[];func=[];evidence=[];edges=[];access=[]
    for i,(bank,base,lo,hi,name,kind,desc) in enumerate(REGIONS,1):
        rid=f'E{i:02d}';m=MPU();m.memory[base:base+8192]=prg[bank*8192:(bank+1)*8192];d=Disassembler(m)
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
    all_ranges=[r for r in read('analysis/reviewed_ranges.csv') if not r['id'].startswith('E')]+ranges
    all_ins=[r for r in read('analysis/reviewed_instructions.csv') if not r['region_id'].startswith('E')]+ins
    all_ranges.sort(key=lambda r:int(r['prg_offset'],16));all_ins.sort(key=lambda r:int(r['prg_offset'],16))
    covered=set();code=set();data=set()
    for r in all_ranges:
        lo=int(r['prg_offset'],16);span=set(range(lo,lo+int(r['size'])));assert not covered&span,r;covered|=span;(code if r['classification']=='code' else data).update(span)
    write_csv(ROOT/'analysis/reviewed_ranges.csv',all_ranges);write_csv(ROOT/'analysis/reviewed_instructions.csv',all_ins)
    for rel,new in [('analysis/functions.csv',func),('analysis/evidence.csv',evidence)]:write_csv(ROOT/rel,[r for r in read(rel) if not r['id'].startswith('E')]+new)
    def is_new(bank,pc):return any(int(r['bank'],16)==bank and int(r['cpu'],16)<=pc<int(r['end_cpu_exclusive'],16) for r in ranges)
    for rel,new,bk,pc in [('analysis/cross_references.csv',edges,'from_bank','from_cpu'),('analysis/memory_accesses.csv',access,'bank','cpu')]:write_csv(ROOT/rel,[r for r in read(rel) if not is_new(int(r[bk],16),int(r[pc],16))]+new)
    accesses=read('analysis/memory_accesses.csv');write_csv(ROOT/'analysis/hardware_accesses.csv',[r for r in accesses if 0x2000<=int(r['operand_base'],16)<=0x4017 or r['access']!='read' and int(r['operand_base'],16)>=0x8000])
    candidates=read('analysis/fixed_window_candidates.csv');keys={(r['bank'],r['cpu']) for r in all_ins}
    for r in candidates:
        if (r['bank'],r['cpu']) in keys:r['status']='REVIEWED'
        elif is_new(int(r['bank'],16),int(r['cpu'],16)):r['status']='CONFLICT_WITH_REVIEWED_RANGE'
    write_csv(ROOT/'analysis/fixed_window_candidates.csv',candidates)



    def byte(b,a):return prg[b*8192+(a&8191)]
    def word(b,a):return byte(b,a)|byte(b,a+1)<<8
    def source(b,a):return {f'source_{k}':v for k,v in loc(b,0xC000 if b==14 else 0xE000 if b==15 else 0xA000,a).items()}
    menu=[byte(7,0xAC35+i) for i in range(12)];assert sorted(menu)==list(range(12))
    names=['Life Up 1','Life Up 2','Harpy Flying / Harpy Wings','Lightning / Lightning Spirit','Whip Lightning','Bouncing Bulb / Bouncing Bulb Spirit','Pulse Wave / Pulse Wave Spirit','Earthquake','Magic Boots','?? Magic','Force Shield','Twin Power']
    costs=[60,90,10,20,30,3,5,20,20,1,30,20]
    policies=['per Select','per Select','activation and each30 active handler updates; toggle off free','per launch','per inactive launch','per projectile only if free reserved slot','per projectile only if free reserved slot','per inactive activation','per inactive activation','per inactive activation','per launch','per launch']
    mapping=[];selected=read('analysis/selected_spell_dispatch.csv')
    for i in range(12):
        mask=word(8,0xA860+i*2);assert mask==1<<i;r=selected[i]
        mapping.append({'effect_index':f'0x{i:02X}','pickup_type_even':f'0x{0x50+2*i:02X}','pickup_type_odd':f'0x{0x51+2*i:02X}','unlock_mask_16bit':f'0x{mask:04X}','unlock_RAM_byte':f'0x{0x6BE+i//8:04X}','unlock_bit':i%8,'menu_cell':menu.index(i),'menu_row':menu.index(i)//4,'menu_column':menu.index(i)%4,**source(8,0xA860+i*2),'menu_source_cpu':f'0x{0xAC35+menu.index(i):04X}','handler_bank':'09','handler_cpu':r['handler_cpu'],'cost_MP_decimal':costs[i],'charge_policy':policies[i],'external_name_correlation':names[i],'name_evidence':'ROM behavior/cost plus supplied Wyrenth Spells lines262-331 and prior manual reference; glyph identity not visually validated','full_spell_semantics':'PARTIAL; activation/control path reviewed; downstream collision/damage/AI may remain unresolved'})
        r['MP_cost_decimal']=costs[i];r['effect']=names[i];r['review_scope']='02C activation/control plus02B healing; no claim of full projectile/collision semantics';r['charge_policy']=policies[i]
    selected[-1]['review_scope']='none';selected[-1]['charge_policy']='none'
    write_csv(ROOT/'analysis/magic_unlock_menu_map.csv',mapping);write_csv(ROOT/'analysis/selected_spell_dispatch.csv',selected)
    pickups=read('analysis/pickup_effects.csv')
    for r in pickups:
        typ=int(r['type_even'],16)
        if 0x50<=typ<0x68:r['handler_review']='STATIC_REVIEWED';r['effect']='unlock effect index'+str((typ-0x50)//2)+'; begin acquisition animation/presentation; full presentation rendering not tested'
    write_csv(ROOT/'analysis/pickup_effects.csv',pickups)
    routes=[];descriptions=[]
    for i in range(32):
        value=byte(8,0xBDBB+i)
        routes.append({'scene_index':f'0x{i:02X}',**source(8,0xBDBB+i),'route_byte':f'0x{value:02X}','action':'advance via0E:C79D' if value==255 else 'replace9A then restart via0E:C77F','stage_name':'UNRESOLVED; table route alone does not establish sector identity'})
    for i in range(12):
        target=word(8,0xBDDB+i*2);assert 0x8000<=target<0xA000
        targetloc=loc(3,0x8000,target);targetloc['mapping_condition']='MMC3 mode0; explicit R6=03 at08:BD70..BD74'
        descriptions.append({'effect_index':f'0x{i:02X}',**source(8,0xBDDB+i*2),**{'target_'+k:v for k,v in targetloc.items()},'payload_review':'UNREVIEWED description bytes'})
    write_csv(ROOT/'analysis/magic_acquisition_scene_routes.csv',routes);write_csv(ROOT/'analysis/magic_description_pointers.csv',descriptions)
    aim=[]
    for i in range(16):
        vx=byte(9,0xB727+i);vy=byte(9,0xB737+i)
        aim.append({'held_direction_nibble':f'0x{i:02X}','aim_target':byte(9,0xB7B2+i),'projectile_velocity_x':vx if vx<128 else vx-256,'projectile_velocity_y':vy if vy<128 else vy-256,'zero_nibble_caveat':'runtime substitutes1(right)/2(left) based on facing, not literal row0',**source(9,0xB7B2+i),'velocity_x_source_cpu':f'0x{0xB727+i:04X}','velocity_y_source_cpu':f'0x{0xB737+i:04X}'})
    write_csv(ROOT/'analysis/magic_aim_and_velocity.csv',aim)
    indirect=[r for r in read('analysis/indirect_dispatch_tables.csv') if not r['group'].startswith('E_')]
    for i in range(12):
        target=word(9,0xAC0F+i*2)
        name=next((r['symbol'] for r in all_ranges if r['bank']=='09' and r['classification']=='code' and int(r['cpu'],16)<=target<int(r['end_cpu_exclusive'],16)),'UNREVIEWED')
        indirect.append({'group':'E_MagicContinuations','dispatch_bank':'09','dispatch_cpu':'0xBF65','index':i,'selector':f'0568,X&FE equals0x{0x88+2*i:02X}','table_bank':'09','table_cpu':f'0x{0xAC0F+2*i:04X}','target_bank':'09','target_cpu':f'0x{target:04X}','target_semantics':name})
    for r in indirect:
        for area in ranges:
            if area['classification']=='code' and r['target_bank']==area['bank'] and int(area['cpu'],16)<=int(r['target_cpu'],16)<int(area['end_cpu_exclusive'],16):r['target_semantics']=area['symbol']
    write_csv(ROOT/'analysis/indirect_dispatch_tables.csv',indirect)
    states=read('analysis/player_state_dispatch.csv')
    for r in states:
        r['handler_review']=next((a['symbol'] for a in all_ranges if a['bank']==r['handler_bank'] and a['classification']=='code' and int(a['cpu'],16)<=int(r['handler_cpu'],16)<int(a['end_cpu_exclusive'],16)),'UNREVIEWED')
    write_csv(ROOT/'analysis/player_state_dispatch.csv',states)
    cov=json.loads((ROOT/'analysis/coverage.json').read_text());cov.update({'reviewed_code_bytes':len(code),'reviewed_data_bytes':len(data),'reviewed_code_plus_data_bytes':len(covered),'reviewed_prg_fraction':len(covered)/131072,'reviewed_code_range_count':sum(r['classification']=='code' for r in all_ranges),'reviewed_data_range_count':sum(r['classification']=='data' for r in all_ranges),'stage02C_added_bytes':sum(int(r['size']) for r in ranges)})
    write_json(ROOT/'analysis/coverage.json',cov)
    result={'new_ranges':len(ranges),'new_code_ranges':sum(r['classification']=='code' for r in ranges),'new_data_ranges':sum(r['classification']=='data' for r in ranges),'new_instructions':len(ins),'new_bytes':sum(int(r['size']) for r in ranges),'magic_effect_rows':12,'menu_cells':12,'acquisition_routes':32,'description_pointers':12,'new_indirect_edges':12,'unresolved_targets_from_new_code':[r for r in edges if r['to_bank']=='UNRESOLVED'],'scope':'bounded acquisition/menu/effect control; downstream collision/projectile AI not complete'}
    write_json(ROOT/'analysis/stage02C_static_summary.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
