#!/usr/bin/env python3
"""Original-ROM CPU probes for scene setup, player states, damage and HUD.

No ROM patching, full emulator, scanline timing or visual-gameplay claim.
All skipped callees are explicit; principal damage/death sequences have none.
"""
import argparse,json
from baseline import ROOT,verified_rom,write_csv,write_json,hashes
from cpu_stage01b import setup,execute,subroutine_frame

def word(bus,a):return bus[a]|bus[a+1]<<8
def putword(bus,a,value):bus[a]=value&255;bus[a+1]=(value>>8)&255

def main():
    ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();rom,_=verified_rom(a.rom);prg=rom[16:0x20010]
    groups=[];vectors=[];traces=[]
    def add(name,obs,rows=None,stubs=None):
        groups.append({'id':name,'status':'PASS','vector_count':len(obs),'observations':obs,'boundary_stubs':stubs or []})
        vectors.extend({'group':name,'data':json.dumps(x,sort_keys=True)} for x in obs)
        if rows:traces.extend(dict(experiment=name,**x) for x in rows)
    def invoke(bus,m,pc,stops=None,stubs=None,trace=False):
        m.pc=pc;subroutine_frame(bus,m)
        return execute(bus,m,stops or {0x8000},stubs=stubs,trace=trace)

    obs=[];saved=[]
    for i in range(32):
        bus,m=setup(prg,0xA4E9,r7=7);bus[0x9A]=i;bus[0xA1]=0xFF
        bank=bus[0xB262+i];x=bus[0xB1E2+i]*256;y=bus[0xB202+i]*240
        px=x+bus[0xB222+i];py=y+bus[0xB242+i]-1
        ptrs={dst:word(bus,src+2*i) for dst,src in [(0xB9,0xB282),(0xBB,0xB2C2),(0xBF,0xB302),(0xBD,0xB342),(0xC1,0xB382)]}
        palette=word(bus,0xB442+2*i);rows,_=execute(bus,m,{0x8000},trace=i in (0,0x17,0x1A,0x1F))
        assert bus.regs[6:]==[bank,7] and bus[0x3B9]==bank
        assert word(bus,0xA7)==x and word(bus,0xA9)==y and word(bus,0xCB)==px and word(bus,0xC9)==py
        assert all(word(bus,dst)==value for dst,value in ptrs.items())
        assert bus[0xDB]==bus[0xB3E2+i] and bus[0xAF]==bus[0xB402+i] and word(bus,0xAD)==bus[0xB422+i]*240
        assert list(bus.ram[0x123:0x133])==[bus[palette+j] for j in range(16)]
        assert list(bus.ram[0x143:0x153])==[15]*16 and bus[0x44]==bus[palette+25] and bus[0x45]==bus[palette+26]
        assert bus[0xA1]==0x40 and list(bus.ram[0x51:0x58])==[x&255]*7 and list(bus.ram[0x58:0x5F])==[y%240]*7
        profile=bus[0xFE6C+i];stream=word(bus,0xFE8C+2*profile);pairs=[]
        while bus[stream]!=0xF0:pairs.append((bus[stream],bus[stream+1]));stream+=2
        selector=bus[stream+1]
        assert list(bus.ram[0x7F:0x7F+len(pairs)+1])==[p[0] for p in pairs]+[0xF0]
        assert list(bus.ram[0x6A:0x6A+len(pairs)])==[p[1] for p in pairs]
        handler=0xF7C2 if selector else 0xF83D if len(pairs)==1 else 0xF803
        assert bus[0x68]==selector and word(bus,0xDC)==handler
        obs.append({'index':i,'bank8000':bank,'camera':[x,y],'player':[px,py],'palette_pointer':f'{palette:04X}','palette_bank':bank if palette<0xA000 else 7,'irq_profile':profile,'irq_handler':f'{handler:04X}','all_callees_executed':True});saved+=rows
    add('C_CPU01_ALL_SCENE_INITIALIZATIONS',obs,saved)

    obs=[];saved=[]
    for i in range(17):
        bus,m=setup(prg,0xA5AB,r7=7);bus[0x4E2]=i;raw=bus[0xB4A4+i]
        rows,_=execute(bus,m,{0xA990},stubs={(14,0xC749):None,(15,0xF6C1):None},trace=i in (0,16))
        assert bus[0x3B9]==bus.regs[6]==raw&127 and bus[0xA8]==raw>>7
        assert bus[0x44]==bus[0xB482+i] and bus[0x45]==bus[0xB493+i]
        assert all(word(bus,d)==word(bus,s+2*i) for d,s in [(0xB9,0xB4B5),(0xBB,0xB4D7),(0xBF,0xB4F9),(0xBD,0xB51B)])
        obs.append({'layout':i,'encoded_bank':raw,'R6':bus.regs[6],'camera_x_page':bus[0xA8],'stop_before':'07:A990'});saved+=rows
    add('C_CPU02_SPECIAL_LAYOUT_BANKS',obs,saved,['0E:C749 rendering-disable service','0F:F6C1 unreviewed setup service'])

    obs=[]
    for n in (0,1,2,14,15,127,128,129,255):
        bus,m=setup(prg,0xAAB6,r7=7);m.a=n;m.x=0x65
        execute(bus,m,{0x8000},trace=False);expected=n*240 if n<=128 else 0
        assert word(bus,0x22)==expected and m.x==0x65
        obs.append({'input':n,'product':word(bus,0x22),'X_preserved':True})
    add('C_CPU03_SCREEN_MULTIPLICATION_DOMAIN',obs)
    obs=[]
    for high in range(16):
        for low in range(256):
            bus,m=setup(prg,0xF78B);m.a=high;m.y=low
            execute(bus,m,{0x8000},trace=False);position=high*256+low
            assert (m.y,m.a)==divmod(position,240),(high,low,m.y,m.a)
            obs.append({'position':position,'page':m.y,'remainder':m.a})
    add('C_CPU04_Y_NORMALIZATION_DOMAIN',obs)

    obs=[];saved=[]
    for entry,lo,hi in [(0xA0DB,0xA0F2,0xA0F6),(0xA0FA,0xA111,0xA115),(0xA119,0xA130,0xA134)]:
        for flags in range(256):
            bus,m=setup(prg,entry,r7=7);bus[0xDB]=flags;idx=(flags>>1)&3
            target=bus[lo+idx]|bus[hi+idx]<<8 if flags&0x81==0x81 else 0x8000
            rows,_=execute(bus,m,{target},trace=flags in (0x05,0x85,0x87))
            assert m.pc==target
            obs.append({'entry':f'{entry:04X}','DB':flags,'target':f'{target:04X}','target_body_executed':False});saved+=rows
    add('C_CPU05_SCENE_PHASE_DISPATCH',obs,saved)

    obs=[];saved=[]
    for family,chrtable,sprtable,handler,count in [(0,0xB0A5,0xB114,0xB1F2,111),(1,0xBDF3,0xBDF8,0xBE02,5)]:
        for state in range(count*2):
            bus,m=setup(prg,0xACF7,r7=8);m.a=family;bus[0xCD]=state;target=word(bus,handler+(state&254))
            rows,_=execute(bus,m,{target},trace=family==0 and state in (0,0xBA,0xC4,0xCA))
            assert bus[0x46]==bus[chrtable+(state>>1)] and word(bus,0xB6)==word(bus,sprtable+(state&254))
            assert word(bus,0x2C)==target and bus[0xCD]==state
            obs.append({'family':family,'CD':state,'handler':f'{target:04X}','CHR':bus[0x46],'sprite':f'{word(bus,0xB6):04X}','handler_body_executed':False});saved+=rows
    add('C_CPU06_ALL_PLAYER_TABLE_ENTRIES',obs,saved)

    obs=[]
    for flags in range(256):
        bus,m=setup(prg,0xAB19,r7=8);bus[0xCE]=flags;bus[0xD3]=0xFF
        execute(bus,m,{0xACF7},trace=False)
        assert bus[0xCE]==m.a==flags&1 and bus[0xD3]==0x7F
        obs.append({'CE_before':flags,'CE_after':bus[0xCE],'D3_after':bus[0xD3],'dispatch_family':m.a})
    bus,m=setup(prg,0xAB19,r7=8);bus[0xF8]=0x20;bus[0xCE]=0xAA;bus[0xD3]=0xFF
    execute(bus,m,{0xC79D},trace=False);assert bus[0xCE]==0xAA and bus[0xD3]==0x7F
    obs.append({'F8':0x20,'stop':'0E:C79D','CE_preserved':True})
    add('C_CPU07_TRANSIENT_PLAYER_FLAGS',obs)

    obs=[];saved=[]
    boundaries=(0,1,15,16,63,64,175,176,255)
    for hp in boundaries:
        for damage in boundaries:
            for direction in (0,1):
                bus,m=setup(prg,0xDDD9,r7=8);bus[0x6B9]=hp;bus[0xCE]=0x6F;bus[0xDB]=0x85;bus[0xD3]=7;bus[0xCD]=0x11;bus[0xCF]=9
                m.a=damage;m.p=(m.p&254)|direction
                rows,_=execute(bus,m,{0x8000},trace=(hp,damage,direction) in [(16,15,0),(16,16,1),(16,17,0)])
                fatal=damage>hp
                assert bus[0x6B9]==max(0,hp-damage) and m.p&1==direction
                assert bus[0xD3]==(0x87 if fatal else 7|0x20|(0x10 if direction else 0)) and bus[0xCF]==0
                if fatal:assert bus[0xCD]==0xBB and bus[0xCE]==0x60 and bus[0xDB]==0x84 and bus[0xD2]==0 and bus[1]==0xF4
                else:assert bus[0xCD]==0x11 and bus[0xCE]==0x6F and bus[0xDB]==0x85 and bus[0xD2]==60 and bus[1]==0xDE
                obs.append({'hp':hp,'damage':damage,'incoming_carry':direction,'result':bus[0x6B9],'death_branch':fatal,'CD':bus[0xCD],'D3':bus[0xD3]});saved+=rows
    add('C_CPU08_DAMAGE_BOUNDARIES',obs,saved)

    obs=[]
    for timer,protection in [(1,0),(60,0),(255,0),(0,1),(0,255),(60,1)]:
        bus,m=setup(prg,0xDDD9);bus[0xD2]=timer;bus[0x1A4]=protection;bus[0x6B9]=16;bus[0xD3]=7;bus[0xCF]=9;m.a=255;m.p|=1
        before=list(bus.ram[0xC9:0xD4]);execute(bus,m,{0x8000},trace=False)
        assert bus[0x6B9]==16 and list(bus.ram[0xC9:0xD4])==before and m.p&1
        obs.append({'D2':timer,'01A4':protection,'damage_ignored':True})
    add('C_CPU09_DAMAGE_SUPPRESSION',obs)

    obs=[];saved=[]
    for facing in (0,1):
        bus,m=setup(prg,0xDDD9,r7=8);bus[0x6B9]=16;bus[0xCD]=facing;bus[0xC9]=128;bus[0xCB]=128;bus[0x30E]=3;bus[0xDB]=5;m.a=17
        execute(bus,m,{0x8000},trace=False);timeline=[]
        for frame in range(1,91):
            rows,_=invoke(bus,m,0xAB19,trace=frame in (1,15,75,90));saved+=rows
            if frame in (1,14,15,30,45,60,74,75,89,90):timeline.append({'update':frame,'CD':bus[0xCD],'CF':bus[0xCF],'CE':bus[0xCE]})
            assert bool(bus[0xCE]&0x80)==(frame==90)
        assert bus[0xCD]==0xCA|facing
        rows,_=invoke(bus,m,0xD39F,stops={0xD17A},stubs={(15,0xE154):None},trace=True);saved+=rows
        assert bus[0x30E]==2 and m.a==1
        obs.append({'initial_facing':facing,'death_handler_updates':90,'timeline':timeline,'remaining_attempts':bus[0x30E],'restart_target':'0E:D17A','death_animation_and_sprite_code_executed':True})
    add('C_CPU10_DAMAGE_TO_RESTART_CHAIN',obs,saved,['0F:E154 fade boundary after terminal flag; all 90 player updates execute original callees'])

    obs=[];saved=[]
    for start_y,cam_y in [(192,0),(224,0),(255,0),(432,240)]:
        bus,m=setup(prg,0xB007,r7=8);putword(bus,0xC9,start_y);putword(bus,0xA9,cam_y);bus[0xCB]=128
        execute(bus,m,{0x8000},trace=False);frames=0
        while not bus[0xCE]&128 and frames<100:
            frames+=1;rows,_=invoke(bus,m,0xAB19,trace=start_y==192 and frames in (1,12));saved+=rows
        assert frames<100 and bus[0xD3]&128
        expected=next(i for i in range(1,101) if ((start_y+4*i-cam_y)&255)>=240)
        assert frames==expected
        obs.append({'start_y':start_y,'camera_y':cam_y,'updates_to_CE80':frames,'final_y':word(bus,0xC9),'low_byte_threshold':True})
    add('C_CPU11_FALL_TERMINAL_THRESHOLD',obs,saved)

    obs=[]
    for state in (0xC6,0xC7,0xC8,0xC9):
        for timer in (0,1,47,48,49,60):
            bus,m=setup(prg,0xBB6E,r7=8);bus[0xCD]=state;bus[0xD2]=timer;bus[0xD3]=0x37
            stubs={(8,0xBCEF):None,(8,0xAEB1):None,(8,0xAE14):None}
            _,calls=execute(bus,m,{0x8000},stubs=stubs,trace=False)
            if timer>=48:
                assert bus[0xCD]==state and bus[0xD3]==0xB7 and len(calls)==2
                assert calls[-1]['cpu']==('0xAE14' if state&8 else '0xAEB1')
            else:assert bus[0xCD]==state&1 and bus[0xD3]==0x87 and len(calls)==1
            obs.append({'CD':state,'D2':timer,'CD_after':bus[0xCD],'movement_requested':timer>=48})
    add('C_CPU12_HURT_REACTION_GATE',obs,stubs=['08:BCEF physics','08:AEB1 right movement','08:AE14 left movement'])

    obs=[];saved=[]
    for capacity in range(64,177,16):
        for hp in range(capacity+1):
            for delta in (-1,0,1):
                displayed=max(0,min(capacity,hp+delta));bus,m=setup(prg,0xB04B,r7=7)
                bus[0x6BB]=capacity;bus[0x6B9]=hp;bus[0x6BA]=displayed;bus[1]=0
                rows,_=execute(bus,m,{0x8000},trace=capacity==64 and hp in (0,1,15,16,63,64) and delta==0)
                after=min(hp,displayed+1) if displayed<hp else hp
                full=after//16;partial=(after//2)%8;expected=[0x4F]*full+([0x47+partial] if partial else [])
                expected += [0x47]*(capacity//16-len(expected));expected += [0x3F]*(11-len(expected))
                assert bus[0x6BA]==after and list(bus.ram[0x163:0x16E])==expected
                assert bus[1]==(0xA1 if displayed<hp else 0)
                obs.append({'capacity':capacity,'HP':hp,'display_before':displayed,'display_after':after});saved+=rows
    add('C_CPU13_HP_BAR_VALID_DOMAIN',obs,saved)

    obs=[]
    for facing in (0,1):
        for held,prev,older in [(0,0,0),(1,0,0),(2,0,0),(3,0,0),(0,1,2),(0,0,2)]:
            bus,m=setup(prg,0xADE2,r7=8);bus[0xCD]=0xA0|facing;bus[0x20]=held;bus[0x713]=prev;bus[0x714]=older
            execute(bus,m,{0x8000},trace=False);combined=held|prev|older
            expected=0 if combined&1 else 1 if combined&2 else facing
            assert bus[0xCD]==0xA0|expected
            obs.append({'initial_facing':facing,'held':held,'previous':prev,'older':older,'result_facing':expected})
    add('C_CPU14_FACING_HISTORY_PRECEDENCE',obs)

    obs=[];saved=[]
    for entry in (0xF6ED,0xF737):
        for origin in (0,128,255,256):
            for used in (0,63,64):
                bus,m=setup(prg,entry);bus[0x99]=used;bus[0xB1]=2;putword(bus,0xB6,0x400)
                bus.ram[0x400:0x409]=bytes([0xF8,0x21,1,0xF8,0xFF,0,0,0,0]);bus[0x22]=100;putword(bus,0x24,origin);bus[0x2C]=0x20
                rows,_=execute(bus,m,{0x8000},trace=origin==128 and used==0);saved+=rows
                assert bus[0x99]==min(64,used+1)
                if used<64:
                    offset=-8 if entry==0xF6ED else 0;x=origin+offset;visible=0<=x<=255
                    assert list(bus.ram[0x200+used*4:0x204+used*4])==[92 if visible else 0xF1,0x21,0x21 if entry==0xF6ED else 0x61,x&255]
                obs.append({'entry':f'{entry:04X}','origin_x':origin,'initial_sprites':used,'final_sprites':bus[0x99],'synthetic_sprite_data_in_RAM':True})
    add('C_CPU15_METASPRITE_FACING_AND_OAM_LIMIT',obs,saved)

    obs=[]
    for flag in (0,1,3,5,7,8,9,11,13,15,0x89):
        for position in (0,255,256,65535):
            bus,m=setup(prg,0xB04C,r7=8);bus[0xDB]=flag;putword(bus,0xA7,position);putword(bus,0xA9,position)
            execute(bus,m,{0x8000},trace=False);x=y=position
            if flag&9==9:
                index=(flag>>1)&3
                if index==0:y=(y+1)&65535
                elif index==1:y=(y-1)&65535
                elif index==2:x=(x+1)&65535
                else:x=(x-1)&65535
                assert bus[0xDB]==flag|128
            assert (word(bus,0xA7),word(bus,0xA9))==(x,y)
            obs.append({'DB':flag,'before':position,'camera_x':x,'camera_y':y})
    add('C_CPU16_AUTOMATIC_CAMERA_STEP',obs)
    obs=[]
    for sample in range(256):
        for flags in (0,4):
            for effect,active in [(0,0),(8,0),(8,1)]:
                bus,m=setup(prg,0xDB02);bus[0xDB]=flags;bus[0x6BD]=effect;bus[0x593]=active;bus[0xCE]=1;bus[0x6B9]=176;bus[0x9A]=26
                def collision_stub(bus,m):bus[0x3C]=sample;m.a=sample
                _,calls=execute(bus,m,{0x8000},stubs={(14,0xDA07):collision_stub,(14,0xDAC2):collision_stub},trace=False)
                priority=bool(sample&0xC0);damage=30 if not priority and sample&0x10 and not(effect==8 and active) else 0
                expected_return=3 if sample&0x40 else 0 if sample&0x80 else sample
                assert m.a==expected_return and bus[0x6B9]==176-damage
                assert bus[0xCE]==(1 if priority else 1|(sample&12))
                assert calls[0]['cpu']==('0xDA07' if flags else '0xDAC2')
                obs.append({'sample':sample,'DB':flags,'effect':effect,'active':active,'damage':damage,'returned':m.a})
    add('C_CPU17_TERRAIN_CLASSIFICATION_AND_DAMAGE',obs,stubs=['0E:DA07 collision sample supplied in 3C/A','0E:DAC2 collision sample supplied in 3C/A; actual geometry lookup not exercised'])
    obs=[]
    for initial,target in [(0,0xB165),(1,0xF681),(2,0xB04B),(3,0xB104),(4,0xB0B0),(5,0xB165),(0x80,0x8000),(0xFF,0x8000)]:
        bus,m=setup(prg,0xB022,r7=7);bus[0xA1]=initial
        execute(bus,m,{target},trace=False)
        assert bus[0xA1]==(initial if initial&128 else 1 if initial==5 else initial+1)
        obs.append({'A1_before':initial,'A1_after':bus[0xA1],'target':f'{target:04X}','target_body_executed':False})
    add('C_CPU18_HUD_DISPATCH_PHASES',obs)
    result={'stage':'02A','model':'py65 original CPU bytes; MMC3/PPU/controller test doubles; no full NES timing','rom_sha256':hashes(rom)['sha256'],'groups':len(groups),'passed_groups':len(groups),'vectors':len(vectors),'trace_rows':len(traces),'results':groups}
    write_json(ROOT/'analysis/cpu_stage02A.json',result);write_csv(ROOT/'analysis/cpu_stage02A_vectors.csv',vectors);write_csv(ROOT/'analysis/cpu_stage02A_trace.csv',traces)
    print(json.dumps({k:v for k,v in result.items() if k!='results'},indent=2))
if __name__=='__main__':main()
