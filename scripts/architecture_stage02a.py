#!/usr/bin/env python3
"""Stage 02A: bounded player/state and scene configuration reconstruction.

Preserve A/B evidence; table targets are not automatically promoted to reviewed code.
"""
import argparse,json
from baseline import ROOT,verified_rom,write_csv,write_json
from architecture_stage01b import read,loc,MPU,Disassembler

REGIONS=[]
def region(bank,lo,hi,name,kind,description):
    base=0xC000 if bank==14 else 0xE000 if bank==15 else 0xA000
    REGIONS.append((bank,base,lo,hi,name,kind,description))
for lo,hi,name,kind,desc in [
 (0xA0DB,0xA0F2,'DispatchSceneEven','code','Require DB bits 7 and 0; select one of four targets with (DB>>1)&3.'),
 (0xA0F2,0xA0FA,'SceneEvenTargets','data','Four split low/high target bytes; down/up/right/left order follows DB direction selector.'),
 (0xA0FA,0xA111,'DispatchSceneOdd','code','Same DB gate and selector as even phase, different four-target table.'),
 (0xA111,0xA119,'SceneOddTargets','data','Four split low/high target bytes for odd phase.'),
 (0xA119,0xA130,'DispatchSceneExtra','code','Third DB-gated four-target dispatch used in even phases.'),
 (0xA130,0xA138,'SceneExtraTargets','data','Four split low/high target bytes for extra even-phase work.'),
 (0xA138,0xA139,'SceneDispatchReturn','code','Shared RTS when DB gate is closed.'),
 (0xA4E9,0xA537,'InitializeSceneCoordinates','code','Mask scene index to 7 bits; initialize camera and player coordinates, scroll shadows and IRQ profile; fall through configuration loader.'),
 (0xA537,0xA5AB,'LoadSceneConfiguration','code','Read 32-entry parallel arrays; set 03B9 and map R6, five pointers, DB flags, extents, palette selector and palette profile.'),
 (0xA5AB,0xA63E,'InitializeSpecialLayout','code','04E2 indexes 17-entry layout arrays; bank byte bit7 initializes camera X page then is cleared for R6; downstream A990/A6FE unreviewed.'),
 (0xA916,0xA935,'InitializeSevenScrollShadows','code','Populate seven PPUCTRL/X/Y shadow entries from camera coordinates, preserving input X.'),
 (0xA935,0xA990,'LoadScenePaletteProfile','code','Read 27-byte pointed profile into palette staging, eight bytes at 017D, 06B8 and CHR 44/45; install fixed sprite colors.'),
 (0xAAB6,0xAAD8,'MultiplyScreenCountBy240','code','Produce 16-bit 22/23 = input * F0 for input 00..80; 81..FF yield zero due to signed DEX gate; preserve X.'),
 (0xB022,0xB03F,'DispatchHudMaintenance','code','Negative A1 returns; otherwise increment, wrap exact 06 to 01, then dispatch six-entry table; not a general out-of-range clamp.'),
 (0xB03F,0xB04B,'HudMaintenanceTargets','data','Six split low/high pointers; valid normal rotation is indexes 01..05, index00 is RTS.'),
 (0xB04B,0xB0B0,'BuildPlayerHpBar','code','06BA decreases immediately to 06B9 or rises by one; encode full/partial/empty cells using capacity 06BB>>4 into eleven bytes at 0163.'),
 (0xB482,0xB53D,'SpecialLayoutArrays','data','17-entry CHR0, CHR1 and bank/page arrays followed by four arrays of 17 little-endian pointers.')
]:region(7,lo,hi,name,kind,desc)
for lo,hi,name,desc in [
 (0xB1E2,0xB202,'SceneInitialCameraXPages','32 initial camera X high bytes; low byte is zero.'),
 (0xB202,0xB222,'SceneInitialCameraYScreens','32 initial camera Y screen counts multiplied by F0.'),
 (0xB222,0xB242,'ScenePlayerXOffsets','32 player X offsets added to initial camera X.'),
 (0xB242,0xB262,'ScenePlayerYOffsets','32 player Y offsets added to initial camera Y; low result decremented once.'),
 (0xB262,0xB282,'SceneBank8000Table','32 PRG bank bytes for 03B9 and MMC3 R6.'),
 (0xB282,0xB2C2,'ScenePointerB9Table','32 little-endian pointers loaded into B9/BA; target meaning not inferred from address alone.'),
 (0xB2C2,0xB302,'ScenePointerBBTable','32 little-endian pointers loaded into BB/BC.'),
 (0xB302,0xB342,'ScenePointerBFTable','32 little-endian pointers loaded into BF/C0.'),
 (0xB342,0xB382,'ScenePointerBDTable','32 little-endian pointers loaded into BD/BE.'),
 (0xB382,0xB3C2,'ScenePointerC1Table','32 little-endian pointers loaded into C1/C2; used by collision path DA3D.'),
 (0xB3C2,0xB3E2,'ScenePaletteCycleTable','32 bytes loaded into 03BA; downstream palette-cycle encoding not fully reviewed.'),
 (0xB3E2,0xB402,'SceneDirectionFlagsTable','32 DB flag bytes; low direction codes 01 down,03 up,05 right,07 left; bit7 is runtime scroll activity.'),
 (0xB402,0xB422,'SceneHorizontalBoundPages','32 bytes loaded into AF; downstream movement compares camera X page.'),
 (0xB422,0xB442,'SceneVerticalBoundScreens','32 screen counts multiplied by F0 into AD/AE.'),
 (0xB442,0xB482,'ScenePaletteProfilePointers','32 pointers to 27-byte palette/CHR profiles; some targets reside in R7 bank07, others in R6-selected bank.')
]:region(7,lo,hi,name,'data',desc)
for lo,hi,name,kind,desc in [
 (0xAB16,0xAB19,'PlayerStageAdvanceTail','code','Tail through C79D to scene advance D1AA when F8 bit20 is set.'),
 (0xAB19,0xABC5,'UpdateAndDrawPlayer','code','Clear transient D3 bit7, honor advance flag, retain only CE bit0, dispatch player state, compute camera-relative coordinates, service hurt display and draw metasprite.'),
 (0xACF7,0xAD39,'DispatchPlayerState','code','A selects normal/alternate table family; CD>>1 selects CHR and CD&FE selects metasprite pointer plus handler; tail JMP through 2C/2D.'),
 (0xAD39,0xAD44,'SetPlayerStateKeepFacing','code','Replace CD bits7..1 with A bits7..1, preserve old CD bit0 and clear CF.'),
 (0xADCF,0xADE2,'SetPlayerMotionAndScrollFlags','code','ADCF sets CE bit40; ADD6 sets DB bit80; ADDC clears DB bit80.'),
 (0xADE2,0xADFD,'UpdateFacingFromInputHistory','code','OR current and two previous held inputs; Right takes precedence and clears CD bit0, otherwise Left sets it.'),
 (0xB007,0xB016,'EnterPlayerFallState','code','Set D3 bit80, CD=C4/C5 preserving facing, CF=0 and CE=0.'),
 (0xB02A,0xB042,'InitializePlayerStateBlock','code','Copy ten bytes to C9..D2, then clear active flags 057C..057C+0013 inclusive under valid small slot-count precondition.'),
 (0xB042,0xB04C,'InitialPlayerStateBytes','data','C9..D2 initial bytes 80 00 80 00 00 00 00 00 00 00.'),
 (0xB04C,0xB06B,'DispatchAutomaticCameraStep','code','Require DB bits08 and01; set DB bit80 and dispatch direction (DB>>1)&3.'),
 (0xB06B,0xB073,'AutomaticCameraStepTargets','data','Four split low/high pointers: B073,B07A,B086,B08D.'),
 (0xB073,0xB099,'StepCameraOnePixel','code','Four entries add/subtract one to 16-bit camera Y or X, wrapping naturally.'),
 (0xB099,0xB0A5,'PlayerTableFamilyPointers','data','Three two-entry pointer arrays for CHR, metasprites and state handlers; ACF7 input A=0/1 selects family.'),
 (0xB0A5,0xB114,'PlayerNormalChrTable','data','111 CHR bank bytes indexed by CD>>1; table contents identified, not every corresponding state behavior.'),
 (0xB114,0xB1F2,'PlayerNormalSpritePointers','data','111 little-endian metasprite pointers indexed by even CD.'),
 (0xB1F2,0xB2D0,'PlayerNormalHandlerPointers','data','111 little-endian handler pointers covering CD pairs 00/01 through DC/DD; many handlers remain unreviewed.'),
 (0xBB2B,0xBB4F,'AdvancePlayerDeathAnimation','code','Set D3 bit80; every exact 0F CF updates advance CD by2; after C2/C3 select CA/CB and reset CF.'),
 (0xBB4F,0xBB6E,'UpdatePlayerFallExit','code','Set D3 bit80; add4 to player Y; set CE bit80 if low-byte camera-relative Y >=F0.'),
 (0xBB6E,0xBB99,'UpdatePlayerHurtReaction','code','Set D3 bit80; call unreviewed BCEF; while D2>=30 request horizontal movement by2 using CD bit08, otherwise clear D3 bits30 and reset CD to facing.'),
 (0xBB99,0xBBAD,'FinishPlayerDeathDelay','code','Set D3 bit80; increment CF; exact CF=0F sets CE bit80 without resetting CF.'),
 (0xBDF3,0xBDF8,'PlayerAlternateChrTable','data','Five CHR bytes for alternate family; precise gameplay activation not assigned.'),
 (0xBDF8,0xBE02,'PlayerAlternateSpritePointers','data','Five little-endian metasprite pointers for alternate family.'),
 (0xBE02,0xBE0C,'PlayerAlternateHandlerPointers','data','Five little-endian handler pointers for alternate family.')
]:region(8,lo,hi,name,kind,desc)
region(14,0xD29F,0xD2F7,'InitializeSceneBankedServices','code','Map scene bank and R7=08 for player initialization, then R7=07 for scene setup; preserve unresolved callee boundaries.')
region(14,0xDB02,0xDB4A,'ClassifyPlayerTerrainSample','code','Choose sample helper with DB bit04; priority bits40/80 return solid/empty; bit10 may invoke damage (9A+04) except active effect08; accumulate terrain bits0C into CE.')
region(14,0xDDD9,0xDE37,'ApplyPlayerDamage','code','Ignore while D2 or01A4 nonzero; subtract raw A from06B9. Borrow starts BA/BB death animation; equality zero takes hurt path. Preserve input carry as reaction direction.')
for lo,hi,name,kind,desc in [
 (0xF6ED,0xF737,'DrawMetaspriteNormal','code','Draw FF-terminated four-byte sprite records from B6/B7; relative Y from22, X from24/25, attribute OR2C; hide horizontally offscreen sprites and cap valid OAM count64.'),
 (0xF737,0xF78B,'DrawMetaspriteFlipped','code','As normal renderer, XOR attribute40 and mirror signed X offset using -(offset+8).'),
 (0xF78B,0xF7A1,'NormalizeYTo240LinePages','code','For input A high 00..0F and Y low, return A=remainder and Y=quotient of the 16-bit position divided by F0.'),
 (0xF7A1,0xF7B1,'YPageCorrectionTable','data','16 bytes 00,10,...F0 used by Y-coordinate normalization.'),
 (0xFAD3,0xFB1E,'LoadSceneIrqProfile','code','Select profile with FE6C[9A], copy latch/index pairs until F0, then NMI selector and IRQ source chosen by selector and pair count.'),
 (0xFDE0,0xFDE8,'PlayerHpCapacityByIndex','data','Eight raw capacities 40,50,60,70,80,90,A0,B0 indexed by D3&07 on restore; match 4..11 sixteen-unit cells.'),
 (0xFE6C,0xFE8C,'SceneIrqProfileIndex','data','32 selectors for six IRQ profiles.'),
 (0xFE8C,0xFE98,'SceneIrqProfilePointers','data','Six little-endian pointers to F0-terminated latch/index streams.'),
 (0xFE98,0xFEDE,'SceneIrqProfiles','data','Six streams; final F0 byte is a terminal latch followed by NMI selector, not an ordinary latch/index pair.')
]:region(15,lo,hi,name,kind,desc)

COMMENTS={
 (7,0xA53F):'03B9 is data-driven, not a universal player-code bank.',
 (7,0xA5F7):'Bit7 is metadata consumed here; R6 receives the low seven bits.',
 (7,0xAAD3):'Signed branch means 81..FF do not multiply as ordinary unsigned inputs.',
 (7,0xB027):'Only exact 06 wraps. Normal callers must keep A1 in the expected range.',
 (7,0xB067):'Displayed HP rises one raw unit per invocation; this routine is only one HUD phase.',
 (8,0xAB19):'Bit7 is cleared then reasserted by active terminal/hurt state handlers; not a permanent global game-over flag.',
 (8,0xAB2C):'A is zero here. LSR CE; ROL A retains only old CE bit0.',
 (8,0xAB31):'A=old CE&1 selects the normal or alternate state-table family.',
 (8,0xAD24):'Even CD indexes little-endian pointer pairs; bit0 is rendering direction.',
 (8,0xBB42):'Five states BA,BC,BE,C0,C2 each last 15 updates; CA then waits 15 more.',
 (8,0xBB64):'Comparison uses low-byte subtraction only, not a full 16-bit distance.',
 (14,0xDDE9):'BCS includes exact zero: death branch requires unsigned borrow (damage > current raw HP).',
 (14,0xDE26):'Restore caller carry before encoding reaction direction in D3 bit10.',
 (15,0xF701):'CMP #FF cleared carry for each non-terminator record, supplying the implicit clear for ADC.',
 (15,0xF761):'Eight-pixel sprite width is part of horizontal mirroring.',
}
R7_AT_CALL={0xD2B1:8,0xD2CD:7,0xD2D6:7}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();rom,_=verified_rom(a.rom);prg=rom[16:0x20010]
    ranges=[];ins=[];func=[];evidence=[];edges=[];access=[]
    for i,(bank,base,lo,hi,name,kind,desc) in enumerate(REGIONS,1):
        rid=f'C{i:02d}';m=MPU();m.memory[base:base+8192]=prg[bank*8192:(bank+1)*8192];d=Disassembler(m)
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
    all_ranges=[r for r in read('analysis/reviewed_ranges.csv') if not r['id'].startswith('C')]+ranges
    all_ins=[r for r in read('analysis/reviewed_instructions.csv') if not r['region_id'].startswith('C')]+ins
    all_ranges.sort(key=lambda r:int(r['prg_offset'],16));all_ins.sort(key=lambda r:int(r['prg_offset'],16))
    covered=set();code=set();data=set()
    for r in all_ranges:
        lo=int(r['prg_offset'],16);span=set(range(lo,lo+int(r['size'])));assert not covered&span,r;covered|=span;(code if r['classification']=='code' else data).update(span)
    write_csv(ROOT/'analysis/reviewed_ranges.csv',all_ranges);write_csv(ROOT/'analysis/reviewed_instructions.csv',all_ins)
    for rel,new in [('analysis/functions.csv',func),('analysis/evidence.csv',evidence)]:write_csv(ROOT/rel,[r for r in read(rel) if not r['id'].startswith('C')]+new)
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
    configs=[];pointers=[]
    for i in range(32):
        bank=byte(7,0xB262+i)
        row={'scene_index':f'0x{i:02X}','bank8000':f'{bank:02X}','initial_camera_x':f'0x{byte(7,0xB1E2+i)*256:04X}','initial_camera_y':f'0x{byte(7,0xB202+i)*240:04X}','player_x_offset':f'0x{byte(7,0xB222+i):02X}','player_y_offset_before_low_decrement':f'0x{byte(7,0xB242+i):02X}','DB_flags':f'0x{byte(7,0xB3E2+i):02X}','horizontal_bound_page':byte(7,0xB402+i),'vertical_bound_pixels':byte(7,0xB422+i)*240,'palette_cycle':f'0x{byte(7,0xB3C2+i):02X}','irq_profile':byte(15,0xFE6C+i),'stage_name':'UNRESOLVED'}
        for field,table in [('B9',0xB282),('BB',0xB2C2),('BF',0xB302),('BD',0xB342),('C1',0xB382),('palette',0xB442)]:
            target=word(7,table+2*i);tb=bank if 0x8000<=target<0xA000 else 7 if 0xA000<=target<0xC000 else 14 if target<0xE000 else 15
            base=0x8000 if target<0xA000 else 0xA000 if target<0xC000 else 0xC000 if target<0xE000 else 0xE000
            row[field+'_pointer']=f'{tb:02X}:{target:04X}'
            target_loc=loc(tb,base,target)
            if base==0x8000:target_loc['mapping_condition']=f'MMC3 PRG mode 0; R6={tb:02X} at 8000'
            pointers.append({'scene_index':f'0x{i:02X}','field':field,**{f'source_{k}':v for k,v in loc(7,0xA000,table+2*i).items()},**{f'target_{k}':v for k,v in target_loc.items()},'mapping_condition':f'at load time: mode0; R6={bank:02X}; R7=07','target_semantics':'27-byte palette/CHR profile' if field=='palette' else 'downstream structure incompletely reviewed'})
        configs.append(row)
    write_csv(ROOT/'analysis/scene_configurations.csv',configs);write_csv(ROOT/'analysis/scene_configuration_pointers.csv',pointers)
    states=[]
    for family,chrtable,sprtable,handtable,count in [(0,0xB0A5,0xB114,0xB1F2,111),(1,0xBDF3,0xBDF8,0xBE02,5)]:
        for i in range(count):
            handler=word(8,handtable+2*i);name=next((r['symbol'] for r in all_ranges if r['bank']=='08' and r['classification']=='code' and int(r['cpu'],16)<=handler<int(r['end_cpu_exclusive'],16)),'UNREVIEWED')
            states.append({'family':family,'CD_even':f'0x{2*i:02X}','CD_odd':f'0x{2*i+1:02X}','CHR_R2':f'0x{byte(8,chrtable+i):02X}','sprite_pointer':f'0x{word(8,sprtable+2*i):04X}','handler_bank':'08','handler_cpu':f'0x{handler:04X}','handler_prg_offset':f'0x{8*8192+handler-0xA000:06X}','handler_file_offset':f'0x{16+8*8192+handler-0xA000:06X}','handler_review':name,'handler_pointer_source':f'08:{handtable+2*i:04X}'})
    write_csv(ROOT/'analysis/player_state_dispatch.csv',states)
    indirect=[]
    for r in states:
        source=int(r['handler_pointer_source'].split(':')[1],16)
        indirect.append({'group':'PlayerStateFamily'+str(r['family']),'dispatch_bank':'08','dispatch_cpu':'0xAD36','index':int(r['CD_even'],16)//2,'selector':'CD&FE byte offset; A selects family','table_bank':'08','table_cpu':f'0x{source:04X}','target_bank':'08','target_cpu':r['handler_cpu'],'target_semantics':r['handler_review']})
    for group,bank,dispatch,lo,hi,count in [('SceneEven',7,0xA0EF,0xA0F2,0xA0F6,4),('SceneOdd',7,0xA10E,0xA111,0xA115,4),('SceneExtra',7,0xA12D,0xA130,0xA134,4),('AutoCameraStep',8,0xB067,0xB06B,0xB06F,4),('HudMaintenance',7,0xB03B,0xB03F,0xB045,6)]:
        for i in range(count):
            target=byte(bank,lo+i)|byte(bank,hi+i)<<8;tb=15 if target>=0xE000 else 14 if target>=0xC000 else bank
            indirect.append({'group':group,'dispatch_bank':f'{bank:02X}','dispatch_cpu':f'0x{dispatch:04X}','index':i,'selector':'A1 after increment/wrap' if group=='HudMaintenance' else '(DB>>1)&3 with entry-specific gates','table_bank':f'{bank:02X}','table_cpu':f'0x{lo+i:04X} + high at 0x{hi+i:04X}','target_bank':f'{tb:02X}','target_cpu':f'0x{target:04X}','target_semantics':'see reviewed ranges; otherwise UNREVIEWED'})
    write_csv(ROOT/'analysis/indirect_dispatch_tables.csv',indirect)
    cov=json.loads((ROOT/'analysis/coverage.json').read_text());cov.update({'reviewed_code_bytes':len(code),'reviewed_data_bytes':len(data),'reviewed_code_plus_data_bytes':len(covered),'reviewed_prg_fraction':len(covered)/131072,'reviewed_code_range_count':sum(r['classification']=='code' for r in all_ranges),'reviewed_data_range_count':sum(r['classification']=='data' for r in all_ranges),'stage02A_added_bytes':sum(int(r['size']) for r in ranges)})
    write_json(ROOT/'analysis/coverage.json',cov)
    result={'new_ranges':len(ranges),'new_code_ranges':sum(r['classification']=='code' for r in ranges),'new_data_ranges':sum(r['classification']=='data' for r in ranges),'new_instructions':len(ins),'new_bytes':sum(int(r['size']) for r in ranges),'scene_configurations':32,'scene_pointers':len(pointers),'player_state_pairs':len(states),'unresolved_targets_from_new_code':[r for r in edges if r['to_bank']=='UNRESOLVED']}
    write_json(ROOT/'analysis/stage02A_static_summary.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
