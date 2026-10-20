#!/usr/bin/env python3
"""Original-byte magic probes; no ROM patches or callee stubs.
Dispatch/presentation/selection-prefix probes use explicit stopping boundaries.
Existing02B arithmetic suites are reused,not rerun. No full NES timing claim.
"""
import argparse,json
from baseline import ROOT,verified_rom,write_json,write_csv,hashes
from cpu_stage01b import setup,execute,subroutine_frame
from cpu_stage02a import word,putword
from cpu_stage02b import putnum,getnum
MENU=[5,0,8,11,9,3,1,6,4,10,2,7]
COSTS=[60,90,10,20,30,3,5,20,20,1,30,20]
HANDLERS=[0xB6BA,0xB6CD,0xBA3B,0xB869,0xBA75,0xB6DF,0xB7D4,0xB88E,0xB8B7,0xB830,0xB8F0,0xB90C]
AIM=[4,2,6,4,4,8,0,3,4,1,7,2,4,4,4,4]
OFFSETS=[(-20,-16),(-20,-24),(-16,-32),(-8,-36),(0,-40),(8,-36),(16,-32),(20,-24),(20,-16)]
VX=[8,8,-8,8,0,6,-6,8,0,6,-6,8,8,8,8,8]
VY=[0,0,0,0,8,6,6,0,-8,-6,-6,0,0,0,0,0]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();rom,_=verified_rom(a.rom);prg=rom[16:0x20010]
    groups=[];vectors=[];traces=[]
    def add(name,obs,rows=None,scope='original bytes to RTS; no substituted callees'):
        groups.append({'id':name,'status':'PASS','vector_count':len(obs),'observations':obs,'boundary_stubs':[],'scope':scope})
        vectors.extend({'group':name,'data':json.dumps(o,sort_keys=True)} for o in obs)
        if rows:traces.extend(dict(experiment=name,**r) for r in rows)
        print(name,len(obs),'PASS',flush=True)
    def run(bus,m,pc,trace=False,stops=None):
        m.pc=pc;subroutine_frame(bus,m);rows,calls=execute(bus,m,stops or {0x8000},trace=trace);assert not calls;return rows
    def base(bank=9,pc=0x8000,mp=999):
        bus,m=setup(prg,pc,r7=bank);putnum(bus,0xEA,mp,3);bus[0x4EF]=16;bus[0x6BD]=12;bus[0x6C0]=bus[0x6C1]=12
        putword(bus,0xCB,128);putword(bus,0xC9,128);bus[0xB8]=0xFF;m.x=3;return bus,m

    obs=[];saved=[]
    masks=sorted(set([0,0xFFF,0xFFFF,0xA55A,0x5AA5]+[1<<i for i in range(16)]+[0xFFFF^(1<<i) for i in range(16)]))
    for typ in range(0x50,0x68):
        idx=(typ-0x50)//2
        for before in masks:
            for first in (12,0,11):
                bus,m=base(8);putword(bus,0x6BE,before);bus[0x56C]=typ;bus[0x6C0]=first;bus[0x6C1]=7;m.y=1
                saved+=run(bus,m,0xA831,trace=typ in (0x50,0x67) and before==0 and first==12)
                assert word(bus,0x6BE)==before|1<<idx and bus[0x4E3]==idx and bus[0x6BD]==12
                assert (bus[0x6C0],bus[0x6C1])==((idx,7) if first==12 else (first,idx))
                obs.append({'type':typ,'mask_before':before,'mask_after':word(bus,0x6BE),'pending_first_before':first,'pending_after':[bus[0x6C0],bus[0x6C1]]})
    add('E_CPU01_UNLOCK_ALL_TYPES_AND_PENDING_SLOTS',obs,saved)

    obs=[];saved=[]
    for idx in range(12):
        for facing in (0,1):
            for pos in (0,4,5,255,256,65535):
                bus,m=base(8);putword(bus,0xCB,pos);putword(bus,0xC9,pos);bus[0xCD]=0x22|facing;bus[0xCE]=0xFF;bus[0xCF]=0xAA;bus[0x56C]=0x50+2*idx;bus[0x580]=0xA0;m.y=1
                saved+=run(bus,m,0xA7DB,trace=idx==11 and pos==0)
                assert bus[0xD0]==1 and bus[0xCD]==0xCC+facing and bus[0xCF]==0 and bus[0xCE]==0xFE
                assert (bus[0],bus[1],bus[0x580],bus[0x6BD])==(0x2D,0,0xA0,12)
                assert (bus[0x51C]|bus[0x530]<<8)==(pos+(-5 if facing else 5))&65535
                assert (bus[0x4F4]|bus[0x508]<<8)==(pos-0x26)&65535
                obs.append({'effect':idx,'facing':facing,'position':pos,'HP_and_MP_untouched':getnum(bus,0xEA,3)==999})
    add('E_CPU02_ACQUISITION_ENTRY_COORDINATES',obs,saved)

    obs=[];saved=[];states=[0xCC,0xCE,0xD0,0xD0,0xD0,0xCE,0xCC,0xCC,0xCC,0xCC,0xCC,0xCC,0]
    for facing in (0,1):
        bus,m=base(8);bus[0xD0]=1;bus[0x580]=0xA0;bus[0xCD]=0xCC|facing
        for tick in range(1,97):
            saved+=run(bus,m,0xBBAD,trace=tick in (1,8,95,96),stops={0x8000,0xBD56})
            assert bus[0xCD]==states[tick//8]|facing and bus[0xD3]&128
            assert bus[0xCF]==(0 if tick==96 else tick) and bus[0x580]==(0 if tick==96 else 0x80)
            assert m.pc==(0xBD56 if tick==96 else 0x8000)
            obs.append({'facing':facing,'handler_update':tick,'state':bus[0xCD],'presentation_reached':tick==96})
    add('E_CPU03_ACQUISITION_ANIMATION_TO_PRESENTATION',obs,saved,'96 actual handler calls; stop before08:BD56 presentation/fade')

    obs=[];saved=[]
    for scene in range(32):
        bus,m=base(8);bus[0x9A]=scene;route=bus[0xBDBB+scene]
        saved+=run(bus,m,0xBDAA,trace=scene in (0,2,15,31),stops={0xC77F,0xC79D})
        assert m.pc==(0xC79D if route==255 else 0xC77F) and bus[0x9A]==(scene if route==255 else route)
        obs.append({'scene':scene,'route':route,'tail':f'{m.pc:04X}','downstream_executed':False})
    for effect in range(12):
        bus,m=base(8);bus[0x4E3]=effect;pointer=word(bus,0xBDDB+2*effect)
        saved+=run(bus,m,0xBD70,trace=effect in (0,11),stops={0xC782});assert bus.regs[6]==3 and bus.regs[7]==8 and word(bus,0x3A)==pointer
        obs.append({'effect':effect,'text_pointer':f'03:{pointer:04X}','text_renderer_executed':False})
    add('E_CPU04_PRESENTATION_BANK_AND_SCENE_ROUTES',obs,saved,'entryBD70 orBDAA; stop before text/scene service; full presentation not run')

    obs=[];saved=[]
    for bits in masks:
        for cell,idx in enumerate(MENU):
            bus,m=base(7);putword(bus,0x6BE,bits);m.x=cell
            saved+=run(bus,m,0xAEA0,trace=bits==0x800 and cell in (0,3,11))
            assert bool(m.p&1)==bool(bits&(1<<idx)) and word(bus,0x6BE)==bits
            obs.append({'owned_bits':bits,'cell':cell,'effect':idx,'carry':m.p&1})
    for idx in (*range(13),255):
        bus,m=base(7);bus[0x6BD]=idx;run(bus,m,0xAEB6);expected=MENU.index(idx) if idx<12 else 0
        assert bus[0x2C]==expected;obs.append({'reverse_effect':idx,'cell':expected})
    add('E_CPU05_MENU_OWNERSHIP_AND_REVERSE_MAPPING',obs,saved)

    obs=[];saved=[]
    for cell in range(12):
        for pressed in range(256):
            bus,m=base(7);bus[0x2C]=cell;bus[0x1F]=pressed;bus[1]=0x55;expected=cell
            if pressed&1:expected=cell+1 if cell%4<3 else cell
            elif pressed&2:expected=cell-1 if cell%4 else cell
            elif pressed&4:expected=cell+4 if cell<8 else cell
            elif pressed&8:expected=cell-4 if cell>=4 else cell
            saved+=run(bus,m,0xACBD,trace=cell==3 and pressed in (1,3,9,15))
            assert bus[0x2C]==expected and bus[0x1F]==pressed and bus[1]==(0x39 if expected!=cell else 0x55)
            obs.append({'cell':cell,'pressed':pressed,'cell_after':expected})
    add('E_CPU06_CURSOR_ALL_INPUTS_AND_EDGE_PRIORITY',obs,saved)

    obs=[]
    for state in range(256):
        for pressed in (0,0x40):
            for bypass in (0,1):
                bus,m=base(7);bus[0xD3]=state;bus[0x1F]=pressed;bus[0x1A5]=bypass;bus[0x6BB]=0x5A
                run(bus,m,0xAD03);expected=(state&0xF0)|((state+1)&7) if pressed and bypass else state
                assert bus[0xD3]==expected and bus[0x6BB]==0x5A
                obs.append({'D3':state,'pressed_B':bool(pressed),'bypass':bypass,'D3_after':expected})
    add('E_CPU07_MENU_LEVEL_CYCLE_GUARD',obs)

    obs=[];saved=[]
    for cell,idx in enumerate(MENU):
        for owned in (False,True):
            bus,m=base(7);bus[0x2C]=cell;putword(bus,0x6BE,(1<<idx) if owned else 0)
            saved+=run(bus,m,0xAD65,trace=cell in (0,11),stops={0x8000,0xAD81})
            assert bus[0x6BD]==(idx if owned else 12) and m.pc==(0xAD81 if owned else 0x8000)
            assert bus[0x2C]==cell
            obs.append({'cell':cell,'owned':owned,'selected':bus[0x6BD],'selection_animation_executed':False})
    add('E_CPU08_SELECTION_COMMIT_PREFIX',obs,saved,'locked selection returns; unlocked stops at07:AD81 before animation')

    obs=[];saved=[]
    for idx in range(2,12):
        cost=COSTS[idx]
        for mp in (0,cost-1,cost,cost+1):
            for pressed in (0,0x20):
                for state in (0,0x80):
                    for bypass in (0,1):
                        bus,m=base(8,mp=mp);m.y=1;bus[0x56C]=0x50+2*idx;run(bus,m,0xA831)
                        bus.regs[7]=7;bus[0x2C]=MENU.index(idx);run(bus,m,0xAD65,stops={0xAD81});run(bus,m,0xAE3A)
                        bus.regs[7]=9;bus[0x1F]=pressed;bus[0xD3]=state;bus[0x1A5]=bypass;bus[0xD9]=1
                        rows=run(bus,m,0xBE90,trace=mp==cost and pressed and state==0 and bypass==0);saved+=rows
                        success=bool(pressed) and (bool(bypass) or state==0 and mp>=cost) and not(idx==2 and state&128)
                        expected=mp-cost if success and not bypass else mp
                        assert getnum(bus,0xEA,3)==expected,(idx,mp,pressed,state,bypass)
                        assert bus[0x6BD]==idx and m.sp==0xFF
                        if idx==2:assert bool(bus[0xCE]&1)==success
                        if idx==3:assert bus[0x56B]==(0x8C if success else 0x76)
                        if idx==4:assert list(bus.ram[0x57C:0x57F])==([0x84]*3 if success else [0]*3)
                        if idx in (5,6):assert bus[0x57E]==((0x80 if idx==5 else 0x90) if success else 0)
                        if idx==7:assert bus[0x593]==bus[0x3D6]==int(success) and bus[0x3DC]==int(success)
                        if idx==8:assert (bus[0x593],bus[0x5A7])==((0xEF,4) if success else (0,0))
                        if idx==9:assert (bus[0x593],bus[0xB8])==((0xF0,0xDF) if success else (0,0xFF))
                        if idx==10:assert bus[0x56B]==(0x8A if success else 0x84)
                        if idx==11:assert bus[0x56B]==(0x88 if success else 0x86) and bus[0x593]==(0xC9 if success else 0)
                        obs.append({'effect':idx,'MP':mp,'pressed':pressed,'D3':state,'bypass':bypass,'success':success,'MP_after':expected})
    add('E_CPU09_UNLOCK_SELECT_INITIALIZE_AND_FULL_FIRST_FRAME',obs,saved,'actual unlock,selection commit prefix,initialization,and full object frame; menu icon tween skipped explicitly')

    obs=[];saved=[]
    for idx in (5,6):
        for occupied in range(8):
            for facing in (0,1):
                for direction in range(16):
                    for mp in (COSTS[idx]-1,COSTS[idx]):
                        bus,m=base(mp=mp);bus[0x1F]=0x20;bus[0x20]=direction;bus[0xCD]=facing;bus[0x593]=bus[0x5A7]=4
                        for j in range(3):bus[0x57C+j]=0x80 if occupied&(1<<j) else 0
                        free=next((j for j in (2,1,0) if not occupied&(1<<j)),None);success=free is not None and mp>=COSTS[idx]
                        saved+=run(bus,m,HANDLERS[idx],trace=occupied in (0,7) and direction==5 and mp==COSTS[idx])
                        assert getnum(bus,0xEA,3)==(mp-COSTS[idx] if success else mp) and m.x==3
                        if success:
                            d=direction or (2 if facing else 1)
                            assert bus[0x540+free]==((VX[d] if idx==5 else -8 if facing else 8)&255)
                            assert bus[0x554+free]==((VY[d] if idx==5 else 0)&255)
                            assert bus[0x568+free]==(0x10 if idx==5 else facing)
                            assert bus[0x57C+free]==(0x80 if idx==5 else 0x90)
                            assert bus[0x4F0+free]==(bus[0x4F3]-(8 if idx==6 else 0))&255
                        obs.append({'effect':idx,'occupied_mask':occupied,'facing':facing,'direction':direction,'MP':mp,'spawned_slot':free if success else None})
    add('E_CPU10_PROJECTILE_POOL_COST_AND_DIRECTION',obs,saved)

    obs=[]
    for current in range(9):
        for old_target in range(9):
            for facing in (0,1):
                for direction in range(16):
                    bus,m=base();putword(bus,0xCB,0x100);putword(bus,0xC9,0x100);bus[0x593]=current;bus[0x5A7]=old_target;bus[0xCD]=facing;bus[0x20]=direction;bus[0x56B]=0x7A
                    run(bus,m,0xB747);position=current+(1 if current<old_target else -1 if current>old_target else 0);dx,dy=OFFSETS[position]
                    assert bus[0x593]==position and bus[0x5A7]==AIM[direction or (2 if facing else 1)] and bus[0x56B]==0x7A|facing
                    assert bus[0x51B]|bus[0x52F]<<8==0x100+dx
                    assert bus[0x4F3]|bus[0x507]<<8==0x100+dy
                    obs.append({'current':current,'previous_target':old_target,'facing':facing,'direction':direction,'next_position':position,'next_target':bus[0x5A7]})
    add('E_CPU11_AIM_INTERPOLATION_AND_NEXT_TARGET',obs)

    obs=[];saved=[]
    for idx,total in ((9,241),(8,1008)):
        bus,m=base(mp=100);bus[0x1F]=0x20
        for tick in range(1,total+1):
            saved+=run(bus,m,HANDLERS[idx],trace=tick in (1,2,240,total))
            assert getnum(bus,0xEA,3)==100-COSTS[idx]
            if idx==9:
                expected=240 if tick==1 else 241-tick;assert bus[0x593]==expected
                if tick==total:assert bus[0xB8]==0xFF
            else:
                remaining=1008-tick;low=bus[0x593];high=bus[0x5A7]
                assert (high-int(low!=0))*256+low==remaining
                if tick==total:assert bus[0x158]==bus[0xFFB5]
            obs.append({'effect':idx,'handler_update':tick,'timer_low':bus[0x593],'timer_high':bus[0x5A7] if idx==8 else 0,'held_new_Select_fixture':True})
    add('E_CPU12_ATTRIBUTE_AND_TERRAIN_TIMER_LIFETIMES',obs,saved)

    obs=[];saved=[]
    for value in range(256):
        bus,m=base();initial=[(value+j*29)&255 for j in range(8)];bus.ram[0x473:0x47B]=bytes(initial);bus[0x47B]=0x55
        run(bus,m,0xD7E7);expected=[v if v&0x20 else (v&0xAF)|0x10 for v in initial]
        assert list(bus.ram[0x473:0x47B])==expected and bus[0x47B]==0x55 and bus[0x3DC]==1
        obs.append({'seed':value,'enemy_flags_before':initial,'enemy_flags_after':expected})
    bus,m=base(mp=100);bus[0x1F]=0x20
    for tick in range(1,61):
        saved+=run(bus,m,0xB88E,trace=tick in (1,59,60));assert bus[0x593]==bus[0x3D6]==tick%60 and getnum(bus,0xEA,3)==80
        obs.append({'quake_handler_update':tick,'phase':bus[0x593]})
    add('E_CPU13_QUAKE_FLAGS_AND_SCROLL_PHASE',obs,saved)

    obs=[];saved=[]
    for initial in (0,9,10,20,40,50):
        bus,m=base(mp=initial);bus[0x1F]=0x20;expected_mp=initial;active=False;timer=0
        for tick in range(1,122):
            bus[0x1F]=0x20 if tick==1 else 0
            if tick==1 or active and timer==1:
                if expected_mp>=10:expected_mp-=10;active=True;timer=30
                else:active=False;timer=0
            elif active:timer-=1
            saved+=run(bus,m,0xBA3B,trace=initial==50 and tick in (1,30,31,121))
            assert getnum(bus,0xEA,3)==expected_mp and bool(bus[0xCE]&1)==active
            obs.append({'MP_initial':initial,'handler_update':tick,'MP_after':expected_mp,'flight':active,'timer':bus[0x593]})
    for state in (0,0x80):
        bus,m=base(mp=100);bus[0xCE]=1;bus[0x593]=17;bus[0xCD]=0x45;bus[0xD3]=state;bus[0x1F]=0x20
        run(bus,m,0xBA3B);assert bus[0xCE]==(1 if state else 0) and getnum(bus,0xEA,3)==100
        assert bus[0xCD]==(0x45 if state else 1);obs.append({'toggle_D3':state,'flight_after':bus[0xCE],'CD_after':bus[0xCD]})
    add('E_CPU14_FLIGHT_PERIODIC_COST_AND_TOGGLE',obs,saved)

    obs=[];saved=[]
    for counter in (0,1,10,127,128,255):
        bus,m=base();bus[0x5A7]=counter;bus[0x56B]=0x8A;run(bus,m,0xB964)
        assert bus[0x56B]==(0x84 if counter&128 else 0x8A)
        if counter<128:assert bus[0x51B]==bus[0x4F3]==128
        obs.append({'shield_budget':counter,'type_after':bus[0x56B]})
    for x,y in [(128,128),(0,0),(255,239),(256,128),(128,240),(65535,128),(128,65535)]:
        bus,m=base();bus[0x51B]=x&255;bus[0x52F]=x>>8;bus[0x4F3]=y&255;bus[0x507]=y>>8;bus[0x593]=201;bus[0x56B]=0x88
        run(bus,m,0xB930);inside=0<=x<256 and 0<=y<240;assert bus[0x593]==(200 if inside else 0) and bus[0x56B]==(0x88 if inside else 0x86)
        obs.append({'decoy_x':x,'decoy_y':y,'inside':inside})
    bus,m=base();bus[0x51B]=bus[0x4F3]=128;bus[0x593]=201;bus[0x56B]=0x88
    for tick in range(1,202):
        saved+=run(bus,m,0xB930,trace=tick in (1,200,201));assert bus[0x593]==201-tick and bus[0x56B]==(0x86 if tick==201 else 0x88)
        obs.append({'decoy_handler_update':tick,'remaining':bus[0x593]})
    add('E_CPU15_SHIELD_AND_DECOY_CONTINUATIONS',obs,saved)

    obs=[];saved=[]
    bus,m=base();bus[0x1F]=0x20;run(bus,m,0xB869);assert (bus[0x56B],bus[0x557],bus[0x593],bus[0x5A7])==(0x8C,0xF8,5,0)
    bus[0x4F3]=47;saved+=run(bus,m,0xB972,trace=True);assert (bus[0x56B],bus[0x557])==(0x8E,0)
    for tick in range(1,6):
        saved+=run(bus,m,0xB991,trace=tick==5);assert bus[0x593]==5-tick
    assert list(bus.ram[0x568:0x56B])==[0x28,0x18,0x29] and list(bus.ram[0x57C:0x57F])==[0xD4]*3
    assert list(bus.ram[0x590:0x593])==[8,0x15,8] and bus[0x56B]==0x90
    for tick in range(1,257):
        saved+=run(bus,m,0xB9E1,trace=tick in (1,255,256));assert bus[0x5A7]==(256-tick)&255
        if tick==256:assert bus[0x56B]==0x94 and bus[0x557]==8
        obs.append({'lightning_hold_update':tick,'timer':bus[0x5A7],'type':bus[0x56B]})
    bus[0x4F3]=128;saved+=run(bus,m,0xBA19,trace=True);assert bus[0x56B]==0x76 and bus[0x557]==0
    obs.append({'spawned_types':[0x28,0x18,0x29],'return_type':0x76,'bolt_handlers_executed':False})
    add('E_CPU16_OVERHEAD_LIGHTNING_PHASES',obs,saved,'selected-effect control handlers; actual bolt movement/collision not executed')

    obs=[];saved=[]
    bus,m=base();bus[0x1F]=0x20;run(bus,m,0xBA75);assert bus[0x593]==1
    for tick in range(1,31):
        for slot in range(3):
            m.x=slot
            for j in range(10):bus[0x469+j]=0xC0;bus[0x473+j]=0;bus[0x441+j]=0xA5;bus[0x47D+j]=0xFF
            saved+=run(bus,m,0xBAC7,trace=slot==0 and tick in (1,8,24,30))
            queued=slot==0 and tick in (8,16,24)
            assert list(bus.ram[0x441:0x44B])==([6]*10 if queued else [0xA5]*10)
            assert bus[0x57C+slot]==(0 if tick==30 else 0x84)
            obs.append({'column':slot,'handler_update':tick,'damage_request_queued':queued,'active':bus[0x57C+slot]!=0})
    assert bus[0x593]==0
    add('E_CPU17_LIGHTNING_COLUMNS_AND_DAMAGE_REQUEST_TIMES',obs,saved)

    obs=[]
    for flags in range(256):
        for other in (0,1,2,3,0x20,0x21,0x80,255):
            bus,m=base();m.a=6
            for j in range(10):bus[0x469+j]=flags;bus[0x473+j]=other;bus[0x441+j]=0xA5;bus[0x47D+j]=0xFF
            run(bus,m,0xBD1B);accept=flags>=0xC0 and other&3==0
            for j in range(10):
                assert bus[0x441+j]==(6 if accept else 0xA5)
                assert bus[0x469+j]==(flags|0x20 if accept else flags) and bus[0x47D+j]==(0xF8 if accept else 0xFF)
            obs.append({'flags':flags,'secondary_flags':other,'queued_for_all10':accept})
    add('E_CPU18_ENEMY_DAMAGE_REQUEST_FILTER',obs)
    result={'stage':'02C','model':'py65 original CPU bytes with MMC3/PPU test doubles; no full NES timing','rom_sha256':hashes(rom)['sha256'],'groups':len(groups),'passed_groups':len(groups),'vectors':len(vectors),'trace_rows':len(traces),'results':groups}
    write_json(ROOT/'analysis/cpu_stage02C.json',result);write_csv(ROOT/'analysis/cpu_stage02C_vectors.csv',vectors);write_csv(ROOT/'analysis/cpu_stage02C_trace.csv',traces)
    print(json.dumps({k:v for k,v in result.items() if k!='results'},indent=2))
if __name__=='__main__':main()
