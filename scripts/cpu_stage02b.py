#!/usr/bin/env python3
"""Execute original bytes for progression, collection and selected healing effects.

Assertions use decimal arithmetic and independent boundary expectations. No ROM
patches or substituted callees. Selected entry/exit probes explicitly stop before
unreviewed handlers; full healing and pickup integration runs have no stubs.
This CPU/MMC3 test double is not a timed NES emulator.
"""
import argparse,json
from baseline import ROOT,verified_rom,write_csv,write_json,hashes
from cpu_stage01b import setup,execute,subroutine_frame
from cpu_stage02a import word,putword

def digits(value,n,bias=0x60):return bytes(bias+int(x) for x in f'{value:0{n}d}'[::-1])
def putnum(bus,a,value,n,bias=0x60):bus.ram[a:a+n]=digits(value,n,bias)
def getnum(bus,a,n,bias=0x60):
    ds=[bus[a+i]-bias for i in range(n)];assert all(0<=d<=9 for d in ds),ds
    return sum(d*10**i for i,d in enumerate(ds))
def threshold(level):return (level+1)*1000 if level<7 else 9999
def mpcap(level):return (level+1)*100 if level<7 else 999
def hpcap(level):return 0x40+16*level

def main():
    ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();rom,_=verified_rom(a.rom);prg=rom[16:0x20010]
    groups=[];vectors=[];traces=[]
    def add(name,obs,rows=None,scope='original bytes through RTS; no callee stubs'):
        groups.append({'id':name,'status':'PASS','vector_count':len(obs),'observations':obs,'boundary_stubs':[],'scope':scope})
        vectors.extend({'group':name,'data':json.dumps(x,sort_keys=True)} for x in obs)
        if rows:traces.extend(dict(experiment=name,**x) for x in rows)
        print(f'{name}: {len(obs)} vectors PASS',flush=True)
    def invoke(bus,m,pc,trace=False,stops=None):
        m.pc=pc;subroutine_frame(bus,m)
        rows,calls=execute(bus,m,stops or {0x8000},trace=trace);assert not calls
        return rows
    def progression(bus,level,exp=0,mp=77,hp=31):
        bus[0xD3]=level;bus[0x4EF]=16;bus[0x6B9]=hp;bus[0x6BA]=11;bus[0x6BB]=hpcap(level)
        putnum(bus,0xEA,mp,3);putnum(bus,0xED,exp,4);putnum(bus,0xF1,threshold(level),4);putnum(bus,0xF5,mpcap(level),3)
    def pickup(bus,index=1,typ=0x40,velocity=0,active=0x80,x=128,y=128):
        bus[0x56B+index]=typ;bus[0x57F+index]=active;bus[0x557+index]=velocity
        bus[0x51B+index]=x;bus[0x4F3+index]=y

    obs=[];saved=[]
    for entry,amount in [(0xA6AB,10),(0xA6B4,30),(0xA6BD,50)]:
        for initial in range(10000):
            level=min(initial//1000,7);bus,m=setup(prg,entry,r7=8);progression(bus,level,initial);m.y=1;bus[0x580]=0x80;bus[1]=0x55
            trace=initial in (989,990,999,6950,6999,9949,9950,9999)
            rows,_=execute(bus,m,{0x8000},trace=trace);saved+=rows
            overflow=initial+amount>9999;result=min(initial+amount,9999)
            advanced=not overflow and level<7 and result>=threshold(level);newlevel=level+int(advanced)
            assert getnum(bus,0xED,4)==result and bus[0xD3]==newlevel,(entry,initial)
            assert getnum(bus,0xF1,4)==threshold(newlevel) and getnum(bus,0xF5,3)==mpcap(newlevel)
            assert bus[0x6BB]==hpcap(newlevel) and (bus[0x6B9],bus[0x6BA],getnum(bus,0xEA,3))==(31,11,77)
            assert bus[0x580]==0 and bus[1]==(0x55 if overflow else 0xE4 if advanced else 0x2B)
            if advanced:assert bus[0x3D5]==0xB4 and bus[0x56B+15]==0x96 and bus[0x57F+15]==0x80
            obs.append({'EXP':initial,'add':amount,'result':result,'level_after':newlevel,'overflow_early_return':overflow})
    add('D_CPU01_EXP_ALL_DECIMAL_VALUES',obs,saved)

    obs=[];saved=[]
    for level in range(7):
        for initial in (threshold(level)-11,threshold(level)-10,threshold(level)-1,threshold(level),9000):
            bus,m=setup(prg,0xA6AB,r7=8);progression(bus,level,initial);m.y=1
            saved+=invoke(bus,m,0xA6AB,trace=initial==9000)
            advanced=initial+10>=threshold(level)
            assert bus[0xD3]==level+advanced and getnum(bus,0xED,4)==initial+10
            obs.append({'level_before':level,'EXP':initial,'level_after':bus[0xD3],'at_most_one_advance':True})
    for flags in (0x10,0x40,0x80):
        bus,m=setup(prg,0xA6AB,r7=8);progression(bus,0,990);bus[0xD3]=flags;m.y=1
        expected=bus[0xFDE0+flags+1];saved+=invoke(bus,m,0xA6AB,trace=True)
        assert bus[0xD3]==flags+1 and bus[0x6BB]==expected
        assert getnum(bus,0xF5,3)==200 and getnum(bus,0xF1,4)==2000
        obs.append({'out_of_contract_direct_entry_D3':flags,'HP_table_index':flags+1,'HP_capacity_byte':expected,'normal_gameplay_reachability':'NOT_ESTABLISHED'})
    add('D_CPU02_LEVEL_BOUNDARIES_AND_UNMASKED_INDEX',obs,saved)

    obs=[];saved=[]
    for level in range(8):
        cap=mpcap(level)
        for entry,amount in [(0xA73D,5),(0xA744,10)]:
            for initial in range(cap+1):
                bus,m=setup(prg,entry,r7=8);progression(bus,level,mp=initial);m.y=1;bus[0x580]=0x80
                rows,_=execute(bus,m,{0x8000},trace=level==7 and initial in (0,9,99,989,990,999));saved+=rows
                result=min(initial+amount,cap);assert getnum(bus,0xEA,3)==result and bus[0x580]==0 and bus[1]==0x2B
                obs.append({'level':level,'MP':initial,'add':amount,'result':result})
    add('D_CPU03_MP_PICKUP_VALID_DOMAINS',obs,saved)

    obs=[];saved=[]
    for initial in range(1000):
        for cost in (0,1,3,5,10,20,30,60,90,99):
            bus,m=setup(prg,0xBD46,r7=9);putnum(bus,0xEA,initial,3);m.a=((cost//10)<<4)|(cost%10)
            rows,_=execute(bus,m,{0x8000},trace=initial in (0,59,60,89,90,99,100,999) and cost in (60,90));saved+=rows
            success=initial>=cost;result=initial-cost if success else initial
            assert getnum(bus,0xEA,3)==result and bool(m.p&1)==(not success),(initial,cost)
            obs.append({'MP':initial,'cost_decimal':cost,'MP_after':result,'success':success})
    add('D_CPU04_MP_SPEND_BORROW_AND_ROLLBACK',obs,saved)

    obs=[];saved=[]
    for state in (0,7,0x20,0x7F,0x80,0xFF):
        for bypass in (0,1,0x80,0xFF):
            for initial in (0,59,60,999):
                bus,m=setup(prg,0xBD46,r7=9);putnum(bus,0xEA,initial,3);bus[0xD3]=state;bus[0x1A5]=bypass;m.a=0x60
                saved+=invoke(bus,m,0xBD46,trace=state==0x80 and initial==0)
                success=bool(bypass) or not(state&0x80) and initial>=60
                expected=initial-60 if success and not bypass else initial
                assert bool(m.p&1)==(not success) and getnum(bus,0xEA,3)==expected
                obs.append({'D3':state,'bypass':bypass,'MP':initial,'MP_after':expected,'success':success})
    add('D_CPU05_MP_GUARD_PRECEDENCE',obs,saved)

    obs=[];saved=[]
    for level in range(8):
        for hp in range(hpcap(level)+1):
            for amount in (0x10,0x20,0x40):
                entry=0xA78A if amount==0x10 else 0xBD98;bus,m=setup(prg,entry,r7=8 if amount==0x10 else 9);progression(bus,level,hp=hp);m.a=amount;m.y=1;bus[0x580]=0x80
                rows,_=execute(bus,m,{0x8000},trace=hp in (0,hpcap(level)) and level==7);saved+=rows
                expected=min(hp+amount,hpcap(level));assert bus[0x6B9]==expected and bus[0x6BA]==11
                if amount==0x10:assert bus[0x580]==0 and bus[1]==0xA1
                obs.append({'level':level,'HP_raw':hp,'heal_raw':amount,'HP_after':expected})
    bus,m=setup(prg,0xBD98,r7=9);bus[0x6B9]=0xF0;bus[0x6BB]=0xB0;m.a=0x40;invoke(bus,m,0xBD98);assert bus[0x6B9]==0x30
    obs.append({'out_of_domain_HP':0xF0,'heal':0x40,'wrapped_HP':0x30,'normal_gameplay_reachability':'NOT_ESTABLISHED'})
    add('D_CPU06_HP_HEALING_CLAMPS',obs,saved)

    obs=[];saved=[]
    for selected in range(13):
        bus,m=setup(prg,0xAE3A,r7=7);progression(bus,3);bus[0x6BD]=selected;bus[0xCE]=0xFF;putword(bus,0xCB,0x2345);putword(bus,0xC9,0x1234)
        bus.ram[0x57C:0x580]=bytes([0xFF]*4);encoded=bus[0xAE93+selected];tiles=[bus[0xFF2A+selected*4+i] for i in range(4)]
        saved+=invoke(bus,m,0xAE3A,trace=selected in (0,1,3,12))
        assert list(bus.ram[0x57C:0x57F])==[0,0,0] and bus[0xCE]==0xFE and bus[0xB8]==0xFF
        assert list(bus.ram[0x185:0x189])==tiles and bus[0xA0]==0x16
        assert bus[0x57F]==(0 if not encoded else 0x8C if encoded&1 else 0x88)
        if encoded:assert bus[0x56B]==encoded&0xFE and (bus[0x51B],bus[0x52F],bus[0x4F3],bus[0x507])==(0x45,0x23,0x34,0x12)
        obs.append({'selector':selected,'encoded_type':encoded,'flags':bus[0x57F],'icon_tiles':tiles})
    add('D_CPU07_SELECTED_SPELL_INITIALIZATION',obs,saved)

    obs=[];saved=[]
    for selected,cost,gain in [(0,60,0x20),(1,90,0x40)]:
        for mp in (0,cost-1,cost,cost+1,999):
            for hp in (0,1,0xA0,0xB0):
                for pressed in (0,0x20):
                    bus,m=setup(prg,0xAE3A,r7=7);progression(bus,7,mp=mp,hp=hp);bus[0x6BD]=selected;putword(bus,0xCB,128);putword(bus,0xC9,128)
                    invoke(bus,m,0xAE3A);bus.regs[7]=9;bus[0x1F]=pressed;bus[0xD9]=1
                    rows=invoke(bus,m,0xBE90,trace=hp==1 and mp in (cost-1,cost) and pressed!=0);saved+=rows
                    success=bool(pressed) and mp>=cost
                    assert getnum(bus,0xEA,3)==(mp-cost if success else mp)
                    assert bus[0x6B9]==(min(hp+gain,0xB0) if success else hp)
                    assert bus[0x57F]==0x88 and bus[0x2E]==20 and bus[0xD9]==2 and m.sp==0xFF
                    if rows:assert any(r['pc']=='0xF6ED' for r in rows) and any(r['pc']=='0xBD46' for r in rows)
                    obs.append({'selected':selected,'MP':mp,'HP':hp,'pressed':pressed,'MP_after':getnum(bus,0xEA,3),'HP_after':bus[0x6B9],'all_callees_executed':True})
    add('D_CPU08_FULL_SELECTED_HEALING_OBJECT_FRAME',obs,saved)

    obs=[];saved=[]
    for value in range(256):
        bus,m=setup(prg,0xA64D,r7=8);m.y=1;bus[0x56C]=value
        target=word(bus,0xA629+(value&0xFE)) if 0x40<=value<0x70 else 0x8000
        rows,_=execute(bus,m,{target},trace=value in (0x3F,0x40,0x6F,0x70));saved+=rows
        assert m.pc==target and m.sp==(0xFD if target!=0x8000 else 0xFF)
        obs.append({'type':value,'target':f'08:{target:04X}' if target!=0x8000 else 'RTS','target_body_executed':False})
    for phase in (*range(6),0x40,0x80,0xC0,0xFF):
        bus,m=setup(prg,0xA012,r7=8);bus[0xA1]=phase
        target=(bus[0xA028+phase]|bus[0xA02E+phase]<<8) if phase<6 else 0x8000
        execute(bus,m,{target},trace=False);assert m.pc==target
        obs.append({'phase':phase,'target':f'08:{target:04X}' if target!=0x8000 else 'RTS','target_body_executed':False})
    add('D_CPU09_PICKUP_AND_PHASE_DISPATCH_DOMAINS',obs,saved,'dispatch only; stop at selected handler without executing it')

    obs=[];saved=[]
    for axis in ('x','y'):
        for delta in range(-128,128):
            bus,m=setup(prg,0xA14F,r7=8);progression(bus,0,hp=1);bus[0x4EF]=1;pickup(bus);bus[0xCB]=(128+(delta if axis=='x' else 0))&255;bus[0xC9]=(128+(delta if axis=='y' else 0))&255
            invoke(bus,m,0xA14F);inside=(-13<=delta<=12) if axis=='x' else (-20<=delta<=26)
            assert (bus[0x580]==0)==inside and bus[0x6B9]==(17 if inside else 1),(axis,delta)
            obs.append({'axis':axis,'player_minus_object':delta,'collected':inside})
    for velocity in range(256):
        bus,m=setup(prg,0xA14F,r7=8);progression(bus,0,hp=1);bus[0x4EF]=1;pickup(bus,velocity=velocity);bus[0xCB]=bus[0xC9]=128
        saved+=invoke(bus,m,0xA14F,trace=velocity in (0x7F,0x80,0xFA,0xFB,0xFF));accepted=velocity<128 or velocity>=0xFB
        assert (bus[0x580]==0)==accepted;obs.append({'velocity':velocity,'collected':accepted})
    add('D_CPU10_FULL_PICKUP_RECTANGLE_AND_VELOCITY',obs,saved)

    obs=[];saved=[]
    for state in (0,7,0x10,0x20,0x40,0x80,0xA0,0xFF):
        for d8,d9 in ((0,0),(0,1),(1,0),(1,1)):
            bus,m=setup(prg,0xA14F,r7=8);progression(bus,0,hp=1);bus[0x4EF]=1;bus[0xD3]=state;bus[0x3D8]=d8;bus[0x3D9]=d9;pickup(bus);bus[0xCB]=bus[0xC9]=128
            saved+=invoke(bus,m,0xA14F,trace=state==0);blocked=bool(state&0xA0) or bool(d8 and d9)
            assert (bus[0x580]==0)==(not blocked) and m.sp==0xFF
            assert bus.regs[1]==(2 if d8 and not d9 else 0) and bus.regs[6:]==[4,8]
            obs.append({'D3':state,'03D8':d8,'03D9':d9,'collected':not blocked,'CHR_R1':bus.regs[1],'SP_after':m.sp})
    for active in (0,1,0x7F,0x80,0xFF):
        bus,m=setup(prg,0xA14F,r7=8);progression(bus,0,hp=1);bus[0x4EF]=1;pickup(bus,active=active);bus[0xCB]=bus[0xC9]=128
        invoke(bus,m,0xA14F);assert bus[0x6B9]==(17 if active&0x80 else 1)
        obs.append({'active_flags':active,'collected':bool(active&0x80)})
    bus,m=setup(prg,0xA14F,r7=8);progression(bus,0,990,20,1);bus[0x4EF]=4;bus[0xCB]=bus[0xC9]=128
    for i,typ in ((0,0x40),(1,0x40),(2,0x42),(3,0x46),(4,0x40)):pickup(bus,i,typ)
    saved+=invoke(bus,m,0xA14F,trace=True)
    assert (bus[0x6B9],getnum(bus,0xEA,3),getnum(bus,0xED,4),bus[0xD3])==(33,25,1000,1) and bus[0x57F]==0x80
    obs.append({'multi_pickup_order':'4,3,2,1; excludes0','HP':33,'MP':25,'EXP':1000,'level':1,'all_callees_executed':True})
    add('D_CPU11_PICKUP_GATES_STACK_AND_MULTIPLE_OBJECTS',obs,saved)

    obs=[];saved=[];score_thresholds=(10000,50000,100000,200000,500000,999999)
    for index,limit in enumerate(score_thresholds):
        for amount,packed in ((10,0x11),(100,0x12)):
            for initial in sorted(set([0,max(0,limit-amount-1),max(0,limit-amount),max(0,limit-1),limit,999900,999990,999999])):
                for attempts in (3,9,10):
                    bus,m=setup(prg,0xD8B5);putnum(bus,0x306,initial,6,0x20);bus[0x30F]=index*6;bus[0x30E]=attempts;bus[1]=0x55;m.a=packed
                    rows,_=execute(bus,m,{0x8000},trace=attempts==10 and initial==limit-amount);saved+=rows
                    overflow=initial+amount>999999;result=min(initial+amount,999999);award=not overflow and result>=limit
                    assert getnum(bus,0x306,6,0x20)==result and bus[0x30F]==index*6+6*award
                    assert bus[0x30E]==attempts+int(award and attempts!=10) and bus[1]==(0xDC if award and attempts!=10 else 0x55)
                    obs.append({'threshold_index':index,'score':initial,'add':amount,'result':result,'attempts_before':attempts,'attempts_after':bus[0x30E],'next_threshold_offset':bus[0x30F],'overflow_early_return':overflow})
    bus,m=setup(prg,0xA7A3,r7=8);putnum(bus,0x306,9900,6,0x20);bus[0x30E]=9;m.y=1;bus[0x580]=0x80
    saved+=invoke(bus,m,0xA7A3,trace=True);assert getnum(bus,0x306,6,0x20)==10000 and bus[0x30E]==10 and bus[0x580]==0
    obs.append({'full_score_pickup':True,'before':9900,'after':10000,'attempts_after':10})
    add('D_CPU12_SCORE_THRESHOLDS_CAP_AND_OVERFLOW',obs,saved)

    obs=[];saved=[]
    for attempts in (0,1,3,9,10,11,255):
        bus,m=setup(prg,0xA699,r7=8);bus[0x30E]=attempts;bus[1]=0x55;m.y=1;bus[0x580]=0x80
        saved+=invoke(bus,m,0xA699,trace=True);expected=attempts if attempts==10 else (attempts+1)&255
        assert bus[0x30E]==expected and bus[0x580]==0 and bus[1]==(0x55 if attempts==10 else 0xDC)
        obs.append({'attempts_before':attempts,'attempts_after':expected,'normal_domain':1<=attempts<=10})
    for level in range(8):
        for attempts in range(1,11):
            for flags in (0,0xB0):
                bus,m=setup(prg,0xF681);bus[0xD3]=level|flags;bus[0x30E]=attempts;invoke(bus,m,0xF681)
                assert bus[0x167]==0x60+level and bus[0x16C]==0x5F+attempts
                obs.append({'level':level,'high_flags':flags,'internal_attempts':attempts,'HUD_digit':attempts-1})
    add('D_CPU13_EXTRA_ATTEMPT_AND_HUD',obs,saved)

    obs=[];saved=[]
    for level in range(8):
        for hp in (0,1,hpcap(level)):
            bus,m=setup(prg,0xAEC6,r7=7);progression(bus,level,exp=7000+level,mp=901+level,hp=hp);bus[0xD3]|=0xB0;bus[0x6BE]=0xA5;bus[0x6BF]=0x5A
            invoke(bus,m,0xAEC6);expected=bytes([level,hp])+digits(901+level,3)+digits(7000+level,4)+bytes([0xA5,0x5A])
            assert bytes(bus.ram[0x6C2:0x6CD])==expected
            bus[0xD3]=0xFF;bus[0x6B9]=3;bus[0x6BA]=4;bus[0x6BB]=0x5A;bus.ram[0xEA:0xF8]=bytes(14);bus[0x6BE]=bus[0x6BF]=0
            saved+=invoke(bus,m,0xAEF7,trace=hp==1)
            assert bus[0xD3]==level and bus[0x6B9]==bus[0x6BA]==hpcap(level) and bus[0x6BB]==0x5A
            assert getnum(bus,0xEA,3)==901+level and getnum(bus,0xED,4)==7000+level
            assert getnum(bus,0xF5,3)==mpcap(level) and getnum(bus,0xF1,4)==threshold(level) and (bus[0x6BE],bus[0x6BF])==(0xA5,0x5A)
            obs.append({'level':level,'saved_HP':hp,'restored_HP':bus[0x6B9],'06BB_unchanged':bus[0x6BB],'MP_not_clamped':getnum(bus,0xEA,3)})
    for level in range(8):
        for mp in sorted(set([0,mpcap(level)-1,mpcap(level),min(999,mpcap(level)+1),999])):
            bus,m=setup(prg,0xB829,r7=7);progression(bus,level,mp=mp);invoke(bus,m,0xB829);assert bool(m.p&1)==(mp>mpcap(level))
            obs.append({'compare_MP':mp,'maximum':mpcap(level),'carry':m.p&1})
    add('D_CPU14_SNAPSHOT_RESTORE_DERIVED_VALUES',obs,saved)

    obs=[];saved=[]
    for free in (None,0,*range(1,16),16):
        bus,m=setup(prg,0xE0ED);bus[0x4EF]=16
        for i in range(17):bus[0x57F+i]=0x80
        if free is not None:bus[0x57F+free]=0
        saved+=invoke(bus,m,0xE0ED,trace=free in (None,0,1,15,16));success=free is not None and 1<=free<=15
        assert m.a==(0 if success else 0xFF) and bool(m.p&0x80)==(not success)
        if success:assert m.y==free
        obs.append({'only_free_index':free,'success':success,'returned_index':m.y})
    for full in (False,True):
        bus,m=setup(prg,0xA6AB,r7=8);progression(bus,0,990);m.y=16;putword(bus,0xCB,0x2345);putword(bus,0xC9,0x1234)
        if full:
            for i in range(1,16):bus[0x57F+i]=0x80
        saved+=invoke(bus,m,0xA6AB,trace=True);assert bus[0xD3]==1 and bus[0x3D5]==0xB4 and bus[1]==0xE4
        if not full:assert (bus[0x51B+15],bus[0x52F+15],bus[0x4F3+15],bus[0x507+15],bus[0x557+15],bus[0x56B+15])==(0x45,0x23,0x34,0x12,0xFD,0x96)
        obs.append({'level_up_pool_full':full,'level_after':1,'effect_spawned':not full,'level_and_sound_still_advance':True})
    add('D_CPU15_ALLOCATOR_AND_LEVEL_EFFECT',obs,saved)

    obs=[];saved=[]
    for entry in (0xA7CB,0xA7CE):
        for facing in (0,1):
            for hp in (3,4,5,64):
                for state in (0,0x80):
                    bus,m=setup(prg,entry,r7=8);progression(bus,0,hp=hp);bus[0xD3]=state;bus[0xCD]=facing;m.y=1;bus[0x580]=0x80
                    saved+=invoke(bus,m,entry,trace=hp==4 and not state)
                    assert bus[0x580]==(0 if entry==0xA7CB else 0x80)
                    if state:assert bus[0x6B9]==hp
                    else:
                        assert bus[0x6B9]==max(0,hp-4)
                        if hp<4:assert bus[0xCD]==0xBA+facing
                        else:assert bus[0xD2]==0x3C and bool(bus[0xD3]&0x10)==bool(facing)
                    obs.append({'entry':f'08:{entry:04X}','facing':facing,'HP':hp,'initial_D3':state,'HP_after':bus[0x6B9],'active_after':bus[0x580]})
    add('D_CPU16_DAMAGE_PICKUP_TWO_ENTRIES',obs,saved)

    result={'stage':'02B','model':'py65 original CPU bytes; MMC3/PPU/controller test doubles; no full NES timing','rom_sha256':hashes(rom)['sha256'],'groups':len(groups),'passed_groups':len(groups),'vectors':len(vectors),'trace_rows':len(traces),'results':groups}
    write_json(ROOT/'analysis/cpu_stage02B.json',result);write_csv(ROOT/'analysis/cpu_stage02B_vectors.csv',vectors);write_csv(ROOT/'analysis/cpu_stage02B_trace.csv',traces)
    print(json.dumps({k:v for k,v in result.items() if k!='results'},indent=2))
if __name__=='__main__':main()
